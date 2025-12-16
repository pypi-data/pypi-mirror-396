#!/usr/bin/env python3
"""
File utilities for Dataform Checklist
"""

import re
from pathlib import Path
from typing import Optional, List

from .models import SqlxFile


def find_excel_file(output_path: Path, repository_name: str, version: Optional[str] = None) -> Path:
    """Find existing Excel file by repository name or create new path"""
    # If version is explicitly provided, create new file with that version
    if version:
        filename = f"PTTEP_Dataform_Deployment_Checklist_{repository_name}_{version}.xlsx"
        filepath = output_path / filename
        if filepath.exists():
            print(f"Found existing file: {filename}")
        else:
            print(f"Will create new file: {filename}")
        return filepath
    
    # Otherwise, search for existing files matching pattern
    pattern = f"PTTEP_Dataform_Deployment_Checklist_{repository_name}_*.xlsx"
    existing_files = list(output_path.glob(pattern))
    
    # Filter out temporary Excel files (starting with ~$)
    existing_files = [f for f in existing_files if not f.name.startswith('~$')]
    
    if existing_files:
        # Use the most recently modified file
        existing_file = max(existing_files, key=lambda f: f.stat().st_mtime)
        print(f"Found existing file: {existing_file.name}")
        return existing_file
    else:
        # Create new filename with default version
        filename = f"PTTEP_Dataform_Deployment_Checklist_{repository_name}_v1.00.00.xlsx"
        print(f"No existing file found. Will create: {filename}")
        return output_path / filename


def extract_version_from_filename(excel_path: Path) -> str:
    """Extract version from existing filename or return default"""
    if excel_path.exists():
        # Extract version from filename pattern: PTTEP_Dataform_Deployment_Checklist_{name}_{version}.xlsx
        name_parts = excel_path.stem.split('_')
        if len(name_parts) >= 4:
            # Last part should be the version
            return name_parts[-1]
    return "v1.00.00"


def find_template() -> Path:
    """Find the template Excel file"""
    # Check in package directory
    package_dir = Path(__file__).parent
    template_dir = package_dir / "template"
    
    if template_dir.exists():
        templates = list(template_dir.glob("*.xlsx"))
        templates = [t for t in templates if not t.name.startswith('~$')]
        if templates:
            return templates[0]
    
    # Check in current directory (for development)
    local_template_dir = Path("dataform_checklist/template")
    if local_template_dir.exists():
        templates = list(local_template_dir.glob("*.xlsx"))
        templates = [t for t in templates if not t.name.startswith('~$')]
        if templates:
            return templates[0]
    
    raise FileNotFoundError("Template Excel file not found. Expected in 'dataform_checklist/template/' directory")


def extract_sources_from_js(js_file_path: Path) -> str:
    """Extract sources array from JavaScript dependencies.js file"""
    try:
        content = js_file_path.read_text(encoding='utf-8')
        # Match: var sources = ["item1", "item2", ...] or var sources = ['item1', 'item2', ...]
        pattern = r'var\s+sources\s*=\s*\[([^\]]+)\]'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            sources_str = match.group(1)
            # Extract quoted strings
            sources = re.findall(r'["\']([^"\']+)["\']', sources_str)
            # Join with comma and newline for better readability in Excel
            return ',\n'.join(sources)
        return ''
    except Exception as e:
        print(f"Warning: Could not parse {js_file_path}: {e}")
        return ''


def scan_dataform_files(repository_path: Path) -> List[SqlxFile]:
    """Scan repository for all .sqlx and dependencies.js files"""
    print(f"Scanning for .sqlx and dependencies.js files in: {repository_path}")
    
    files = []
    
    # Scan for .sqlx files
    for sqlx_file in repository_path.rglob("*.sqlx"):
        directory = _extract_directory_path(sqlx_file, repository_path)
        files.append(SqlxFile(
            full_path=str(sqlx_file),
            directory=directory,
            filename=sqlx_file.name,
            sources=''
        ))
    
    # Scan for dependencies.js files
    for js_file in repository_path.rglob("dependencies.js"):
        directory = _extract_directory_path(js_file, repository_path)
        sources = extract_sources_from_js(js_file)
        files.append(SqlxFile(
            full_path=str(js_file),
            directory=directory,
            filename=js_file.name,
            sources=sources
        ))
    
    files.sort(key=lambda x: x.full_path)
    print(f"Found {len(files)} files (.sqlx and dependencies.js)")
    
    return files


def _extract_directory_path(file_path: Path, repository_path: Path) -> str:
    """Extract directory path starting from 'definitions' folder"""
    relative_dir = file_path.parent.relative_to(repository_path)
    path_parts = relative_dir.parts
    
    if 'definitions' in path_parts:
        # Start from 'definitions' folder
        definitions_idx = path_parts.index('definitions')
        return str(Path(*path_parts[definitions_idx:]))
    else:
        # If no 'definitions' folder, use the full relative path
        return str(relative_dir)
