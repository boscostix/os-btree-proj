import sys
import os
from file_manager import FileManager
from header import Header
from btree_node import Node


def create_command(filename):
    if os.path.exists(filename):
        print("Error: File '{}' already exists.".format(filename))
        sys.exit(1)
    fm = FileManager(filename)
    header = Header(root_id=0, next_block_id=1)
    fm.write_header(header)
    print("Created index file '{}' successfully.".format(filename))


def find_leaf_block(fm, current_block_id, key):
    node = fm.read_node(current_block_id)
    while node.children[0] != 0:
        i = 0
        while i < node.num_keys and key >= node.keys[i]:
            i += 1
        next_block_id = node.children[i]
        if next_block_id == 0:
            break
        node = fm.read_node(next_block_id)
    return node.block_id


def insert_into_node(node, key, value):
    i = node.num_keys - 1
    while i >= 0 and node.keys[i] > key:
        if i + 1 < 19:
            node.keys[i + 1] = node.keys[i]
            node.values[i + 1] = node.values[i]
        i -= 1
    node.keys[i + 1] = key
    node.values[i + 1] = value
    node.num_keys += 1


def split_node(fm, node, header):
    mid_index = node.num_keys // 2
    promoted_key = node.keys[mid_index]
    promoted_value = node.values[mid_index]

    right_node = Node(
        block_id=header.next_block_id,
        parent_id=node.parent_id,
        num_keys=node.num_keys - mid_index - 1,
        keys=node.keys[mid_index + 1:] + [0] * (19 - (node.num_keys - mid_index - 1)),
        values=node.values[mid_index + 1:] + [0] * (19 - (node.num_keys - mid_index - 1)),
        children=node.children[mid_index + 1:] + [0] * (20 - (node.num_keys - mid_index))
    )
    header.next_block_id += 1

    node.num_keys = mid_index
    node.keys[mid_index:] = [0] * (19 - mid_index)
    node.values[mid_index:] = [0] * (19 - mid_index)
    node.children[mid_index + 1:] = [0] * (20 - (mid_index + 1))

    fm.write_node(node.block_id, node)
    fm.write_node(right_node.block_id, right_node)

    if node.parent_id == 0:
        new_root = Node(
            block_id=header.next_block_id,
            parent_id=0,
            num_keys=1,
            keys=[promoted_key] + [0] * 18,
            values=[promoted_value] + [0] * 18,
            children=[node.block_id, right_node.block_id] + [0] * 18
        )
        header.root_id = new_root.block_id
        header.next_block_id += 1
        fm.write_node(new_root.block_id, new_root)
        fm.write_header(header)
        print("Root split: new root created in block {}".format(new_root.block_id))
    else:
        parent = fm.read_node(node.parent_id)
        if parent.num_keys < 19:
            insert_into_node(parent, promoted_key, promoted_value)
            insert_pos = 0
            while insert_pos < parent.num_keys and parent.keys[insert_pos] != promoted_key:
                insert_pos += 1
            parent.children = (
                parent.children[:insert_pos + 1]
                + [right_node.block_id]
                + parent.children[insert_pos + 1:19]
            )
            fm.write_node(parent.block_id, parent)
        else:
            split_node(fm, parent, header)
            updated_parent = fm.read_node(parent.block_id)
            insert_into_node(updated_parent, promoted_key, promoted_value)
            insert_pos = 0
            while insert_pos < updated_parent.num_keys and updated_parent.keys[insert_pos] != promoted_key:
                insert_pos += 1
            updated_parent.children = (
                updated_parent.children[:insert_pos + 1]
                + [right_node.block_id]
                + updated_parent.children[insert_pos + 1:19]
            )
            fm.write_node(updated_parent.block_id, updated_parent)


def insert_command(filename, key, value):
    fm = FileManager(filename)
    header = fm.read_header()

    key = int(key)
    value = int(value)

    if header.root_id == 0:
        # Tree is empty → create new root
        new_node = Node(
            block_id=header.next_block_id,
            parent_id=0,
            num_keys=1,
            keys=[key] + [0] * 18,
            values=[value] + [0] * 18,
            children=[0] * 20
        )
        fm.write_node(header.next_block_id, new_node)
        header.root_id = new_node.block_id
        header.next_block_id += 1
        fm.write_header(header)
        print("Inserted key={} value={} as root node in block {}".format(key, value, new_node.block_id))

    else:
        leaf_block_id = find_leaf_block(fm, header.root_id, key)
        leaf_node = fm.read_node(leaf_block_id)

        if leaf_node.num_keys < 19:
            insert_into_node(leaf_node, key, value)
            fm.write_node(leaf_node.block_id, leaf_node)
            print("Inserted key={} value={} into leaf node block {}".format(key, value, leaf_node.block_id))
        else:
            print("Leaf node {} full -> splitting...".format(leaf_node.block_id))
            split_node(fm, leaf_node, header)
            # After split, re-run insert to retry traversal (since root/parent may have changed)
            insert_command(filename, key, value)


def search_command(filename, key):
    fm = FileManager(filename)
    header = fm.read_header()
    key = int(key)

    if header.root_id == 0:
        print("Search failed: tree is empty.")
        return

    current_block_id = header.root_id
    while True:
        node = fm.read_node(current_block_id)
        for i in range(node.num_keys):
            if node.keys[i] == key:
                print("Found key={} value={} in block {}".format(key, node.values[i], node.block_id))
                return
        if node.children[0] == 0:
            break
        i = 0
        while i < node.num_keys and key >= node.keys[i]:
            i += 1
        next_block_id = node.children[i]
        if next_block_id == 0:
            break
        current_block_id = next_block_id
    print("Search failed: key={} not found.".format(key))


def print_subtree(fm, block_id):
    node = fm.read_node(block_id)
    for i in range(node.num_keys):
        if node.children[i] != 0:
            print_subtree(fm, node.children[i])
        print("{}={}".format(node.keys[i], node.values[i]))
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
    node = fm.read_node(block_id)
    for i in range(node.num_keys):
        if node.children[i] != 0:
            extract_subtree(fm, node.children[i], file_handle)
        file_handle.write("{}, {}\n".format(node.keys[i], node.values[i]))
    if node.children[node.num_keys] != 0:
        extract_subtree(fm, node.children[node.num_keys], file_handle)


def extract_command(filename, output_csv):
    if os.path.exists(output_csv):
        print("Error: Output file '{}' already exists.".format(output_csv))
        sys.exit(1)
    fm = FileManager(filename)
    header = fm.read_header()
    if header.root_id == 0:
        print("Tree is empty. No data to extract.")
        return
    with open(output_csv, 'w') as f:
        extract_subtree(fm, header.root_id, f)
    print("Extracted all key/value pairs to '{}' successfully.".format(output_csv))


def load_command(filename, input_csv):
    if not os.path.exists(input_csv):
        print("Error: Input file '{}' does not exist.".format(input_csv))
        sys.exit(1)
    with open(input_csv, 'r') as f:
        line_num = 0
        for line in f:
            line_num += 1
            line = line.strip()
            if not line:
                continue
            try:
                key_str, value_str = line.split(',', 1)
                key = int(key_str.strip())
                value = int(value_str.strip())
                insert_command(filename, key, value)
            except Exception as e:
                print("Error parsing line {}: {}".format(line_num, line))
                print("Reason: {}".format(e))
                continue
    print("Loaded all key/value pairs from '{}' into '{}' successfully.".format(input_csv, filename))


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
        if len(sys.argv) != 4:
            print("Usage: project3 load <filename> <csvfile>")
            sys.exit(1)
        load_command(filename, sys.argv[3])
    else:
        print("Unknown command: {}".format(command))


if __name__ == "__main__":
    main()
