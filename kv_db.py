import json 
import os 
class KeyValueDB:
    def __init__(self, filepath="db.log"):
        self.filepath = filepath
        self.store = {}
        self.immutable_keys = set()
        self._recover()

    def _write_log(self, command:dict):
        with open(self.filepath, "a") as f:
            f.write(json.dumps(command) + "\n")

    def set(self, key:str, value:str):
        if key in self.immutable_keys:
            return False, "Key is immutable and cannot be overwritten."
        
        self.store[key] = value
        self._write_log({"action": "SET", "key": key, "value": value})
        return True, "OK"
    def set_immutable(self, key:str, value:str):
        if key in self.immutable_keys:
            return False, "Key is already immutable and cannot be overwritten."
        
        self.store[key] = value
        self.immutable_keys.add(key)
        self._write_log({"action": "SET_IMUT", "key": key, "value": value})
        return True, "OK"
    def get(self, key:str):
        if key in self.immutable_keys:
            result = self.store.get(key, "(nil)") 
            if result == "(nil)":
                return "(nil)"
            return "" + result + " (immutable)"
        return self.store.get(key, "(nil)")

    def delete (self, key:str):
        if key in self.immutable_keys:
            return False, "Key is immutable and cannot be deleted using the DELETE command."
        if key in self.store:
            del self.store[key]
            self._write_log({"action": "DELETE", "key": key})
            return True, "OK"
        return False, "Key not found."
    def delete_IMUT(self, key:str):
            if key in self.immutable_keys:
                self.immutable_keys.remove(key)
                self._write_log({"action": "DELETE_IMUT", "key": key})
                return True, "OK"
            return False, "Key is not immutable or does not exist."
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
    print("Simple KV Database installed. COMMANDS: SET <key> <value> | SET IMUT <key> <value> | GET <key> | DELETE <key> | DELETE IMUT <key> | EXIT")
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
                
                if parts[1].upper() == "IMUT":
                    if len(parts) < 3:
                        printError("DELETE IMUT command requires a key.")
                    else:
                        success, msg = db.delete_IMUT(parts[2])
                        if not success:
                            printError(msg)
                        else:
                            print(f"Successfully removed immutability from key: {parts[2]}")
                else:
                    success, msg = db.delete(parts[1])
                    if not success:
                        printError(msg)
                    else:
                        print(f"Successfully deleted: {parts[1]}")
        except KeyboardInterrupt:
            print("\nExiting...\n")
            break


            


                
            




