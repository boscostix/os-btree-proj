class Node:
    def __init__(self, block_id=0, parent_id=0, num_keys=0, keys=None, values=None, children=None):
        self.block_id = block_id
        self.parent_id = parent_id
        self.num_keys = num_keys
        self.keys = keys if keys is not None else [0] * 19
        self.values = values if values is not None else [0] * 19
        self.children = children if children is not None else [0] * 20

    def to_bytes(self):
        data = bytearray(512)
        data[0:8] = self.block_id.to_bytes(8, 'big', signed=False)
        data[8:16] = self.parent_id.to_bytes(8, 'big', signed=False)
        data[16:24] = self.num_keys.to_bytes(8, 'big', signed=False)
        for i in range(19):
            start = 24 + i * 8
            data[start:start+8] = self.keys[i].to_bytes(8, 'big', signed=False)
        for i in range(19):
            start = 24 + 152 + i * 8
            data[start:start+8] = self.values[i].to_bytes(8, 'big', signed=False)
        for i in range(20):
            start = 24 + 152 + 152 + i * 8
            data[start:start+8] = self.children[i].to_bytes(8, 'big', signed=False)
        return bytes(data)

    @classmethod
    def from_bytes(cls, data):
        if len(data) != 512:
            raise ValueError("Node block must be exactly 512 bytes")
        block_id = int.from_bytes(data[0:8], 'big', signed=False)
        parent_id = int.from_bytes(data[8:16], 'big', signed=False)
        num_keys = int.from_bytes(data[16:24], 'big', signed=False)
        keys = [int.from_bytes(data[24 + i*8:32 + i*8], 'big', signed=False) for i in range(19)]
        values = [int.from_bytes(data[24 + 152 + i*8:32 + 152 + i*8], 'big', signed=False) for i in range(19)]
        children = [int.from_bytes(data[24 + 152 + 152 + i*8:32 + 152 + 152 + i*8], 'big',
                                   signed=False) for i in range(20)]
        return cls(block_id, parent_id, num_keys, keys, values, children)

    def __repr__(self):
        return ("<Node block_id={} parent_id={} num_keys={} keys={} values={} children={}>"
                .format(self.block_id, self.parent_id, self.num_keys,
                        self.keys[:self.num_keys], self.values[:self.num_keys], self.children[:self.num_keys + 1]))
