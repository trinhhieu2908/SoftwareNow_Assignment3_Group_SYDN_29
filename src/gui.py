import tkinter as tk
from tkinter import filedialog, messagebox

class SpotTheDifferenceApp(tk.Tk):
    """GUI for Spot The Difference Game."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Spot the Difference")
        self.geometry("980x560")
        self.minsize(860, 500)
        self._build_ui()

    def _build_ui(self) -> None:
        controls = tk.Frame(self, padx=10, pady=10)
        controls.pack(fill=tk.X)

        tk.Button(controls, text="Load Image", command=self._load_image).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        tk.Button(controls, text="Reveal", command=self._reveal_differences).pack(
            side=tk.LEFT
        )

        status = tk.Frame(self, padx=10)
        status.pack(fill=tk.X, pady=(0, 6))
        tk.Label(status, text="Remaining: 5", font=(None, 14)).pack(side=tk.LEFT)
        tk.Label(status, text="Mistakes: 0 / 3", font=(None, 14)).pack(
            side=tk.LEFT, padx=(20, 0)
        )

        image_row = tk.Frame(self, padx=10, pady=10)
        image_row.pack(fill=tk.BOTH, expand=True)

        left_col = tk.Frame(image_row)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        tk.Label(left_col, text="Original (reference)").pack()
        tk.Label(
            left_col,
            text="No image loaded",
            bg="#2b2b2b",
            fg="#efefef",
            width=46,
            height=20,
        ).pack(fill=tk.BOTH, expand=True)

        right_col = tk.Frame(image_row)
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))
        tk.Label(right_col, text="Modified (click area)").pack()
        tk.Label(
            right_col,
            text="No image loaded",
            bg="#2b2b2b",
            fg="#efefef",
            width=46,
            height=20,
            cursor="crosshair",
        ).pack(fill=tk.BOTH, expand=True)

    def _load_image(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose image",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*"),
            ],
        )
        if path:
            messagebox.showinfo("Spot The Difference", f"Selected image:\n{path}")

    def _reveal_differences(self) -> None:
        messagebox.showinfo("Spot The Difference", "Reveal differences is not implemented yet.")


def run_app() -> None:
    app = SpotTheDifferenceApp()
    app.mainloop()

