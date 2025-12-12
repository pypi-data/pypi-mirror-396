"""Halstead complexity metrics analyzer with multi-language support."""

import ast
from pathlib import Path
from typing import Dict, Optional, Set

try:
    import tree_sitter_languages as tsl
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False

from ossval.models import HalsteadMetrics


# Language file extension mapping
LANGUAGE_EXTENSIONS = {
    "python": [".py", ".pyw"],
    "javascript": [".js", ".mjs", ".cjs"],
    "typescript": [".ts", ".tsx"],
    "java": [".java"],
    "c": [".c", ".h"],
    "cpp": [".cpp", ".cc", ".cxx", ".hpp", ".hh", ".hxx"],
    "c_sharp": [".cs"],
    "go": [".go"],
    "rust": [".rs"],
    "php": [".php"],
    "ruby": [".rb"],
    "swift": [".swift"],
}

# Operator and operand node types by language
OPERATOR_TYPES = {
    "python": {
        "binary_operator", "unary_operator", "comparison_operator",
        "boolean_operator", "augmented_assignment", "attribute",
        "subscript", "call", "return_statement", "if_statement",
        "for_statement", "while_statement", "with_statement",
        "try_statement", "raise_statement", "assert_statement",
        "import_statement", "import_from_statement", "class_definition",
        "function_definition", "lambda",
    },
    "javascript": {
        "binary_expression", "unary_expression", "update_expression",
        "assignment_expression", "call_expression", "member_expression",
        "subscript_expression", "return_statement", "if_statement",
        "for_statement", "while_statement", "switch_statement",
        "try_statement", "throw_statement", "function_declaration",
        "class_declaration", "arrow_function", "new_expression",
    },
    "typescript": {
        "binary_expression", "unary_expression", "update_expression",
        "assignment_expression", "call_expression", "member_expression",
        "subscript_expression", "return_statement", "if_statement",
        "for_statement", "while_statement", "switch_statement",
        "try_statement", "throw_statement", "function_declaration",
        "class_declaration", "arrow_function", "new_expression",
        "interface_declaration", "type_alias_declaration",
    },
    "java": {
        "binary_expression", "unary_expression", "update_expression",
        "assignment_expression", "method_invocation", "field_access",
        "array_access", "return_statement", "if_statement",
        "for_statement", "while_statement", "switch_expression",
        "try_statement", "throw_statement", "method_declaration",
        "class_declaration", "constructor_declaration",
    },
    "c": {
        "binary_expression", "unary_expression", "update_expression",
        "assignment_expression", "call_expression", "field_expression",
        "subscript_expression", "return_statement", "if_statement",
        "for_statement", "while_statement", "switch_statement",
        "function_definition", "struct_specifier",
    },
    "cpp": {
        "binary_expression", "unary_expression", "update_expression",
        "assignment_expression", "call_expression", "field_expression",
        "subscript_expression", "return_statement", "if_statement",
        "for_statement", "while_statement", "switch_statement",
        "function_definition", "class_specifier", "namespace_definition",
    },
    "c_sharp": {
        "binary_expression", "prefix_unary_expression", "postfix_unary_expression",
        "assignment_expression", "invocation_expression", "member_access_expression",
        "element_access_expression", "return_statement", "if_statement",
        "for_statement", "while_statement", "switch_statement",
        "try_statement", "throw_statement", "method_declaration",
        "class_declaration", "interface_declaration",
    },
    "go": {
        "binary_expression", "unary_expression", "assignment_statement",
        "call_expression", "selector_expression", "index_expression",
        "return_statement", "if_statement", "for_statement",
        "switch_statement", "function_declaration", "method_declaration",
        "type_declaration", "struct_type",
    },
    "rust": {
        "binary_expression", "unary_expression", "assignment_expression",
        "call_expression", "field_expression", "index_expression",
        "return_expression", "if_expression", "loop_expression",
        "for_expression", "while_expression", "match_expression",
        "function_item", "impl_item", "trait_item", "struct_item",
    },
    "php": {
        "binary_expression", "unary_op_expression", "assignment_expression",
        "function_call_expression", "member_access_expression",
        "subscript_expression", "return_statement", "if_statement",
        "for_statement", "while_statement", "switch_statement",
        "try_statement", "throw_statement", "function_definition",
        "class_declaration", "method_declaration",
    },
    "ruby": {
        "binary", "unary", "assignment", "call", "element_reference",
        "return", "if", "unless", "while", "until", "for",
        "case", "begin", "method", "class", "module",
    },
    "swift": {
        "binary_expression", "prefix_expression", "postfix_expression",
        "assignment", "call_expression", "navigation_expression",
        "subscript_expression", "return_statement", "if_statement",
        "for_statement", "while_statement", "switch_statement",
        "do_statement", "throw_statement", "function_declaration",
        "class_declaration", "protocol_declaration",
    },
}

OPERAND_TYPES = {
    "python": {"identifier", "integer", "float", "string", "true", "false", "none"},
    "javascript": {"identifier", "number", "string", "true", "false", "null", "undefined"},
    "typescript": {"identifier", "number", "string", "true", "false", "null", "undefined"},
    "java": {"identifier", "decimal_integer_literal", "string_literal", "true", "false", "null_literal"},
    "c": {"identifier", "number_literal", "string_literal", "char_literal"},
    "cpp": {"identifier", "number_literal", "string_literal", "char_literal", "true", "false"},
    "c_sharp": {"identifier", "integer_literal", "string_literal", "character_literal", "true", "false", "null"},
    "go": {"identifier", "int_literal", "float_literal", "string_literal", "rune_literal", "true", "false", "nil"},
    "rust": {"identifier", "integer_literal", "float_literal", "string_literal", "char_literal", "true", "false"},
    "php": {"name", "integer", "float", "string", "true", "false", "null"},
    "ruby": {"identifier", "integer", "float", "string", "symbol", "true", "false", "nil"},
    "swift": {"simple_identifier", "integer_literal", "real_literal", "string_literal", "true", "false", "nil"},
}


class PythonHalsteadAnalyzer(ast.NodeVisitor):
    """AST visitor to compute Halstead metrics for Python code (fallback)."""

    def __init__(self):
        """Initialize the analyzer."""
        self.operators: Set[str] = set()
        self.operands: Set[str] = set()
        self.operator_count = 0
        self.operand_count = 0

    def visit_BinOp(self, node):
        """Visit binary operators."""
        self.operators.add(node.op.__class__.__name__)
        self.operator_count += 1
        self.generic_visit(node)

    def visit_UnaryOp(self, node):
        """Visit unary operators."""
        self.operators.add(node.op.__class__.__name__)
        self.operator_count += 1
        self.generic_visit(node)

    def visit_Compare(self, node):
        """Visit comparison operators."""
        for op in node.ops:
            self.operators.add(op.__class__.__name__)
            self.operator_count += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        """Visit boolean operators."""
        self.operators.add(node.op.__class__.__name__)
        self.operator_count += 1
        self.generic_visit(node)

    def visit_Call(self, node):
        """Visit function calls."""
        self.operators.add("Call")
        self.operator_count += 1
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Visit assignments."""
        self.operators.add("Assign")
        self.operator_count += 1
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        """Visit augmented assignments."""
        self.operators.add(f"AugAssign_{node.op.__class__.__name__}")
        self.operator_count += 1
        self.generic_visit(node)

    def visit_If(self, node):
        """Visit if statements."""
        self.operators.add("If")
        self.operator_count += 1
        self.generic_visit(node)

    def visit_For(self, node):
        """Visit for loops."""
        self.operators.add("For")
        self.operator_count += 1
        self.generic_visit(node)

    def visit_While(self, node):
        """Visit while loops."""
        self.operators.add("While")
        self.operator_count += 1
        self.generic_visit(node)

    def visit_Return(self, node):
        """Visit return statements."""
        self.operators.add("Return")
        self.operator_count += 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Visit function definitions."""
        self.operators.add("FunctionDef")
        self.operator_count += 1
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Visit class definitions."""
        self.operators.add("ClassDef")
        self.operator_count += 1
        self.generic_visit(node)

    def visit_Name(self, node):
        """Visit variable names."""
        self.operands.add(node.id)
        self.operand_count += 1
        self.generic_visit(node)

    def visit_Constant(self, node):
        """Visit constants."""
        self.operands.add(str(node.value))
        self.operand_count += 1
        self.generic_visit(node)

    def visit_Attribute(self, node):
        """Visit attribute access."""
        self.operands.add(node.attr)
        self.operand_count += 1
        self.generic_visit(node)


def detect_language(file_path: Path) -> Optional[str]:
    """
    Detect programming language from file extension.

    Args:
        file_path: Path to source file

    Returns:
        Language name or None
    """
    ext = file_path.suffix.lower()
    for language, extensions in LANGUAGE_EXTENSIONS.items():
        if ext in extensions:
            return language
    return None


def analyze_with_tree_sitter(file_path: Path, language: str) -> Optional[HalsteadMetrics]:
    """
    Analyze file using tree-sitter.

    Args:
        file_path: Path to source file
        language: Programming language

    Returns:
        HalsteadMetrics or None
    """
    if not TREE_SITTER_AVAILABLE:
        return None

    try:
        parser = tsl.get_parser(language)
        with open(file_path, "rb") as f:
            source_code = f.read()

        tree = parser.parse(source_code)
        root_node = tree.root_node

        operators: Set[str] = set()
        operands: Set[str] = set()
        operator_count = 0
        operand_count = 0

        operator_types = OPERATOR_TYPES.get(language, set())
        operand_types = OPERAND_TYPES.get(language, set())

        def traverse(node):
            nonlocal operator_count, operand_count

            if node.type in operator_types:
                operators.add(node.type)
                operator_count += 1

            if node.type in operand_types:
                operand_text = source_code[node.start_byte:node.end_byte].decode('utf-8', errors='ignore')
                operands.add(operand_text[:50])  # Limit length
                operand_count += 1

            for child in node.children:
                traverse(child)

        traverse(root_node)

        n1 = len(operators)
        n2 = len(operands)
        N1 = operator_count
        N2 = operand_count

        if n1 == 0 or n2 == 0:
            return None

        vocabulary = n1 + n2
        length = N1 + N2
        calculated_length = n1 * (n1 / 2 if n1 > 0 else 0) + n2 * (n2 / 2 if n2 > 0 else 0)
        volume = length * (vocabulary.bit_length() if vocabulary > 0 else 0)
        difficulty = (n1 / 2.0) * (N2 / n2 if n2 > 0 else 0)
        effort = difficulty * volume
        time_seconds = effort / 18.0
        bugs = volume / 3000.0

        return HalsteadMetrics(
            vocabulary=vocabulary,
            length=length,
            calculated_length=calculated_length,
            volume=volume,
            difficulty=difficulty,
            effort=effort,
            time_seconds=time_seconds,
            bugs=bugs,
        )

    except Exception:
        return None


def analyze_python_file_fallback(file_path: Path) -> Optional[HalsteadMetrics]:
    """
    Analyze Python file using built-in AST (fallback).

    Args:
        file_path: Path to Python file

    Returns:
        HalsteadMetrics or None
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        analyzer = PythonHalsteadAnalyzer()
        analyzer.visit(tree)

        n1 = len(analyzer.operators)
        n2 = len(analyzer.operands)
        N1 = analyzer.operator_count
        N2 = analyzer.operand_count

        if n1 == 0 or n2 == 0:
            return None

        vocabulary = n1 + n2
        length = N1 + N2
        calculated_length = n1 * (n1 / 2 if n1 > 0 else 0) + n2 * (n2 / 2 if n2 > 0 else 0)
        volume = length * (vocabulary.bit_length() if vocabulary > 0 else 0)
        difficulty = (n1 / 2.0) * (N2 / n2 if n2 > 0 else 0)
        effort = difficulty * volume
        time_seconds = effort / 18.0
        bugs = volume / 3000.0

        return HalsteadMetrics(
            vocabulary=vocabulary,
            length=length,
            calculated_length=calculated_length,
            volume=volume,
            difficulty=difficulty,
            effort=effort,
            time_seconds=time_seconds,
            bugs=bugs,
        )

    except Exception:
        return None


def analyze_python_file(file_path: Path) -> Optional[HalsteadMetrics]:
    """
    Analyze a Python file for Halstead metrics.

    Args:
        file_path: Path to Python file

    Returns:
        HalsteadMetrics or None
    """
    # Try tree-sitter first, fall back to AST
    if TREE_SITTER_AVAILABLE:
        result = analyze_with_tree_sitter(file_path, "python")
        if result:
            return result

    return analyze_python_file_fallback(file_path)


def analyze_source_file(file_path: Path) -> Optional[HalsteadMetrics]:
    """
    Analyze any supported source file for Halstead metrics.

    Args:
        file_path: Path to source file

    Returns:
        HalsteadMetrics or None
    """
    language = detect_language(file_path)
    if not language:
        return None

    # For Python, use fallback if tree-sitter not available
    if language == "python":
        return analyze_python_file(file_path)

    # For other languages, require tree-sitter
    if not TREE_SITTER_AVAILABLE:
        return None

    return analyze_with_tree_sitter(file_path, language)


def analyze_directory_halstead(repo_path: Path) -> Optional[HalsteadMetrics]:
    """
    Analyze all supported source files in a directory for aggregate Halstead metrics.

    Args:
        repo_path: Path to repository

    Returns:
        Aggregated HalsteadMetrics or None
    """
    total_volume = 0.0
    total_difficulty = 0.0
    total_effort = 0.0
    total_time = 0.0
    total_bugs = 0.0
    file_count = 0

    # Get all extensions to search for
    all_extensions = set()
    for extensions in LANGUAGE_EXTENSIONS.values():
        all_extensions.update(extensions)

    for ext in all_extensions:
        for source_file in repo_path.rglob(f"*{ext}"):
            # Skip common non-source directories
            if any(skip in str(source_file) for skip in ["venv", "node_modules", ".git", "build", "dist", "target"]):
                continue

            metrics = analyze_source_file(source_file)
            if metrics:
                total_volume += metrics.volume
                total_difficulty += metrics.difficulty
                total_effort += metrics.effort
                total_time += metrics.time_seconds
                total_bugs += metrics.bugs
                file_count += 1

    if file_count == 0:
        return None

    avg_difficulty = total_difficulty / file_count

    return HalsteadMetrics(
        vocabulary=0,  # Not meaningful at aggregate level
        length=0,  # Not meaningful at aggregate level
        calculated_length=0,  # Not meaningful at aggregate level
        volume=total_volume,
        difficulty=avg_difficulty,
        effort=total_effort,
        time_seconds=total_time,
        bugs=total_bugs,
    )
