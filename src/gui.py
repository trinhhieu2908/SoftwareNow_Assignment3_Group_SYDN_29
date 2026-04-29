import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class SpotTheDifferenceApp(tk.Tk):
    """GUI for Spot The Difference Game."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Spot the Difference")
        self.geometry("980x560")
        self.minsize(860, 500)
        self._left_image_label: tk.Label | None = None
        self._right_image_label: tk.Label | None = None
        self._left_photo: ImageTk.PhotoImage | None = None
        self._right_photo: ImageTk.PhotoImage | None = None
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
        self._left_image_label = tk.Label(
            left_col,
            text="No image loaded",
            bg="#2b2b2b",
            fg="#efefef",
            width=46,
            height=20,
        )
        self._left_image_label.pack(fill=tk.BOTH, expand=True)

        right_col = tk.Frame(image_row)
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))
        tk.Label(right_col, text="Modified (click area)").pack()
        self._right_image_label = tk.Label(
            right_col,
            text="No image loaded",
            bg="#2b2b2b",
            fg="#efefef",
            width=46,
            height=20,
            cursor="crosshair",
        )
        self._right_image_label.pack(fill=tk.BOTH, expand=True)

    def _load_image(self) -> None:
        path = filedialog.askopenfilename(
            title="Choose image",
            filetypes=[
                ("Images", "*.jpg *.jpeg *.png *.bmp"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        try:
            image = Image.open(path).convert("RGB")
        except OSError as exc:
            messagebox.showerror("Spot The Difference", f"Could not load image:\n{exc}")
            return

        if self._left_image_label is None or self._right_image_label is None:
            return

        self.update_idletasks()
        left_size = (
            max(80, self._left_image_label.winfo_width()),
            max(80, self._left_image_label.winfo_height()),
        )
        right_size = (
            max(80, self._right_image_label.winfo_width()),
            max(80, self._right_image_label.winfo_height()),
        )

        left_preview = self._fit_image(image, left_size)
        right_preview = self._fit_image(image, right_size)

        self._left_photo = ImageTk.PhotoImage(left_preview)
        self._right_photo = ImageTk.PhotoImage(right_preview)

        self._left_image_label.config(image=self._left_photo, text="")
        self._right_image_label.config(image=self._right_photo, text="")

    @staticmethod
    def _fit_image(image: Image.Image, box_size: tuple[int, int]) -> Image.Image:
        out = image.copy()
        out.thumbnail(box_size, Image.Resampling.LANCZOS)
        return out

    def _reveal_differences(self) -> None:
        messagebox.showinfo("Spot The Difference", "Reveal differences is not implemented yet.")


def run_app() -> None:
    app = SpotTheDifferenceApp()
    app.mainloop()

