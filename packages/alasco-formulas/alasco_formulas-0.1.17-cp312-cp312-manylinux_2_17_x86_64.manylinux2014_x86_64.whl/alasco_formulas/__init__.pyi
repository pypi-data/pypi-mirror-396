from typing import Literal, TypedDict

TokenType = Literal[
    "number",
    "operator",
    "symbolreference",
    "function",
    "aggregation",
    "parenthesis",
    "unexpected",
]

class Node(TypedDict):
    """A node in the formula evaluation tree.

    Attributes:
        name: Display name for the node
        formula: Formula string to evaluate (e.g., "=10+5" or "=@symbol1")
        value: The evaluated result as a string (empty before evaluation)
        is_hidden: Whether the node is hidden
        children: List of child nodes
    """

    name: str
    formula: str
    value: str
    is_hidden: bool
    children: list[Node]

def evaluate(formula: str) -> str:
    """Evaluates a single formula string.

    Args:
        formula: Formula string to evaluate (e.g., "=10+5" or "=@symbol1")

    Returns:
        The evaluated result as a string, or an error indication.
    """
    ...

def evaluate_tree(root: Node) -> Node:
    """Evaluates a tree of nodes with formulas.

    This function evaluates all formulas in the tree, handling references
    between nodes (e.g., "=@symbol1" references another node's value).

    Args:
        root: A Node dictionary representing the root of the tree to evaluate

    Returns:
        The same tree structure with all 'value' fields populated with evaluation results

    Raises:
        ValueError: If the input cannot be parsed or is invalid
    """
    ...

def get_tokens(formula: str) -> list[tuple[str, TokenType]]:
    """Parses a formula string into tokens with preserved number formats.

    This function parses a formula and returns a list of tokens, where each token
    contains the original string value and its type. Numbers preserve their original
    decimal separator (comma or point) for locale-based formatting.

    Args:
        formula: Formula string to tokenize (e.g., "=3,14 + 2.5")

    Returns:
        A list of tuples, where each tuple contains (value, token_type)

    Raises:
        ValueError: If the input cannot be parsed or is invalid
    """
    ...

def replace_symbol(root: Node, old_symbol: str, new_symbol: str) -> Node:
    """Replaces all occurrences of a symbol reference with a new symbol in a node tree.

    This function recursively traverses the node tree and replaces all references
    to the old symbol (e.g., "@oldId" or "@{old item}") with the new symbol
    (e.g., "@newId" or "@{new item}") in all formula strings. The function preserves
    extra properties on nodes that are not part of the standard Node interface.

    Args:
        root: A Node dictionary representing the root of the tree
        old_symbol: The symbol identifier to replace (e.g., "oldId" or "old item")
        new_symbol: The new symbol identifier to use (e.g., "newId" or "new item")

    Returns:
        The same tree structure with all symbol references updated

    Raises:
        ValueError: If the input cannot be parsed or is invalid
    """
    ...
