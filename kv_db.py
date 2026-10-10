import json 
import os 

class KeyValueDB:
    # Initialization function to set up the empty store and tracking sets
    def __init__(self, filepath="db.log"):
        self.filepath = filepath
        self.store = {}
        self.immutable_keys = set()
        self.mutation_counter = 0
        self._recover()

    # Appends a serialized command dictionary to the disk log file
    def _write_log(self, command: dict):
        with open(self.filepath, "a") as f:
            f.write(json.dumps(command) + "\n")
        self.mutation_counter += 1
        if self.mutation_counter >= 100:
            self.compact()
            self.mutation_counter = 0
    # Compacts the db.log file by making a temporary file and writes only the current active keys and values to it, 
    # then replace the db.log file with the temporary file, effectively removing any deleted or overwritten entries from the log 
    def compact(self):
        temp_filepath = self.filepath + ".tmp"
        with open(temp_filepath, "w") as f:
            for key, value in self.store.items():
                action = "SET_IMUT" if key in self.immutable_keys else "SET"
                f.write(json.dumps({"action": action, "key": key, "value": value}) + "\n")
        os.replace(temp_filepath, self.filepath)
        print("[System] Log compaction completed.")


    # Sets a standard key-value pair if the key is not immutable
    def set(self, key: str, value: str):
        if key in self.immutable_keys:
            return False, "Key is immutable and cannot be overwritten."
        
        self.store[key] = value
        self._write_log({"action": "SET", "key": key, "value": value})
        return True, "OK"

    # Sets a key-value pair and locks it against future modifications
    def set_immutable(self, key: str, value: str):
        if key in self.immutable_keys:
            return False, "Key is already immutable and cannot be overwritten."
        
        self.store[key] = value
        self.immutable_keys.add(key)
        self._write_log({"action": "SET_IMUT", "key": key, "value": value})
        return True, "OK"

    # Retrieves the value of the provided key, appending a tag if it's immutable
    def get(self, key: str):
        if key in self.immutable_keys:
            result = self.store.get(key, "(nil)") 
            if result == "(nil)":
                return "(nil)"
            return result + " (immutable)"
        return self.store.get(key, "(nil)")

    # Deletes a standard key-value pair if it is not locked
    def delete(self, key: str):
        if key in self.immutable_keys:
            return False, "Key is immutable and cannot be deleted using the DELETE command."
        if key in self.store:
            del self.store[key]
            self._write_log({"action": "DELETE", "key": key})
            return True, "OK"
        return False, "Key not found."

    # Removes the immutability lock from a key-value pair
    def remove_imut(self, key: str):
        if key in self.immutable_keys:
            self.immutable_keys.remove(key)
            self._write_log({"action": "DELETE_IMUT", "key": key})
            return True, "OK"
        return False, "Key is not immutable or does not exist."
    # Lists all keys currently stored in the database as well as their values and immutability status
    def list_all(self):
        entries = []
        for key, value in self.store.items():
            is_immutable = key in self.immutable_keys
            entries.append((key, value, is_immutable))
        return entries
    # Replays the db.log file to rebuild the database state on startup
    def _recover(self):
        if not os.path.exists(self.filepath):
            return 
        with open(self.filepath, "r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    record = json.loads(line.strip())
                except json.JSONDecodeError:
                    # Skip partial or corrupted trailing writes from crashes
                    continue
                
                action = record.get("action")
                key = record.get("key")

                if action == "SET":
                    self.store[key] = record.get("value")
                elif action == "DELETE":
                    self.store.pop(key, None)
                elif action == "SET_IMUT":
                    self.store[key] = record.get("value")
                    self.immutable_keys.add(key)
                elif action == "DELETE_IMUT":
                    self.immutable_keys.discard(key)

# --- CLI ---
def printError(errorMessage):
    print(f"ERROR: {errorMessage}")

if __name__ == "__main__":
    db = KeyValueDB()
    print("Simple KV Database installed. COMMANDS: SET <key> <value> | SET IMUT <key> <value> | GET <key> | DELETE <key> | REMOVE IMUT <key> | LIST | COMPACT | EXIT")
    while True:
        try:
            parts = input("db< ").strip().split(" ", 2)
            if not parts:
                continue

            cmd = parts[0].upper()

            if cmd == "EXIT":
                break 
            elif cmd == "SET":
                if parts[1].upper() == "IMUT":
                    sub_parts = parts[2].split(" ", 1) if len(parts) > 2 else []
                    if len(sub_parts) < 2:
                        printError("SET IMUT command requires both key and value.")
                    else:
                        success, msg = db.set_immutable(sub_parts[0], sub_parts[1])
                        if success:
                            print(msg)
                        else:
                            printError(msg)
                else:
                    if len(parts) < 3:
                        printError("SET command requires both key and value.")
                        continue
                    success, msg = db.set(parts[1], parts[2])
                    if success:
                        print("OK")
                    else:
                        printError(msg)

            elif cmd == "GET":
                if len(parts) < 2:
                    printError("GET command requires a key.")
                    continue
                result = db.get(parts[1])
                if result == "(nil)":
                    printError("Key not found")
                else:
                    print(result)

            elif cmd == "DELETE":
                if len(parts) < 2:
                    printError("DELETE command requires a key.")
                    continue
                else:
                    success, msg = db.delete(parts[1])
                    if not success:
                        printError(msg)
                    else:
                        print(f"Successfully deleted: {parts[1]}")
            elif cmd == "REMOVE":
                if len(parts) < 3 or parts[1].upper() != "IMUT":
                    printError("REMOVE IMUT command requires a key.")
                    continue
                else:
                    success, msg = db.remove_imut(parts[2])
                    if not success:
                        printError(msg)
                    else:
                        print(f"Successfully removed immutability from: {parts[2]}")
            elif cmd == "LIST":
                entries = db.list_all()
                if not entries:
                    print("(empty database)")
                else:
                    print("--- Database Entries ---")
                    for key, value, is_immutable in entries:
                        status = " (immutable)" if is_immutable else ""
                        print(f"{key}: {value}{status}")
                    print("------------------------")
            elif cmd == "COMPACT":
                db.compact()
            else:
                printError("Unknown command. Available commands: SET, SET IMUT, GET, DELETE, REMOVE IMUT, LIST, COMPACT, EXIT")
        except KeyboardInterrupt:
            print("\nExiting...\n")
            break