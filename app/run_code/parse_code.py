import ast


class _Result:
    is_code = False
    uses_orig = False


def _is_node_unknown_variable(node: ast.AST, locs: dict) -> bool:
    """Check if AST node is a Name or Attribute not present in locals"""
    if isinstance(node, ast.Attribute):
        return _is_node_unknown_variable(node.value, locs)
    return isinstance(node, ast.Name) and node.id not in locs


def _is_node_suspicious_binop(node: ast.AST, locs: dict) -> bool:
    """Check if AST node can be an operand of binary operation (ast.BinOp, ast.Compare, ast.BoolOp)
    with operands which do not pass _is_node_unknown_variable check, or is such operation"""
    if _is_node_unknown_variable(node, locs):
        return True
    if not isinstance(node, (ast.BoolOp, ast.BinOp, ast.Compare)):
        return False
    if isinstance(node, ast.Compare):
        return _is_node_unknown_variable(node.left, locs) and all(_is_node_unknown_variable(x, locs)
                                                                  for x in node.comparators)
    return all(_is_node_suspicious_binop(operand, locs)
               for operand in ((node.left, node.right) if isinstance(node, ast.BinOp) else node.values))


def _ignore_node(node: ast.AST, locs: dict) -> bool:
    """Check if AST node didn't seem to be meant to be code"""
    return (
        # Messages like "python", "123" or "example.com"
        isinstance(node, ast.Constant) or _is_node_unknown_variable(node, locs)
        # Messages like "-1", "+spam" and "not foo.bar"
        # `getattr(..., None) or node.value` is used here to avoid AttributeError and because in UnaryOp and Starred
        # operands are stored in different attributes ("operand" and "value" respectively)
        or isinstance(node, (ast.Starred, ast.UnaryOp)) and isinstance(getattr(node, 'operand', None) or node.value,
                                                                       (ast.Constant, ast.Name, ast.Attribute))
        # Messages like one-two, one is two, one >= two, one.b in two.c
        or _is_node_suspicious_binop(node, locs)
        # Messages like "yes, understood"
        or isinstance(node, ast.Tuple) and all(_ignore_node(elt, locs) for elt in node.elts)
    )


def parse_code(text: str, locs: dict) -> _Result:
    """Parse given text and decide should it be evaluated as Python code"""
    result = _Result()

    try:
        root = ast.parse(text, '', 'exec')
    except (SyntaxError, ValueError):
        return result

    if all(isinstance(body_item, ast.Expr) and _ignore_node(body_item.value, locs) for body_item in root.body):
        return result

    result.is_code = True

    for node in ast.walk(root):
        if isinstance(node, ast.Name) and node.id == 'orig':
            result.uses_orig = True
            return result

    return result

