"""
CSV Generator

Generates CSV output from Gherkin test scenarios.
"""

import csv
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class CSVGenerator:
    """Generates CSV files from Gherkin test scenarios."""
    
    def __init__(self, output_dir: str = "docs/output/csv"):
        """
        Initialize the CSV Generator.
        
        Args:
            output_dir: Directory where CSV files will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def parse_gherkin_to_csv_data(self, gherkin_content: str) -> List[Dict[str, Any]]:
        """
        Parse Gherkin content and extract scenarios into CSV rows.
        
        Args:
            gherkin_content: Gherkin scenarios as string
            
        Returns:
            List of dictionaries representing CSV rows
        """
        # Clean up the content - remove markdown code blocks if present
        gherkin_content = self._clean_gherkin_content(gherkin_content)
        
        rows = []
        lines = gherkin_content.split('\n')
        
        current_feature = None
        current_scenario = None
        current_steps = []
        current_tags = []
        in_scenario = False
        in_examples = False
        example_headers = []
        example_rows = []
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            # Feature
            if line.startswith('Feature:'):
                current_feature = line.replace('Feature:', '').strip()
                continue
            
            # Tags
            if line.startswith('@'):
                tags = re.findall(r'@(\w+)', line)
                current_tags.extend(tags)
                continue
            
            # Scenario
            if line.startswith('Scenario:') or line.startswith('Scenario Outline:'):
                # Save previous scenario if exists
                if current_scenario and current_steps:
                    rows.append(self._create_csv_row(
                        current_feature, current_scenario, current_steps, current_tags
                    ))
                
                current_scenario = line.replace('Scenario:', '').replace('Scenario Outline:', '').strip()
                current_steps = []
                # Keep tags for the scenario (they apply to all scenarios until new tags are found)
                in_scenario = True
                in_examples = False
                continue
            
            # Background
            if line.startswith('Background:'):
                in_scenario = False
                continue
            
            # Examples
            if line.startswith('Examples:') or line.startswith('Scenarios:'):
                in_examples = True
                example_headers = []
                example_rows = []
                continue
            
            # Steps (Given, When, Then, And, But)
            # Also handle steps that might have different indentation or formatting
            step_keywords = ['Given', 'When', 'Then', 'And', 'But']
            if in_scenario:
                # Check if line starts with any step keyword (case-insensitive)
                line_lower = line.lower()
                for keyword in step_keywords:
                    if line_lower.startswith(keyword.lower() + ' ') or line_lower.startswith(keyword.lower() + ':'):
                        # Normalize the step (capitalize keyword and ensure space after)
                        remaining = line[len(keyword):].lstrip(':').lstrip()
                        # Ensure there's a space after the keyword
                        normalized_step = keyword + (' ' + remaining if remaining else '')
                        current_steps.append(normalized_step)
                        break
                else:
                    # If it's indented and we're in a scenario, it might be a continuation
                    # or a step without proper keyword - skip for now
                    pass
                continue
            
            # Example table headers
            if in_examples and '|' in line:
                parts = [p.strip() for p in line.split('|') if p.strip()]
                if not example_headers:
                    example_headers = parts
                else:
                    # This is a data row
                    if len(parts) == len(example_headers):
                        example_rows.append(parts)
                continue
            
            # End of examples
            if in_examples and not line.startswith('|'):
                in_examples = False
                # Add rows for each example
                for example_row in example_rows:
                    scenario_with_example = f"{current_scenario} (Example: {example_row[0] if example_row else 'N/A'})"
                    steps_with_example = current_steps.copy()
                    # Replace placeholders in steps with example values
                    for i, header in enumerate(example_headers):
                        if i < len(example_row):
                            placeholder = f"<{header}>"
                            value = example_row[i]
                            steps_with_example = [s.replace(placeholder, value) for s in steps_with_example]
                    
                    rows.append(self._create_csv_row(
                        current_feature, scenario_with_example, steps_with_example, current_tags
                    ))
                example_rows = []
                continue
        
        # Save last scenario
        if current_scenario and current_steps:
            rows.append(self._create_csv_row(
                current_feature, current_scenario, current_steps, current_tags
            ))
        
        return rows
    
    def _clean_gherkin_content(self, content: str) -> str:
        """
        Clean Gherkin content by removing markdown code blocks and extra formatting.
        
        Args:
            content: Raw Gherkin content (may include markdown)
            
        Returns:
            Cleaned Gherkin content
        """
        # Remove markdown code blocks (```gherkin ... ``` or ``` ... ```)
        import re
        
        # Remove code blocks
        content = re.sub(r'```gherkin\s*\n', '', content, flags=re.IGNORECASE)
        content = re.sub(r'```\s*\n', '', content)
        content = re.sub(r'```\s*$', '', content, flags=re.MULTILINE)
        
        # Remove leading/trailing whitespace
        content = content.strip()
        
        return content
    
    def _create_csv_row(
        self,
        feature: Optional[str],
        scenario: Optional[str],
        steps: List[str],
        tags: List[str]
    ) -> Dict[str, Any]:
        """Create a CSV row from scenario data."""
        # Separate steps by type, ensuring proper keyword matching
        given_steps = []
        when_steps = []
        then_steps = []
        
        for step in steps:
            step_lower = step.lower().strip()
            if step_lower.startswith('given '):
                given_steps.append(step)
            elif step_lower.startswith('when '):
                when_steps.append(step)
            elif step_lower.startswith('then '):
                then_steps.append(step)
            elif step_lower.startswith('and '):
                # Determine context from previous steps
                all_previous = given_steps + when_steps + then_steps
                if given_steps and (not when_steps or given_steps[-1] == all_previous[-1]):
                    given_steps.append(step)
                elif when_steps and (not then_steps or when_steps[-1] == all_previous[-1]):
                    when_steps.append(step)
                elif then_steps:
                    then_steps.append(step)
                else:
                    given_steps.append(step)  # Default to Given if unclear
        
        return {
            'Feature': feature or '',
            'Scenario': scenario or '',
            'Tags': ', '.join(tags) if tags else '',
            'Given': ' | '.join(given_steps) if given_steps else '',
            'When': ' | '.join(when_steps) if when_steps else '',
            'Then': ' | '.join(then_steps) if then_steps else '',
            'All Steps': ' | '.join(steps) if steps else ''
        }
    
    def save_to_csv(
        self,
        data: List[Dict[str, Any]],
        filename: str,
        fieldnames: Optional[List[str]] = None
    ) -> str:
        """
        Save data to CSV file.
        
        Args:
            data: List of dictionaries to write
            filename: Output filename (without extension)
            fieldnames: Optional list of field names (uses data keys if not provided)
            
        Returns:
            Path to saved CSV file
        """
        if not data:
            raise ValueError("No data to write to CSV")
        
        # Generate filename with timestamp prefix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Clean filename to remove extension if present
        clean_filename = filename.replace('.json', '').replace('.yaml', '').replace('.yml', '')
        csv_filename = f"{timestamp}_{clean_filename}_scenarios.csv"
        csv_path = self.output_dir / csv_filename
        
        # Determine fieldnames
        if fieldnames is None:
            fieldnames = list(data[0].keys())
        
        # Write CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        return str(csv_path)
    
    def gherkin_to_csv(
        self,
        gherkin_content: str,
        swagger_name: str
    ) -> str:
        """
        Convert Gherkin content to CSV file.
        
        Args:
            gherkin_content: Gherkin scenarios as string
            swagger_name: Name of the swagger (for filename)
            
        Returns:
            Path to saved CSV file
        """
        if not gherkin_content or not gherkin_content.strip():
            print("⚠ Warning: Empty Gherkin content received")
            csv_data = [{
                'Feature': 'No Scenarios Generated',
                'Scenario': 'Empty Response',
                'Tags': '',
                'Given': '',
                'When': '',
                'Then': '',
                'All Steps': 'No Gherkin scenarios were generated by the LLM.'
            }]
        else:
            # Parse Gherkin to CSV data
            csv_data = self.parse_gherkin_to_csv_data(gherkin_content)
            
            if not csv_data:
                # If parsing fails, try to extract at least some information
                print("⚠ Warning: Gherkin parser found no scenarios. Saving raw content.")
                
                # Try to find at least Feature and Scenario keywords
                lines = gherkin_content.split('\n')
                feature = None
                scenario = None
                
                for line in lines:
                    line_stripped = line.strip()
                    if line_stripped.startswith('Feature:'):
                        feature = line_stripped.replace('Feature:', '').strip()
                    elif line_stripped.startswith('Scenario:'):
                        scenario = line_stripped.replace('Scenario:', '').strip()
                        break
                
                csv_data = [{
                    'Feature': feature or 'Generated Scenarios',
                    'Scenario': scenario or 'Parsing Failed - See All Steps',
                    'Tags': '',
                    'Given': '',
                    'When': '',
                    'Then': '',
                    'All Steps': gherkin_content[:5000]  # Limit to first 5000 chars
                }]
        
        # Save to CSV
        return self.save_to_csv(csv_data, swagger_name)

