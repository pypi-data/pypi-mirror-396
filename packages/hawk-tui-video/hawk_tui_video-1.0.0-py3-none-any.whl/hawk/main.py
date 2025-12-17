"""Hawk TUI entry point."""

from hawk.app import HawkTUI


def main():
    """Main entry point."""
    app = HawkTUI()
    app.run()


if __name__ == "__main__":
    main()
