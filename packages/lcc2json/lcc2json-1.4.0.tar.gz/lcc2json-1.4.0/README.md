# Library of Congress Classification to JSON
`lcc2json` outputs a single JSON file of the
Library of Congress Classification system.

For input, it downloads 699 `.json` files, 14 megabytes in total,
from the Library of Congress.

# Install
Install from PyPI:
```
pip install lcc2json
```

Or install from main source repo, such as:
```
git clone https://spacecruft.org/books/lcc2json
cd lcc2json/
python -m venv venv
source venv/bin/activate
pip install -U setuptools pip wheel
pip install -e .
```

# Usage
Thusly.

Download the source JSON files from the Library of Congress
```
lcc2json-dl
```

Parse the downloaded JSON files and output a single JSON file:
```
lcc2json
```

# Help
Download script help:

```
(venv) jebba@rs-pencil:~/devel/spacecruft/books/lcc2json$ lcc2json-dl --help
usage: lcc2json-dl [-h] [-o OUTPUT_DIR] [-d MAX_DEPTH] [-v] [--dry-run]

Download Library of Congress Classification JSON files from id.loc.gov

options:
  -h, --help            show this help message and exit
  -o, --output-dir OUTPUT_DIR
                        Output directory for JSON files (default: json)
  -d, --max-depth MAX_DEPTH
                        Maximum depth to crawl (default: 2)
  -v, --verbose         Enable verbose logging
  --dry-run             Show what would be downloaded without actually downloading

Examples:
  lcc2json-dl                     # Download all classifications to ./json/ (depth 2)
  lcc2json-dl --max-depth 4       # Download to depth 4 (includes subdivisions)
  lcc2json-dl -o lcc_data         # Download to ./lcc_data/
  lcc2json-dl -v                  # Verbose output
  lcc2json-dl --dry-run           # Show what would be downloaded

Depth levels:
  0 = Root classification scheme
  1 = Main classes (A-Z)
  2 = Subclass ranges (e.g., PR1-PR9680) [default]
  3 = Period/topic divisions (e.g., PR6050-PR6076)
  4 = Alphabetical ranges (e.g., PR6066.A-PR6066.Z)
  5+ = Individual entries (e.g., PR6066.A84)
```

Output JSON script help:
```
$ lcc2json --help
usage: lcc2json [-h] [-i INPUT_DIR] [-o OUTPUT] [-v] [--ranges]

Extract LCC outlines from downloaded JSON files.

options:
  -h, --help            show this help message and exit
  -i, --input-dir INPUT_DIR
                        Directory containing JSON files (default: json)
  -o, --output OUTPUT   Output file path (default: lcc.json)
  -v, --verbose         Enable verbose output
  --ranges              Include start/stop/prefix range fields in output (larger file size)
```

# JSON Data
## Depth 1
* 21 files.
* ~5 second download.
* 215K size.
* 21 classification entries.

## Depth 2
* 698 files.
* 2 minute download.
* 14M size.
* 14,786 classification entries.
* 516 unique prefixes.

## Depth 3
* 14,581 files.
* 2 hour download.
* 161M size.
* 101,699 classification entries.

## Depth 4
* 100,551 files.
* 14 hour download.
* 824M size.
* 344,073 classification entries.
* Two missing (404) files.

## Depth 5
* 342,499 files.
* 2 day download.
* 2.9G size.
*  766,892 classification entries.
* Three missing files.

## Downloads
JSON data snapshots are also available at this URL, so, optionally you don't have to
download with this script:

* https://spacecruft.org/books/lcc2json-data

## 📄 License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE-apache.txt) file for details.

*Copyright © 2025 Jeff Moe*
