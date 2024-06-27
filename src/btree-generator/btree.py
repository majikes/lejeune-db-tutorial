#!/usr/bin/env python3
"""A script to generate dot files for nice looking B+ tree diagrams."""
import argparse
import collections
import itertools
import sys
import yaml

PROGRAM_DESCRIPTION = '''\
Creates a dot language graph for a B+ tree read from a yaml data file.
Have a look at the examples for the format of the yaml file.
'''

GRAPH_TEMPLATE = '''digraph G
{{
    splines=false
{nodes}

{parent_child_edges}

{cross_edges}

{rank_statements}
}}'''

INSIDE_GRAPH_INDENT = 4

NODE_TEMPLATE = '''"{name}"
[
    shape = none
    label = <<table border="1" cellborder="{cellborder}" cellspacing="0">
                <tr>
{cells}
                </tr>
            </table>>
]'''
HIGHLIGHTED_NODE_TEMPLATE = '''"{name}"
[
    shape = none
    color = red
    fontcolor = red
    fontname = "bold"
    label = <<table border="2" cellborder="{cellborder}" cellspacing="0">
                <tr>
{cells}
                </tr>
            </table>>
]'''

CELL_INDENT = 20
CONNECTOR_TEMPLATE = '<td port="connector{number}"></td>'
CONNECTOR_NAME_TEMPLATE = 'connector{number}'
KEY_TEMPLATE = '<td port="key{number}">{content}</td>'
KEY_NAME_TEMPLATE = 'key{number}'
EDGE_TEMPLATE = '"{src_node}":"{src_port}" -> "{dst_node}":"{dst_port}"'
HIGHLIGHTED_EDGE_TEMPLATE = \
    '"{src_node}":"{src_port}" -> "{dst_node}":"{dst_port}" [color=red, penwidth=2]'
RANK_SAME_TEMPLATE = '{{rank=same; {blocks}}}'

DUMMY_KEY = '_'


Block = collections.namedtuple('Block', ('keys', 'data'))


class BPlusTree:
    """A B+ tree with possibly omitted subtrees"""

    def __init__(self, keys_per_block, cellborder, two_head, tree):
        self.keys_per_block = keys_per_block
        self._indexed_blocks = {}
        self._cellborder = int(cellborder)
        self._two_head = bool(two_head)
        if tree:
            self._add_block(self.root_index, tree)

    @property
    def two_head(self):
        """Returns boolean whether the leaf nodes have two headed arrors connection them"""
        return self._two_head

    @property
    def cellborder(self):
        """Returns the cellborder value"""
        return self._cellborder

    @property
    def children_per_block(self):
        """Returns the maximum number of children per block"""
        return self.keys_per_block + 1

    @property
    def all_indices(self):
        """Returns all indices which have associated blocks"""
        return self._indexed_blocks.keys()

    @property
    def all_blocks(self):
        """An iterable of all blocks with their indices

        Returns an iterable of tuples, which contain the index of the
        block and the block itself.
        """
        return self._indexed_blocks.items()

    @property
    def root_index(self):
        """Returns the index for the root node."""
        return ()

    def nth_child(self, parent_index, child_num):
        """Returns the index for the nth child of a parent block."""
        if not self._is_valid_child_num(child_num):
            raise IndexError(f'Out of range child number {child_num}')
        return parent_index + (child_num,)

    def children(self, index):
        """Returns the indices of all children below a block"""
        child_num_range = range(self.children_per_block)
        return (self.nth_child(index, i) for i in child_num_range)

    def child_num(self, index):
        """Returns the n for nth child of a block"""
        if index == self.root_index:
            return None
        return index[-1]

    def parent(self, index):
        """Returns the index of the parent of a block"""
        if index == self.root_index:
            return None
        return index[:-1]

    def right_sibling(self, index):
        """Returns the index of the block to the right on the same level"""
        if index == self.root_index:
            return None
        child_num = self.child_num(index)
        if child_num < self.children_per_block - 1:
            return self.nth_child(self.parent(index), child_num + 1)
        parent_sibling = self.right_sibling(self.parent(index))
        if parent_sibling is None:
            return None
        return self.nth_child(parent_sibling, 0)

    def level(self, index):
        """Returns the level of index. This is 0 for the root index"""
        return len(index)

    def was_omitted(self, index):
        """Returns whether a block should have been included.

        This is based on B+ tree semantics, where the number of
        childrens is based on the number of keys and vice-versa.
        """
        parent = self.parent(index)
        parent_keys = self[parent]
        if parent_keys:
            return self.child_num(index) <= len(parent_keys)
        return self.was_omitted(parent)

    def __getitem__(self, index):
        """Returns the keys of the block at the given index"""
        if not self._is_valid_index(index):
            raise IndexError(f'Invalid tree index {index}')
        return self._indexed_blocks.get(index, None)

    def _is_valid_index(self, index):
        """Returns whether an index is valid in this tree"""
        return all(self._is_valid_child_num(i) for i in index)

    def _is_valid_child_num(self, num):
        """Returns whether a children number is valid in this tree"""
        return 0 <= num < self.children_per_block

    def _add_block(self, index, block_tree):
        """Adds a block to the internal data structure"""
        # Allow simple lists of keys for leaves
        if not isinstance(block_tree, dict):
            block_tree = {'keys': block_tree}
        data = {k: v for k, v in block_tree.items()
                if k not in {'keys', 'children'}}
        self._indexed_blocks[index] = Block(block_tree['keys'], data)
        children = block_tree.get('children', [])
        for i, child_tree in enumerate(children):
            self._add_block(self.nth_child(index, i), child_tree)


def generate_node_name(index):
    """Generate the dot node name from an tree index"""
    return 'block' + '.'.join(str(i) for i in index)


def find_middle_port_name(tree):
    """Finds the name of the middle port of each generated node"""
    if tree.keys_per_block % 2 != 0:
        return KEY_NAME_TEMPLATE.format(number=tree.keys_per_block // 2)
    return CONNECTOR_NAME_TEMPLATE.format(number=(tree.keys_per_block + 1) // 2)


def is_highlighted(block):
    """ Return boolean of whether this block is highlighted """
    return block.data.get('highlight', False)


def generate_node_cells(tree, block):
    """Generates the table cells for a single block node"""
    keys = pad(block.keys, tree.keys_per_block, DUMMY_KEY)
    for i, key in enumerate(keys):
        yield CONNECTOR_TEMPLATE.format(number=i)
        yield KEY_TEMPLATE.format(number=i, content=key)
    yield CONNECTOR_TEMPLATE.format(number=tree.children_per_block - 1)


def generate_dot_node(tree, index, block):
    """Generates a dot node to render a single block"""
    template = NODE_TEMPLATE
    if is_highlighted(block):
        template = HIGHLIGHTED_NODE_TEMPLATE
    cells = generate_node_cells(tree, block)
    return template.format(
        name=generate_node_name(index),
        cellborder=tree.cellborder,
        cells=indent('\n'.join(cells), CELL_INDENT)
    )


def generate_parent_child_edges(tree, index):
    """Generates parent to child edges for the subtree below the index"""
    highlighted = is_highlighted(tree[index])
    children = ((i, tree[i]) for i in tree.children(index))
    children = ((i, block) for i, block in children if block is not None)
    for i, child in enumerate(children):
        child_index, child_block = child
        template = EDGE_TEMPLATE
        if highlighted and is_highlighted(child_block):
            template = HIGHLIGHTED_EDGE_TEMPLATE
        yield template.format(
            src_node=generate_node_name(index),
            src_port=CONNECTOR_NAME_TEMPLATE.format(number=i),
            dst_node=generate_node_name(child_index),
            dst_port=find_middle_port_name(tree)
        )
        yield from generate_parent_child_edges(tree, child_index)


def find_max_level(tree, index):
    """Finds the maximum depth of a tree below a block"""
    if tree[index] is None:
        return 0
    return 1 + max(find_max_level(tree, c) for c in tree.children(index))


def find_adjacent_leaves(tree, index):
    """Finds adjacent leaf nodes that should be connected with cross edges.

    We generate cross edges from left to right between the leaves of
    the tree. Because we allow for omitting subtrees, we cannot just
    connect all nodes at the lowest level left to right, because we
    would possibly connect nodes over "holes" where other leaves were
    omitted.

    This method finds adjacent nodes left to right until the tree ends or
    until such a "hole" is found.

    Returns all nodes which should be connected.
    """
    while index is not None:
        if tree[index] is not None:
            yield index
        elif tree.was_omitted(index):
            return
        index = tree.right_sibling(index)


def generate_cross_edge_range(tree, leaves):
    """Creates dot edges to cross connect adjacent leaves"""
    left_port = CONNECTOR_NAME_TEMPLATE.format(number=0)
    right_port = CONNECTOR_NAME_TEMPLATE.format(number=tree.keys_per_block)
    for index1, index2 in pairwise(leaves):
        template = EDGE_TEMPLATE
        if is_highlighted(tree[index1]) and is_highlighted(tree[index2]):
            template = HIGHLIGHTED_EDGE_TEMPLATE
        if tree.two_head:
            yield template.format(
                src_node=generate_node_name(index2),
                src_port=left_port,
                dst_node=generate_node_name(index1),
                dst_port=right_port
            )
        yield template.format(
            src_node=generate_node_name(index1),
            src_port=right_port,
            dst_node=generate_node_name(index2),
            dst_port=left_port
        )


def generate_cross_edges(tree):
    """Generates an iterable of all needed cross edges in a tree"""
    max_level = find_max_level(tree, tree.root_index)
    index = tree.root_index
    for _ in range(max_level - 1):
        index = tree.nth_child(index, 0)
    while True:
        while index is not None and tree[index] is None:
            index = tree.right_sibling(index)
        if index is None:
            return
        adjacent_leaves = list(find_adjacent_leaves(tree, index))
        yield from generate_cross_edge_range(tree, adjacent_leaves)
        # yield from itertools.chain(generate_cross_edge_range(tree, adjacent_leaves),
        #                          generate_cross_edge_range(tree, adjacent_leaves[::-1]))
        index = tree.right_sibling(adjacent_leaves[-1])


def generate_same_rank_statements(tree):
    """Generate statements to constrain nodes to the same rank"""
    indices = sorted(tree.all_indices, key=tree.level)
    grouped = itertools.groupby(indices, tree.level)
    for _, group in grouped:
        blocks = ' '.join('"' + generate_node_name(i) + '"' for i in group)
        yield RANK_SAME_TEMPLATE.format(blocks=blocks)


def generate_dot_graph(tree):
    """Generates a dot graph string from a B+ tree"""
    nodes = '\n'.join(generate_dot_node(tree, i, k) for i, k in tree.all_blocks)
    parent_child_edges = '\n'.join(generate_parent_child_edges(tree,
                                                               tree.root_index))
    cross_edges = '\n'.join(generate_cross_edges(tree))
    rank_statements = '\n'.join(generate_same_rank_statements(tree))
    return GRAPH_TEMPLATE.format(
        nodes=indent(nodes, INSIDE_GRAPH_INDENT),
        parent_child_edges=indent(parent_child_edges, INSIDE_GRAPH_INDENT),
        cross_edges=indent(cross_edges, INSIDE_GRAPH_INDENT),
        rank_statements=indent(rank_statements, INSIDE_GRAPH_INDENT)
    )


def pad(iterable, count, default):
    """Pads an iterable to a given length with a default value."""
    iterator = iter(iterable)
    for _ in range(count):
        yield next(iterator, default)


def indent(string, num_spaces):
    """Indents a string to a certain level."""
    indent_string = num_spaces * ' '
    return indent_string + string.replace('\n', '\n' + indent_string)


def pairwise(iterable):
    "Returns all pairs of adjacent values in the given iterable"""
    iter1, iter2 = itertools.tee(iterable)
    next(iter2, None)
    return zip(iter1, iter2)


def main():
    """Main function. Called when run as main module."""
    parser = argparse.ArgumentParser(description=PROGRAM_DESCRIPTION)
    parser.add_argument('-y', '--YAMLfile',
                        dest='datafile',
                        action='store',
                        nargs='?',
                        type=argparse.FileType('r'),
                        default=sys.stdin,
                        help='YAML file to read from. Default to reading from stdin')
    parser.add_argument('-o', '--outputfile',
                        dest='outputfile',
                        action='store',
                        nargs='?',
                        type=argparse.FileType('w'),
                        default=sys.stdout,
                        help='DOT file to be written to. Default to write to stdout')
    parser.add_argument('-c', '--cellborder',
                        dest='cellborder',
                        action='store',
                        type=bool,
                        default=True,
                        help='Should node cells have borders between items? Default True')
    parser.add_argument('-t', '--two_head',
                        dest='two_head',
                        action='store',
                        type=bool,
                        default=False,
                        help='Should leaf nodes be connected with two headed arrows? Default False')
    args = parser.parse_args()
    data = yaml.safe_load(args.datafile)
    tree = BPlusTree(data['keys_per_block'], args.cellborder, args.two_head, data['tree'])
    print(generate_dot_graph(tree), file=args.outputfile)


if __name__ == '__main__':
    main()
