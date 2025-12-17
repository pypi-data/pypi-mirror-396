from dataclasses import dataclass
import json
import os
import sys

DATA_DIR = ".pynstal/"

@dataclass
class InterpretersData:
    FILE_PATH: str
    
    interpreters: list[str] | None = None
    default_interpreter: str | None = None
    
    def is_empty(self) -> bool:
        return self.interpreters is None and self.default_interpreter is None
    
    def save(self) -> None:
        SAVE_PATH = os.path.join(DATA_DIR, self.FILE_PATH)
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.__dict__, f, indent=4)
            
    def __init__(self, file_path) -> None:
        self.FILE_PATH = file_path
        
        LOAD_PATH = os.path.join(DATA_DIR, self.FILE_PATH)
        if os.path.exists(LOAD_PATH):
            with open(LOAD_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.interpreters = data.get("interpreters")
                self.default_interpreter = data.get("default_interpreter")
        else:
            self.interpreters = None
            self.default_interpreter = None

        # If no default interpreter configured, default to current Python executable
        try:
            current = sys.executable
            if not self.default_interpreter and current and os.path.isfile(current):
                # ensure interpreters list exists and contains the current executable
                if self.interpreters is None:
                    self.interpreters = [current]
                else:
                    if current not in self.interpreters:
                        self.interpreters.insert(0, current)
                self.default_interpreter = current
                # persist the change
                self.save()
        except Exception:
            # avoid failing import/initialization on unexpected environments
            pass

interpreters_data = InterpretersData("interpreters.json")
