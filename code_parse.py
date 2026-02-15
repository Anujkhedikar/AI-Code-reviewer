import ast

print("===== Beginner Python AST Analyzer =====")

# Take user input
lines = []
while True:
    line = input()
    if line == "":
        break
    lines.append(line)

user_code = "\n".join(lines)

# Step 1: Parse the code
try:
    tree = ast.parse(user_code)
    print("\n Code parsed successfully!")
except SyntaxError as e:
    print("\n Syntax Error:", e)
    exit()


# Step 2: Creating NodeVisitor
class SimpleAnalyzer(ast.NodeVisitor):

    def visit_FunctionDef(self, node):
        print(f"Function found: {node.name}")
        self.generic_visit(node)   # Continue visiting inside function

    def visit_For(self, node):
        print("For loop detected.")
        self.generic_visit(node)

    def visit_While(self, node):
        print("While loop detected.")
        self.generic_visit(node)


# Step 3: Run Analyzer
print("\n----- Feedback -----")
analyzer = SimpleAnalyzer()
analyzer.visit(tree)


# Step 4: AST structure
print("\n----- AST Structure -----")
print(ast.dump(tree, indent=4))


# Step 5: formatted code
print("\n----- Formatted Code -----")
print(ast.unparse(tree))

print("\n✅ Analysis Complete!")
