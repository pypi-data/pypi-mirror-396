# PyClassStruct

A powerful CLI tool that converts simple Python scripts to well-organized class-based structures.

## Installation

```bash
pip install pyclassstruct
```
OR From Source Code


```bash
git clone https://github.com/Mirjan-Ali-Sha/pyclassstruct.git
```

```bash
cd pyclassstruct
```

```bash
pip install -e .
```

## Usage

### Analyze Python Files

Analyze files/folders to generate a report and classes.txt:

```bash
# Analyze a folder
pyclassstruct analyze ./tests/sample_scripts
```
OR

```bash
pyclassstruct analyze ./tests/sample_scripts --force
```

#### Analyze a single file
```bash
pyclassstruct analyze ./my_script.py
```

This generates:
- `report.txt` - Statistics and structure visualization
- `classes.txt` - Proposed class structure (edit this to customize)

#### classes.txt Format

```txt
# PyClassStruct Class Definitions
# Format: ClassName: function1, function2, function3
# Edit this file to customize the class structure
# Then run: pyclassstruct convert <path>

FileHandler: read_file, write_file, append_file, delete_file, read_json, write_json, parse_json, format_json, validate_path, ensure_directory, list_files
DatabaseManager: create_user, delete_user, update_user, get_user, validate_user_data, connect_database, query_database, save_to_database, delete_from_database, update_in_database, hash_password, validate_email
Utils: format_date, generate_id
```
#### report.txt Format
```txt
============================================================
PYSTRUCT ANALYSIS REPORT
============================================================
Generated: 2025-12-14 21:56:08

Source: C:\Users\acer\Downloads\Documents\to_class\pyclassstruct\tests\sample_scripts
Type: Folder analysis
Files analyzed: 2

------------------------------------------------------------

STATISTICS
------------------------------
Total functions found:     25
Total global variables:    5
Proposed classes:          3
Methods (in classes):      25
Properties (from globals): 0

------------------------------------------------------------

FUNCTIONS DETECTED
------------------------------
  • read_file(filepath) -> calls: read, validate_path, open
  • write_file(filepath, content) -> calls: validate_path, write, dirname
  • append_file(filepath, content) -> calls: write, validate_path, open
  • delete_file(filepath) -> calls: exists, validate_path, remove
  • read_json(filepath) -> calls: read_file, parse_json
  • write_json(filepath, data) -> calls: write_file, format_json
  • parse_json(content) -> calls: loads
  • format_json(data) -> calls: dumps
  • validate_path(filepath) -> calls: ValueError, normpath
  • ensure_directory(dirpath) -> calls: exists, makedirs
  • list_files(directory, extension) -> calls: validate_path, listdir, endswith
  • create_user(username, email, password) -> calls: save_to_database, validate_user_data, hash_password
  • delete_user(user_id) -> calls: get_user, delete_from_database
  • update_user(user_id) -> calls: get_user, update_in_database
  • get_user(user_id) -> calls: query_database
  • validate_user_data(username, email) -> calls: ValueError, validate_email, len
  • connect_database(()) -> calls: print
  • query_database(table, filters) -> calls: print, connect_database
  • save_to_database(table, data) -> calls: print, connect_database
  • delete_from_database(table, record_id) -> calls: print, connect_database
  • update_in_database(table, record_id, data) -> calls: print, connect_database
  • hash_password(password) -> calls: sha256, encode, hexdigest
  • validate_email(email) -> calls: match, bool
  • format_date(date_obj) -> calls: strftime
  • generate_id(()) -> calls: uuid4, str

------------------------------------------------------------

GLOBAL VARIABLES DETECTED
------------------------------
  • DEFAULT_ENCODING: str = 'utf-8'
  • BUFFER_SIZE: int = 8192
  • DATABASE_URL: str = 'postgresql://localhost/mydb'
  • MAX_RETRIES: int = 3
  • TIMEOUT: int = 30

------------------------------------------------------------

PROPOSED CLASS STRUCTURE
------------------------------

  class FileHandler:
    # Auto-detected class grouping 11 related functions
    # Methods:
    #   - read_file()
    #   - write_file()
    #   - append_file()
    #   - delete_file()
    #   - read_json()
    #   - write_json()
    #   - parse_json()
    #   - format_json()
    #   - validate_path()
    #   - ensure_directory()
    #   - list_files()

  class DatabaseManager:
    # Auto-detected class grouping 12 related functions
    # Methods:
    #   - create_user()
    #   - delete_user()
    #   - update_user()
    #   - get_user()
    #   - validate_user_data()
    #   - connect_database()
    #   - query_database()
    #   - save_to_database()
    #   - delete_from_database()
    #   - update_in_database()
    #   - hash_password()
    #   - validate_email()

  class Utils:
    # Utility functions
    # Methods:
    #   - format_date()
    #   - generate_id()

============================================================
END OF REPORT
============================================================
```

### Convert to Structured Classes

Convert scripts to a class-based structure:
**[OPTIONAL - Recommended]**: classes.txt (either create this file manually or run `pyclassstruct analyze ./my_scripts` or `pyclassstruct analyze my_scripts.py`)

```bash
# Convert using auto-detection or existing classes.txt
pyclassstruct convert ./tests/sample_scripts

# Convert a single file
pyclassstruct convert ./my_script.py
```

This creates a `structured/` folder with organized class files.

## Features

- 🔍 **Smart Detection**: Automatically groups related functions into classes
- 📊 **Dependency Analysis**: Detects function call relationships
- 🏷️ **Naming Patterns**: Groups functions by common prefixes
- 📁 **Flexible Input**: Works with single files or entire folders
- 📝 **Customizable**: Edit classes.txt to define your own structure

## License

MIT License