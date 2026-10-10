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
   ```bash
   python kv_db.py
