"""
Example usage of SheetWise's enhanced features

This example demonstrates:
1. Formula extraction and analysis
2. Multi-sheet workbook support
3. Advanced table detection
4. Visualization tools
"""

import pandas as pd
import os
import matplotlib.pyplot as plt

from sheetwise import (
    SpreadsheetLLM,
    FormulaParser,
    FormulaDependencyAnalyzer,
    CompressionVisualizer,
    WorkbookManager,
    SmartTableDetector,
    TableType
)


def example_formula_extraction(excel_path):
    """Example of formula extraction and analysis."""
    print("\n=== Formula Extraction Example ===")
    
    # Initialize the formula parser
    parser = FormulaParser()
    
    # Extract formulas from the Excel file
    formulas = parser.extract_formulas(excel_path)
    print(f"Found {len(formulas)} formulas in the spreadsheet")
    
    # Build dependency graph
    parser.build_dependency_graph()
    
    # Show formula details for the first few formulas
    print("\nFormula Details:")
    for cell, formula in list(formulas.items())[:3]:
        explanation = parser.simplify_formula(formula)
        print(f"  {cell}: {formula} - {explanation}")
    
    # Analyze formula impact for a sample cell
    if formulas:
        sample_cell = list(formulas.keys())[0]
        impact = parser.get_formula_impact(sample_cell)
        print(f"\nImpact analysis for {sample_cell}:")
        print(f"  Formula: {impact['formula']}")
        print(f"  Explanation: {impact['simplified_explanation']}")
        print(f"  Dependencies: {impact['dependencies']}")
        print(f"  Dependents: {impact['dependents']}")
    
    # Find critical cells
    analyzer = FormulaDependencyAnalyzer(parser)
    critical_cells = analyzer.identify_critical_cells()
    
    print("\nCritical formula cells:")
    for cell in critical_cells[:3]:
        formula = parser.formula_map.get(cell, "")
        explanation = parser.simplify_formula(formula)
        print(f"  {cell}: {explanation}")
    
    # Generate LLM-ready encoding
    encoded = parser.encode_formulas_for_llm()
    print("\nFormula encoding for LLM (excerpt):")
    print(encoded[:300] + "...")
    
    return formulas, parser


def example_visualization(df):
    """Example of visualization tools."""
    print("\n=== Visualization Example ===")
    
    # Initialize the visualizer
    visualizer = CompressionVisualizer()
    
    # Initialize the compressor
    sllm = SpreadsheetLLM()
    compressed_result = sllm.compress_spreadsheet(df)
    
    # Create a data density heatmap
    print("Creating data density heatmap...")
    fig = visualizer.create_data_density_heatmap(df)
    viz_path = "example_density_heatmap.png"
    visualizer.save_visualization_to_file(fig, viz_path)
    print(f"Saved visualization to {viz_path}")
    
    # Create a comparison visualization
    print("Creating compression comparison...")
    fig2 = visualizer.compare_original_vs_compressed(df, compressed_result)
    viz_path2 = "example_compression_comparison.png"
    visualizer.save_visualization_to_file(fig2, viz_path2)
    print(f"Saved comparison visualization to {viz_path2}")
    
    # Generate HTML report
    print("Generating HTML report...")
    html_report = visualizer.generate_html_report(df, compressed_result)
    report_path = "example_report.html"
    with open(report_path, "w") as f:
        f.write(html_report)
    print(f"Saved HTML report to {report_path}")
    
    return compressed_result


def example_multi_sheet(excel_path):
    """Example of multi-sheet workbook support."""
    print("\n=== Multi-Sheet Example ===")
    
    # Initialize the workbook manager
    workbook = WorkbookManager()
    
    # Load all sheets from the workbook
    sheets = workbook.load_workbook(excel_path)
    print(f"Loaded {len(sheets)} sheets: {', '.join(sheets.keys())}")
    
    # Detect cross-sheet references
    try:
        cross_refs = workbook.detect_cross_sheet_references()
        print("\nDetected cross-sheet references:")
        for sheet, refs in cross_refs.items():
            if refs:
                print(f"  {sheet} references: {', '.join(refs)}")
    except Exception as e:
        print(f"Warning: Could not detect cross-sheet references: {e}")
    
    # Compress the workbook
    sllm = SpreadsheetLLM()
    compressed_results = workbook.compress_workbook(sllm.compressor)
    
    # Get sheet importance ranking
    try:
        # Set the file path to enable cross-reference detection
        workbook.excel_file_path = excel_path
        ranked_sheets = workbook.get_sheet_importance_ranking()
        print("\nSheet importance ranking:")
        for sheet, score in ranked_sheets[:3]:
            print(f"  {sheet}: {score:.2f}")
    except Exception as e:
        print(f"\nWarning: Could not rank sheets by importance: {e}")
        print("Using default order instead.")
        ranked_sheets = [(sheet, 1.0) for sheet in sheets.keys()]
    
    # Generate LLM-ready encoding
    encoded = workbook.encode_workbook_for_llm(compressed_results)
    print("\nWorkbook encoding for LLM (excerpt):")
    print(encoded[:300] + "...")
    
    return sheets, workbook, compressed_results


def example_table_detection(df):
    """Example of advanced table detection."""
    print("\n=== Table Detection Example ===")
    
    # Initialize the table detector
    detector = SmartTableDetector()
    
    # Detect tables
    tables = detector.detect_tables(df)
    print(f"Detected {len(tables)} tables")
    
    # Show details for each table
    for i, table in enumerate(tables):
        print(f"\nTable {i+1}:")
        print(f"  Rows: {table.start_row}-{table.end_row}")
        print(f"  Columns: {table.start_col}-{table.end_col}")
        print(f"  Type: {table.table_type.value}")
        print(f"  Has Headers: {table.has_headers}")
        if table.has_headers:
            print(f"  Header Rows: {table.header_rows}")
            print(f"  Header Columns: {table.header_cols}")
        print(f"  Confidence: {table.confidence:.2f}")
    
    # Extract tables to separate dataframes
    table_dfs = detector.extract_tables_to_dataframes(df)
    
    # Show a preview of each extracted table
    print("\nExtracted tables:")
    for name, table_df in table_dfs.items():
        print(f"\n{name} (shape: {table_df.shape}):")
        print(table_df.head(2))
    
    return tables, table_dfs
    """Example of bidirectional capabilities."""
    print("\n=== Bidirectional Processing Example ===")
    
    # Initialize the bidirectional processor
    processor = BidirectionalProcessor()
    
    # Set the original data
    processor.set_original_data(df)
    
    # Sample LLM response suggesting changes
    llm_response = """
    Based on my analysis of the spreadsheet, I recommend the following changes:
    
    1. Change A1 to "Updated Header"
    2. In cell B2, replace the current value with 42.5
    3. Update C3 with the value "New Value"
    
    Here's a summary of all changes:
    
    | Cell | Original Value | New Value |
    |------|----------------|-----------|
    | A1   | Header         | Updated Header |
    | B2   | 15.0           | 42.5 |
    | C3   | Old Value      | New Value |
    """
    
    # Parse the LLM response to extract changes
    changes = processor.parse_llm_response(llm_response)
    print(f"Detected {len(changes)} changes in LLM response")
    
    # Show the detected changes
    print("\nDetected changes:")
    for change in changes:
        print(f"  {change.cell_address}: {change.original_value} -> {change.new_value}")
    
    # Apply the changes to the dataframe
    modified_df = processor.apply_changes(changes)
    print("\nApplied changes to dataframe")
    
    # Generate a description of the changes
    description = processor.generate_change_description(changes)
    print("\nChange description:")
    print(description)
    
    # Serialize changes to JSON
    json_str = processor.serialize_changes_to_json(changes)
    print("\nSerialized changes (excerpt):")
    print(json_str[:300] + "...")
    
    # Create Excel file with highlighted changes
    if len(changes) > 0:
        try:
            output_path = "example_changes.xlsx"
            processor.create_excel_with_changes(changes, output_path)
            print(f"\nCreated Excel file with highlighted changes: {output_path}")
        except Exception as e:
            print(f"Error creating Excel file: {e}")
    
    return changes, modified_df


def main():
    """Main function demonstrating all features."""
    print("SheetWise Enhanced Features Example")
    print("==================================")
    
    # Create a sample spreadsheet for testing
    from sheetwise import create_realistic_spreadsheet
    df = create_realistic_spreadsheet()
    
    # Save the sample data to Excel for formula examples
    excel_path = "example_spreadsheet.xlsx"
    df.to_excel(excel_path, index=False)
    print(f"Created sample spreadsheet: {excel_path}")
    
    # Run the examples
    try:
        # Run individual examples
        example_formula_extraction(excel_path)
        example_visualization(df)
        example_multi_sheet(excel_path)
        example_table_detection(df)
        
        print("\nAll examples completed successfully!")
        
    except Exception as e:
        import traceback
        print(f"Error running examples: {e}")
        traceback.print_exc()
    
    print("\nExample files:")
    print("  - example_spreadsheet.xlsx: Sample spreadsheet")
    print("  - example_density_heatmap.png: Data density visualization")
    print("  - example_compression_comparison.png: Compression comparison")
    print("  - example_report.html: HTML report")


if __name__ == "__main__":
    main()
