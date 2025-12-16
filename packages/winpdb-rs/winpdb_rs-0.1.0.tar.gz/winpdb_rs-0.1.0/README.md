# winpdb_rs

High-performance Python bindings for Microsoft PDB (Program Database) parsing, powered by the [getsentry/pdb](https://github.com/getsentry/pdb) Rust crate.

## Features

- **Fast**: 10-100x faster than pure Python PDB parsers
- **Cross-platform**: Works on Windows, Linux, and macOS
- **No DIA SDK required**: Pure Rust implementation, no Windows dependencies
- **Type hints**: Full type annotations and stub files included

## Installation

### From source (requires Rust toolchain)

```bash
# Install maturin if you don't have it
pip install maturin

# Build and install
cd winpdb_rs
maturin develop --release
```

### Pre-built wheels

Pre-built wheels are available for common platforms:

```bash
pip install winpdb-rs
```

## Usage

### Find a symbol by name

```python
import winpdb_rs

# Find a specific symbol
result = winpdb_rs.find_symbol("ntdll.pdb", "LdrLoadDll")
if result:
    print(f"Found: {result.name}")
    print(f"RVA: 0x{result.rva:x}")
    print(f"Segment: {result.segment}, Offset: 0x{result.offset:x}")
```

### Get function info for PE analysis

```python
# Returns (segment, offset, rva, matched_name)
info = winpdb_rs.get_function_info("ntdll.pdb", "LdrLoadDll")
if info:
    segment, offset, rva, name = info
    print(f"{name} at section {segment}+0x{offset:x} (RVA: 0x{rva:x})")
```

### Batch symbol lookup

```python
# More efficient than individual lookups
symbols = winpdb_rs.find_symbols_batch(
    "ntdll.pdb",
    ["LdrLoadDll", "NtCreateFile", "RtlInitUnicodeString"]
)
for name, info in symbols.items():
    print(f"{name}: RVA 0x{info.rva:x}")
```

### List all symbols

```python
result = winpdb_rs.get_all_symbols("ntdll.pdb")
print(f"Found {len(result)} symbols")
for sym in result.symbols[:10]:
    print(f"  {sym.name}: 0x{sym.rva:x}")
```

### Build a symbol table

```python
# Get all symbols as a dict for fast repeated lookups
table = winpdb_rs.build_symbol_table("ntdll.pdb")
# table[name] = (segment, offset, rva, is_function)
```

## API Reference

### Classes

#### `SymbolInfo`
Information about a found symbol.
- `name: str` - Symbol name
- `segment: int` - Section number (1-indexed)
- `offset: int` - Offset within section
- `rva: int` - Relative Virtual Address
- `is_function: bool` - Whether symbol is a function

#### `SymbolLookupResult`
Container for symbol lookup results.
- `symbols: List[SymbolInfo]` - List of found symbols

### Functions

| Function | Description | Returns |
|----------|-------------|---------|
| `find_symbol(pdb_path, name)` | Find symbol by name | `Optional[SymbolInfo]` |
| `get_symbol_rva(pdb_path, name)` | Get RVA directly | `Optional[Tuple[int, str]]` |
| `get_function_info(pdb_path, name)` | Get full function info | `Optional[Tuple[int,int,int,str]]` |
| `get_all_symbols(pdb_path)` | List all symbols | `SymbolLookupResult` |
| `build_symbol_table(pdb_path)` | Build lookup dict | `Dict[str, Tuple]` |
| `find_symbols_batch(pdb_path, names)` | Batch lookup | `Dict[str, SymbolInfo]` |
| `get_pdb_info(pdb_path)` | Get PDB metadata | `Dict[str, str]` |

## Integration with pe-signgen

This package is designed to be a drop-in replacement for pdbparse in pe-signgen:

```python
# In symbols.py
try:
    import winpdb_rs
    _HAS_NATIVE = True
except ImportError:
    _HAS_NATIVE = False
    # Fall back to pure Python

# Use native when available
if _HAS_NATIVE:
    result = winpdb_rs.get_function_info(pdb_path, func_name)
```

## Building from Source

### Requirements

- Rust 1.70+ (install via [rustup](https://rustup.rs/))
- Python 3.8+
- maturin (`pip install maturin`)

### Build steps

```bash
# Development build
maturin develop

# Release build
maturin develop --release

# Build wheel
maturin build --release
```

## License

MIT 

## Credits

- [getsentry/pdb](https://github.com/getsentry/pdb) - The Rust PDB parsing library
- [PyO3](https://pyo3.rs/) - Rust-Python bindings
