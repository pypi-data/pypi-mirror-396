from pathlib import Path
from typing import TypedDict


class Document(TypedDict):
    filename: str
    path: str
    content: str
    size: int
    extension: str


class DocumentProcessor:
    """Load and parse text documents from filesystem."""

    def load(
        self,
        directory: str,
        extensions: list[str],
        max_files: int,
    ) -> list[Document]:
        """Load documents from directory."""
        documents: list[Document] = []
        dir_path = Path(directory)

        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        files = []
        for ext in extensions:
            files.extend(dir_path.glob(f"*{ext}"))

        files = sorted(files)[:max_files]

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
                documents.append(
                    {
                        "filename": file_path.name,
                        "path": str(file_path),
                        "content": content,
                        "size": len(content),
                        "extension": file_path.suffix,
                    }
                )
            except Exception:
                continue  # Skip unreadable files

        return documents
