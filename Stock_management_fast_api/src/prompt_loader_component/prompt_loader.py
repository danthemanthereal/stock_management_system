from pathlib import Path

class PromptLoader:

    def __init__(self):
        pass

    def load_prompt(self, file_path: str) -> str:
        file = Path(file_path)
        return file.read_text(encoding="utf-8")