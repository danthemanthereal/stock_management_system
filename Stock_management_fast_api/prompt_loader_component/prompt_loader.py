from pathlib import Path

class PromptLoader:

    def init(self, file_path: str):
        self.file = Path(file_path)

    def load_prompt(self) -> str:
        return self.file.read_text(encoding="utf-8")