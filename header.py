class Header:
    def __init__(self, root_id=0, next_block_id=1):
        self.magic = b'4348PRJ3'  # 8-byte ASCII string
        self.root_id = root_id
        self.next_block_id = next_block_id

    def to_bytes(self):
        data = bytearray(512)
        data[0:8] = self.magic
        data[8:16] = self.root_id.to_bytes(8, 'big', signed=False)
        data[16:24] = self.next_block_id.to_bytes(8, 'big', signed=False)
        return bytes(data)

    @classmethod
    def from_bytes(cls, data):
        if len(data) != 512:
            raise ValueError("Header block must be exactly 512 bytes")
        magic = data[0:8]
        if magic != b'4348PRJ3':
            raise ValueError(f"Invalid magic number: {magic}")
        root_id = int.from_bytes(data[8:16], 'big', signed=False)
        next_block_id = int.from_bytes(data[16:24], 'big', signed=False)
        return cls(root_id, next_block_id)

    def __repr__(self):
        return f"<Header magic={self.magic.decode()} root_id={self.root_id} next_block_id={self.next_block_id}>"
