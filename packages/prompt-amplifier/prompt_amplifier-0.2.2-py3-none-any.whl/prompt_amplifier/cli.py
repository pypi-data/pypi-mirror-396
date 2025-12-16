"""Command-line interface for Prompt Amplifier."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Optional


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        prog="prompt-amplifier",
        description="Transform short prompts into detailed, structured instructions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Expand a prompt
  prompt-amplifier expand "How's the deal going?"

  # Expand with context from files
  prompt-amplifier expand "Summarize" --docs ./docs/

  # Search without expansion
  prompt-amplifier search "customer satisfaction" --docs ./docs/

  # Compare embedders
  prompt-amplifier compare-embedders --docs ./docs/

  # Run evaluation
  prompt-amplifier evaluate --docs ./docs/
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Expand command
    expand_parser = subparsers.add_parser("expand", help="Expand a short prompt")
    expand_parser.add_argument("prompt", help="The short prompt to expand")
    expand_parser.add_argument("--docs", "-d", help="Path to documents directory")
    expand_parser.add_argument("--texts", "-t", nargs="+", help="Text strings to use as context")
    expand_parser.add_argument(
        "--embedder",
        "-e",
        choices=["tfidf", "bm25", "sentence-transformers", "openai", "google"],
        default="tfidf",
        help="Embedder to use (default: tfidf)",
    )
    expand_parser.add_argument(
        "--generator",
        "-g",
        choices=["openai", "anthropic", "google", "ollama"],
        default="openai",
        help="Generator to use (default: openai)",
    )
    expand_parser.add_argument("--model", "-m", help="Model name for generator")
    expand_parser.add_argument(
        "--top-k", "-k", type=int, default=5, help="Number of context chunks"
    )
    expand_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search documents without expansion")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--docs", "-d", help="Path to documents directory")
    search_parser.add_argument("--texts", "-t", nargs="+", help="Text strings to search")
    search_parser.add_argument("--top-k", "-k", type=int, default=5, help="Number of results")
    search_parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")

    # Compare embedders command
    compare_parser = subparsers.add_parser("compare-embedders", help="Compare different embedders")
    compare_parser.add_argument("--docs", "-d", help="Path to documents directory")
    compare_parser.add_argument("--texts", "-t", nargs="+", help="Text strings to use")
    compare_parser.add_argument("--queries", "-q", nargs="+", help="Test queries")

    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Run evaluation suite")
    eval_parser.add_argument("--docs", "-d", help="Path to documents directory")
    eval_parser.add_argument("--prompts", "-p", nargs="+", help="Test prompts")

    # Version command
    subparsers.add_parser("version", help="Show version")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    if args.command == "version":
        from prompt_amplifier import __version__

        print(f"prompt-amplifier {__version__}")
        return

    if args.command == "expand":
        run_expand(args)
    elif args.command == "search":
        run_search(args)
    elif args.command == "compare-embedders":
        run_compare_embedders(args)
    elif args.command == "evaluate":
        run_evaluate(args)


def get_embedder(name: str):
    """Get embedder instance by name."""
    if name == "tfidf":
        from prompt_amplifier.embedders import TFIDFEmbedder

        return TFIDFEmbedder()
    elif name == "bm25":
        from prompt_amplifier.embedders import BM25Embedder

        return BM25Embedder()
    elif name == "sentence-transformers":
        from prompt_amplifier.embedders import SentenceTransformerEmbedder

        return SentenceTransformerEmbedder()
    elif name == "openai":
        from prompt_amplifier.embedders import OpenAIEmbedder

        return OpenAIEmbedder()
    elif name == "google":
        from prompt_amplifier.embedders import GoogleEmbedder

        return GoogleEmbedder()
    else:
        raise ValueError(f"Unknown embedder: {name}")


def run_expand(args):
    """Run expand command."""
    from prompt_amplifier import PromptForge
    from prompt_amplifier.core.config import GeneratorConfig, PromptForgeConfig

    # Build config
    config = PromptForgeConfig(
        generator=GeneratorConfig(
            provider=args.generator,
            model=args.model if args.model else None,
        ),
        top_k=args.top_k,
    )

    # Get embedder
    embedder = get_embedder(args.embedder)

    # Create forge
    forge = PromptForge(config=config, embedder=embedder)

    # Load documents
    if args.docs:
        forge.load_documents(args.docs)
    if args.texts:
        forge.add_texts(args.texts)

    if forge.chunk_count == 0:
        print(
            "Error: No documents loaded. Use --docs or --texts to provide context.", file=sys.stderr
        )
        sys.exit(1)

    # Expand
    try:
        result = forge.expand(args.prompt)

        if args.json:
            output = {
                "original": args.prompt,
                "expanded": result.prompt,
                "expansion_ratio": result.expansion_ratio,
                "retrieval_time_ms": result.retrieval_time_ms,
                "generation_time_ms": result.generation_time_ms,
            }
            print(json.dumps(output, indent=2))
        else:
            print("=" * 60)
            print("EXPANDED PROMPT")
            print("=" * 60)
            print(result.prompt)
            print()
            print(f"📊 Expansion: {result.expansion_ratio:.1f}x")
            print(f"⏱️  Retrieval: {result.retrieval_time_ms:.0f}ms")
            print(f"⏱️  Generation: {result.generation_time_ms:.0f}ms")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def run_search(args):
    """Run search command."""
    from prompt_amplifier import PromptForge

    forge = PromptForge()

    # Load documents
    if args.docs:
        forge.load_documents(args.docs)
    if args.texts:
        forge.add_texts(args.texts)

    if forge.chunk_count == 0:
        print("Error: No documents loaded.", file=sys.stderr)
        sys.exit(1)

    # Search
    results = forge.search(args.query, k=args.top_k)

    if args.json:
        output = [
            {
                "score": r.score,
                "content": r.chunk.content,
                "source": r.chunk.metadata.get("source", ""),
            }
            for r in results
        ]
        print(json.dumps(output, indent=2))
    else:
        print(f"Search results for: '{args.query}'")
        print("=" * 60)
        for i, r in enumerate(results):
            print(f"\n{i+1}. [{r.score:.3f}]")
            print(f"   {r.chunk.content[:200]}...")


def run_compare_embedders(args):
    """Run embedder comparison."""
    from prompt_amplifier.embedders import TFIDFEmbedder
    from prompt_amplifier.evaluation import compare_embedders

    texts = args.texts or ["Sample document 1", "Sample document 2", "Sample document 3"]
    queries = args.queries or ["test query"]

    embedders = [TFIDFEmbedder()]
    names = ["TF-IDF"]

    try:
        from prompt_amplifier.embedders import SentenceTransformerEmbedder

        embedders.append(SentenceTransformerEmbedder())
        names.append("Sentence Transformers")
    except ImportError:
        pass

    results = compare_embedders(texts, queries, embedders, names)

    print("Embedder Comparison")
    print("=" * 60)
    for name, data in results.items():
        print(f"\n{name}:")
        if "error" in data:
            print(f"  Error: {data['error']}")
        else:
            print(f"  Dimension: {data['dimension']}")
            print(f"  Embedding time: {data['embedding_time_ms']:.1f}ms")
            print(f"  Query time: {data['query_time_ms']:.1f}ms")


def run_evaluate(args):
    """Run evaluation suite."""
    from prompt_amplifier import PromptForge
    from prompt_amplifier.evaluation import EvaluationSuite

    forge = PromptForge()

    # Load documents
    if args.docs:
        forge.load_documents(args.docs)
    else:
        forge.add_texts(
            [
                "POC Health: Healthy means all milestones on track.",
                "Key metrics: Winscore 0-100, Feature fit percentage.",
            ]
        )

    # Create evaluation suite
    suite = EvaluationSuite()

    prompts = args.prompts or ["How's the deal going?", "Check project status", "Summarize metrics"]

    for i, prompt in enumerate(prompts):
        suite.add_test_case(f"Test {i+1}", prompt)

    # Run and report
    results = suite.run(forge)
    suite.print_report(results)


if __name__ == "__main__":
    main()
