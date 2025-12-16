"""Evaluation metrics for measuring prompt amplification quality."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import numpy as np


@dataclass
class PromptMetrics:
    """
    Metrics for evaluating expanded prompt quality.

    Attributes:
        expansion_ratio: Length ratio of expanded to original prompt.
        structure_score: Score based on presence of structure elements (0-1).
        specificity_score: Score based on specific instructions (0-1).
        completeness_score: Score based on section coverage (0-1).
        readability_score: Flesch-Kincaid readability score.
        overall_score: Weighted combination of all metrics (0-1).
    """

    expansion_ratio: float = 0.0
    structure_score: float = 0.0
    specificity_score: float = 0.0
    completeness_score: float = 0.0
    readability_score: float = 0.0
    overall_score: float = 0.0
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert metrics to dictionary."""
        return {
            "expansion_ratio": self.expansion_ratio,
            "structure_score": self.structure_score,
            "specificity_score": self.specificity_score,
            "completeness_score": self.completeness_score,
            "readability_score": self.readability_score,
            "overall_score": self.overall_score,
            "details": self.details,
        }


@dataclass
class RetrievalMetrics:
    """
    Metrics for evaluating retrieval quality.

    Attributes:
        precision_at_k: Precision at k retrieved documents.
        recall_at_k: Recall at k retrieved documents.
        mrr: Mean Reciprocal Rank.
        ndcg: Normalized Discounted Cumulative Gain.
        relevance_scores: Individual relevance scores.
    """

    precision_at_k: float = 0.0
    recall_at_k: float = 0.0
    mrr: float = 0.0
    ndcg: float = 0.0
    average_score: float = 0.0
    relevance_scores: list[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert metrics to dictionary."""
        return {
            "precision_at_k": self.precision_at_k,
            "recall_at_k": self.recall_at_k,
            "mrr": self.mrr,
            "ndcg": self.ndcg,
            "average_score": self.average_score,
        }


def calculate_expansion_quality(
    original_prompt: str,
    expanded_prompt: str,
    weights: Optional[dict] = None,
) -> PromptMetrics:
    """
    Calculate quality metrics for an expanded prompt.

    Args:
        original_prompt: The original short prompt.
        expanded_prompt: The expanded prompt.
        weights: Optional weights for overall score calculation.

    Returns:
        PromptMetrics with all calculated scores.

    Example:
        >>> metrics = calculate_expansion_quality(
        ...     "Summarize the data",
        ...     "**GOAL:** Generate a summary...\\n**SECTIONS:**..."
        ... )
        >>> print(f"Overall: {metrics.overall_score:.2f}")
    """
    weights = weights or {
        "structure": 0.25,
        "specificity": 0.25,
        "completeness": 0.25,
        "readability": 0.25,
    }

    metrics = PromptMetrics()

    # Expansion ratio
    orig_len = len(original_prompt)
    exp_len = len(expanded_prompt)
    metrics.expansion_ratio = exp_len / orig_len if orig_len > 0 else 0

    # Structure score - check for structural elements
    structure_elements = {
        "headers": len(re.findall(r"^#+\s|\*\*[A-Z][^*]+\*\*:", expanded_prompt, re.M)),
        "bullet_points": len(re.findall(r"^[\-\*]\s", expanded_prompt, re.M)),
        "numbered_lists": len(re.findall(r"^\d+\.\s", expanded_prompt, re.M)),
        "tables": len(re.findall(r"\|.*\|.*\|", expanded_prompt)),
        "sections": len(re.findall(r"^#{1,3}\s", expanded_prompt, re.M)),
    }

    structure_count = sum(min(v, 5) for v in structure_elements.values())
    metrics.structure_score = min(structure_count / 15, 1.0)
    metrics.details["structure_elements"] = structure_elements

    # Specificity score - check for specific instructions
    specificity_indicators = {
        "action_verbs": len(
            re.findall(
                r"\b(generate|create|analyze|list|describe|explain|provide|include)\b",
                expanded_prompt.lower(),
            )
        ),
        "constraints": len(
            re.findall(
                r"\b(must|should|required|at least|maximum|minimum)\b",
                expanded_prompt.lower(),
            )
        ),
        "examples": len(re.findall(r"\b(example|e\.g\.|such as|like)\b", expanded_prompt.lower())),
        "formats": len(
            re.findall(r"\b(format|table|list|json|markdown)\b", expanded_prompt.lower())
        ),
    }

    specificity_count = sum(min(v, 5) for v in specificity_indicators.values())
    metrics.specificity_score = min(specificity_count / 12, 1.0)
    metrics.details["specificity_indicators"] = specificity_indicators

    # Completeness score - check for expected sections
    expected_sections = [
        r"\b(goal|objective|purpose)\b",
        r"\b(section|part|step)\b",
        r"\b(instruction|guideline|rule)\b",
        r"\b(output|result|format)\b",
        r"\b(context|background|information)\b",
    ]

    sections_found = sum(
        1 for pattern in expected_sections if re.search(pattern, expanded_prompt.lower())
    )
    metrics.completeness_score = sections_found / len(expected_sections)
    metrics.details["sections_found"] = sections_found

    # Readability score (simplified Flesch-Kincaid)
    sentences = re.split(r"[.!?]+", expanded_prompt)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = expanded_prompt.split()

    if sentences and words:
        avg_sentence_length = len(words) / len(sentences)
        # Simplified readability (lower is more readable, we normalize)
        # Ideal avg sentence length is 15-20 words
        if 10 <= avg_sentence_length <= 25:
            metrics.readability_score = 1.0
        elif avg_sentence_length < 10:
            metrics.readability_score = avg_sentence_length / 10
        else:
            metrics.readability_score = max(0, 1 - (avg_sentence_length - 25) / 25)

        metrics.details["avg_sentence_length"] = avg_sentence_length
        metrics.details["sentence_count"] = len(sentences)
        metrics.details["word_count"] = len(words)

    # Calculate overall score
    metrics.overall_score = (
        weights["structure"] * metrics.structure_score
        + weights["specificity"] * metrics.specificity_score
        + weights["completeness"] * metrics.completeness_score
        + weights["readability"] * metrics.readability_score
    )

    return metrics


def calculate_retrieval_metrics(
    retrieved_scores: list[float],
    relevant_indices: Optional[list[int]] = None,
    k: int = 5,
) -> RetrievalMetrics:
    """
    Calculate retrieval quality metrics.

    Args:
        retrieved_scores: Similarity scores of retrieved documents.
        relevant_indices: Indices of known relevant documents (for precision/recall).
        k: Number of retrieved documents to consider.

    Returns:
        RetrievalMetrics with calculated scores.

    Example:
        >>> scores = [0.9, 0.8, 0.6, 0.4, 0.3]
        >>> metrics = calculate_retrieval_metrics(scores, relevant_indices=[0, 1, 4])
        >>> print(f"Precision@5: {metrics.precision_at_k:.2f}")
    """
    metrics = RetrievalMetrics()
    metrics.relevance_scores = retrieved_scores[:k]

    if not retrieved_scores:
        return metrics

    # Average score
    metrics.average_score = sum(retrieved_scores[:k]) / min(k, len(retrieved_scores))

    # If we have ground truth labels
    if relevant_indices is not None:
        retrieved_set = set(range(min(k, len(retrieved_scores))))
        relevant_set = set(relevant_indices)

        # Precision at k
        true_positives = len(retrieved_set & relevant_set)
        metrics.precision_at_k = true_positives / k if k > 0 else 0

        # Recall at k
        metrics.recall_at_k = true_positives / len(relevant_set) if relevant_set else 0

        # MRR (Mean Reciprocal Rank)
        for i, idx in enumerate(range(min(k, len(retrieved_scores)))):
            if idx in relevant_set:
                metrics.mrr = 1 / (i + 1)
                break

        # NDCG
        dcg = sum(
            1 / np.log2(i + 2) if i in relevant_set else 0
            for i in range(min(k, len(retrieved_scores)))
        )
        idcg = sum(1 / np.log2(i + 2) for i in range(min(k, len(relevant_set))))
        metrics.ndcg = dcg / idcg if idcg > 0 else 0

    return metrics


def calculate_diversity_score(embeddings: list[list[float]]) -> float:
    """
    Calculate diversity score for a set of embeddings.

    Higher score means more diverse (less similar) results.

    Args:
        embeddings: List of embedding vectors.

    Returns:
        Diversity score (0-1).

    Example:
        >>> embeddings = [[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]]
        >>> score = calculate_diversity_score(embeddings)
        >>> print(f"Diversity: {score:.2f}")
    """
    if len(embeddings) < 2:
        return 1.0

    embeddings_array = np.array(embeddings)

    # Calculate pairwise cosine similarities
    norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
    normalized = embeddings_array / (norms + 1e-9)
    similarity_matrix = np.dot(normalized, normalized.T)

    # Get upper triangle (excluding diagonal)
    upper_triangle = similarity_matrix[np.triu_indices(len(embeddings), k=1)]

    # Diversity is inverse of average similarity
    avg_similarity = np.mean(upper_triangle)
    diversity = 1 - avg_similarity

    return float(diversity)


def calculate_coherence_score(
    prompt: str,
    context_chunks: list[str],
) -> float:
    """
    Calculate coherence between prompt and context.

    Measures how well the expanded prompt relates to the context.

    Args:
        prompt: The expanded prompt.
        context_chunks: List of context strings used for expansion.

    Returns:
        Coherence score (0-1).
    """
    if not context_chunks:
        return 0.0

    prompt_lower = prompt.lower()
    prompt_words = set(re.findall(r"\b\w+\b", prompt_lower))

    # Calculate word overlap with each chunk
    overlaps = []
    for chunk in context_chunks:
        chunk_words = set(re.findall(r"\b\w+\b", chunk.lower()))
        if chunk_words:
            overlap = len(prompt_words & chunk_words) / len(chunk_words)
            overlaps.append(overlap)

    return sum(overlaps) / len(overlaps) if overlaps else 0.0


def compare_embedders(
    texts: list[str],
    queries: list[str],
    embedders: list[Any],
    embedder_names: Optional[list[str]] = None,
) -> dict[str, dict]:
    """
    Compare multiple embedders on the same data.

    Args:
        texts: Documents to embed.
        queries: Queries to test retrieval.
        embedders: List of embedder instances.
        embedder_names: Optional names for embedders.

    Returns:
        Dictionary with comparison results.

    Example:
        >>> from prompt_amplifier.embedders import TFIDFEmbedder, SentenceTransformerEmbedder
        >>> results = compare_embedders(
        ...     texts=["doc1", "doc2"],
        ...     queries=["query1"],
        ...     embedders=[TFIDFEmbedder(), SentenceTransformerEmbedder()],
        ...     embedder_names=["TF-IDF", "Sentence Transformers"]
        ... )
    """
    if embedder_names is None:
        embedder_names = [type(e).__name__ for e in embedders]

    results = {}

    for name, embedder in zip(embedder_names, embedders):
        embedder_results = {
            "embedding_time_ms": 0,
            "query_time_ms": 0,
            "dimension": 0,
            "avg_query_scores": [],
        }

        try:
            # Time embedding
            start = time.time()
            if hasattr(embedder, "fit"):
                embedder.fit(texts)
            doc_result = embedder.embed(texts)
            embedder_results["embedding_time_ms"] = (time.time() - start) * 1000
            embedder_results["dimension"] = doc_result.dimension

            # Time queries
            query_times = []
            for query in queries:
                start = time.time()
                query_result = embedder.embed([query])
                query_times.append((time.time() - start) * 1000)

                # Calculate similarity scores
                query_vec = np.array(query_result.embeddings[0])
                doc_vecs = np.array(doc_result.embeddings)

                # Cosine similarity
                query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-9)
                doc_norms = doc_vecs / (np.linalg.norm(doc_vecs, axis=1, keepdims=True) + 1e-9)
                scores = np.dot(doc_norms, query_norm)

                embedder_results["avg_query_scores"].append(float(np.mean(scores)))

            embedder_results["query_time_ms"] = sum(query_times) / len(query_times)

        except Exception as e:
            embedder_results["error"] = str(e)

        results[name] = embedder_results

    return results


def benchmark_generators(
    prompt: str,
    context: str,
    generators: list[Any],
    generator_names: Optional[list[str]] = None,
    num_runs: int = 1,
) -> dict[str, dict]:
    """
    Benchmark multiple generators on the same prompt.

    Args:
        prompt: The prompt to expand.
        context: Context for expansion.
        generators: List of generator instances.
        generator_names: Optional names for generators.
        num_runs: Number of runs to average.

    Returns:
        Dictionary with benchmark results.

    Example:
        >>> results = benchmark_generators(
        ...     prompt="Summarize the data",
        ...     context="Sales data shows...",
        ...     generators=[openai_gen, anthropic_gen],
        ...     generator_names=["GPT-4", "Claude"]
        ... )
    """
    if generator_names is None:
        generator_names = [type(g).__name__ for g in generators]

    results = {}

    for name, generator in zip(generator_names, generators):
        gen_results = {
            "avg_time_ms": 0,
            "avg_expansion_ratio": 0,
            "avg_quality_score": 0,
            "outputs": [],
        }

        times = []
        expansion_ratios = []
        quality_scores = []

        for _ in range(num_runs):
            try:
                start = time.time()
                output = generator.generate(prompt=prompt, context=context)
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)

                # Calculate metrics
                expansion_ratio = len(output) / len(prompt) if prompt else 0
                expansion_ratios.append(expansion_ratio)

                metrics = calculate_expansion_quality(prompt, output)
                quality_scores.append(metrics.overall_score)

                gen_results["outputs"].append(output[:500] + "..." if len(output) > 500 else output)

            except Exception as e:
                gen_results["error"] = str(e)
                break

        if times:
            gen_results["avg_time_ms"] = sum(times) / len(times)
            gen_results["avg_expansion_ratio"] = sum(expansion_ratios) / len(expansion_ratios)
            gen_results["avg_quality_score"] = sum(quality_scores) / len(quality_scores)

        results[name] = gen_results

    return results


class EvaluationSuite:
    """
    Comprehensive evaluation suite for Prompt Amplifier.

    Example:
        >>> suite = EvaluationSuite()
        >>> suite.add_test_case("deal health", "How's the deal going?", ["relevant doc"])
        >>> results = suite.run(forge)
        >>> suite.print_report(results)
    """

    def __init__(self):
        self.test_cases: list[dict] = []

    def add_test_case(
        self,
        name: str,
        prompt: str,
        relevant_docs: Optional[list[str]] = None,
        expected_keywords: Optional[list[str]] = None,
    ) -> None:
        """Add a test case to the suite."""
        self.test_cases.append(
            {
                "name": name,
                "prompt": prompt,
                "relevant_docs": relevant_docs or [],
                "expected_keywords": expected_keywords or [],
            }
        )

    def run(self, forge: Any) -> list[dict]:
        """Run all test cases against a PromptForge instance."""
        results = []

        for case in self.test_cases:
            result = {
                "name": case["name"],
                "prompt": case["prompt"],
            }

            try:
                # Run expansion
                start = time.time()
                expand_result = forge.expand(case["prompt"])
                elapsed = (time.time() - start) * 1000

                result["time_ms"] = elapsed
                result["expanded_prompt"] = expand_result.prompt
                result["expansion_ratio"] = expand_result.expansion_ratio

                # Calculate quality metrics
                metrics = calculate_expansion_quality(case["prompt"], expand_result.prompt)
                result["quality_metrics"] = metrics.to_dict()

                # Check for expected keywords
                if case["expected_keywords"]:
                    found_keywords = sum(
                        1
                        for kw in case["expected_keywords"]
                        if kw.lower() in expand_result.prompt.lower()
                    )
                    result["keyword_coverage"] = found_keywords / len(case["expected_keywords"])

                result["success"] = True

            except Exception as e:
                result["success"] = False
                result["error"] = str(e)

            results.append(result)

        return results

    def print_report(self, results: list[dict]) -> None:
        """Print a formatted report of results."""
        print("=" * 70)
        print("EVALUATION REPORT")
        print("=" * 70)

        for result in results:
            print(f"\n📝 Test: {result['name']}")
            print(f"   Prompt: {result['prompt'][:50]}...")

            if result["success"]:
                print("   ✅ Success")
                print(f"   ⏱️  Time: {result['time_ms']:.0f}ms")
                print(f"   📊 Expansion: {result['expansion_ratio']:.1f}x")
                print(f"   🎯 Quality: {result['quality_metrics']['overall_score']:.2f}")

                if "keyword_coverage" in result:
                    print(f"   🔑 Keywords: {result['keyword_coverage']:.0%}")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")

        # Summary
        successful = sum(1 for r in results if r["success"])
        print(f"\n{'='*70}")
        print(f"Summary: {successful}/{len(results)} tests passed")

        if successful > 0:
            avg_quality = (
                sum(r["quality_metrics"]["overall_score"] for r in results if r["success"])
                / successful
            )
            avg_expansion = sum(r["expansion_ratio"] for r in results if r["success"]) / successful
            print(f"Average Quality: {avg_quality:.2f}")
            print(f"Average Expansion: {avg_expansion:.1f}x")
