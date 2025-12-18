# rfind - Restricted File Finder
.
## Overview

`rfind` is a security and system administration tool designed for situations where you have **execute (`x`) permission** on a directory but **lack read (`r`) permission**. In such cases, traditional directory listing commands like `ls` fail with "Permission denied", yet you can still access files if you know their names.

This tool helps you discover what files exist in such restricted directories through intelligent enumeration techniques.

## The Problem

On Unix-like systems (including Linux and Android), directory permissions work like this:
- **Read (`r`) permission**: List directory contents
- **Execute (`x`) permission**: Access files within the directory (if you know their names)
- **Both are needed**: To both list AND access files

When you have `x` but not `r`, you're in a "blind" situation - you can't see what's there, but you can touch what you find.

## How rfind Helps

`rfind` provides several approaches to discover files:

1. **Smart pattern matching** - Common file naming conventions
2. **Brute-force enumeration** - Systematic checking of possible names
3. **Multi-process scanning** - Leverage all CPU cores for speed
4. **Custom character sets** - Tailor searches to specific environments

## Use Cases

- **Security auditing** - Discovering hidden or protected files
- **Digital forensics** - Investigating system directories
- **System administration** - Recovering from permission issues  
- **Penetration testing** - Exploring restricted environments
- **Android device analysis** - Accessing protected system directories

## Installation

```bash
pip install rfind
```

Basic Usage

```bash
# Scan a directory with limited permissions
rfind /system/bin

# Use smart mode for common patterns
rfind --smart /dev
```

Technical Details

The tool employs parallel processing to efficiently enumerate possible filenames based on:

· Length constraints (1-6 characters typically)
· Character sets (alphanumeric, specific symbols, etc.)
· Common naming patterns in Unix/Linux/Android systems

Ethical Use

This tool should only be used on:

· Systems you own or have explicit permission to test
· For legitimate security auditing and system administration
· Educational and research purposes

Development Status

Early alpha release. Core functionality is implemented with ongoing development for additional features and optimizations.

Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

License

MIT License - see LICENSE file for details.
