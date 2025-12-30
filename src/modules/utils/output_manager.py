"""
Output Manager

Manages output directory structure and file naming for runs.
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional


class OutputManager:
    """Manages output directory structure and file naming."""
    
    def __init__(self, base_output_dir: str = "output"):
        """
        Initialize Output Manager.
        
        Args:
            base_output_dir: Base output directory (default: "output")
        """
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_run_directory(
        self,
        schema_name: str,
        schema_url: Optional[str] = None,
        run_timestamp: Optional[str] = None
    ) -> Path:
        """
        Create a new run directory. All files go directly in this directory.
        
        Args:
            schema_name: Name of the schema (without extension)
            schema_url: Optional URL of the schema
            run_timestamp: Optional timestamp (generates if not provided)
            
        Returns:
            Path to the run directory
        """
        # Generate timestamp if not provided
        if not run_timestamp:
            run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sanitize schema name for filesystem
        safe_schema_name = self._sanitize_filename(schema_name)
        
        # Create run directory name: <timestamp>-<schema_name>
        run_dir_name = f"{run_timestamp}-{safe_schema_name}"
        run_dir = self.base_output_dir / run_dir_name
        run_dir.mkdir(parents=True, exist_ok=True)
        
        return run_dir
    
    def get_timestamped_filename(self, run_timestamp: str, base_name: str, extension: str = "") -> str:
        """
        Generate a timestamped filename in format: timestamp-nameoffile
        
        Args:
            run_timestamp: Timestamp string (YYYYMMDD_HHMMSS)
            base_name: Base name for the file (without extension)
            extension: File extension (with or without dot)
            
        Returns:
            Timestamped filename
        """
        # Ensure extension starts with dot if provided
        if extension and not extension.startswith('.'):
            extension = '.' + extension
        
        # Format: timestamp-nameoffile.ext
        return f"{run_timestamp}-{base_name}{extension}"
    
    def create_manifest(
        self,
        run_dir: Path,
        schema_name: str,
        schema_url: Optional[str] = None,
        run_timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Create manifest.json file for a run.
        
        Args:
            run_dir: Run directory path
            schema_name: Name of the schema
            schema_url: Optional URL of the schema
            run_timestamp: Optional timestamp
            metadata: Optional additional metadata
            
        Returns:
            Path to manifest.json
        """
        if not run_timestamp:
            run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        manifest = {
            "run_id": run_dir.name,
            "timestamp": run_timestamp,
            "schema": {
                "name": schema_name,
                "url": schema_url
            },
            "metadata": metadata or {}
        }
        
        manifest_path = run_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        return manifest_path
    
    def create_run_readme(
        self,
        run_dir: Path,
        schema_name: str,
        schema_url: Optional[str] = None,
        summary: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Create README.md file for a run.
        
        Args:
            run_dir: Run directory path
            schema_name: Name of the schema
            schema_url: Optional URL of the schema
            summary: Optional summary data
            
        Returns:
            Path to README.md
        """
        readme_content = f"""# Run Output: {run_dir.name}

## Schema Information

- **Schema Name**: {schema_name}
- **Schema URL**: {schema_url or 'N/A'}
- **Run Directory**: `{run_dir.name}`

## Directory Structure

```
{run_dir.name}/
├── manifest.json              # Run metadata and configuration
├── README.md                  # This file
├── <timestamp>-scenarios.csv # Generated test scenarios
├── <timestamp>-analytics.txt  # Analytics and metrics
├── <timestamp>-reports.txt    # Algorithm execution reports
└── <timestamp>-validation.txt # BRD validation reports
```

## Output Files

All files from this execution are stored directly in this directory with the format:
`<timestamp>-<name>.<ext>`

### File Types

- **Scenarios**: CSV files with Gherkin test scenarios
- **Analytics**: Text files with LLM execution metrics
- **Reports**: Text files with algorithm execution reports
- **Validation**: Text files with BRD validation reports

"""
        
        readme_content += """## Summary

"""
        
        if summary:
            readme_content += "### Run Summary\n\n"
            for key, value in summary.items():
                readme_content += f"- **{key.replace('_', ' ').title()}**: {value}\n"
        
        readme_path = run_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return readme_path
    
    def get_run_directory(self) -> Path:
        """
        Get the base output directory (all runs go directly here).
        
        Returns:
            Path to base output directory
        """
        return self.base_output_dir
    
    def _generate_short_id(self, schema_name: str, timestamp: str) -> str:
        """
        Generate a short ID from schema name and timestamp.
        
        Args:
            schema_name: Name of the schema
            timestamp: Timestamp string
            
        Returns:
            Short 8-character ID
        """
        # Create hash from schema name + timestamp
        hash_input = f"{schema_name}_{timestamp}".encode('utf-8')
        hash_obj = hashlib.md5(hash_input)
        # Return first 8 characters of hex digest
        return hash_obj.hexdigest()[:8]
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for filesystem compatibility.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove extension if present
        filename = filename.replace('.json', '').replace('.yaml', '').replace('.yml', '')
        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        # Limit length
        if len(filename) > 50:
            filename = filename[:50]
        return filename
    
    def clear_old_outputs(self, keep_latest: int = 0) -> int:
        """
        Clear old output directories.
        
        Args:
            keep_latest: Number of latest runs to keep (0 = remove all)
            
        Returns:
            Number of directories removed
        """
        if not self.base_output_dir.exists():
            return 0
        
        # Get all run directories (timestamp-* format) sorted by modification time (newest first)
        run_dirs = sorted(
            [d for d in self.base_output_dir.iterdir() if d.is_dir() and not d.name.startswith('.')],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        # Keep latest N if specified
        if keep_latest > 0:
            run_dirs = run_dirs[keep_latest:]
        
        # Remove directories
        removed_count = 0
        for run_dir in run_dirs:
            try:
                import shutil
                shutil.rmtree(run_dir)
                removed_count += 1
            except Exception as e:
                print(f"Warning: Could not remove {run_dir}: {e}")
        
        return removed_count
    
    def create_output_readme(self) -> Path:
        """
        Create main README.md in output directory.
        
        Returns:
            Path to README.md
        """
        readme_content = """# Output Directory

This directory contains all execution outputs from the API Parameter Coverage tool.

## Structure

```
output/
├── <timestamp>-<schema_name>/     # Each execution creates one directory
│   ├── <timestamp>-scenarios.csv  # Test scenarios
│   ├── <timestamp>-analytics.txt  # Analytics and metrics
│   ├── <timestamp>-reports.txt   # Algorithm reports
│   └── <timestamp>-validation.txt # BRD validation reports
└── README.md                      # This file
```

## Run Directories

Each run is stored in a directory with the format:
`<YYYYMMDD_HHMMSS>-<schema_name>/`

Example: `20251230_110000-api_weather_gov_openapi/`

## File Naming

All files use the format: `<timestamp>-<name>.<ext>`
- Scenarios: `<timestamp>-scenarios.csv`
- Analytics: `<timestamp>-analytics.txt`
- Reports: `<timestamp>-<report_type>.txt`
- Validation: `<timestamp>-validation.txt`

## Accessing Results

1. Find your run directory by timestamp or schema name
2. All artifacts from that execution are in that single directory
3. Files are named with timestamps for easy identification

## Cleanup

To remove old runs, you can manually delete directories or use the output manager's cleanup functionality.
"""
        
        readme_path = self.base_output_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        return readme_path

