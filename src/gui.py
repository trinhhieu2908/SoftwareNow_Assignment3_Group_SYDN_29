import tkinter as tk

class SpotTheDifferenceApp(tk.Tk):
    """GUI for Spot The Difference Game."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Spot the Difference")
        self.geometry("980x560")
        self.minsize(860, 500)
        self._build_ui()

    def _build_ui(self) -> None:
        container = tk.Frame(self, padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            container,
            text="Welcome to the Spot the Difference game!",
            font=("Arial", 18, "bold"),
        ).pack(expand=True)


def run_app() -> None:
    app = SpotTheDifferenceApp()
    app.mainloop()

