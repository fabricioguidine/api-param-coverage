"""
Scenario Generator

Handles Gherkin scenario generation and export workflows.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..engine import LLMPrompter
from ..engine.algorithms import CSVGenerator
from ..cli import InteractiveSelector, print_success, print_info, confirm_action


def _parse_gherkin_to_scenarios(gherkin_content: str) -> List[Dict[str, Any]]:
    """
    Parse Gherkin content to extract scenario data.
    
    Args:
        gherkin_content: Gherkin scenarios string
        
    Returns:
        List of scenario dictionaries
    """
    scenarios = []
    current_feature = None
    current_scenario = None
    current_steps = []
    tags = []
    
    lines = gherkin_content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('Feature:'):
            current_feature = line.replace('Feature:', '').strip()
        elif line.startswith('@'):
            tags = [tag.strip('@') for tag in line.split() if tag.startswith('@')]
        elif line.startswith('Scenario:') or line.startswith('Scenario Outline:'):
            if current_scenario:
                scenarios.append({
                    'Feature': current_feature or 'Unknown',
                    'Scenario': current_scenario,
                    'Tags': ', '.join(tags) if tags else '',
                    'All Steps': '\n'.join(current_steps)
                })
            current_scenario = line.replace('Scenario:', '').replace('Scenario Outline:', '').strip()
            current_steps = []
            tags = []
        elif line and (line.startswith('Given') or line.startswith('When') or 
                      line.startswith('Then') or line.startswith('And') or 
                      line.startswith('But')):
            current_steps.append(line)
    
    # Add last scenario
    if current_scenario:
        scenarios.append({
            'Feature': current_feature or 'Unknown',
            'Scenario': current_scenario,
            'Tags': ', '.join(tags) if tags else '',
            'All Steps': '\n'.join(current_steps)
        })
    
    return scenarios


def generate_gherkin_scenarios(
    filtered_analysis_data: Dict[str, Any],
    processed_data: Dict[str, Any],
    llm_prompter: LLMPrompter,
    schema_name: str
) -> Optional[str]:
    """
    Generate Gherkin scenarios using LLM.
    
    Args:
        filtered_analysis_data: Filtered analysis data
        processed_data: Processed schema data
        llm_prompter: LLMPrompter instance
        schema_name: Schema name for output
        
    Returns:
        Gherkin content string or None if error
    """
    print("\n" + "=" * 70)
    print("Step 6: Generating Gherkin test scenarios...")
    print("=" * 70)
    
    print_info(f"Generating scenarios for {len(filtered_analysis_data.get('endpoints', []))} endpoints...")
    
    prompt = llm_prompter.create_prompt(
        processed_data,
        task="gherkin",
        analysis_data=filtered_analysis_data
    )
    
    gherkin_content = llm_prompter.send_prompt(prompt)
    
    if not gherkin_content:
        print("✗ Failed to generate Gherkin scenarios.")
        return None
    
    print_success(f"Gherkin scenarios generated ({len(gherkin_content)} characters)")
    return gherkin_content


def export_scenarios(
    gherkin_content: str,
    schema_name: str,
    run_output_dir: Path,
    run_timestamp: str
) -> List[Path]:
    """
    Export scenarios to CSV format.
    
    Args:
        gherkin_content: Gherkin scenarios string
        schema_name: Schema name
        run_output_dir: Output directory
        run_timestamp: Run timestamp
        
    Returns:
        List of exported file paths
    """
    print("\n" + "=" * 70)
    print("Step 7: Exporting scenarios to CSV...")
    print("=" * 70)
    
    exported_files = []
    
    # Generate CSV
    csv_generator = CSVGenerator(output_dir=str(run_output_dir))
    csv_path = csv_generator.generate_csv(gherkin_content, schema_name)
    
    if csv_path:
        print_success(f"CSV exported: {csv_path}")
        exported_files.append(csv_path)
    
    return exported_files

