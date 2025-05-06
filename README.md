# Operating Systems Project 3: B-Tree Index File

This project implements a simple B-Tree index system for storing key-value pairs in a file. It supports inserting, searching, printing, extracting, and loading data from a CSV file, all while keeping the index stored on disk in 512-byte blocks.

## Features

- B-Tree with minimum degree 10 (up to 19 keys and 20 children per node)
- Stores data in an index file on disk 

# Supports the following commands:
- python main.py create <filename>
- python main.py insert <filename> <key> <value>
- python main.py search <filename> <key>
- python main.py load <filename> <csvfile>
- python main.py print <filename>
- python main.py extract <filename> <csvfile>


- Automatically splits nodes and promotes keys when inserting into a full node
- Always keeps at most 3 nodes in memory at a time
- File format uses fixed-size 512-byte blocks with a header and node structure
- Keys and values stored as 8-byte big-endian integers

## Notes

The program handles errors like trying to create a file that already exists, inserting into a non-existent file, or loading from a missing CSV file. I tested it by inserting more than 19 keys to make sure node splitting and promotion work.

All outputs are printed to the terminal, and the index file can also be exported to a CSV file using the `extract` command.

## How to Run

Make sure Python is installed, then run any command like:
- python main.py create test.idx
- python main.py insert test.idx 15 100
- python main.py print test.idx

