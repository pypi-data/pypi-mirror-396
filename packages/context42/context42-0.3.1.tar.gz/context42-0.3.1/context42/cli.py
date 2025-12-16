"""CLI for Context42 MCP server with CLaRa support."""

import argparse

# Check if CLaRa dependencies are available
CLARA_AVAILABLE = False
try:
    from .clara import CLaRaConfig, ModelManager, CLARA_AVAILABLE as _CA

    CLARA_AVAILABLE = _CA
except ImportError:
    pass


def _get_manager():
    """Get ModelManager instance if CLaRa is available."""
    if not CLARA_AVAILABLE:
        return None
    config = CLaRaConfig()
    return ModelManager(config)


def main():
    """CLI entry point for Context42."""
    parser = argparse.ArgumentParser(description="Context42 MCP Server")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # serve command (default)
    serve_parser = subparsers.add_parser("serve", help="Start MCP server")
    serve_parser.add_argument("--model", default=None, help="Model to use")
    serve_parser.add_argument("--preload", action="store_true", help="Preload model")
    serve_parser.add_argument(
        "--fallback", action="store_true", help="Keyword-only mode"
    )

    # mcp command
    mcp_parser = subparsers.add_parser("mcp", help="Run MCP server directly")
    mcp_parser.add_argument("--model", default=None, help="Model to use")
    mcp_parser.add_argument("--preload", action="store_true", help="Preload model")
    mcp_parser.add_argument("--fallback", action="store_true", help="Keyword-only mode")

    # download command
    download_parser = subparsers.add_parser("download", help="Download CLaRa model")
    download_parser.add_argument(
        "--model", default="clara-7b-instruct-16", help="Model to download"
    )
    download_parser.add_argument(
        "--force", action="store_true", help="Force re-download"
    )

    # models command
    models_parser = subparsers.add_parser("models", help="List available models")
    models_parser.add_argument(
        "--local", action="store_true", help="Show only downloaded models"
    )

    # remove command
    remove_parser = subparsers.add_parser("remove", help="Remove downloaded model")
    remove_parser.add_argument("model", help="Model name to remove")

    # info command
    info_parser = subparsers.add_parser("info", help="Show model information")
    info_parser.add_argument("model", help="Model name")

    args = parser.parse_args()

    # Handle commands
    if args.command in ("serve", None):
        from .server import main as serve_main

        serve_main()
    elif args.command == "mcp":
        from .server import main as serve_main

        serve_main()
    elif args.command == "download":
        if not CLARA_AVAILABLE:
            print("CLaRa model download requires: pip install context42[clara]")
            print("Available models:")
            print("  clara-7b-instruct-16 (16× compression, ~14GB)")
            print("  clara-7b-instruct-128 (128× compression, ~14GB)")
            print("  clara-7b-base-16 (base model, ~14GB)")
            print("  clara-7b-e2e-16 (end-to-end trained, ~14GB)")
        else:
            manager = _get_manager()
            print(f"Downloading model: {args.model}")
            result = manager.download(args.model, force=args.force)
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Status: {result['status']}")
                if "path" in result:
                    print(f"Path: {result['path']}")
    elif args.command == "models":
        print("Available models:")
        print("  clara-7b-instruct-16 (16× compression, ~14GB)")
        print("  clara-7b-instruct-128 (128× compression, ~14GB)")
        print("  clara-7b-base-16 (base model, ~14GB)")
        print("  clara-7b-e2e-16 (end-to-end trained, ~14GB)")
        if args.local:
            print("\nDownloaded models:")
            if CLARA_AVAILABLE:
                manager = _get_manager()
                config = CLaRaConfig()
                found = False
                for model_name in config.MODELS:
                    model_path = config.model_path / model_name
                    if model_path.exists():
                        print(f"  {model_name}")
                        found = True
                if not found:
                    print("  (none)")
            else:
                print("  Install with: pip install context42[clara]")
    elif args.command == "remove":
        if not CLARA_AVAILABLE:
            print("CLaRa model management requires: pip install context42[clara]")
        else:
            manager = _get_manager()
            print(f"Removing model: {args.model}")
            result = manager.remove(args.model)
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(f"Status: {result['status']}")
                if result["status"] == "removed":
                    print(f"Removed from: {result['path']}")
    elif args.command == "info":
        model_info = {
            "clara-7b-instruct-16": {
                "description": "Instruction-tuned model with 16× compression",
                "size": "~14GB",
                "use_case": "General Q&A, recommended for most users",
            },
            "clara-7b-instruct-128": {
                "description": "Instruction-tuned model with 128× compression",
                "size": "~14GB",
                "use_case": "Large document corpus search",
            },
            "clara-7b-base-16": {
                "description": "Base model with 16× compression",
                "size": "~14GB",
                "use_case": "Custom fine-tuning",
            },
            "clara-7b-e2e-16": {
                "description": "End-to-end trained model with 16× compression",
                "size": "~14GB",
                "use_case": "Multi-document RAG, complex reasoning",
            },
        }

        if args.model in model_info:
            info = model_info[args.model]
            print(f"Model: {args.model}")
            print(f"  Description: {info['description']}")
            print(f"  Size: {info['size']}")
            print(f"  Best for: {info['use_case']}")
        else:
            print(f"Unknown model: {args.model}")
            print("Use 'context42 models' to see available models.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
