import ast


class AIReviewer(ast.NodeVisitor):
    def __init__(self):
        self.defined = set()      # For tracking defined variables/imports
        self.used = set()         # For tracking used variables
        self.violations = []      # List for style and error messages
        self.score = 100          # Baseline code score
        self._function_nodes = [] # Track function nodes for complexity checks

    # ── Imports ─────────────────────────────────────────────────────────────

    def visit_Import(self, node):
        for alias in node.names:
            self.defined.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.defined.add(alias.asname or alias.name)
        self.generic_visit(node)

    # ── Variable / Name tracking ─────────────────────────────────────────

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.defined.add(node.id)

            # Short variable name check (single char, excluding common loop vars)
            ALLOWED_SHORT = {"i", "j", "k", "n", "x", "y", "z", "_"}
            if len(node.id) == 1 and node.id not in ALLOWED_SHORT:
                message = f"Line {node.lineno}: Variable '{node.id}' name too short — use a descriptive name."
                if message not in self.violations:
                    self.violations.append(message)
                    self.score -= 5

        elif isinstance(node.ctx, ast.Load):
            self.used.add(node.id)

        self.generic_visit(node)

    # ── Function checks ──────────────────────────────────────────────────

    def visit_FunctionDef(self, node):
        self._check_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self._check_function(node)
        self.generic_visit(node)

    def _check_function(self, node):
        # Function length check
        if hasattr(node, "end_lineno"):
            length = node.end_lineno - node.lineno + 1
            if length > 40:
                self.violations.append(
                    f"Line {node.lineno}: Function '{node.name}' is too long ({length} lines). Consider splitting it."
                )
                self.score -= 10

        # Missing docstring check
        if not (node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str)):
            self.violations.append(
                f"Line {node.lineno}: Function '{node.name}' is missing a docstring."
            )
            self.score -= 3

        # Cyclomatic complexity (count branches)
        complexity = self._cyclomatic_complexity(node)
        if complexity > 10:
            self.violations.append(
                f"Line {node.lineno}: Function '{node.name}' has high cyclomatic complexity ({complexity}). Simplify the logic."
            )
            self.score -= 8

        # Nested loop detection
        if self._has_nested_loops(node):
            self.violations.append(
                f"Line {node.lineno}: Function '{node.name}' contains nested loops — possible O(n²) complexity. Consider refactoring."
            )
            self.score -= 5

    def _cyclomatic_complexity(self, node) -> int:
        """Count decision points as a rough cyclomatic complexity."""
        count = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler,
                                   ast.With, ast.Assert, ast.comprehension)):
                count += 1
            elif isinstance(child, ast.BoolOp):
                count += len(child.values) - 1
        return count

    def _has_nested_loops(self, node) -> bool:
        """Return True if any loop is directly nested inside another loop."""
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While)):
                for inner in ast.walk(child):
                    if inner is not child and isinstance(inner, (ast.For, ast.While)):
                        return True
        return False

    # ── Class checks ────────────────────────────────────────────────────

    def visit_ClassDef(self, node):
        # PascalCase check for class names
        if not node.name[0].isupper():
            self.violations.append(
                f"Line {node.lineno}: Class '{node.name}' should use PascalCase (e.g. MyClass)."
            )
            self.score -= 5
        self.generic_visit(node)

    # ── Magic number detection ───────────────────────────────────────────

    def visit_Constant(self, node):
        """Flag bare numeric literals that look like magic numbers (not 0 or 1)."""
        ALLOWED_NUMBERS = {0, 1, -1, 2, 100}
        if isinstance(node.value, (int, float)) and node.value not in ALLOWED_NUMBERS:
            self.violations.append(
                f"Line {node.lineno}: Magic number '{node.value}' detected. Consider using a named constant."
            )
            self.score -= 2
        self.generic_visit(node)

    # ── Final Report ────────────────────────────────────────────────────

    def report_unused(self) -> dict:
        """
        Compute and return the analysis report.

        Returns:
            dict with keys: score, unused, violations
        """
        BUILTINS = {
            "print", "len", "range", "enumerate", "zip", "map", "filter",
            "sorted", "reversed", "list", "dict", "set", "tuple", "int",
            "float", "str", "bool", "type", "isinstance", "hasattr", "getattr",
            "setattr", "open", "input", "super", "object", "Exception",
        }
        unused = self.defined - self.used - BUILTINS

        # Clamp score between 0 and 100
        final_score = max(0, min(100, self.score))

        return {
            "score": final_score,
            "unused": sorted(unused),
            "violations": self.violations,
        }