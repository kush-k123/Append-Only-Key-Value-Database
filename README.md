Append-Only Log (AOL) Key-Value Database

A lightweight, persistent key-value store built from scratch in Python. This project implements an Append-Only Log (AOL) architecture—the same foundational design pattern used by high-performance systems like Redis and Bitcask—combining fast in-memory lookups with durable disk persistence.
Key Features

    O(1) In-Memory Lookups: Leverages a Python dictionary for instantaneous retrieval speeds.

    Persistent Storage: Every mutation (SET, DELETE) is sequentially serialized and appended to a disk log (db.log), ensuring data survives application restarts.

    Automatic Crash Recovery: On initialization, the database parses and replays the transaction log to accurately rebuild its previous in-memory state.

    Key Immutability (SET IMUT): Introduces a protection layer allowing specific keys to be locked against accidental overwrites or standard modifications until explicitly unlocked.

Getting Started
Prerequisites

    Python 3.x installed on your system. No external libraries or dependencies are required.

Installation & Running

    Clone the repository or download the source code script.

    Run the database engine from your terminal:
    Bash

    python kv_db.py

Command Reference

Once the interactive REPL starts (db< ), you can use the following commands:
Command	Syntax	Description
Set Standard Key	SET <key> <value>	Stores a key-value pair (overwrites if key exists).
Set Immutable Key	SET IMUT <key> <value>	Stores a key and locks it, preventing standard overwrites.
Retrieve Value	GET <key>	Fetches the value associated with the key.
Delete Key	DELETE <key>	Removes a standard key from memory and logs the deletion.
Remove Immutability	DELETE IMUT <key>	Unlocks an immutable key so it can be modified or deleted.
Exit	EXIT	Safely closes the database interface.
Architectural Design

    Storage Engine: Mutating actions are converted to JSON and written sequentially to db.log. Sequential disk I/O provides high write performance compared to random disk writes.

    Crash Resilience: The _recover() routine safeguards startup by reading historical logs line-by-line, wrapping parsing logic in error-handling blocks to gracefully manage malformed trailing lines if a crash occurs mid-write.

Known Limitations & Future Roadmap

    Log Compaction: The log file grows monotonically with every operation over time. Implementing a background compaction routine to rewrite only active keys is a planned optimization.

    Newline Restrictions: Values currently do not support raw internal newline characters due to line-delimited log serialization.

    Concurrency: Designed for single-process execution; multi-process file locking (fcntl/msvcrt) is not implemented.
