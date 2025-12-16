"""TMCP Client CLI - Command-line interface for the TMCP client."""

import asyncio
import sys
from .bridge import main as bridge_main


def main():
    """Main CLI entry point."""
    try:
        asyncio.run(bridge_main())
    except KeyboardInterrupt:
        print("\n🛑 TMCP Client stopped", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"❌ TMCP Client error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
