# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

XRayLabTool is a Python package for calculating X-ray optical properties of materials using CXRO/NIST atomic scattering factor databases. It provides both a Python API and CLI for synchrotron/X-ray science applications.

- **Python**: >=3.12
- **Package Manager**: uv (preferred), pip
- **Version**: See `pyproject.toml` and `xraylabtool/__init__.py`

## Common Commands

### Development Setup
```bash
uv pip install -e .[all]           # Full dev install with uv
pip install -e .[dev]              # Development dependencies only
make dev-setup                     # Complete environment setup
```

### Testing
```bash
pytest tests/ -v                   # All tests
pytest tests/ -v --no-cov          # Fast (no coverage)
pytest tests/unit/ -v              # Unit tests only
pytest tests/integration/ -v       # Integration tests only
pytest tests/performance/ -v       # Performance benchmarks
pytest -m "unit" -v                # By marker
python run_tests.py                # Comprehensive test suite
make test-fast                     # Quick test run
make claude                        # Full quality analysis (pre-commit)
```

### Code Quality
```bash
ruff check xraylabtool/ tests/ --fix   # Lint with auto-fix
ruff format xraylabtool/ tests/        # Format code
black --check xraylabtool/ tests/      # Check formatting
isort xraylabtool/ tests/              # Sort imports
mypy xraylabtool/ --strict             # Type checking
python scripts/run_type_check.py --target core  # Enhanced type check
```

### Documentation
```bash
sphinx-build -b html docs docs/_build/html   # Build docs
make docs-serve                              # Build and serve locally
```

### CLI Testing
```bash
xraylabtool --version
xraylabtool calc SiO2 -e 10.0 -d 2.2
xraylabtool --help
```

## Architecture

### Source Layout (`xraylabtool/`)

```
xraylabtool/
├── __init__.py           # Lazy imports for fast startup, public API
├── constants.py          # Physical constants (PLANCK, AVOGADRO, etc.)
├── utils.py              # parse_formula(), energy/wavelength conversions
├── exceptions.py         # Custom exception hierarchy
├── calculators/          # Core X-ray calculations
│   ├── core.py           # calculate_single_material_properties(), XRayResult
│   └── derived_quantities.py  # Critical angle, attenuation, SLD
├── data_handling/        # Atomic data caching and processing
│   ├── atomic_cache.py   # Scattering factor cache (92 elements)
│   ├── adaptive_preloading.py  # Smart cache warming
│   └── batch_processing.py     # Parallel processing (threshold: 20 items)
├── interfaces/           # CLI and shell completion
│   ├── cli.py            # Main CLI entry point
│   └── completion_v2/    # Virtual environment-centric completion
├── validation/           # Input validation and exceptions
├── optimization/         # Performance: vectorized_core, memory_profiler
├── analysis/             # Material comparison (comparator.py)
├── io/                   # File I/O operations
├── export/               # CSV/JSON export
├── gui/                  # PySide6 desktop application
└── data/AtomicScatteringFactor/  # .nff data files (CXRO)
```

### Key Design Patterns

1. **Lazy Imports**: `__init__.py` uses `__getattr__` for ultra-fast startup (~130ms cold start)
2. **XRayResult Dataclass**: All calculations return this with snake_case fields (legacy CamelCase supported with deprecation warnings)
3. **Adaptive Batch Processing**: Sequential for <20 items, parallel (ThreadPoolExecutor) for >=20
4. **Smart Cache Warming**: Formula-specific element loading vs. full 92-element preload

### Test Structure

```
tests/
├── unit/           # Component tests (core, formula parsing, validation)
├── integration/    # CLI, cross-module, export tests
├── performance/    # Benchmarks, optimization validation, memory
└── fixtures/       # Test utilities and configuration
```

Test markers: `unit`, `integration`, `performance`, `slow`, `memory`, `benchmark`, `smoke`

## Key Files

- `pyproject.toml` - All project config (deps, pytest, mypy, ruff, black)
- `Makefile` - Development commands (run `make help`)
- `run_tests.py` - Comprehensive test runner script
- `scripts/run_type_check.py` - Enhanced mypy wrapper

## Coding Standards

- Use explicit imports
- NumPy-style docstrings
- Type hints for all public APIs
- Snake_case for new field names in XRayResult
- Energy range: 0.03-30 keV
