class SearchEngine:
    """Keyword-based search over document chunks."""

    def search(
        self,
        chunks: list[dict],
        query: str,
        top_k: int,
    ) -> list[dict]:
        """Search chunks by keyword relevance."""
        query_terms = query.lower().split()
        scored: list[dict] = []

        for chunk in chunks:
            content_lower = chunk["content"].lower()
            score = 0

            for term in query_terms:
                count = content_lower.count(term)
                score += count * len(term)  # Weight by term length

            if score > 0:
                scored.append(
                    {
                        **chunk,
                        "score": score,
                        "preview": chunk["content"][:200] + "..."
                        if len(chunk["content"]) > 200
                        else chunk["content"],
                    }
                )

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]
