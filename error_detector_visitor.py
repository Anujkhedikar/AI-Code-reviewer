import ast

class AIReviewer(ast.NodeVisitor):
    def __init__(self):
        self.defined = set()    # For tracking defined variables/imports
        self.used = set()       # For tracking used variables
        self.violations = []    # List for style and error messages
        self.score = 100        # Baseline code score

    # Track Imports
    def visit_Import(self, node):
        for alias in node.names:
            self.defined.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.defined.add(alias.name)
        self.generic_visit(node)

    # Track Variable Definitions and Usage
    def visit_Name(self, node):
        # If storing (e.g., x = 5), it's a definition
        if isinstance(node.ctx, ast.Store):
            self.defined.add(node.id)
            
            # Logic from screenshot: Check for short variable names
            if len(node.id) == 1:
                message = f"Variable '{node.id}' name too short at line {node.lineno}"
                if message not in self.violations:
                    self.violations.append(message)
                    self.score -= 5
        
        # If loading (e.g., print(x)), it's a usage
        elif isinstance(node.ctx, ast.Load):
            self.used.add(node.id)
        
        self.generic_visit(node)

    # Logic from screenshot: Check function length
    def visit_FunctionDef(self, node):
        if hasattr(node, "end_lineno"):
            length = node.end_lineno - node.lineno + 1
            if length > 40:
                print(f"Line {node.lineno}: Function '{node.name}' is too long ({length} lines).")
        self.generic_visit(node)

    # The Final Report Logic
    def report_unused(self):
        # Subtract 'used' items from 'defined' items
        # We also ignore 'print' as it's a built-in, not our variable
        unused = self.defined - self.used - {'print', 'os', 'sys'}

        print("\n--- AI REVIEW REPORT ---")
        print(f"Current Code Score: {self.score}")
        
        if not unused and not self.violations:
            print("No major style issues found!")
        
        for item in unused:
            print(f"UNUSED ITEM FOUND: {item}")
            
        for violation in self.violations:
            print(f"STYLE ISSUE: {violation}")