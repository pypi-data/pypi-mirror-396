#!/usr/bin/env python3
"""
Data models for Dataform Checklist
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class SqlxFile:
    """Represents a Dataform .sqlx file"""
    full_path: str
    directory: str
    filename: str
    sources: str = ""


@dataclass
class InventoryItem:
    """Represents an item in the deployment checklist"""
    index: int
    directory: str
    filename: str
    status: str
    sources: str = ""


@dataclass
class ExporterConfig:
    """Configuration for the DataformInventoryExporter"""
    repository_path: Path
    output_path: Path
    repository_name: str
    version: str
    excel_path: Path
    excel_filename: str
    template_path: Path
    
    @classmethod
    def create(cls, 
               repository_path: str,
               output_path: Optional[str] = None,
               repository_name: Optional[str] = None,
               version: Optional[str] = None,
               template_path: Optional[Path] = None) -> 'ExporterConfig':
        """Factory method to create ExporterConfig with sensible defaults"""
        repo_path = Path(repository_path)
        out_path = Path(output_path) if output_path else repo_path
        repo_name = repository_name or repo_path.name
        
        return cls(
            repository_path=repo_path,
            output_path=out_path,
            repository_name=repo_name,
            version=version or "v1.00.00",
            excel_path=out_path / f"PTTEP_Dataform_Deployment_Checklist_{repo_name}_{version or 'v1.00.00'}.xlsx",
            excel_filename=f"PTTEP_Dataform_Deployment_Checklist_{repo_name}_{version or 'v1.00.00'}.xlsx",
            template_path=template_path or Path(".")
        )


@dataclass
class StatusColors:
    """Excel color fills for different statuses"""
    NEW: str = '90EE90'      # LightGreen
    EXISTED: str = 'ADD8E6'  # LightBlue
    DELETED: str = 'F08080'  # LightCoral
