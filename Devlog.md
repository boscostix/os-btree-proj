# May 4 @ 7pm
- Created the project structure and files
- Will start on header.py first
- Figure out how to do the indexing part, looks tricky

# May 5 @ 10am
- implemented the header file
- attributes include magic number and the block IDs
- added necessary functions to it and tested it to run

# May 5 @ 11am
- implemented the file_manager.py file
- properly reads and writes the 512 blocks
- manages block positions
- next is implementing the btree_node.py file

# May 5 @ 11:45pm
- Implemented the btree_node.py file
- defines the node class
- serializes and parses to and from 512 bytes
- next up is to work on main.py, which will have the CLI

# May 5 @ 1pm
- Did a big chunk of the main.py methods
- It should be able to create, insert, search, and traverse data as well
- Inserting into a non-empty tree was a little tricky, but I figured it out
- also implemented the print function which shows the nodes in correct order
- Also figured out loading it to csv but want to ensure bugs are fixed.

# May 5 @ 10am
- Finished implementing all functions required in main
- Finished writing up the Readme file
- Need to double-check and test everything, but seems to be working fine right now