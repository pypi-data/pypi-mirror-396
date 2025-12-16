from pathlib import Path

def write_text(text: str, filename: str, encoding: str = "utf-8") -> None:
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding=encoding)
