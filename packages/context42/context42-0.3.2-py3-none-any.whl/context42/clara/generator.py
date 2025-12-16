"""CLaRa answer generation using compressed documents."""

from typing import Dict, Any, List


class CLaRaGenerator:
    """Generate answers using CLaRa model."""

    def __init__(self, manager):
        self.manager = manager

    def ask(
        self,
        question: str,
        documents: List[str],
        max_new_tokens: int = 64,
    ) -> Dict[str, Any]:
        """Ask a question about documents using CLaRa.

        Uses generate_from_text for Stage 2 (Instruct) models.
        CLaRa expects: questions=[str], documents=[[str, str, ...]]
        """
        if not self.manager.is_loaded():
            return {"error": "Model not loaded. Call init_clara first."}

        try:
            # CLaRa expects documents as list of lists (batch of document sets)
            output = self.manager.model.generate_from_text(
                questions=[question],
                documents=[documents],  # Wrap in list for batch format
                max_new_tokens=max_new_tokens,
            )

            return {
                "answer": output[0] if output else "",
                "model": self.manager.current_model_name,
                "documents_used": len(documents),
                "method": "clara",
            }
        except Exception as e:
            return {"error": f"Generation failed: {str(e)}"}

    def search(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Search documents using CLaRa's latent space."""
        if not self.manager.is_loaded():
            return [{"error": "Model not loaded. Call init_clara first."}]

        # Extract content from documents
        doc_texts = [d["content"] for d in documents]

        try:
            # Use CLaRa for semantic retrieval
            # Set max_new_tokens=1 for retrieval-only (minimal generation)
            output, topk_indices = self.manager.model.generate_from_questions(
                questions=[query],
                documents=[doc_texts],
                max_new_tokens=1,
            )

            # Map indices to documents with relevance scoring
            results = []
            retrieved_indices = topk_indices[0][:top_k] if topk_indices else []

            for idx in retrieved_indices:
                if idx < len(documents):
                    # Higher score for earlier retrieved documents
                    relevance_score = 1.0 - (retrieved_indices.index(idx) * 0.1)
                    results.append(
                        {
                            **documents[idx],
                            "score": relevance_score,
                            "method": "clara",
                            "preview": documents[idx]["content"][:200] + "..."
                            if len(documents[idx]["content"]) > 200
                            else documents[idx]["content"],
                        }
                    )

            return results
        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]
