# Testing Guide for dataform-checklist Package

## ✅ Test Results Summary

Package has been successfully tested with all features working correctly!

## 🧪 What Was Tested

### Test 1: Basic Functionality ✅
- **Created test repository** with .sqlx files
- **Ran package**: `dataform-checklist test-dataform-repo -v v1.00.00`
- **Result**: Successfully generated Excel file with:
  - Template structure preserved (PTTEP_Dataform_Deployment_Checklist_)
  - Data written starting from row 9
  - All files listed with "New" status (green color)
  - Proper formatting with top alignment

### Test 2: Dependencies.js Support ✅
- **Added dependencies.js** with sources array
- **Result**: Successfully detected and processed:
  - dependencies.js file included in inventory
  - Sources extracted and listed in Remark column
  - Newline formatting applied (comma + newline)
  - Text wrapping enabled for readability

### Test 3: Update/Merge Functionality ✅
- **Added new files** and re-ran with same version
- **Result**: Successfully tracked changes:
  - New files marked as "New" (green)
  - Existing files marked as "Existed" (blue)
  - Deleted files marked as "Deleted" (red)
  - Status preserved across runs

### Test 4: Version Checking ✅
- **Verified**: Automatic version check on CLI startup
- **Confirmed**: Notification when newer version available on PyPI
- **Validated**: Silent failure when network unavailable

## 📋 How to Test

### Quick Installation Test
```bash
# Install from PyPI
pip install dataform-checklist

# Verify installation
dataform-checklist --help

# Run on test repository
dataform-checklist test-dataform-repo -v v1.00.00

# Check the output file
# File: test-dataform-repo\PTTEP_Dataform_Deployment_Checklist_test-dataform-repo_v1.00.00.xlsx
```

### Complete Test Workflow

#### Test 1: Initial Run with dependencies.js
```bash
# Create a test Dataform repository with:
# - .sqlx files in definitions/
# - dependencies.js with sources array

# Run the tool
dataform-checklist "C:\path\to\dataform\repo" -v v1.00.00

# Expected output:
# - Excel file with all .sqlx and dependencies.js files
# - All files marked as "New" (green)
# - Sources listed in Remark column with newlines
# - Data starts at row 9 with top alignment
```

#### Test 2: Update Detection
```bash
# Add a new .sqlx file to your repository
# Then run again with same version
dataform-checklist "C:\path\to\your\dataform\repo" -v v1.00.00

# Expected output:
# - Old files marked as "Existed" (blue)
# - New files marked as "New" (green)
```

#### Test 3: Deletion Detection
```bash
# Delete a .sqlx file from your repository
# Then run again
dataform-checklist "C:\path\to\your\dataform\repo" -v v1.00.00

# Expected output:
# - Deleted files marked as "Deleted" (red)
# - Existing files marked as "Existed" (blue)
```

## 🔍 What to Check in Excel

1. **Sheet Selection**: Look for "DataForm" sheet
2. **Row 8**: Should contain headers (#, Path/Folder/Directory, Job/Script Name, Remark, status)
3. **Row 9+**: Should contain your data
4. **Remark Column**: 
   - Should show sources from dependencies.js
   - Each source on a new line (text wrapping enabled)
5. **Alignment**: All data cells should have top vertical alignment
6. **Colors**:
   - 🟢 Green (LightGreen) = New files
   - 🔵 Blue (LightBlue) = Existed files  
   - 🔴 Red (LightCoral) = Deleted files
7. **Template Content**: Rows 1-8 should have template headers and formatting

## 📦 Test Package Distribution

### Test Installation from PyPI
```bash
# Install latest version
pip install dataform-checklist

# Upgrade to latest
pip install --upgrade dataform-checklist

# Test it works
dataform-checklist --help
dataform-checklist "C:\path\to\dataform\repo" -v v1.00.00
```

### Test Clean Installation
```bash
# Create new virtual environment
python -m venv test-env
.\test-env\Scripts\Activate.ps1

# Install from wheel
pip install dist\dataform_checklist-1.0.0-py3-none-any.whl

# Test
dataform-checklist test-dataform-repo -v v1.00.00

# Cleanup
deactivate
Remove-Item -Recurse test-env
```

## 🐛 Known Issues and Fixes

### v1.2.3 - Row Alignment Refactor ✅
- **Status**: ✅ Fixed
- **Change**: Refactored to apply vertical top alignment to entire rows
- **Benefit**: Improved code maintainability

### v1.2.2 - Cell Alignment ✅
- **Status**: ✅ Fixed
- **Problem**: Data cells not aligned to top
- **Solution**: Added vertical='top' alignment to all columns with text wrapping for Remark

### v1.2.1 - Header Row Reading ✅
- **Status**: ✅ Fixed
- **Problem**: Reading data from wrong row when loading existing inventory
- **Solution**: Updated `load_existing_inventory()` to use header=7 (row 8)

### v1.2.0 - Dependencies.js Support ✅
- **Status**: ✅ Implemented
- **Feature**: Added scanning of dependencies.js files
- **Feature**: Extract sources array and display in Remark column
- **Feature**: Newline formatting for better readability

## ✅ Test Checklist

- [x] Package installs from PyPI
- [x] Command-line tool accessible (`dataform-checklist`)
- [x] Template file included in distribution
- [x] Scans .sqlx files correctly
- [x] Scans dependencies.js files correctly
- [x] Extracts sources from dependencies.js
- [x] Creates Excel with PTTEP template
- [x] Writes data to row 9
- [x] Applies color formatting
- [x] Applies top vertical alignment to all cells
- [x] Text wrapping in Remark column
- [x] Newline formatting for sources
- [x] Detects new files (green)
- [x] Detects existing files (blue)
- [x] Detects deleted files (red)
- [x] Version checking on startup
- [x] Handles different versions

## 🎯 Performance Test

Tested with:
- **4 .sqlx files + 1 dependencies.js**: < 1 second
- **Expected for 100+ files**: < 5 seconds
- **Excel file size**: ~150KB with template
- **Remark column**: Handles multiple sources efficiently

## 📝 Test Artifacts

Generated test files:
```
test-dataform-repo/
├── definitions/
│   ├── staging/
│   │   ├── stg_customers.sqlx
│   │   └── stg_orders.sqlx
│   ├── marts/
│   │   ├── fct_sales.sqlx
│   │   └── dim_products.sqlx
│   └── trusted/
│       └── dependencies.js
├── PTTEP_Dataform_Deployment_Checklist_test-dataform-repo_v1.00.00.xlsx
├── PTTEP_Dataform_Deployment_Checklist_test-dataform-repo_v1.00.01.xlsx
└── PTTEP_Dataform_Deployment_Checklist_test-dataform-repo_v1.00.02.xlsx
```

## ✨ Next Steps

1. **Install from PyPI**:
   ```bash
   pip install dataform-checklist
   ```

2. **Test on your Dataform repository**

3. **Check for updates**:
   ```bash
   pip install --upgrade dataform-checklist
   ```

4. **Report issues** on GitHub: https://github.com/OshigeAkito/dataform-checklist-package/issues

## 🚀 Ready for Production!

Package is fully tested and available on PyPI! 🎉

**Latest Version**: 1.2.3
**PyPI**: https://pypi.org/project/dataform-checklist/
**GitHub**: https://github.com/OshigeAkito/dataform-checklist-package
