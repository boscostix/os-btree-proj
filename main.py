import sys
import os
from file_manager import FileManager
from header import Header
from btree_node import Node


def create_command(filename):
    if os.path.exists(filename):
        print(f"Error: File '{filename}' already exists. Aborting create.")
        sys.exit(1)

    fm = FileManager(filename)
    header = Header(root_id=0, next_block_id=1)
    fm.write_header(header)
    print(f"Created index file '{filename}' successfully.")


def find_leaf_block(fm, current_block_id, key):
    """
    Traverse from root to leaf to find the block ID of the leaf node where key should go.
    """
    node = fm.read_node(current_block_id)
    while node.children[0] != 0:  # internal node → has children
        i = 0
        while i < node.num_keys and key >= node.keys[i]:
            i += 1
        next_block_id = node.children[i]
        if next_block_id == 0:
            break
        node = fm.read_node(next_block_id)
    return node.block_id


def insert_into_node(node, key, value):
    """
    Insert key/value into node's keys/values in sorted order (assuming node not full).
    """
    i = node.num_keys - 1
    while i >= 0 and node.keys[i] > key:
        if i + 1 < 19:
            node.keys[i + 1] = node.keys[i]
            node.values[i + 1] = node.values[i]
        i -= 1
    node.keys[i + 1] = key
    node.values[i + 1] = value
    node.num_keys += 1


def insert_command(filename, key, value):
    fm = FileManager(filename)
    header = fm.read_header()

    key = int(key)
    value = int(value)

    if header.root_id == 0:
        # Tree is empty → create new root node
        new_node = Node(
            block_id=header.next_block_id,
            parent_id=0,
            num_keys=1,
            keys=[key] + [0] * 18,
            values=[value] + [0] * 18,
            children=[0] * 20
        )
        fm.write_node(header.next_block_id, new_node)

        header.root_id = header.next_block_id
        header.next_block_id += 1
        fm.write_header(header)

        print(f"Inserted key={key} value={value} as root node in block {new_node.block_id}")
    else:
        leaf_block_id = find_leaf_block(fm, header.root_id, key)
        leaf_node = fm.read_node(leaf_block_id)

        if leaf_node.num_keys >= 19:
            print("Insert failed: leaf node is full (splitting not implemented yet).")
            return

        insert_into_node(leaf_node, key, value)
        fm.write_node(leaf_node.block_id, leaf_node)

        print(f"Inserted key={key} value={value} into leaf node block {leaf_node.block_id}")


def search_command(filename, key):
    fm = FileManager(filename)
    header = fm.read_header()

    key = int(key)

    if header.root_id == 0:
        print(f"Search failed: tree is empty.")
        return

    current_block_id = header.root_id

    while True:
        node = fm.read_node(current_block_id)

        for i in range(node.num_keys):
            if node.keys[i] == key:
                print(f"Found key={key} value={node.values[i]} in block {node.block_id}")
                return

        if node.children[0] == 0:
            break  # no children → leaf

        i = 0
        while i < node.num_keys and key >= node.keys[i]:
            i += 1
        next_block_id = node.children[i]

        if next_block_id == 0:
            break
        current_block_id = next_block_id

    print(f"Search failed: key={key} not found in tree.")


def print_subtree(fm, block_id):
    """
    Recursive in-order traversal: print all key/value pairs in subtree rooted at block_id.
    """
    node = fm.read_node(block_id)

    for i in range(node.num_keys):
        if node.children[i] != 0:
            print_subtree(fm, node.children[i])
        print(f"{node.keys[i]}={node.values[i]}")

    if node.children[node.num_keys] != 0:
        print_subtree(fm, node.children[node.num_keys])


def print_command(filename):
    fm = FileManager(filename)
    header = fm.read_header()

    if header.root_id == 0:
        print("Tree is empty.")
        return

    print_subtree(fm, header.root_id)


def extract_subtree(fm, block_id, file_handle):
    """
    Recursive in-order traversal: write key,value pairs to open file handle.
    """
    node = fm.read_node(block_id)

    for i in range(node.num_keys):
        if node.children[i] != 0:
            extract_subtree(fm, node.children[i], file_handle)
        file_handle.write(f"{node.keys[i]},{node.values[i]}\n")

    if node.children[node.num_keys] != 0:
        extract_subtree(fm, node.children[node.num_keys], file_handle)


def extract_command(filename, output_csv):
    if os.path.exists(output_csv):
        print(f"Error: Output file '{output_csv}' already exists. Aborting extract.")
        sys.exit(1)

    fm = FileManager(filename)
    header = fm.read_header()

    if header.root_id == 0:
        print("Tree is empty. No data to extract.")
        return

    with open(output_csv, 'w') as f:
        extract_subtree(fm, header.root_id, f)

    print(f"Extracted all key/value pairs to '{output_csv}' successfully.")


def main():
    if len(sys.argv) < 3:
        print("Usage:")
        print("  project3 create <filename>")
        print("  project3 insert <filename> <key> <value>")
        print("  project3 search <filename> <key>")
        print("  project3 load <filename> <csvfile>")
        print("  project3 print <filename>")
        print("  project3 extract <filename> <csvfile>")
        sys.exit(1)

    command = sys.argv[1]
    filename = sys.argv[2]

    if command == "create":
        create_command(filename)
    elif command == "insert":
        if len(sys.argv) != 5:
            print("Usage: project3 insert <filename> <key> <value>")
            sys.exit(1)
        insert_command(filename, sys.argv[3], sys.argv[4])
    elif command == "search":
        if len(sys.argv) != 4:
            print("Usage: project3 search <filename> <key>")
            sys.exit(1)
        search_command(filename, sys.argv[3])
    elif command == "print":
        print_command(filename)
    elif command == "extract":
        if len(sys.argv) != 4:
            print("Usage: project3 extract <filename> <csvfile>")
            sys.exit(1)
        extract_command(filename, sys.argv[3])
    elif command == "load":
        print("Load command not yet implemented.")
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main()
