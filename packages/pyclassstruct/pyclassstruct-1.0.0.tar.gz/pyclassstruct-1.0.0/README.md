# PyClassStruct

A powerful CLI tool that converts simple Python scripts to well-organized class-based structures.

## Installation

```bash
pip install -e .
```

## Usage

### Analyze Python Files

Analyze files/folders to generate a report and classes.txt:

```bash
# Analyze a folder
pyclassstruct analyze ./my_scripts

# Analyze a single file
pyclassstruct analyze ./my_script.py
```

This generates:
- `report.txt` - Statistics and structure visualization
- `classes.txt` - Proposed class structure (edit this to customize)

### Convert to Structured Classes

Convert scripts to class-based structure:

```bash
# Convert using auto-detection or existing classes.txt
pyclassstruct convert ./my_scripts

# Convert a single file
pyclassstruct convert ./my_script.py
```

This creates a `structured/` folder with organized class files.

## classes.txt Format

```txt
# Class definitions - one per line
# Format: ClassName: function1, function2, function3

UserManager: create_user, delete_user, update_user
DatabaseHandler: connect_db, query, close_connection
```

## Features

- 🔍 **Smart Detection**: Automatically groups related functions into classes
- 📊 **Dependency Analysis**: Detects function call relationships
- 🏷️ **Naming Patterns**: Groups functions by common prefixes
- 📁 **Flexible Input**: Works with single files or entire folders
- 📝 **Customizable**: Edit classes.txt to define your own structure

## License

MIT License
