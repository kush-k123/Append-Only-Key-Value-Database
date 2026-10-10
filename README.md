# Append-Only Log (AOL) Key-Value Database

A lightweight, persistent key-value store built from scratch in Python. This project implements an **Append-Only Log (AOL)** architecture—the same foundational design pattern used by high-performance systems like Redis and Bitcask—combining fast in-memory lookups with durable disk persistence.

---

## Key Features

* **$O(1)$ In-Memory Lookups:** Leverages a Python dictionary for instantaneous retrieval speeds.
* **Persistent Storage:** Every mutation (`SET`, `DELETE`) is sequentially serialized and appended to a disk log (`db.log`), ensuring data survives application restarts.
* **Automatic Crash Recovery:** On initialization, the database parses and replays the transaction log to accurately rebuild its previous in-memory state.
* **Key Immutability (`SET IMUT`):** Introduces a protection layer allowing specific keys to be locked against accidental overwrites or standard modifications until explicitly unlocked.

---

## Getting Started

### Prerequisites
* Python 3.x installed on your system. No external libraries or dependencies are required.

### Installation & Running
1. Clone the repository or download the source code script.
2. Run the database engine from your terminal:
   python kv_db.py


---

## Command Reference

Once the interactive REPL starts (`db< `), you can use the following commands:

| Command | Syntax | Description |
| --- | --- | --- |
| **Set Standard Key** | `SET <key> <value>` | Stores a key-value pair (overwrites if key exists). |
| **Set Immutable Key** | `SET IMUT <key> <value>` | Stores a key and locks it, preventing standard overwrites. |
| **Retrieve Value** | `GET <key>` | Fetches the value associated with the key. |
| **Delete Key** | `DELETE <key>` | Removes a standard key from memory and logs the deletion. |
| **Remove Immutability** | `REMOVE IMUT <key>` | Unlocks an immutable key so it can be modified or deleted. |
| **List Active Keys** | `LIST` | Lists all active keys, their values, and immutability status. |
| **Compact Database Log** | `COMPACT` | Rewrites `db.log` to remove dead entries. Automatically triggers after 100 mutations or when file size exceeds 1MB. |
| **Display Session Stats** | `INFO` | Lists uptime, active/immutable key counts, total mutations, log file size, and file path. |
| **Start Transaction** | `MULTI` | Begins a transaction block, queuing subsequent commands. |
| **Execute Transaction** | `EXEC` | Commits and executes all queued transaction commands atomically. |
| **Discard Transaction** | `DISCARD` | Clears the current transaction queue and exits transaction mode. |
| **Exit** | `EXIT` | Safely closes the database interface. |

---

## Architectural Design

1. **Storage Engine:** Mutating actions are converted to JSON and written sequentially to `db.log`. Sequential disk I/O provides high write performance compared to random disk writes.
2. **Crash Resilience:** The `_recover()` routine safeguards startup by reading historical logs line-by-line, wrapping parsing logic in error-handling blocks to gracefully manage malformed trailing lines if a crash occurs mid-write.

---

## Known Limitations & Future Roadmap

* **Newline Restrictions:** Values currently do not support raw internal newline characters due to line-delimited log serialization.
* **Concurrency:** Designed for single-process execution; multi-process file locking (`fcntl`/`msvcrt`) is not implemented.
