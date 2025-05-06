import os
from header import Header
from btree_node import Node


class FileManager:
    BLOCK_SIZE = 512

    def __init__(self, filename):
        self.filename = filename
        # Ensure file exists; create it if not
        if not os.path.exists(filename):
            with open(filename, 'wb') as f:
                pass  # create an empty file

    def read_block(self, block_index):
        with open(self.filename, 'rb') as f:
            f.seek(block_index * self.BLOCK_SIZE)
            data = f.read(self.BLOCK_SIZE)
            if len(data) < self.BLOCK_SIZE:
                raise IOError("Block {} is incomplete or missing".format(block_index))
            return data

    def write_block(self, block_index, data):
        if len(data) != self.BLOCK_SIZE:
            raise ValueError("Data must be exactly 512 bytes")
        with open(self.filename, 'rb+') as f:
            f.seek(block_index * self.BLOCK_SIZE)
            f.write(data)

    def read_header(self):
        block_data = self.read_block(0)
        return Header.from_bytes(block_data)

    def write_header(self, header):
        self.write_block(0, header.to_bytes())

    def read_node(self, block_index):
        if block_index == 0:
            raise ValueError("Block 0 is reserved for header, not a node")
        block_data = self.read_block(block_index)
        return Node.from_bytes(block_data)

    def write_node(self, block_index, node):
        if block_index == 0:
            raise ValueError("Block 0 is reserved for header, not a node")
        self.write_block(block_index, node.to_bytes())
