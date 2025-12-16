# Dataform Deployment Checklist Exporter

A Python package for generating Excel deployment checklists from Dataform repositories with automatic status tracking.

## Features

- 🔍 Automatically scans all `.sqlx` and `dependencies.js` files in Dataform repositories
- 📊 Exports to formatted Excel with color-coded status
- 🔄 Tracks changes: New, Existed, Deleted files
- 🎨 Professional Excel formatting with conditional colors and top alignment
- 📝 Remark column with sources from dependencies.js (formatted with newlines)
- 🔔 Automatic version checking and update notifications
- 📦 Easy installation via PyPI
- 🚀 Command-line interface

## Installation

### From PyPI (Recommended)
```bash
pip install dataform-checklist
```

### From Source
```bash
git clone https://github.com/OshigeAkito/dataform-checklist-package.git
cd dataform-checklist-package
pip install -e .
```

### Upgrade to Latest Version
```bash
pip install --upgrade dataform-checklist
```

## Usage

### Command Line

After installation, use the `dataform-checklist` command:

```bash
# Basic usage
dataform-checklist /path/to/dataform/repo

# With version
dataform-checklist /path/to/dataform/repo -v v1.01.00

# With custom output path
dataform-checklist /path/to/dataform/repo -o /output/path -v v1.02.00

# With custom repository name
dataform-checklist /path/to/dataform/repo -n MyRepo -v v2.00.00

# Full options
dataform-checklist /path/to/repo -o /output -n WWIM -v v1.00.00
```

### As Python Library

```python
from dataform_checklist import DataformInventoryExporter

# Create exporter
exporter = DataformInventoryExporter(
    repository_path="/path/to/dataform/repo",
    output_path="/output/path",
    repository_name="WWIM",
    version="v1.00.00"
)

# Run export
exporter.run()

# Or use individual methods
files = exporter.scan_sqlx_files()
inventory = exporter.create_new_inventory(files)
exporter.export_to_excel(inventory)
```

## Output

### Filename Format
```
PTTEP_Dataform_Deployment_Checklist_{repository_name}_{version}.xlsx
```

### Excel Structure
| # | Path/Folder/Directory | Job/Script Name | Remark | status |
|---|----------------------|-----------------|--------|--------|
| 1 | dashboard_wwim | ins_pbi_well_info.sqlx | | New |
| 2 | datamart_wwim | ins_well_allocation.sqlx | | Existed |
| 3 | trusted | dependencies.js | wild_asset,<br>production_data,<br>external_api | Existed |
| 4 | refined_wwim | p2_refined_a_ann_barrier.sqlx | | Deleted |

### Status Colors
- **New** 🟢 - LightGreen (#90EE90)
- **Existed** 🔵 - LightBlue (#ADD8E6)
- **Deleted** 🔴 - LightCoral (#F08080)

## Version History

### v1.2.3 (Latest)
- Refactored row alignment to apply vertical top alignment to entire rows
- Improved code maintainability

### v1.2.2
- Added top vertical alignment to all columns for better readability
- Enabled text wrapping in remark column

### v1.2.1
- Fixed header row reading issue
- Updated filename prefix format

### v1.2.0
- Added remark column for dependencies.js sources
- Sources displayed with newline formatting
- Automatic scanning of dependencies.js files
- Automatic version checking on CLI startup

### v1.0.0
- Initial release with basic .sqlx scanning
- Status tracking (New/Existed/Deleted)
- Excel export with color coding

## Requirements

- Python 3.7+
- pandas >= 2.0.0
- openpyxl >= 3.1.0

## Examples

### Local Development
```bash
# Install in editable mode for development
pip install -e .

# Run from anywhere
dataform-checklist ~/projects/dataform-repo
```

### Production Use
```bash
# Install from PyPI
pip install dataform-checklist

# Schedule daily exports
dataform-checklist /prod/dataform/repo -v "v1.$(date +%Y%m%d).0"
```

### CI/CD Integration
```yaml
# .github/workflows/checklist.yml
- name: Generate Deployment Checklist
  run: |
    pip install dataform-checklist
    dataform-checklist . -v "v${{ github.run_number }}.0.0"
    
- name: Upload Checklist
  uses: actions/upload-artifact@v3
  with:
    name: deployment-checklist
    path: PTTEP_Dataform_Deployment_Checklist_*.xlsx
```

## Uninstallation

```bash
pip uninstall dataform-checklist
```

## Dependencies.js Support

The tool automatically detects `dependencies.js` files and extracts source declarations:

```javascript
// dependencies.js
var sources = ["wild_asset", "production_data", "external_api"];
```

These sources will be listed in the Remark column with newline formatting for readability.

## License

MIT License - See LICENSE file for details

## Repository

GitHub: [OshigeAkito/dataform-checklist-package](https://github.com/OshigeAkito/dataform-checklist-package)

PyPI: [dataform-checklist](https://pypi.org/project/dataform-checklist/)

## Support

For issues or questions, please open an issue on GitHub.
