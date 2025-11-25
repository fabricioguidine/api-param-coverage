"""
BRD Handler

Handles BRD selection, loading, parsing, and generation workflows.
"""

from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from ..brd import BRDLoader, BRDParser, BRDSchema, BRDGenerator
from ..cli import InteractiveSelector, ErrorHandler, print_success, print_warning, print_info, print_error
from ..utils.constants import DEFAULT_COVERAGE_PERCENTAGE, MAX_COVERAGE_PERCENTAGE, MIN_COVERAGE_PERCENTAGE


def handle_brd_selection(
    brd_loader: BRDLoader,
    api_key: str,
    status_updater
) -> Tuple[Optional[BRDSchema], Optional[str]]:
    """
    Handle BRD selection from available files.
    
    Args:
        brd_loader: BRDLoader instance
        api_key: OpenAI API key
        status_updater: StatusUpdater instance
        
    Returns:
        Tuple of (BRD schema or None, choice string)
    """
    status_updater.update("Loading available BRD files...", "info")
    available_brds = brd_loader.list_available_brds()
    
    if not available_brds:
        from ..utils.constants import DEFAULT_BRD_INPUT_SCHEMA_DIR, DEFAULT_BRD_INPUT_TRANSFORMATOR_DIR
        print_warning(f"No BRD schema files found in {DEFAULT_BRD_INPUT_SCHEMA_DIR}/")
        print_info("Options:")
        print_info(f"  - Place BRD documents in {DEFAULT_BRD_INPUT_TRANSFORMATOR_DIR}/ and choose option 2")
        print_info("  - Choose option 3 to generate from Swagger schema")
        
        fallback_options = [
            "Parse BRD from document",
            "Generate BRD from Swagger schema"
        ]
        fallback = InteractiveSelector.select_from_list(fallback_options, "Select alternative option")
        if not fallback:
            return None, None
        return None, str(fallback_options.index(fallback) + 2)
    
    selected_brd = InteractiveSelector.select_from_list(
        available_brds,
        prompt="Select BRD schema file",
        allow_cancel=True
    )
    
    if not selected_brd:
        print_warning("BRD selection canceled.")
        return None, None
    
    status_updater.update(f"Loading BRD: {selected_brd}...", "info")
    brd = brd_loader.load_brd_from_file(selected_brd)
    
    if brd:
        print_success(f"BRD loaded: {brd.title}")
        print(f"  - Requirements: {len(brd.requirements)}")
        return brd, "1"
    else:
        action = ErrorHandler.handle_error(
            Exception("Failed to load BRD file"),
            context="loading BRD",
            recovery_options=["Try different file", "Generate new BRD", "Continue without BRD"]
        )
        if "different file" in action.lower():
            return None, "1"  # Retry selection
        elif "generate" in action.lower():
            return None, "3"
        elif "continue" in action.lower():
            return None, None
        else:
            return None, None


def handle_brd_parsing(
    api_key: str,
    input_dir: Path
) -> Optional[BRDSchema]:
    """
    Handle BRD parsing from document.
    
    Args:
        api_key: OpenAI API key
        input_dir: Input directory for BRD documents
        
    Returns:
        BRD schema or None if error
    """
    parser = BRDParser(api_key=api_key, model="gpt-4")
    
    if not input_dir.exists():
        input_dir.mkdir(parents=True, exist_ok=True)
    
    documents = [
        f for f in input_dir.iterdir() 
        if f.is_file() and f.suffix.lower() in ['.pdf', '.doc', '.docx', '.txt', '.csv', '.md']
    ]
    
    if not documents:
        from ..utils.constants import DEFAULT_BRD_INPUT_TRANSFORMATOR_DIR
        print_warning(f"No BRD documents found in {DEFAULT_BRD_INPUT_TRANSFORMATOR_DIR}/")
        print_info("Please place your BRD document (PDF, Word, TXT, CSV) in that folder.")
        return None
    
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
                print_success(f"BRD parsed: {brd.title}")
                print(f"  - Requirements: {len(brd.requirements)}")
                return brd
            else:
                print_error("Failed to parse BRD document.")
                return None
        else:
            print_warning("Invalid selection.")
            return None
    except (ValueError, IndexError):
        print_warning("Invalid input.")
        return None


def handle_brd_generation(
    processed_data: Dict[str, Any],
    analysis_data: Dict[str, Any],
    schema_filename: str,
    api_key: str,
    model: str,
    analytics_dir: str,
    brd_loader: BRDLoader,
    swagger_name: str
) -> Tuple[Optional[BRDSchema], float]:
    """
    Handle BRD generation from Swagger schema.
    
    Args:
        processed_data: Processed schema data
        analysis_data: Analysis data
        schema_filename: Schema filename
        api_key: OpenAI API key
        model: LLM model name
        analytics_dir: Analytics directory
        brd_loader: BRDLoader instance
        swagger_name: Swagger name for output filename
        
    Returns:
        Tuple of (BRD schema or None, coverage_percentage)
    """
    print("\n📋 Generating BRD from Swagger schema...")
    
    # Ask for coverage percentage
    print("\nWhat percentage of API endpoints would you like to cover?")
    print(f"  - Enter a number between {MIN_COVERAGE_PERCENTAGE}-{MAX_COVERAGE_PERCENTAGE} (e.g., 50 for 50% coverage)")
    print(f"  - Or press Enter to use default ({DEFAULT_COVERAGE_PERCENTAGE}% - all endpoints)")
    
    coverage_input = input(f"\nCoverage percentage (default: {DEFAULT_COVERAGE_PERCENTAGE}): ").strip()
    
    try:
        if coverage_input:
            coverage_percentage = float(coverage_input)
            if coverage_percentage < MIN_COVERAGE_PERCENTAGE or coverage_percentage > MAX_COVERAGE_PERCENTAGE:
                print_warning(f"Invalid percentage. Using default ({DEFAULT_COVERAGE_PERCENTAGE}%).")
                coverage_percentage = DEFAULT_COVERAGE_PERCENTAGE
        else:
            coverage_percentage = DEFAULT_COVERAGE_PERCENTAGE
    except ValueError:
        print_warning(f"Invalid input. Using default ({DEFAULT_COVERAGE_PERCENTAGE}%).")
        coverage_percentage = DEFAULT_COVERAGE_PERCENTAGE
    
    print(f"  → Coverage set to: {coverage_percentage}%")
    
    brd_generator = BRDGenerator(
        api_key=api_key,
        model=model,
        analytics_dir=analytics_dir
    )
    brd = brd_generator.generate_brd_from_swagger(
        processed_data, 
        analysis_data, 
        schema_filename,
        coverage_percentage=coverage_percentage
    )
    
    if brd:
        print_success(f"BRD generated: {brd.title}")
        print(f"  - Requirements: {len(brd.requirements)}")
        
        # Save generated BRD
        brd_filename = f"{swagger_name}_brd"
        brd_path = brd_loader.save_brd_to_file(brd, brd_filename)
        print(f"  - Saved to: {brd_path}")
        return brd, coverage_percentage
    else:
        print_error("Failed to generate BRD. Continuing without BRD filtering...")
        return None, coverage_percentage

