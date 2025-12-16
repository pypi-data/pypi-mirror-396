# Package Distribution Guide

## ✅ Package Ready for Distribution

Your `dataform-checklist` package is now ready to share with others!

## 📦 What's Included

### Distribution Files
Located in `dist/` folder:
- `dataform_checklist-1.0.0-py3-none-any.whl` - Wheel package (recommended)
- `dataform_checklist-1.0.0.tar.gz` - Source distribution

### Key Features
- ✅ Template file included in package
- ✅ Data written starting from cell A9 in "DataForm.*" sheets
- ✅ Automatic status tracking (New/Existed/Deleted)
- ✅ Color-coded Excel formatting
- ✅ Command-line interface
- ✅ MIT License included
- ✅ Complete documentation

## 📤 How to Share

### Option 1: Share Wheel File (Recommended)
Share the file: `dist/dataform_checklist-1.0.0-py3-none-any.whl`

Recipients can install with:
```bash
pip install dataform_checklist-1.0.0-py3-none-any.whl
```

### Option 2: Publish to PyPI (Public)
```bash
pip install twine
twine upload dist/*
```

Then anyone can install with:
```bash
pip install dataform-checklist
```

### Option 3: Private Package Repository
Upload to your organization's private PyPI server or artifact repository.

### Option 4: Git Repository
Users can install directly from GitHub:
```bash
pip install git+https://github.com/OshigeAkito/dataform-checklist-package.git
```

## 💻 Usage After Installation

```bash
# Basic usage
dataform-checklist /path/to/dataform/repo

# With version
dataform-checklist /path/to/dataform/repo -v v1.01.00

# With custom output
dataform-checklist /path/to/dataform/repo -o /output/path -v v1.02.00
```

## 🔧 For Developers

### Install in Development Mode
```bash
git clone https://github.com/OshigeAkito/dataform-checklist-package.git
cd dataform-checklist-package
pip install -e .
```

### Rebuild Package
```bash
python -m build
```

## 📋 Requirements
- Python >= 3.7
- pandas >= 2.0.0
- openpyxl >= 3.1.0

## 📝 What Changed

### Latest Updates
1. ✅ Now uses template file from `template/` folder
2. ✅ Data written to "DataForm.*" sheets starting from cell A9
3. ✅ Template file automatically included in distribution
4. ✅ MIT License added
5. ✅ Package structure optimized for distribution

## 🎯 Next Steps

1. **Test the package**: Install on a different machine and verify it works
2. **Update GitHub**: Push changes to repository
3. **Tag release**: Create a v1.0.0 release on GitHub
4. **Share**: Distribute the wheel file to your team
5. **Publish** (optional): Upload to PyPI for public access

## 📞 Support

For issues or questions:
- GitHub: https://github.com/OshigeAkito/dataform-checklist-package
- Email: data-engineering@pttep.com
