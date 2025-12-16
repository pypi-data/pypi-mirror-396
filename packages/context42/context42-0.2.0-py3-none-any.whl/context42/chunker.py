from typing import TypedDict


class Chunk(TypedDict):
    chunk_id: str
    filename: str
    content: str
    start_pos: int
    end_pos: int


class Chunker:
    """Document chunking with compression levels."""

    BASE_CHUNK_SIZE = 1000
    MIN_CHUNK_SIZE = 100

    def get_chunk_size(self, compression_level: float) -> int:
        """Calculate chunk size from compression level."""
        if compression_level <= 0:
            raise ValueError("compression_level must be > 0")
        if compression_level > 128:
            compression_level = 128  # Cap at max
        return max(self.MIN_CHUNK_SIZE, int(self.BASE_CHUNK_SIZE / compression_level))

    def chunk(
        self,
        documents: list[dict],
        compression_level: float,
    ) -> list[Chunk]:
        """Chunk documents based on compression level."""
        chunk_size = self.get_chunk_size(compression_level)
        overlap = min(chunk_size // 4, 100)
        step = chunk_size - overlap

        chunks: list[Chunk] = []

        for doc in documents:
            content = doc["content"]
            filename = doc["filename"]

            for i in range(0, len(content), step):
                chunk_content = content[i : i + chunk_size]
                if chunk_content.strip():  # Skip empty chunks
                    chunks.append(
                        {
                            "chunk_id": f"{filename}_{i}",
                            "filename": filename,
                            "content": chunk_content,
                            "start_pos": i,
                            "end_pos": min(i + chunk_size, len(content)),
                        }
                    )

        return chunks
