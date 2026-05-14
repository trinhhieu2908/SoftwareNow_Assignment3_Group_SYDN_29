
# Entry point for the HIT137 Assignment 3 – Spot the Difference game.

from src.app import SpotTheDifferenceApp


def main() -> None:
    """Create the application window and start the Tkinter event loop."""
    app = SpotTheDifferenceApp()
    app.mainloop()


if __name__ == "__main__":
    main()
