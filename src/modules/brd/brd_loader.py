"""
BRD Loader

Loads BRD schemas from JSON files.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from .brd_schema import BRDSchema, BRDRequirement, BRDTestScenario, RequirementPriority, RequirementStatus


class BRDLoader:
    """Loads BRD schemas from files."""
    
    def __init__(self, brd_dir: str = "reference/brd/output"):
        """
        Initialize the BRD Loader.
        
        Args:
            brd_dir: Directory where BRD files are stored
        """
        self.brd_dir = Path(brd_dir)
        self.brd_dir.mkdir(parents=True, exist_ok=True)
    
    def load_brd_from_file(self, filename: str) -> Optional[BRDSchema]:
        """
        Load a BRD schema from a JSON file.
        
        Args:
            filename: Name of the BRD file (with or without .json extension)
            
        Returns:
            BRDSchema object, or None if file not found or invalid
        """
        if not filename.endswith('.json'):
            filename += '.json'
        
        brd_path = self.brd_dir / filename
        
        if not brd_path.exists():
            return None
        
        try:
            with open(brd_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return self._parse_brd_data(data)
        except FileNotFoundError:
            print(f"✗ Error: BRD file not found: {filename}")
            print(f"   Expected location: {brd_path}")
            print(f"   Tip: Ensure the file exists in {self.brd_dir}")
            return None
        except json.JSONDecodeError as e:
            print(f"✗ Error: Invalid JSON in BRD file {filename}: {e}")
            print(f"   File location: {brd_path}")
            print(f"   Tip: Validate the JSON format using a JSON validator.")
            return None
        except Exception as e:
            error_type = type(e).__name__
            print(f"✗ Error loading BRD file {filename} ({error_type}): {e}")
            print(f"   File location: {brd_path}")
            return None
    
    def list_available_brds(self) -> list:
        """
        List all available BRD files.
        
        Returns:
            List of BRD filenames (without .json extension)
        """
        if not self.brd_dir.exists():
            return []
        
        brd_files = []
        for file in self.brd_dir.iterdir():
            if file.is_file() and file.suffix == '.json':
                brd_files.append(file.stem)
        
        return sorted(brd_files)
    
    def _parse_brd_data(self, data: Dict[str, Any]) -> BRDSchema:
        """Parse BRD data dictionary into BRDSchema object."""
        requirements = []
        
        for req_data in data.get('requirements', []):
            test_scenarios = []
            for scenario_data in req_data.get('test_scenarios', []):
                scenario = BRDTestScenario(
                    scenario_id=scenario_data.get('scenario_id', ''),
                    scenario_name=scenario_data.get('scenario_name', ''),
                    description=scenario_data.get('description', ''),
                    test_steps=scenario_data.get('test_steps', []),
                    expected_result=scenario_data.get('expected_result', ''),
                    priority=RequirementPriority(scenario_data.get('priority', 'medium')),
                    tags=scenario_data.get('tags', [])
                )
                test_scenarios.append(scenario)
            
            requirement = BRDRequirement(
                requirement_id=req_data.get('requirement_id', ''),
                title=req_data.get('title', ''),
                description=req_data.get('description', ''),
                endpoint_path=req_data.get('endpoint_path', ''),
                endpoint_method=req_data.get('endpoint_method', ''),
                priority=RequirementPriority(req_data.get('priority', 'medium')),
                status=RequirementStatus(req_data.get('status', 'pending')),
                test_scenarios=test_scenarios,
                acceptance_criteria=req_data.get('acceptance_criteria', []),
                related_endpoints=req_data.get('related_endpoints', [])
            )
            requirements.append(requirement)
        
        brd = BRDSchema(
            brd_id=data.get('brd_id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            api_name=data.get('api_name', ''),
            api_version=data.get('api_version', ''),
            created_date=data.get('created_date', ''),
            requirements=requirements,
            metadata=data.get('metadata', {})
        )
        
        return brd
    
    def save_brd_to_file(self, brd: BRDSchema, filename: Optional[str] = None) -> Path:
        """
        Save a BRD schema to a JSON file.
        
        Args:
            brd: BRDSchema object to save
            filename: Optional filename (defaults to brd_id.json)
            
        Returns:
            Path to the saved file
        """
        if filename is None:
            filename = f"{brd.brd_id}.json"
        
        if not filename.endswith('.json'):
            filename += '.json'
        
        brd_path = self.brd_dir / filename
        
        with open(brd_path, 'w', encoding='utf-8') as f:
            json.dump(brd.to_dict(), f, indent=2, ensure_ascii=False)
        
        return brd_path

