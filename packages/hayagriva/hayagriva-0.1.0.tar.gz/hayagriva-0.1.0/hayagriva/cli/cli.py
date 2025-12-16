"""Command line interface for Hayagriva."""
from __future__ import annotations

import argparse
import sys
import os

from hayagriva.core.hayagriva import Hayagriva
from hayagriva.ui.app import launch_ui
from hayagriva.utils.logger import get_logger
from hayagriva.config import HayagrivaConfig

logger = get_logger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hayagriva RAG CLI")
    subparsers = parser.add_subparsers(dest="command")

    # UI Command
    ui_parser = subparsers.add_parser("ui", help="Launch Gradio UI")
    ui_parser.add_argument("--port", type=int, default=7878)
    ui_parser.add_argument("--share", action="store_true", help="Enable Gradio sharing")

    # NEW: backend/model/key support
    ui_parser.add_argument("--backend", type=str, default="groq",
                           choices=["groq", "openai", "local"],
                           help="LLM backend to use")

    ui_parser.add_argument("--api-key", type=str, default=None,
                           help="API key for the selected backend")

    ui_parser.add_argument("--model", type=str, default=None,
                           help="LLM model to use")

    # Ingest command
    ingest_parser = subparsers.add_parser("ingest", help="Ingest text documents")
    ingest_parser.add_argument("paths", nargs="*", help="Paths to text files or directories")

    # Query command
    query_parser = subparsers.add_parser("query", help="Ask a question")
    query_parser.add_argument("question", help="Question to ask the index")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)

    # Handle UI Command -----------------------------------------
    if args.command == "ui":

        # Determine API key if not passed
        api_key = (
            args.api_key
            or os.getenv("GROQ_API_KEY")
            or os.getenv("OPENAI_API_KEY")
        )

        # Default models per backend
        default_model = {
            "groq": "llama-3.1-8b-instant",
            "openai": "gpt-4o-mini",
            "local": "mistral-7b-instruct"
        }[args.backend]

        config = HayagrivaConfig(
            backend=args.backend,
            api_key=api_key,
            model=args.model or default_model,
        )

        rag = Hayagriva(config)
        launch_ui(rag, port=args.port, share=args.share)
        return

    # Handle INGEST Command --------------------------------------
    elif args.command == "ingest":
        if not args.paths:
            logger.error("No paths provided for ingestion")
            sys.exit(1)

        from hayagriva.ingestion.loaders import load_from_paths
        rag = Hayagriva()
        docs = load_from_paths(args.paths)
        rag.add_documents(docs)
        logger.info("Ingested %d documents", len(docs))
        return

    # Handle QUERY Command ---------------------------------------
    elif args.command == "query":
        rag = Hayagriva()
        answer = rag.ask(args.question)
        print(answer)
        return

    # No command given → show help
    else:
        parse_args(["-h"])