from collections import Counter


class KeywordOverlapReranker:
    def rerank(self, query: str, results: list[dict], top_k: int) -> list[dict]:
        query_terms = Counter(self._tokenize(query))
        rescored: list[dict] = []
        for result in results:
            text_terms = Counter(self._tokenize(result["text"]))
            overlap = sum(min(query_terms[token], text_terms[token]) for token in query_terms)
            rescored.append({**result, "score": float(result["score"]) + overlap * 0.05})
        rescored.sort(key=lambda item: item["score"], reverse=True)
        return rescored[:top_k]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return [part.lower() for part in text.split() if len(part) > 2]
