# CLI Documentation

FurlanSpellChecker provides multiple CLI interfaces to suit different use cases, from interactive human use to automated testing.

## Overview

The CLI offers three main modes:

1. **Interactive Mode** - Rich REPL interface with colors, ASCII art, and i18n support
2. **COF Protocol Mode** - stdin/stdout automation compatible with Perl COF implementation
3. **Standard Commands** - Traditional CLI commands for common operations

## Interactive Mode

The interactive mode provides a user-friendly REPL (Read-Eval-Print Loop) interface with enhanced visual features.

### Basic Usage

```bash
furlanspellchecker interactive
```

On startup, you'll see:
1. ASCII art logo
2. Language selection prompt
3. Command instructions
4. Interactive prompt (`>`)

### Language Selection

You can choose between three languages for the interface:

- **English** (`en`) - International users
- **Friulian** (`fur`) - Native Friulian speakers
- **Italian** (`it`) - Italian speakers

**Automatic selection:**
```bash
furlanspellchecker interactive --language fur   # Friulian
furlanspellchecker interactive --language it    # Italian
furlanspellchecker interactive --language en    # English
```

**Interactive selection:**
```
Select language / Sielç lenghe / Seleziona lingua:
1. English
2. Furlan
3. Italiano

Your choice / La tô sielte / La tua scelta (1-3): 2
```

### Commands

#### Check Command (C)

Check the spelling of one or more words:

```
> C preon lenghe
preon is correct
lenghe is correct

> C preon sbaliât xyzabc
preon is correct
sbaliât is incorrect
xyzabc is incorrect
```

**Features:**
- Multiple words in one command
- Automatic endpoint stripping (words ending with `.` have the period removed)
- Color-coded output (green=correct, red=incorrect)

#### Suggest Command (S)

Get spelling suggestions for a word:

```
> S preo
preo is incorrect
Suggestions are: preon, pren, predi

> S preon
preon is correct
```

**Features:**
- Shows up to 10 suggestions by default
- Suggestions ranked by phonetic similarity and frequency
- Indicates when word is already correct

#### Quit Command (Q)

Exit the interactive mode:

```
> Q
Closing the application. Goodbye!
```

**Alternative exit methods:**
- Press `Ctrl+D` (EOF)
- Press `Ctrl+C` (interrupt)

### Options

#### `--language`, `-l`

Specify the interface language directly, skipping the selection prompt:

```bash
furlanspellchecker interactive --language fur
```

Valid values: `en`, `fur`, `it`

#### `--no-color`

Disable colored output (useful for terminals without color support):

```bash
furlanspellchecker interactive --no-color
```

### Localization

The interface strings are stored in JSON files and support three languages:

**Localized strings include:**
- Command instructions
- Status messages ("correct", "incorrect", "is")
- Suggestions labels
- Error messages
- Exit messages

**Location:** `src/furlan_spellchecker/cli/localization/*.json`

## COF Protocol Mode

The COF protocol mode provides 100% output format compatibility with the original Perl COF CLI, enabling seamless integration with existing automation tools and test suites.

### Basic Usage

```bash
# Interactive stdin/stdout
furlanspellchecker cof-cli

# Pipe commands
echo -e "c preon\nq" | furlanspellchecker cof-cli

# From file
furlanspellchecker cof-cli < commands.txt
```

### Protocol Specification

#### Commands (stdin)

**Check command:**
```
c <word1> [<word2> ...]
```
- Checks one or more words
- Output: One line per word: `ok\n` (correct) or `no\n` (incorrect)

**Suggest command:**
```
s <word>
```
- Gets suggestions for exactly one word
- Output: 
  - `ok\n` if word is correct
  - `no\t<sug1>,<sug2>,...\n` if word is incorrect with suggestions
  - `no\t\n` if word is incorrect without suggestions

**Quit command:**
```
q
```
- Exits the protocol loop
- No output

**Error response:**
```
err\n
```
- Returned for invalid commands or syntax errors

#### Examples

**Check multiple words:**
```bash
$ echo -e "c preon lenghe xyzabc\nq" | furlanspellchecker cof-cli
ok
ok
no
```

**Get suggestions:**
```bash
$ echo -e "s preo\nq" | furlanspellchecker cof-cli
no	preon,pren,predi
```

**Check correct word:**
```bash
$ echo -e "s preon\nq" | furlanspellchecker cof-cli
ok
```

**Invalid command:**
```bash
$ echo -e "c\nq" | furlanspellchecker cof-cli
err
```

### Options

#### `--encoding`, `-c`

Specify character encoding (default: `utf8`):

```bash
furlanspellchecker cof-cli --encoding utf8
```

#### `--max-suggestions`, `-n`

Limit the number of suggestions returned (default: 10):

```bash
furlanspellchecker cof-cli --max-suggestions 5
```

### Special Handling

**Endpoint Stripping:**
Words ending with `.` have the period automatically removed before processing:

```bash
$ echo -e "c preon.\nq" | furlanspellchecker cof-cli
ok
```

This matches the behavior of the Perl COF implementation.

**Case Insensitivity:**
Commands are case-insensitive (`C`, `c`, `S`, `s`, `Q`, `q` all work).

### Compatibility with Perl COF

The Python implementation guarantees:

1. **Identical output format** - Tab-separated, newline-terminated
2. **Same command syntax** - Commands, options, and parameters
3. **Matching endpoint stripping** - Period removal behavior
4. **Equivalent error handling** - `err\n` for invalid input

This ensures existing automation scripts and test suites work without modification.

## Standard Commands

### check

Check spelling of text:

```bash
furlanspellchecker check "Cheste e je une frâs in furlan."
```

Options:
- `--dictionary`, `-d` - Custom dictionary file
- `--output`, `-o` - Write results to file
- `--format`, `-f` - Output format (`text` or `json`)

### suggest

Get suggestions for a word:

```bash
furlanspellchecker suggest "cjasa"
```

Options:
- `--max`, `-m` - Maximum suggestions (default: 10)
- `--format`, `-f` - Output format (`text` or `json`)

### lookup

Check if a word is correct:

```bash
furlanspellchecker lookup "cjase"
```

Returns exit code 0 if correct, 1 if incorrect.

### file

Process a text file:

```bash
furlanspellchecker file input.txt -o corrected.txt
```

Options:
- `--output`, `-o` - Output file path
- `--format`, `-f` - Output format
- `--dictionary`, `-d` - Custom dictionary

### download-dicts

Download dictionary databases:

```bash
furlanspellchecker download-dicts
```

Options:
- `--force` - Force re-download even if cached

### db-status

Check database status:

```bash
furlanspellchecker db-status
```

Shows which databases are available and their sizes.

### extract-dicts

Extract dictionaries from database files:

```bash
furlanspellchecker extract-dicts -o output_dir/
```

Options:
- `--output`, `-o` - Output directory
- `--format`, `-f` - Output format (`text`, `json`, `msgpack`)

## Installation Notes

### Dependencies

The interactive mode requires the `colorama` package for cross-platform colored output:

```bash
pip install colorama>=0.4.6
```

This is automatically installed as a dependency when you install FurlanSpellChecker.

### Cross-Platform Support

Both interactive and COF protocol modes work on:
- Windows (PowerShell, CMD, Windows Terminal)
- Linux (bash, zsh, fish)
- macOS (Terminal, iTerm2)

Colors are automatically disabled on terminals that don't support them.

## Use Cases

### For End Users
Use **interactive mode** for:
- Learning Friulian spelling
- Quick word checks while writing
- Exploring the spell checker capabilities

### For Developers/Automation
Use **COF protocol mode** for:
- Integration with text editors
- Automated testing
- Batch processing scripts
- CI/CD pipelines
- Compatibility with existing COF tools

### For Scripting
Use **standard commands** for:
- Shell scripts
- Build pipelines
- Document processing workflows

## Examples

### Shell Script with COF Protocol

```bash
#!/bin/bash
# check_words.sh - Check a list of words

while read -r word; do
    echo "c $word"
done < words.txt | furlanspellchecker cof-cli | while read -r result; do
    if [ "$result" = "ok" ]; then
        echo "✓ Word is correct"
    else
        echo "✗ Word is incorrect"
    fi
done
```

### Python Script with COF Protocol

```python
import subprocess

def check_word(word: str) -> bool:
    """Check if a word is correct using COF protocol."""
    proc = subprocess.Popen(
        ["furlanspellchecker", "cof-cli"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    
    stdout, _ = proc.communicate(f"c {word}\nq\n")
    return stdout.strip() == "ok"

# Usage
if check_word("preon"):
    print("Correct!")
else:
    print("Incorrect!")
```

### Interactive Session Example

```
$ furlanspellchecker interactive --language fur

    ╔═══════════════════════════════════════════════════════════════════════╗
    ║                                                                       ║
    ║   ███████╗██╗   ██╗██████╗ ██╗      █████╗ ███╗   ██╗                ║
    ║   ██╔════╝██║   ██║██╔══██╗██║     ██╔══██╗████╗  ██║                ║
    ║   █████╗  ██║   ██║██████╔╝██║     ███████║██╔██╗ ██║                ║
    ║   ██╔══╝  ██║   ██║██╔══██╗██║     ██╔══██║██║╚██╗██║                ║
    ║   ██║     ╚██████╔╝██║  ██║███████╗██║  ██║██║ ╚████║                ║
    ║   ╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝                ║
    ║                                                                       ║
    ║    ███████╗██████╗ ███████╗██╗     ██╗          ██████╗██╗  ██╗     ║
    ║    ██╔════╝██╔══██╗██╔════╝██║     ██║         ██╔════╝██║  ██║     ║
    ║    ███████╗██████╔╝█████╗  ██║     ██║         ██║     ███████║     ║
    ║    ╚════██║██╔═══╝ ██╔══╝  ██║     ██║         ██║     ██╔══██║     ║
    ║    ███████║██║     ███████╗███████╗███████╗    ╚██████╗██║  ██║     ║
    ║    ╚══════╝╚═╝     ╚══════╝╚══════╝╚══════╝     ╚═════╝╚═╝  ╚═╝     ║
    ║                                                                       ║
    ║              Coretor Ortografic par la lenghe furlane                ║
    ║                   Friulian Language Spell Checker                    ║
    ║                                                                       ║
    ╚═══════════════════════════════════════════════════════════════════════╝

Comants: C <peraulis>... (control), S <peraule> (sugjeriments), Q (jessî)
----------------------------------------------------------------------

> C preon lenghe
preon al è corete
lenghe al è corete

> S sbaliât
sbaliât al è sbaliade
I sugjeriments a son: sbaliât, sbaliâ, sbaliàt

> Q
O sierri la aplicazion. Mandi!
```

## Troubleshooting

### Colors Not Working

If colors aren't displaying correctly:

1. Check if `colorama` is installed: `pip list | grep colorama`
2. Try the `--no-color` flag
3. Check terminal compatibility (Windows CMD may need Windows Terminal)

### COF Protocol Compatibility Issues

If output doesn't match Perl COF:

1. Ensure you're using the exact command format
2. Check for extra whitespace in input
3. Verify encoding matches (`--encoding utf8`)
4. Compare output byte-by-byte

### Database Not Found

If the spell checker can't find dictionaries:

1. Run `furlanspellchecker db-status` to check
2. Run `furlanspellchecker download-dicts --force` to redownload
3. Check cache directory permissions

## Related Documentation

- [Architecture](architecture.md) - System design and components
- [Development Guide](development/) - Contributing and testing
- [COF Parity Roadmap](development/COF_Parity_Roadmap.md) - Compatibility tracking
