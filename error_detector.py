import ast
from error_detector_visitor import AIReviewer

# Sample code to analyze
code = """
import os
import sys
import datetime

x = 10
y = 20
z = 30
print(x)
"""

def run_analysis(source_code):
    try:
        tree = ast.parse(source_code)
        reviewer = AIReviewer()
        reviewer.visit(tree)
        reviewer.report_unused()
        
        # Adding ast.unparse as seen in your PowerPoint slide
        print("\n--- Formatted Code (via ast.unparse) ---")
        print(ast.unparse(tree))
        
    except SyntaxError as e:
        print(f"Syntax Error: {e}")

if __name__ == "__main__":
    run_analysis(code)