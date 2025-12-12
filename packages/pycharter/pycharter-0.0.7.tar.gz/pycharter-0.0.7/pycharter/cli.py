"""
Main CLI entry point for pycharter commands.

Provides commands like:
- pycharter db init
- pycharter db upgrade
- etc.
"""

import argparse
import os
import sys
from pathlib import Path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PyCharter - Data Contract Management and Validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # db subcommand
    db_parser = subparsers.add_parser("db", help="Database management commands")
    db_subparsers = db_parser.add_subparsers(dest="db_command", help="Database command")

    # Import db CLI commands
    from pycharter.db.cli import (
        cmd_current,
        cmd_downgrade,
        cmd_history,
        cmd_init,
        cmd_seed,
        cmd_stamp,
        cmd_truncate,
        cmd_upgrade,
    )

    # init
    init_parser = db_subparsers.add_parser(
        "init",
        help="Initialize database schema from scratch (auto-detects database type from connection string)",
    )
    init_parser.add_argument(
        "database_url",
        nargs="?",
        help="Database connection string (optional if configured)",
    )
    init_parser.add_argument(
        "--db",
        "--database-type",
        dest="db_type",
        choices=["postgresql", "postgres", "mongodb", "sqlite"],
        default=None,
        help="Database type (auto-detected from connection string if not provided)",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Proceed even if database appears initialized",
    )

    # upgrade
    upgrade_parser = db_subparsers.add_parser(
        "upgrade", help="Upgrade database to latest revision"
    )
    upgrade_parser.add_argument(
        "database_url",
        nargs="?",
        help="PostgreSQL connection string (optional if PYCHARTER_DATABASE_URL is set)",
    )
    upgrade_parser.add_argument(
        "--revision", default="head", help="Target revision (default: head)"
    )

    # downgrade
    downgrade_parser = db_subparsers.add_parser(
        "downgrade", help="Downgrade database to a previous revision"
    )
    downgrade_parser.add_argument(
        "database_url",
        nargs="?",
        help="PostgreSQL connection string (optional if PYCHARTER_DATABASE_URL is set)",
    )
    downgrade_parser.add_argument(
        "--revision", default="-1", help="Target revision (default: -1)"
    )

    # current
    current_parser = db_subparsers.add_parser(
        "current", help="Show current database revision"
    )
    current_parser.add_argument(
        "database_url",
        nargs="?",
        help="PostgreSQL connection string (optional if PYCHARTER_DATABASE_URL is set)",
    )

    # history
    history_parser = db_subparsers.add_parser("history", help="Show migration history")
    history_parser.add_argument(
        "database_url",
        nargs="?",
        help="PostgreSQL connection string (optional if PYCHARTER_DATABASE_URL is set)",
    )

    # stamp
    stamp_parser = db_subparsers.add_parser(
        "stamp",
        help="Stamp database with a specific revision (without running migrations)",
    )
    stamp_parser.add_argument(
        "revision", nargs="?", default="head", help="Revision to stamp (default: head)"
    )
    stamp_parser.add_argument(
        "database_url",
        nargs="?",
        help="PostgreSQL connection string (optional if PYCHARTER_DATABASE_URL is set)",
    )

    # seed
    seed_parser = db_subparsers.add_parser(
        "seed", help="Seed database with initial data from YAML files"
    )
    seed_parser.add_argument(
        "seed_dir",
        nargs="?",
        help="Directory containing seed YAML files (default: data/seed)",
    )
    seed_parser.add_argument(
        "database_url",
        nargs="?",
        help="PostgreSQL connection string (optional if PYCHARTER_DATABASE_URL is set)",
    )

    # truncate
    truncate_parser = db_subparsers.add_parser(
        "truncate", help="Truncate all PyCharter database tables (clear all data)"
    )
    truncate_parser.add_argument(
        "database_url",
        nargs="?",
        help="PostgreSQL connection string (optional if PYCHARTER_DATABASE_URL is set)",
    )
    truncate_parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt (use with caution)",
    )

    # api subcommand
    api_parser = subparsers.add_parser("api", help="Start the API server")
    api_parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
    )
    api_parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind to (default: 8000)"
    )
    api_parser.add_argument(
        "--reload",
        action="store_true",
        default=True,
        help="Enable auto-reload (default: True)",
    )
    api_parser.add_argument(
        "--no-reload", dest="reload", action="store_false", help="Disable auto-reload"
    )

    # ui subcommand
    ui_parser = subparsers.add_parser("ui", help="UI management commands")
    ui_subparsers = ui_parser.add_subparsers(dest="ui_command", help="UI command")

    # ui serve
    ui_serve_parser = ui_subparsers.add_parser(
        "serve", help="Serve the built UI (production mode)"
    )
    ui_serve_parser.add_argument(
        "--api-url",
        type=str,
        default=None,
        help="URL of the PyCharter API (default: http://localhost:8000 or PYCHARTER_API_URL env var)",
    )
    ui_serve_parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    ui_serve_parser.add_argument(
        "--port", type=int, default=3000, help="Port to bind to (default: 3000)"
    )

    # ui dev
    ui_dev_parser = ui_subparsers.add_parser("dev", help="Run UI development server")
    ui_dev_parser.add_argument(
        "--api-url",
        type=str,
        default=None,
        help="URL of the PyCharter API (default: http://localhost:8000 or PYCHARTER_API_URL env var)",
    )
    ui_dev_parser.add_argument(
        "--port",
        type=int,
        default=3000,
        help="Port to run dev server on (default: 3000)",
    )

    # ui build
    ui_build_parser = ui_subparsers.add_parser(
        "build", help="Build the UI for production"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "db":
        if not args.db_command:
            db_parser.print_help()
            return 1

        if args.db_command == "init":
            return cmd_init(args.database_url, db_type=args.db_type, force=args.force)
        elif args.db_command == "upgrade":
            return cmd_upgrade(args.database_url, args.revision)
        elif args.db_command == "downgrade":
            return cmd_downgrade(args.database_url, args.revision)
        elif args.db_command == "current":
            return cmd_current(args.database_url)
        elif args.db_command == "history":
            return cmd_history(args.database_url)
        elif args.db_command == "stamp":
            return cmd_stamp(args.database_url, args.revision)
        elif args.db_command == "seed":
            return cmd_seed(args.seed_dir, args.database_url)
        elif args.db_command == "truncate":
            return cmd_truncate(args.database_url, force=args.force)
        else:
            db_parser.print_help()
            return 1
    elif args.command == "api":
        try:
            import uvicorn  # type: ignore[import-not-found,import-untyped]
        except ImportError:
            print("❌ Error: uvicorn is required for API server.", file=sys.stderr)
            print("   Install with: pip install pycharter[api]", file=sys.stderr)
            return 1

        uvicorn.run(
            "api.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
        )
        return 0
    elif args.command == "ui":
        if not args.ui_command:
            ui_parser.print_help()
            return 1

        # Add ui directory to path if it exists
        # Try to find ui directory in multiple locations:
        # 1. Installed package location (when installed from pip)
        # 2. Development locations (when running from source)
        ui_path = None
        possible_paths = []

        # Check installed package location first (for pip installs)
        try:
            import pycharter
            pycharter_path = Path(pycharter.__file__).parent.parent
            package_ui = pycharter_path / "ui"
            possible_paths.append(package_ui)
        except (ImportError, AttributeError):
            pass

        # Check development locations
        possible_paths.extend([
            Path(__file__).parent.parent.parent
            / "ui",  # From pycharter/cli.py -> pycharter -> project root -> ui
            Path.cwd() / "ui",  # Current working directory
            Path(__file__).parent.parent / "ui",  # Alternative path
        ])

        for path in possible_paths:
            if path.exists() and (path / "server.py").exists():
                ui_path = path
                break

        if not ui_path:
            print("❌ Error: UI directory not found.", file=sys.stderr)
            print(
                "   If installed from pip: UI should be included in the package.",
                file=sys.stderr,
            )
            print(
                "   If in development: Make sure you're running from the PyCharter project root.",
                file=sys.stderr,
            )
            print(
                "   Or install the UI dependencies: cd ui && npm install",
                file=sys.stderr,
            )
            return 1

        # Add ui directory to Python path
        if str(ui_path) not in sys.path:
            sys.path.insert(0, str(ui_path))

        if args.ui_command == "serve":
            import importlib.util

            server_path = ui_path / "server.py"
            spec = importlib.util.spec_from_file_location("server", server_path)
            if spec and spec.loader:
                server_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(server_module)
                server_module.serve_ui(
                    api_url=args.api_url, host=args.host, port=args.port
                )
            return 0
        elif args.ui_command == "dev":
            import importlib.util

            dev_path = ui_path / "dev.py"
            spec = importlib.util.spec_from_file_location("dev", dev_path)
            if spec and spec.loader:
                dev_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(dev_module)
                dev_module.run_dev_server(api_url=args.api_url, port=args.port)
            return 0
        elif args.ui_command == "build":
            import importlib.util

            build_path = ui_path / "build.py"
            spec = importlib.util.spec_from_file_location("build", build_path)
            if spec and spec.loader:
                build_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(build_module)
                return build_module.build_ui()
            return 1
        else:
            ui_parser.print_help()
            return 1
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
