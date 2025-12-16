use pdb::{FallibleIterator, PdbInternalSectionOffset, Rva, SymbolData, PDB};
use pyo3::exceptions::{PyFileNotFoundError, PyRuntimeError};
use pyo3::prelude::*;
use std::collections::HashMap;
use std::fs::File;
use std::path::Path;

/// Information about a found symbol
#[pyclass]
#[derive(Clone, Debug)]
pub struct SymbolInfo {
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub segment: u16,
    #[pyo3(get)]
    pub offset: u32,
    #[pyo3(get)]
    pub rva: u32,
    #[pyo3(get)]
    pub is_function: bool,
}

#[pymethods]
impl SymbolInfo {
    fn __repr__(&self) -> String {
        format!(
            "SymbolInfo(name='{}', segment={}, offset=0x{:x}, rva=0x{:x}, is_function={})",
            self.name, self.segment, self.offset, self.rva, self.is_function
        )
    }
}

/// Result from looking up all symbols
#[pyclass]
#[derive(Clone, Debug)]
pub struct SymbolLookupResult {
    #[pyo3(get)]
    pub symbols: Vec<SymbolInfo>,
}

#[pymethods]
impl SymbolLookupResult {
    fn __len__(&self) -> usize {
        self.symbols.len()
    }

    fn __repr__(&self) -> String {
        format!("SymbolLookupResult({} symbols)", self.symbols.len())
    }
}

/// Canonicalize symbol name variants for matching
fn canonicalize_variants(name: &str) -> Vec<String> {
    let mut variants = Vec::new();
    let base = name.to_string();
    let lower = base.to_lowercase();

    variants.push(base.clone());
    variants.push(lower.clone());

    // Handle underscore prefix
    if let Some(stripped) = base.strip_prefix('_') {
        variants.push(stripped.to_string());
        variants.push(stripped.to_lowercase());
    }

    // Handle stdcall @N suffix
    if let Some(at_pos) = base.rfind('@') {
        if base[at_pos + 1..].chars().all(|c| c.is_ascii_digit()) {
            let stripped = &base[..at_pos];
            variants.push(stripped.to_string());
            variants.push(stripped.to_lowercase());
            if let Some(s2) = stripped.strip_prefix('_') {
                variants.push(s2.to_string());
                variants.push(s2.to_lowercase());
            }
        }
    }

    variants.sort();
    variants.dedup();
    variants
}

/// Check if two symbol names match
fn names_match(name1: &str, name2: &str) -> bool {
    let name1_variants = canonicalize_variants(name1);
    let name2_variants = canonicalize_variants(name2);

    for n in &name1_variants {
        for h in &name2_variants {
            if n.eq_ignore_ascii_case(h) {
                return true;
            }
        }
    }
    false
}
/// Find a specific symbol by name in a PDB file
#[pyfunction]
fn find_symbol(pdb_path: &str, symbol_name: &str) -> PyResult<Option<SymbolInfo>> {
    let path = Path::new(pdb_path);
    if !path.exists() {
        return Err(PyFileNotFoundError::new_err(format!(
            "File not found: {}",
            pdb_path
        )));
    }

    let file = File::open(path)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to open {}: {}", pdb_path, e)))?;

    let mut pdb = PDB::open(file)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to parse PDB: {}", e)))?;

    let address_map = pdb
        .address_map()
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to get address map: {}", e)))?;

    let global_symbols = pdb
        .global_symbols()
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to get global symbols: {}", e)))?;

    let mut best_match: Option<SymbolInfo> = None;

    let mut iter = global_symbols.iter();
    while let Some(symbol) = iter
        .next()
        .map_err(|e| PyRuntimeError::new_err(format!("Error iterating symbols: {}", e)))?
    {
        if let Ok(data) = symbol.parse() {
            let (name, segment, offset, is_function) = match data {
                SymbolData::Public(pub_sym) => (
                    pub_sym.name.to_string().to_string(),
                    pub_sym.offset.section,
                    pub_sym.offset.offset,
                    pub_sym.function,
                ),
                SymbolData::Procedure(proc) => (
                    proc.name.to_string().to_string(),
                    proc.offset.section,
                    proc.offset.offset,
                    true,
                ),
                _ => continue,
            };

            if names_match(symbol_name, &name) {
                let pdb_offset = PdbInternalSectionOffset {
                    section: segment,
                    offset,
                };
                let rva = pdb_offset.to_rva(&address_map).unwrap_or(Rva(0));

                let info = SymbolInfo {
                    name: name.clone(),
                    segment,
                    offset,
                    rva: rva.0,
                    is_function,
                };

                // Prefer exact match
                if name.eq_ignore_ascii_case(symbol_name) {
                    return Ok(Some(info));
                }
                if best_match.is_none() {
                    best_match = Some(info);
                }
            }
        }
    }

    Ok(best_match)
}

/// Get function info: (segment, offset, rva, matched_name)
#[pyfunction]
fn get_function_info(
    pdb_path: &str,
    symbol_name: &str,
) -> PyResult<Option<(u16, u32, u32, String)>> {
    match find_symbol(pdb_path, symbol_name)? {
        Some(info) => Ok(Some((info.segment, info.offset, info.rva, info.name))),
        None => Ok(None),
    }
}

/// Get symbol RVA: (rva, matched_name)
#[pyfunction]
fn get_symbol_rva(pdb_path: &str, symbol_name: &str) -> PyResult<Option<(u32, String)>> {
    match find_symbol(pdb_path, symbol_name)? {
        Some(info) => Ok(Some((info.rva, info.name))),
        None => Ok(None),
    }
}

/// Get all public symbols from a PDB
#[pyfunction]
fn get_all_symbols(pdb_path: &str) -> PyResult<SymbolLookupResult> {
    let path = Path::new(pdb_path);
    if !path.exists() {
        return Err(PyFileNotFoundError::new_err(format!(
            "File not found: {}",
            pdb_path
        )));
    }

    let file = File::open(path)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to open {}: {}", pdb_path, e)))?;

    let mut pdb = PDB::open(file)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to parse PDB: {}", e)))?;

    let address_map = pdb
        .address_map()
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to get address map: {}", e)))?;

    let global_symbols = pdb
        .global_symbols()
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to get global symbols: {}", e)))?;

    let mut symbols = Vec::new();

    let mut iter = global_symbols.iter();
    while let Some(symbol) = iter
        .next()
        .map_err(|e| PyRuntimeError::new_err(format!("Error iterating symbols: {}", e)))?
    {
        if let Ok(data) = symbol.parse() {
            match data {
                SymbolData::Public(pub_sym) => {
                    let pdb_offset = PdbInternalSectionOffset {
                        section: pub_sym.offset.section,
                        offset: pub_sym.offset.offset,
                    };
                    let rva = pdb_offset.to_rva(&address_map).unwrap_or(Rva(0));

                    symbols.push(SymbolInfo {
                        name: pub_sym.name.to_string().to_string(),
                        segment: pub_sym.offset.section,
                        offset: pub_sym.offset.offset,
                        rva: rva.0,
                        is_function: pub_sym.function,
                    });
                }
                SymbolData::Procedure(proc) => {
                    let pdb_offset = PdbInternalSectionOffset {
                        section: proc.offset.section,
                        offset: proc.offset.offset,
                    };
                    let rva = pdb_offset.to_rva(&address_map).unwrap_or(Rva(0));

                    symbols.push(SymbolInfo {
                        name: proc.name.to_string().to_string(),
                        segment: proc.offset.section,
                        offset: proc.offset.offset,
                        rva: rva.0,
                        is_function: true,
                    });
                }
                _ => {}
            }
        }
    }

    Ok(SymbolLookupResult { symbols })
}

/// Batch lookup multiple symbols
#[pyfunction]
fn find_symbols_batch(
    pdb_path: &str,
    symbol_names: Vec<String>,
) -> PyResult<HashMap<String, SymbolInfo>> {
    let path = Path::new(pdb_path);
    if !path.exists() {
        return Err(PyFileNotFoundError::new_err(format!(
            "File not found: {}",
            pdb_path
        )));
    }

    let file = File::open(path)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to open {}: {}", pdb_path, e)))?;

    let mut pdb = PDB::open(file)
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to parse PDB: {}", e)))?;

    let address_map = pdb
        .address_map()
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to get address map: {}", e)))?;

    let global_symbols = pdb
        .global_symbols()
        .map_err(|e| PyRuntimeError::new_err(format!("Failed to get global symbols: {}", e)))?;

    let mut results: HashMap<String, SymbolInfo> = HashMap::new();

    let mut iter = global_symbols.iter();
    while let Some(symbol) = iter
        .next()
        .map_err(|e| PyRuntimeError::new_err(format!("Error iterating symbols: {}", e)))?
    {
        if let Ok(data) = symbol.parse() {
            let (name, segment, offset, is_function) = match data {
                SymbolData::Public(pub_sym) => (
                    pub_sym.name.to_string().to_string(),
                    pub_sym.offset.section,
                    pub_sym.offset.offset,
                    pub_sym.function,
                ),
                SymbolData::Procedure(proc) => (
                    proc.name.to_string().to_string(),
                    proc.offset.section,
                    proc.offset.offset,
                    true,
                ),
                _ => continue,
            };

            for sym_name in &symbol_names {
                if !results.contains_key(sym_name) && names_match(sym_name, &name) {
                    let pdb_offset = PdbInternalSectionOffset {
                        section: segment,
                        offset,
                    };
                    let rva = pdb_offset.to_rva(&address_map).unwrap_or(Rva(0));

                    results.insert(
                        sym_name.clone(),
                        SymbolInfo {
                            name: name.clone(),
                            segment,
                            offset,
                            rva: rva.0,
                            is_function,
                        },
                    );
                }
            }

            if results.len() == symbol_names.len() {
                break;
            }
        }
    }

    Ok(results)
}

/// Python module definition
#[pymodule]
fn winpdb_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<SymbolInfo>()?;
    m.add_class::<SymbolLookupResult>()?;
    m.add_function(wrap_pyfunction!(find_symbol, m)?)?;
    m.add_function(wrap_pyfunction!(get_function_info, m)?)?;
    m.add_function(wrap_pyfunction!(get_symbol_rva, m)?)?;
    m.add_function(wrap_pyfunction!(get_all_symbols, m)?)?;
    m.add_function(wrap_pyfunction!(find_symbols_batch, m)?)?;
    Ok(())
}
