#!/usr/bin/env python3
"""
Script to run the tool with weather.gov API and dummy BRD schema.
Non-interactive version for automated testing.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from src.modules.swagger.schema_fetcher import SchemaFetcher
from src.modules.engine import SchemaProcessor, SchemaAnalyzer, LLMPrompter
from src.modules.engine.algorithms import CSVGenerator
from src.modules.brd import BRDLoader, BRDParser, SchemaCrossReference
from src.modules.brd_generator import BRDGenerator

# Load environment variables
load_dotenv()

def main():
    """Run the tool with weather.gov API."""
    print("=" * 70)
    print("Weather.gov API Test Scenario Generator")
    print("=" * 70)
    print()
    
    # Create run identifier at the start
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠ Warning: OPENAI_API_KEY not found in environment variables.")
        print("   Please set it in your .env file.")
        return
    
    # Weather.gov API URL
    url = "https://api.weather.gov/openapi.json"
    
    print(f"Using schema URL: {url}")
    print()
    
    # Step 1: Download schema
    print("=" * 70)
    print("Step 1: Downloading schema...")
    print("=" * 70)
    
    fetcher = SchemaFetcher()
    schema_path = fetcher.download_and_save(url, "json")
    
    if not schema_path:
        print("✗ Failed to download schema. Exiting.")
        return
    
    print(f"✓ Schema downloaded: {schema_path}")
    
    schema_filename = Path(schema_path).name
    swagger_name = Path(schema_path).stem
    
    # Create run directory structure directly in docs/ (flat structure)
    run_id = f"{run_timestamp}_{swagger_name}"
    run_output_dir = Path(f"docs/{run_id}")
    run_output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Output directory: {run_output_dir}")
    
    # Step 2: Process schema
    print("\n" + "=" * 70)
    print("Step 2: Processing schema...")
    print("=" * 70)
    
    processor = SchemaProcessor()
    processed_data = processor.process_schema_file(schema_filename)
    
    if not processed_data:
        print("✗ Failed to process schema. Exiting.")
        return
    
    print(f"✓ Schema processed:")
    print(f"  - API: {processed_data.get('info', {}).get('title', 'Unknown')}")
    print(f"  - Endpoints: {processed_data.get('paths_count', 0)}")
    
    # Step 3: Analyze schema
    print("\n" + "=" * 70)
    print("Step 3: Analyzing schema for test traceability...")
    print("=" * 70)
    
    analyzer = SchemaAnalyzer()
    analysis_data = analyzer.analyze_schema_file(schema_filename)
    
    if not analysis_data or not analysis_data.get('endpoints'):
        print("✗ Failed to analyze schema. Exiting.")
        return
    
    print(f"✓ Schema analyzed:")
    print(f"  - Endpoints analyzed: {len(analysis_data.get('endpoints', []))}")
    
    # Step 4: Load dummy BRD
    print("\n" + "=" * 70)
    print("Step 4: Loading dummy BRD schema...")
    print("=" * 70)
    
    brd_loader = BRDLoader()
    brd = brd_loader.load_brd_from_file("weather_gov_api_brd")
    
    if not brd:
        print("⚠ Dummy BRD not found. Generating one...")
        brd_generator = BRDGenerator(api_key=api_key, model="gpt-4")
        brd = brd_generator.generate_brd_from_swagger(processed_data, analysis_data, schema_filename)
        
        if brd:
            brd_path = brd_loader.save_brd_to_file(brd, "weather_gov_api_brd")
            print(f"✓ BRD generated and saved: {brd_path}")
        else:
            print("✗ Failed to generate BRD. Continuing without BRD filtering...")
            brd = None
    else:
        print(f"✓ BRD loaded: {brd.title}")
        print(f"  - Requirements: {len(brd.requirements)}")
    
    # Step 5: Cross-reference BRD with Swagger
    filtered_analysis_data = analysis_data
    
    if brd:
        print("\n" + "=" * 70)
        print("Step 5: Cross-referencing BRD with Swagger schema...")
        print("=" * 70)
        
        cross_ref = SchemaCrossReference()
        filtered_analysis_data = cross_ref.filter_endpoints_by_brd(analysis_data, brd)
        
        coverage_report = cross_ref.get_brd_coverage_report(analysis_data, brd)
        
        print(f"✓ Cross-reference complete:")
        print(f"  - Total endpoints: {coverage_report['total_endpoints']}")
        print(f"  - BRD covered: {coverage_report['covered_endpoints']}")
        print(f"  - Not covered: {coverage_report['not_covered_endpoints']}")
        print(f"  - Coverage: {coverage_report['coverage_percentage']}%")
    
    # Step 6: Generate Gherkin scenarios
    print("\n" + "=" * 70)
    print("Step 6: Generating Gherkin test scenarios via LLM...")
    print("=" * 70)
    
    # Initialize components with run-specific output directories (flat structure)
    prompter = LLMPrompter(model="gpt-4", api_key=api_key, analytics_dir=str(run_output_dir))
    csv_generator = CSVGenerator(output_dir=str(run_output_dir))
    
    try:
        gherkin_scenarios = prompter.generate_gherkin_scenarios(processed_data, filtered_analysis_data)
        
        if not gherkin_scenarios:
            print("⚠ Failed to generate Gherkin scenarios. Using placeholder.")
            gherkin_scenarios = f"""Feature: {processed_data.get('info', {}).get('title', 'API')} Testing

  Scenario: Placeholder - LLM generation failed
    Given the API is available
    When I request test scenarios
    Then I should receive comprehensive Gherkin scenarios
"""
        else:
            print("✓ Gherkin scenarios generated")
    
    except Exception as e:
        print(f"✗ Error during Gherkin generation: {e}")
        gherkin_scenarios = f"""Feature: {processed_data.get('info', {}).get('title', 'API')} Testing

  Scenario: Placeholder - Error occurred
    Given an error occurred: {str(e)}
    When processing the schema
    Then placeholder scenarios are generated
"""
    
    # Step 7: Save to CSV
    print("\n" + "=" * 70)
    print("Step 7: Saving to CSV...")
    print("=" * 70)
    
    # Use the csv_generator already initialized with run directory
    csv_path = csv_generator.gherkin_to_csv(gherkin_scenarios, swagger_name)
    
    print(f"✓ CSV saved: {csv_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Schema: {schema_filename}")
    print(f"API: {processed_data.get('info', {}).get('title', 'Unknown')}")
    print(f"Total Endpoints: {processed_data.get('paths_count', 0)}")
    if brd:
        print(f"BRD: {brd.title}")
        print(f"BRD Coverage: {filtered_analysis_data.get('coverage_percentage', 0)}%")
        print(f"Tested Endpoints: {filtered_analysis_data.get('brd_covered_endpoints', 0)}")
    print(f"Output: {csv_path}")
    print("\n✓ Processing complete!")
    print(f"\n📁 All outputs saved to: {run_output_dir}")
    print(f"📄 CSV file: {run_output_dir}/*.csv")
    print(f"📊 Analytics: {run_output_dir}/*.txt")
    print(f"📈 Reports: {run_output_dir}/*_algorithm_*.txt")

if __name__ == "__main__":
    main()

