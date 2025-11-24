#!/usr/bin/env python3
"""
Main entry point for Swagger Tool.

Orchestrates the full workflow:
1. Load configuration from files or environment variables
2. Download Swagger schema from URL
3. Process with algorithms
4. Handle BRD (Business Requirement Document) - load, generate, or parse
5. Cross-reference BRD with Swagger schema to filter scope
6. Generate Gherkin scenarios via LLM (only for BRD-covered endpoints)
7. Export to CSV format
8. Generate analytics and coverage reports
"""

import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from src.modules.swagger_tool.schema_fetcher import SchemaFetcher
from src.modules.engine import SchemaProcessor, SchemaAnalyzer, LLMPrompter
from src.modules.engine.algorithms import CSVGenerator
from src.modules.brd import BRDLoader, BRDParser, SchemaCrossReference
from src.modules.brd_generator import BRDGenerator
from src.modules.config import ConfigManager
from src.modules.workflow import (
    handle_brd_selection, handle_brd_generation, handle_brd_parsing,
    apply_coverage_filter, apply_brd_filter
)
from src.modules.workflow.scenario_generator import generate_gherkin_scenarios, export_scenarios
from src.modules.cli import (
    ProgressBar, StatusUpdater, InteractiveSelector, ErrorHandler,
    print_section, print_success, print_error, print_warning, print_info, confirm_action
)

# Load environment variables from .env file
load_dotenv()

# Load configuration
config_manager = ConfigManager()

# Import LLM provider setup
from src.modules.utils.llm_provider import get_api_key_and_provider


def main():
    """Main function to run the complete Swagger processing workflow."""
    print_section("Swagger Schema Processor & Test Scenario Generator")
    
    # Initialize status updater
    status = StatusUpdater()
    
    # Create run identifier at the start
    run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get API key and provider (will prompt on first run if needed)
    api_key, provider = get_api_key_and_provider()
    if not api_key:
        print_error("LLM API key not configured.")
        print_info("Please run the tool again to set up your API key.")
        return
    
    print_info(f"Using LLM provider: {provider}")
    
    # Step 1: Get URL from user input
    while True:
        url = input("\nEnter Swagger/OpenAPI schema URL: ").strip()
        
        if url:
            break
        
        print_warning("URL cannot be empty.")
        if not confirm_action("Do you want to try again?", default=True):
            return
    
    # Step 2: Download schema
    print("\n" + "=" * 70)
    print("Step 1: Downloading schema...")
    print("=" * 70)
    
    fetcher = SchemaFetcher(schemas_dir=config_manager.paths.schemas_dir)
    schema_path = fetcher.download_and_save(url, "json")
    
    if not schema_path:
        print("✗ Failed to download schema. Exiting.")
        return
    
    print_success(f"Schema downloaded: {schema_path}")
    
    # Extract schema name for output
    schema_filename = Path(schema_path).name
    swagger_name = Path(schema_path).stem
    
    # Create run directory structure in output/ folder
    run_id = f"{run_timestamp}_{swagger_name}"
    run_output_dir = Path(f"output/{run_id}")
    run_output_dir.mkdir(parents=True, exist_ok=True)
    
    print_info(f"Output directory: {run_output_dir}")
    
    # Step 3: Process schema
    print_section("Step 2: Processing schema...")
    status.update("Processing schema...", "info")
    
    processor = SchemaProcessor()
    
    try:
        processed_data = processor.process_schema_file(schema_filename)
        
        if not processed_data:
            print_error("Failed to process schema. Exiting.")
            return
        
        print_success("Schema processed:")
        print(f"  - API: {processed_data.get('info', {}).get('title', 'Unknown')}")
        print(f"  - Endpoints: {processed_data.get('paths_count', 0)}")
    except Exception as e:
        action = ErrorHandler.handle_error(e, context="processing schema")
        if action == "exit":
            return
        processed_data = None
    
    # Step 4: Analyze schema for test traceability
    print_section("Step 3: Analyzing schema for test traceability...")
    status.update("Analyzing schema...", "info")
    
    analyzer = SchemaAnalyzer()
    
    try:
        analysis_data = analyzer.analyze_schema_file(schema_filename)
        
        if not analysis_data or not analysis_data.get('endpoints'):
            print_error("Failed to analyze schema. Exiting.")
            return
        
        print_success("Schema analyzed:")
        print(f"  - Endpoints analyzed: {len(analysis_data.get('endpoints', []))}")
    except Exception as e:
        action = ErrorHandler.handle_error(e, context="analyzing schema")
        if action == "exit":
            return
        analysis_data = None
    
    # Step 5: Handle BRD (Business Requirement Document)
    print_section("Step 4: Business Requirement Document (BRD)...")
    
    brd_loader = BRDLoader()
    brd = None
    
    # Ask user about BRD handling with interactive selection
    brd_options = [
        "Load existing BRD schema file (JSON)",
        "Parse BRD from document (PDF, Word, TXT, CSV)",
        "Generate BRD from Swagger schema (using LLM)"
    ]
    
    selected_option = InteractiveSelector.select_from_list(
        brd_options,
        prompt="How would you like to handle the Business Requirement Document (BRD)?",
        allow_cancel=False
    )
    
    if not selected_option:
        print_warning("BRD selection canceled. Exiting.")
        return
    
    brd_choice = str(brd_options.index(selected_option) + 1)
    
    if brd_choice == "1":
        # Load existing BRD schema
        status.update("Loading available BRD files...", "info")
        available_brds = brd_loader.list_available_brds()
        
        if not available_brds:
            print_warning("No BRD schema files found in reference/brd/output/")
            print_info("Options:")
            print_info("  - Place BRD documents in reference/brd/input/ and choose option 2")
            print_info("  - Choose option 3 to generate from Swagger schema")
            
            fallback_options = [
                "Parse BRD from document",
                "Generate BRD from Swagger schema"
            ]
            fallback = InteractiveSelector.select_from_list(fallback_options, "Select alternative option")
            if not fallback:
                return
            brd_choice = str(fallback_options.index(fallback) + 2)
        else:
            selected_brd = InteractiveSelector.select_from_list(
                available_brds,
                prompt="Select BRD schema file",
                allow_cancel=True
            )
            
            if not selected_brd:
                print_warning("BRD selection canceled.")
                return
            
            status.update(f"Loading BRD: {selected_brd}...", "info")
            brd = brd_loader.load_brd_from_file(selected_brd)
            
            if brd:
                print_success(f"BRD loaded: {brd.title}")
                print(f"  - Requirements: {len(brd.requirements)}")
            else:
                action = ErrorHandler.handle_error(
                    Exception("Failed to load BRD file"),
                    context="loading BRD",
                    recovery_options=["Try different file", "Generate new BRD", "Continue without BRD"]
                )
                if "different file" in action:
                    brd_choice = "1"  # Retry selection
                elif "generate" in action:
                    brd_choice = "3"
                elif "continue" in action:
                    brd = None
                else:
                    return
    
    elif brd_choice == "2":
        # Parse BRD from document
        from src.modules.brd import BRDParser
        
        parser = BRDParser(api_key=api_key, model=config_manager.llm.model, provider=provider)
        
        # List available documents in input folder
        input_dir = Path("reference/brd/input")
        if not input_dir.exists():
            input_dir.mkdir(parents=True, exist_ok=True)
        
        documents = [f for f in input_dir.iterdir() if f.is_file() and f.suffix.lower() in ['.pdf', '.doc', '.docx', '.txt', '.csv', '.md']]
        
        if not documents:
            print("⚠ No BRD documents found in reference/brd/input/")
            print("   Please place your BRD document (PDF, Word, TXT, CSV) in that folder.")
            return
        
        print("\nAvailable BRD documents:")
        for i, doc in enumerate(documents, 1):
            print(f"  {i}. {doc.name}")
        
        try:
            doc_choice = int(input("\nSelect document to parse (number): ").strip())
            if 1 <= doc_choice <= len(documents):
                selected_doc = documents[doc_choice - 1]
                print(f"\n📄 Parsing document: {selected_doc.name}...")
                brd = parser.parse_document(selected_doc.name)
                
                if brd:
                    print(f"✓ BRD parsed: {brd.title}")
                    print(f"  - Requirements: {len(brd.requirements)}")
                else:
                    print("✗ Failed to parse BRD document.")
                    return
            else:
                print("⚠ Invalid selection.")
                return
        except (ValueError, IndexError):
            print("⚠ Invalid input.")
            return
    
    if brd_choice == "3" or (not brd):
        # Generate BRD using LLM
        print("\n📋 Generating BRD from Swagger schema...")
        
        # Ask for coverage percentage
        print("\nWhat percentage of API endpoints would you like to cover?")
        print("  - Enter a number between 1-100 (e.g., 50 for 50% coverage)")
        print("  - Or press Enter to use default (100% - all endpoints)")
        
        coverage_input = input("\nCoverage percentage (default: 100): ").strip()
        
        try:
            if coverage_input:
                coverage_percentage = float(coverage_input)
                if coverage_percentage < 1 or coverage_percentage > 100:
                    print("⚠ Invalid percentage. Using default (100%).")
                    coverage_percentage = 100.0
            else:
                coverage_percentage = 100.0
        except ValueError:
            print("⚠ Invalid input. Using default (100%).")
            coverage_percentage = 100.0
        
        print(f"  → Coverage set to: {coverage_percentage}%")
        
        brd_generator = BRDGenerator(
            api_key=api_key,
            model=config_manager.llm.model,
            provider=provider,
            analytics_dir=str(run_output_dir / "analytics")
        )
        brd = brd_generator.generate_brd_from_swagger(
            processed_data, 
            analysis_data, 
            schema_filename,
            coverage_percentage=coverage_percentage
        )
        
        if brd:
            print(f"✓ BRD generated: {brd.title}")
            print(f"  - Requirements: {len(brd.requirements)}")
            
            # Save generated BRD
            brd_filename = f"{swagger_name}_brd"
            brd_path = brd_loader.save_brd_to_file(brd, brd_filename)
            print(f"  - Saved to: {brd_path}")
        else:
            print("✗ Failed to generate BRD. Continuing without BRD filtering...")
            brd = None
    
    # Step 6: Cross-reference BRD with Swagger schema or apply coverage filter
    filtered_analysis_data = analysis_data
    coverage_applied = False
    
    if brd:
        print("\n" + "=" * 70)
        print("Step 5: Cross-referencing BRD with Swagger schema...")
        print("=" * 70)
        
        filtered_analysis_data, coverage_report = apply_brd_filter(analysis_data, brd)
        
        print(f"✓ Cross-reference complete:")
        print(f"  - Total endpoints: {coverage_report['total_endpoints']}")
        print(f"  - BRD covered: {coverage_report['covered_endpoints']}")
        print(f"  - Not covered: {coverage_report['not_covered_endpoints']}")
        print(f"  - Coverage: {coverage_report['coverage_percentage']}%")
        
        if coverage_report['not_covered_endpoints'] > 0:
            print(f"\n⚠ Note: {coverage_report['not_covered_endpoints']} endpoints are not covered by BRD")
            print("   Only BRD-covered endpoints will be included in test scenarios.")
        coverage_applied = True
    else:
        # No BRD - ask if user wants to limit coverage
        print("\n⚠ No BRD provided. All endpoints will be tested by default.")
        print("   Would you like to limit the coverage percentage?")
        coverage_choice = input(f"   Enter coverage % ({MIN_COVERAGE_PERCENTAGE}-{MAX_COVERAGE_PERCENTAGE}, or press Enter for {DEFAULT_COVERAGE_PERCENTAGE}%): ").strip()
        
        if coverage_choice:
            try:
                coverage_percentage = float(coverage_choice)
                if MIN_COVERAGE_PERCENTAGE <= coverage_percentage <= MAX_COVERAGE_PERCENTAGE:
                    filtered_analysis_data, coverage_report = apply_coverage_filter(analysis_data, coverage_percentage)
                    print(f"   → Limited to {coverage_report['selected_endpoints']} out of {coverage_report['total_endpoints']} endpoints ({coverage_percentage}% coverage)")
                    coverage_applied = True
                else:
                    print(f"   ⚠ Invalid percentage. Using all endpoints.")
            except ValueError:
                print("   ⚠ Invalid input. Using all endpoints.")
    
    # Step 7: Generate Gherkin scenarios via LLM
    print("\n" + "=" * 70)
    print("Step 6: Generating Gherkin test scenarios via LLM...")
    print("=" * 70)
    
    # Initialize components with run-specific output directories
    prompter = LLMPrompter(
        model=config_manager.llm.model,
        api_key=api_key,
        provider=provider,
        analytics_dir=str(run_output_dir / "analytics")
    )
    csv_generator = CSVGenerator(output_dir=str(run_output_dir))
    
    try:
        # Use filtered analysis data (only BRD-covered endpoints if BRD exists)
        gherkin_scenarios = prompter.generate_gherkin_scenarios(processed_data, filtered_analysis_data)
        
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
    
    # Step 8: Save to CSV
    print("\n" + "=" * 70)
    print("Step 7: Saving to CSV...")
    print("=" * 70)
    
    csv_path = csv_generator.gherkin_to_csv(gherkin_scenarios, swagger_name)
    print(f"✓ CSV saved: {csv_path}")
    
    # Summary
    print_section("Summary")
    print(f"Schema: {schema_filename}")
    print(f"API: {processed_data.get('info', {}).get('title', 'Unknown')}")
    print(f"Total Endpoints: {processed_data.get('paths_count', 0)}")
    if brd:
        print(f"BRD: {brd.title}")
        print(f"BRD Coverage: {filtered_analysis_data.get('coverage_percentage', 0)}%")
        print(f"Tested Endpoints: {filtered_analysis_data.get('brd_covered_endpoints', 0)}")
    elif coverage_applied:
        tested_count = len(filtered_analysis_data.get('endpoints', []))
        total_count = len(analysis_data.get('endpoints', []))
        coverage_pct = round((tested_count / total_count * 100), 2) if total_count > 0 else 0
        print(f"Coverage Applied: {coverage_pct}%")
        print(f"Tested Endpoints: {tested_count} out of {total_count}")
    else:
        print(f"Tested Endpoints: {len(filtered_analysis_data.get('endpoints', []))} (all endpoints)")
    print(f"Output: {csv_path}")
    print("\n✓ Processing complete!")


if __name__ == "__main__":
    main()
