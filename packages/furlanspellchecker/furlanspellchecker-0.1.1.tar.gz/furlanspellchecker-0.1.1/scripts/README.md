# FurlanSpellChecker Scripts

This directory contains utility scripts for FurlanSpellChecker development, debugging, and maintenance.

## Available Scripts

### `word_lookup.py`
**Word lookup and metadata inspection utility** for debugging and database analysis.

Query the FurlanSpellChecker database to check if specific words exist and retrieve their associated metadata.

**Usage:**
```bash
python scripts/word_lookup.py --word WORD [options]
python scripts/word_lookup.py --batch FILE [options]
```

**Options:**
- `--word, -w WORD` - Look up a single word
- `--batch, -b FILE` - Look up words from file (one per line)
- `--suggest, -s` - Include suggestions for the word
- `--phonetic, -p` - Include phonetic code
- `--similar, -m` - Include similar words (within edit distance 1-2)
- `--json` - Output in JSON format
- `--verbose, -v` - Verbose output with all metadata
- `--help, -h` - Show help message

**Examples:**
```bash
# Basic word lookup
python scripts/word_lookup.py --word Cjas

# Detailed lookup with suggestions and phonetic
python scripts/word_lookup.py --word cjasa --suggest --phonetic

# Check multiple words
python scripts/word_lookup.py --batch words_to_check.txt

# Full metadata with similar words
python scripts/word_lookup.py --word furla --verbose --similar

# JSON output for scripting
python scripts/word_lookup.py --word cjase --json
```

**Output:**
For each word, displays:
- Existence in dictionary (radix tree)
- Frequency value
- Phonetic code (if requested)
- Suggestions (if requested)
- Similar words (if requested)

**Use cases:**
- Debugging why specific words appear/don't appear in suggestions
- Comparing database content between COF (Perl) and Python implementations
- Verifying word frequencies and phonetic codes
- Investigating ranking differences

---

### `create_database_release.py`
Database packaging and release preparation utility.

**Usage:**
```bash
python scripts/create_database_release.py [options]
```

Creates packaged database files for distribution.

---

### `prepare_release.py`
Release preparation and versioning utility.

**Usage:**
```bash
python scripts/prepare_release.py [version]
```

Prepares the project for a new release with proper versioning.

---

## Development Guidelines

### Adding New Scripts
1. Use descriptive names following Python conventions (`snake_case.py`)
2. Include comprehensive docstring with usage examples
3. Support both command-line and programmatic usage where applicable
4. Provide `--help` option with detailed usage information
5. Use `argparse` for consistent CLI argument parsing
6. Support batch processing with files where applicable

### Conventions
- **Naming**: Use descriptive names that clearly indicate purpose
- **Scope**: Each script should focus on a specific task or utility
- **Documentation**: Include inline documentation and usage examples
- **Output**: Support multiple output formats (text, JSON) for scripting
- **Error Handling**: Provide clear error messages and proper exit codes

### Testing
- Scripts should be testable in isolation
- Avoid modifying production databases
- Use test fixtures when possible
- Document expected behavior and edge cases

---

## Comparison with COF Utilities

The Python scripts in this directory parallel the Perl utilities in `COF/util/`:

| Python Script | COF Perl Utility | Purpose |
|---------------|------------------|---------|
| `word_lookup.py` | `word_lookup_utils.pl` | Word metadata and database inspection |
| (future) | `spellchecker_utils.pl` | Spell checking and suggestions |
| (future) | `encoding_utils.pl` | Encoding inspection and validation |

Use `word_lookup.py` alongside COF's `word_lookup_utils.pl` to:
- Compare database content between implementations
- Verify consistent behavior across Perl and Python
- Debug ranking and suggestion differences
- Validate data migration and compatibility

---

## Support

For general development guidelines, see:
- `../docs/development/` - Development documentation
- `../AGENTS.md` - AI agent development guidelines
- `../README.md` - Project overview and setup

For testing, see:
- `../tests/README.md` - Test suite documentation
- `../pytest.ini` - pytest configuration
