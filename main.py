#!/usr/bin/env python3
"""
Main entry point for Swagger Tool.

Orchestrates the full workflow:
1. Download Swagger schema from URL
2. Process with algorithms
3. Generate Gherkin scenarios via LLM
4. Save to CSV
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from src.modules.swagger_tool.schema_fetcher import SchemaFetcher
from src.modules.engine import SchemaProcessor, SchemaAnalyzer, LLMPrompter
from src.modules.engine.algorithms import CSVGenerator

# Load environment variables from .env file
load_dotenv()


def main():
    """Main function to run the complete Swagger processing workflow."""
    print("=" * 70)
    print("Swagger Schema Processor & Test Scenario Generator")
    print("=" * 70)
    print()
    
    # Get API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠ Warning: OPENAI_API_KEY not found in environment variables.")
        print("   Please set it in your .env file or export it.")
        print("   Example: export OPENAI_API_KEY='your-key-here'")
        return
    
    # Step 1: Get URL from user input
    url = input("Enter Swagger/OpenAPI schema URL: ").strip()
    
    if not url:
        print("Error: URL cannot be empty.")
        return
    
    # Step 2: Download schema
    print("\n" + "=" * 70)
    print("Step 1: Downloading schema...")
    print("=" * 70)
    
    fetcher = SchemaFetcher()
    schema_path = fetcher.download_and_save(url, "json")
    
    if not schema_path:
        print("✗ Failed to download schema. Exiting.")
        return
    
    print(f"✓ Schema downloaded: {schema_path}")
    
    # Extract schema name for output
    schema_filename = Path(schema_path).name
    swagger_name = Path(schema_path).stem  # filename without extension
    
    # Step 3: Process schema
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
    
    # Step 4: Analyze schema for test traceability
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
    
    # Step 5: Generate Gherkin scenarios via LLM
    print("\n" + "=" * 70)
    print("Step 4: Generating Gherkin test scenarios via LLM...")
    print("=" * 70)
    
    prompter = LLMPrompter(model="gpt-4", api_key=api_key)
    
    try:
        gherkin_scenarios = prompter.generate_gherkin_scenarios(processed_data, analysis_data)
        
        if not gherkin_scenarios:
            print("⚠ Failed to generate Gherkin scenarios. Using placeholder.")
            # Create a placeholder Gherkin content
            gherkin_scenarios = f"""Feature: {processed_data.get('info', {}).get('title', 'API')} Testing

  Scenario: Placeholder - LLM generation failed
    Given the API is available
    When I request test scenarios
    Then I should receive comprehensive Gherkin scenarios
    
  # Note: Check API key and network connection if this appears.
"""
        else:
            print("✓ Gherkin scenarios generated")
    
    except ValueError as e:
        print(f"✗ Validation Error: {e}")
        print("\nThis usually means:")
        print("  - The schema has no endpoints to analyze")
        print("  - The analysis data is empty or malformed")
        print("  - The processed data is missing required fields")
        print("\nPlease check:")
        print(f"  - Endpoints analyzed: {len(analysis_data.get('endpoints', []))}")
        print(f"  - Processed data keys: {list(processed_data.keys()) if processed_data else 'None'}")
        print("\nUsing placeholder scenarios...")
        # Create a placeholder Gherkin content
        gherkin_scenarios = f"""Feature: {processed_data.get('info', {}).get('title', 'API')} Testing

  Scenario: Placeholder - Input validation failed
    Given the API schema was processed
    When validation checks are performed
    Then an error is detected: {str(e)}
    
  # Note: The schema may be empty or missing required data.
"""
    except Exception as e:
        print(f"✗ Unexpected error during Gherkin generation: {e}")
        print("Using placeholder scenarios...")
        # Create a placeholder Gherkin content
        gherkin_scenarios = f"""Feature: {processed_data.get('info', {}).get('title', 'API')} Testing

  Scenario: Placeholder - Unexpected error
    Given the API schema was processed
    When Gherkin generation is attempted
    Then an error occurs: {str(e)}
    
  # Note: Check the error message above for details.
"""
    
    # Step 6: Save to CSV
    print("\n" + "=" * 70)
    print("Step 5: Saving to CSV...")
    print("=" * 70)
    
    csv_generator = CSVGenerator()
    csv_path = csv_generator.gherkin_to_csv(gherkin_scenarios, swagger_name)
    
    print(f"✓ CSV saved: {csv_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Schema: {schema_filename}")
    print(f"API: {processed_data.get('info', {}).get('title', 'Unknown')}")
    print(f"Endpoints: {processed_data.get('paths_count', 0)}")
    print(f"Output: {csv_path}")
    print("\n✓ Processing complete!")


if __name__ == "__main__":
    main()
