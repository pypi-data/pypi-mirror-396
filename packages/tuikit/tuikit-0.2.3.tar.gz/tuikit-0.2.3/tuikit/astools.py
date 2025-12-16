import ast


MARKER = None


def tolerant_parse_module(source: list[str]|str,
                          get: bool = False) -> ast.Module:
    if isinstance(source, str): source = source.splitlines()
    nodes   = []
    blocks  = split_top_level_blocks(source)
    synerrs = []

    for block, lineno_offset in blocks:
        try:
            parsed = ast.parse('\n'.join(block))
            for node in parsed.body:
                shift_node_lines(node, lineno_offset - 1)
                nodes.append(node)
        except SyntaxError as e:
            lineno = e.lineno + lineno_offset - 1
            synerrs.append((lineno, e.msg))
            continue

    tree = ast.Module(body=nodes, type_ignores=[])
    annotate_parents(tree)
    if get: return tree, synerrs
    return tree


def annotate_parents(node, parent=None):
    if parent is None:
        parent = ast.Module(body=[], type_ignores=[])
    for child in ast.iter_child_nodes(node):
        child.parent = parent
        annotate_parents(child, child)


def in_docstring(marker):
    global MARKER
    marker = marker.strip()
    if MARKER and MARKER == marker: return False
    if MARKER and MARKER != marker: return True
    if not MARKER and marker != '"""': return False
    if not MARKER and marker == '"""':
        MARKER = marker
        return True


def line_indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def is_top_level_start(line: str) -> bool:
    blocks = ("def ", "class ", "if ", "for ", "while ",
              "try", "@")
    if line.lstrip().startswith(blocks): return True
    elif line.lstrip().startswith("#"):
        return any(b in line for b in blocks)
    return False


def split_top_level_blocks(lines: list[str]
                          ) -> list[tuple[list[str], int]]:
    blocks       = []
    buffer       = []
    in_block     = False
    block_indent = 0
    start_lineno = 0
    for idx, line in enumerate(lines):
        if is_top_level_start(line) and line_indent(line) == 0:
            if buffer: blocks.append((buffer, start_lineno))
            buffer       = [line]
            in_block     = True
            block_indent = line_indent(line)
            start_lineno = idx + 1
        elif in_block:
            if line.strip() == "" or in_docstring(line) or line_indent(line) > block_indent:
                buffer.append(line)
            else:
                blocks.append((buffer, start_lineno))
                buffer       = [line]
                in_block     = is_top_level_start(line)
                start_lineno = idx + 1
        else:
            if not buffer: start_lineno = idx + 1
            buffer.append(line)

    if buffer: blocks.append((buffer, start_lineno))
    return blocks


def shift_node_lines(node, offset: int):
    for subnode in ast.walk(node):
        if hasattr(subnode, 'lineno'):
            subnode.lineno += offset
        if hasattr(subnode, 'end_lineno'):
            subnode.end_lineno += offset
