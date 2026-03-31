"""
test_ai_code_reviewer.py
========================
Unit tests for the AI Code Reviewer project.

Covers:
  - error_detector_visitor.AIReviewer
  - code_parse.SimpleAnalyzer
  - error_detector.run_analysis (integration)

Run with:
    python -m pytest test_ai_code_reviewer.py -v
"""

import ast
import unittest
import io
import sys

from error_detector_visitor import AIReviewer


# ─────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────

def analyze(source: str) -> dict:
    """Parse source, run AIReviewer, return report dict."""
    tree = ast.parse(source)
    reviewer = AIReviewer()
    reviewer.visit(tree)
    return reviewer.report_unused()


# ─────────────────────────────────────────────────────────────────
#  Tests: Score
# ─────────────────────────────────────────────────────────────────

class TestScore(unittest.TestCase):

    def test_clean_code_scores_100(self):
        code = """\
def add(a, b):
    \"\"\"Return sum of a and b.\"\"\"
    return a + b
"""
        result = analyze(code)
        self.assertEqual(result["score"], 100)

    def test_score_does_not_go_below_zero(self):
        # Code with many violations
        code = "\n".join(
            [f"def f{i}(): pass" for i in range(30)]
        )
        result = analyze(code)
        self.assertGreaterEqual(result["score"], 0)

    def test_score_does_not_exceed_100(self):
        result = analyze("x = 1")
        self.assertLessEqual(result["score"], 100)


# ─────────────────────────────────────────────────────────────────
#  Tests: Unused Variables / Imports
# ─────────────────────────────────────────────────────────────────

class TestUnused(unittest.TestCase):

    def test_detects_unused_import(self):
        code = "import os\nimport sys\nprint(os.getcwd())"
        result = analyze(code)
        self.assertIn("sys", result["unused"])

    def test_used_import_not_flagged(self):
        code = "import os\nprint(os.getcwd())"
        result = analyze(code)
        self.assertNotIn("os", result["unused"])

    def test_detects_unused_variable(self):
        code = "x = 10\ny = 20\nprint(x)"
        result = analyze(code)
        self.assertIn("y", result["unused"])

    def test_used_variable_not_flagged(self):
        code = "x = 10\nprint(x)"
        result = analyze(code)
        self.assertNotIn("x", result["unused"])

    def test_no_unused_in_clean_code(self):
        code = "import os\nprint(os.getcwd())"
        result = analyze(code)
        self.assertEqual(result["unused"], [])


# ─────────────────────────────────────────────────────────────────
#  Tests: Short Variable Name Check
# ─────────────────────────────────────────────────────────────────

class TestShortVariableNames(unittest.TestCase):

    def test_flags_single_char_variable(self):
        code = "a = 5"
        result = analyze(code)
        self.assertTrue(any("'a'" in v for v in result["violations"]))

    def test_allows_common_loop_vars(self):
        code = "for i in range(10):\n    pass"
        result = analyze(code)
        self.assertFalse(any("'i'" in v for v in result["violations"]))

    def test_allows_underscore(self):
        code = "_ = some_function()"
        result = analyze(code)
        self.assertFalse(any("'_'" in v for v in result["violations"]))

    def test_does_not_flag_long_names(self):
        code = "counter = 5"
        result = analyze(code)
        self.assertFalse(any("counter" in v for v in result["violations"]))


# ─────────────────────────────────────────────────────────────────
#  Tests: Function Length
# ─────────────────────────────────────────────────────────────────

class TestFunctionLength(unittest.TestCase):

    def test_long_function_flagged(self):
        # Build a function > 40 lines
        lines = ["def big_func():"]
        lines.append('    """Docstring."""')
        lines += [f"    x_{i} = {i}" for i in range(45)]
        code = "\n".join(lines)
        result = analyze(code)
        self.assertTrue(any("big_func" in v and "too long" in v for v in result["violations"]))

    def test_short_function_not_flagged_for_length(self):
        code = 'def small():\n    """Docstring."""\n    return 1'
        result = analyze(code)
        self.assertFalse(any("too long" in v for v in result["violations"]))

    def test_long_function_reduces_score(self):
        lines = ["def big():"]
        lines.append('    """Docstring."""')
        lines += [f"    x_{i} = {i}" for i in range(45)]
        code = "\n".join(lines)
        result = analyze(code)
        self.assertLess(result["score"], 100)


# ─────────────────────────────────────────────────────────────────
#  Tests: Missing Docstring
# ─────────────────────────────────────────────────────────────────

class TestDocstring(unittest.TestCase):

    def test_missing_docstring_flagged(self):
        code = "def my_func():\n    return 42"
        result = analyze(code)
        self.assertTrue(any("docstring" in v.lower() for v in result["violations"]))

    def test_present_docstring_not_flagged(self):
        code = 'def my_func():\n    """Does something."""\n    return 42'
        result = analyze(code)
        self.assertFalse(any("docstring" in v.lower() for v in result["violations"]))


# ─────────────────────────────────────────────────────────────────
#  Tests: Cyclomatic Complexity
# ─────────────────────────────────────────────────────────────────

class TestCyclomaticComplexity(unittest.TestCase):

    def _build_complex_function(self, branches: int) -> str:
        lines = ["def complex_func(x):"]
        lines.append('    """Docstring."""')
        for i in range(branches):
            lines.append(f"    if x > {i}:")
            lines.append(f"        x -= {i}")
        lines.append("    return x")
        return "\n".join(lines)

    def test_high_complexity_flagged(self):
        code = self._build_complex_function(12)
        result = analyze(code)
        self.assertTrue(any("complexity" in v.lower() for v in result["violations"]))

    def test_low_complexity_not_flagged(self):
        code = 'def simple(x):\n    """Docstring."""\n    if x > 0:\n        return x\n    return -x'
        result = analyze(code)
        self.assertFalse(any("complexity" in v.lower() for v in result["violations"]))


# ─────────────────────────────────────────────────────────────────
#  Tests: Nested Loop Detection
# ─────────────────────────────────────────────────────────────────

class TestNestedLoops(unittest.TestCase):

    def test_nested_for_loops_flagged(self):
        code = (
            'def matrix_sum(matrix):\n'
            '    """Docstring."""\n'
            '    total = 0\n'
            '    for row in matrix:\n'
            '        for val in row:\n'
            '            total += val\n'
            '    return total\n'
        )
        result = analyze(code)
        self.assertTrue(any("nested" in v.lower() for v in result["violations"]))

    def test_single_loop_not_flagged(self):
        code = (
            'def sum_list(items):\n'
            '    """Docstring."""\n'
            '    total = 0\n'
            '    for item in items:\n'
            '        total += item\n'
            '    return total\n'
        )
        result = analyze(code)
        self.assertFalse(any("nested" in v.lower() for v in result["violations"]))


# ─────────────────────────────────────────────────────────────────
#  Tests: Class Naming (PascalCase)
# ─────────────────────────────────────────────────────────────────

class TestClassNaming(unittest.TestCase):

    def test_lowercase_class_flagged(self):
        code = "class myClass:\n    pass"
        result = analyze(code)
        self.assertTrue(any("PascalCase" in v for v in result["violations"]))

    def test_pascal_case_class_not_flagged(self):
        code = "class MyClass:\n    pass"
        result = analyze(code)
        self.assertFalse(any("MyClass" in v and "PascalCase" in v for v in result["violations"]))


# ─────────────────────────────────────────────────────────────────
#  Tests: Integration — run_analysis from error_detector.py
# ─────────────────────────────────────────────────────────────────

class TestRunAnalysis(unittest.TestCase):

    def setUp(self):
        """Capture stdout."""
        self.held = io.StringIO()
        self._orig = sys.stdout
        sys.stdout = self.held

    def tearDown(self):
        sys.stdout = self._orig

    def test_run_analysis_with_valid_code(self):
        from error_detector import run_analysis
        run_analysis("x = 10\nprint(x)")
        output = self.held.getvalue()
        self.assertIn("Formatted Code", output)

    def test_run_analysis_with_syntax_error(self):
        from error_detector import run_analysis
        run_analysis("def broken(:")
        output = self.held.getvalue()
        self.assertIn("Syntax Error", output)


# ─────────────────────────────────────────────────────────────────
#  Tests: Report Structure
# ─────────────────────────────────────────────────────────────────

class TestReportStructure(unittest.TestCase):

    def test_report_has_required_keys(self):
        result = analyze("x = 1")
        self.assertIn("score", result)
        self.assertIn("unused", result)
        self.assertIn("violations", result)

    def test_unused_is_list(self):
        result = analyze("import os")
        self.assertIsInstance(result["unused"], list)

    def test_violations_is_list(self):
        result = analyze("x = 1")
        self.assertIsInstance(result["violations"], list)

    def test_score_is_int_or_float(self):
        result = analyze("x = 1")
        self.assertIsInstance(result["score"], (int, float))


if __name__ == "__main__":
    unittest.main(verbosity=2)