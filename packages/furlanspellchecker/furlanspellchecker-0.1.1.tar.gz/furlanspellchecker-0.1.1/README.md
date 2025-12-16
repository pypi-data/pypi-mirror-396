# FurlanSpellChecker

A comprehensive spell checker for the Friulian language with CLI and pipeline service.

## Overview

FurlanSpellChecker is a Python library and command-line tool for spell checking text in the Friulian (Furlan) language. It provides a complete spell checking pipeline with dictionary management, phonetic algorithms, and text processing capabilities specifically designed for Friulian linguistic features.

## Features

- **Complete spell checking pipeline** - Tokenization, spell checking, and correction suggestions
- **Friulian-specific phonetic algorithm** - Custom phonetic similarity for better suggestions
- **Flexible dictionary system** - Support for multiple dictionaries with RadixTree optimization
- **Command-line interface** - Easy-to-use CLI for batch processing and interactive use
- **Configurable processing** - Extensive configuration options for different use cases
- **Python API** - Full programmatic access to all functionality

## Installation

### From PyPI (when available)

```bash
pip install furlanspellchecker
```

### From source

```bash
git clone https://github.com/daurmax/FurlanSpellChecker.git
cd FurlanSpellChecker
pip install -e .
```

### Development installation

```bash
git clone https://github.com/daurmax/FurlanSpellChecker.git
cd FurlanSpellChecker
pip install -e ".[dev]"
```

## Quick Start

### Command Line Usage

#### Interactive Mode (New!)

Start the interactive REPL with colored output and multilingual support:

```bash
furlanspellchecker interactive
```

Features:
- **ASCII art logo** - Beautiful Friulian-themed startup banner
- **Colored output** - Easy-to-read colored console output (requires colorama)
- **Multilingual interface** - Choose between English, Friulian (Furlan), and Italian
- **Interactive commands**:
  - `C <words>...` - Check spelling of one or more words
  - `S <word>` - Get suggestions for a misspelled word
  - `Q` - Quit the application

Options:
```bash
# Specify language directly (skip selection prompt)
furlanspellchecker interactive --language fur  # Friulian
furlanspellchecker interactive --language it   # Italian
furlanspellchecker interactive --language en   # English

# Disable colored output
furlanspellchecker interactive --no-color
```

Example session:
```
> C preon lenghe
preon is correct
lenghe is correct

> S preo
preo is incorrect
Suggestions are: preon, pren, predi

> Q
Closing the application. Goodbye!
```

#### COF Protocol Mode (for automation)

For automation and testing compatibility with the Perl COF implementation:

```bash
# Read commands from stdin
echo -e "c preon\ns sbaliât\nq" | furlanspellchecker cof-cli

# With options
furlanspellchecker cof-cli --encoding utf8 --max-suggestions 5
```

Protocol commands:
- `c <word> [<word2> ...]` - Check spelling (returns `ok\n` or `no\n`)
- `s <word>` - Get suggestions (returns `ok\n` or `no\t<sug1>,<sug2>,...\n`)
- `q` - Quit

This mode ensures 100% output format compatibility with the original Perl COF CLI for integration with existing tools and test suites.

#### Database Management

Download dictionary databases:
```bash
furlanspellchecker download-dicts
```

Check database status:
```bash
furlanspellchecker db-status
```

Extract local ZIP files:
```bash
furlanspellchecker extract-dicts /path/to/zipfile.zip
```

#### Standard Commands

Check a single word:
```bash
furlanspellchecker lookup "cjase"
```

Get suggestions for a misspelled word:
```bash
furlanspellchecker suggest "cjasa"
```

Check text from a file:
```bash
furlanspellchecker file input.txt -o corrected.txt
```

### Python API Usage

```python
import asyncio
from furlan_spellchecker import SpellCheckPipeline

# Initialize the spell checker
pipeline = SpellCheckPipeline()

# Check text
result = pipeline.check_text("Cheste e je une frâs in furlan.")
print(f"Incorrect words: {result['incorrect_count']}")

# Check a single word
async def check_word():
    word_result = await pipeline.check_word("furlan")
    print(f"'{word_result['word']}' is {'correct' if word_result['is_correct'] else 'incorrect'}")

asyncio.run(check_word())
```

## Architecture

FurlanSpellChecker is organized as a set of modular components:

| Module | Responsibility |
|--------|----------------|
| `core` | Abstract interfaces, exceptions, and type definitions |
| `entities` | Data structures for processed text elements |
| `spellchecker` | Main spell checking logic and text processing |
| `dictionary` | Dictionary management and RadixTree implementation |
| `database` | Database access, download management, and caching |
| `phonetic` | Friulian-specific phonetic algorithm |
| `services` | High-level pipeline and I/O services |
| `config` | Configuration schemas and management |
| `cli` | Command-line interface |
| `data` | Packaged dictionary data |

## Configuration

The spell checker can be configured through configuration files or programmatically:

```python
from furlan_spellchecker import FurlanSpellCheckerConfig, DictionaryConfig

config = FurlanSpellCheckerConfig(
    dictionary=DictionaryConfig(
        max_suggestions=5,
        use_phonetic_suggestions=True
    )
)
```

## Database Files

FurlanSpellChecker uses database files for dictionary lookups, word frequencies, elisions, and error corrections. These files are **automatically downloaded** from GitHub Releases on first use.

### Automatic Download

When you first use the spell checker, it will automatically download the required database files (~63 MB) and cache them locally in:
- **Windows**: `C:\Users\<username>\.cache\furlan_spellchecker\databases`
- **Linux/Mac**: `~/.cache/furlan_spellchecker/databases`

No manual intervention required! 🎉

### Database Contents

| Database | Size | Description |
|----------|------|-------------|
| `words.sqlite` | ~289 MB | Phonetic dictionary (7.4M phonetic hashes, 10.1M words) |
| `frequencies.sqlite` | ~2 MB | Word frequency data (69,051 words) for suggestion ranking |
| `elisions.sqlite` | ~0.2 MB | Elision rules (10,604 words) |
| `errors.sqlite` | ~0.01 MB | Common error corrections (301 patterns) |
| `words_radix_tree.rt` | ~9.7 MB | RadixTree for fast word lookups |

**Total**: ~300 MB (SQLite + binary formats)

### Manual Download (Optional)

If you prefer to download manually or work offline:

1. Download from: [Latest Database Release](https://github.com/daurmax/FurlanSpellChecker/releases/tag/0.0.2-dictionaries-sqlite)
2. Extract ZIP files to cache directory
3. The spell checker will use the cached files

### For Contributors: Creating Database Releases

If you need to create a new database release (e.g., after updating word lists):

```bash
# Install dependencies
pip install PyGithub

# Set GitHub token
$env:GITHUB_TOKEN = "your_token_here"

# Create release
python scripts/create_database_release.py --tag v1.1.0-databases
```

See [Database Release Guide](docs/development/GitHub_Release_Instructions.md) for detailed instructions.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Clone the repository
2. Install development dependencies: `pip install -e ".[dev]"`
3. Run tests: `pytest`
   - Run specific test modules: `pytest tests/test_radix_tree.py -v`
   - Run performance tests: `pytest tests/test_radix_tree.py -m slow -v`
   - Skip slow tests: `pytest -m "not slow"`
4. Run linting: `ruff check src tests`
5. Run type checking: `mypy src`

### Test Suite

The project includes comprehensive test coverage with special focus on:

- **COF Compatibility**: RadixTree tests ensure 1:1 compatibility with original COF implementation
- **Edge Case Testing**: Comprehensive handling of empty input, special characters, and invalid data
- **Performance Testing**: Batch processing and stress testing for production readiness
- **Integration Testing**: End-to-end testing with DatabaseManager and other components

**RadixTree Test Coverage** (24 tests total):
- **COF Compatibility** (13 tests): Core suggestion matching with verified test cases
- **Edge Cases** (7 tests): Friulian-specific character handling (cjàse, furlanâ, çi)
- **Performance** (2 tests): Batch processing and stress testing benchmarks  
- **Integration** (2 tests): DatabaseManager integration and availability checks

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Based on the original C# implementation in CoretorOrtograficFurlan-Core
- Inspired by the architecture of FurlanG2P
- Dictionary data sourced from Friulian linguistic resources

## Related Projects

- [CoretorOrtograficFurlan-Core](https://github.com/daurmax/CoretorOrtograficFurlan-Core) - Original C# implementation
- [FurlanG2P](https://github.com/daurmax/FurlanG2P) - Friulian grapheme-to-phoneme conversion