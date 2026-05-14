# app.py
# The main window. Builds all the widgets, listens for clicks,
# and updates the display whenever the game state changes.
#
# This class deliberately has no game logic in it — everything
# goes through ImageProcessor and GameState. The GUI just shows
# what those two tell it and passes user actions back to them.

import tkinter as tk
from tkinter import filedialog, messagebox

from .image_processor import ImageProcessor
from .game_state      import GameState
from .difference      import DifferenceRegion
from .constants       import (
    NUM_DIFFERENCES, MAX_MISTAKES,
    CANVAS_MAX_W, CANVAS_MAX_H,
    CIRCLE_FOUND, CIRCLE_REVEALED,
)


class SpotTheDifferenceApp(tk.Tk):
    """
    The application window. Inherits from tk.Tk so it IS the window,
    rather than just containing one.
    """

    # Colours used throughout the UI — change them here if you want a different look
    _C_BG         = "#1c1c2e"
    _C_PANEL      = "#16213e"
    _C_BORDER     = "#0f3460"
    _C_LOAD_BTN   = "#2ecc71"
    _C_REVEAL_BTN = "#e07b39"
    _C_LBL_BLUE   = "#4fc3f7"
    _C_LBL_RED    = "#ef5350"
    _C_LBL_GREEN  = "#66bb6a"
    _C_LBL_GOLD   = "#ffd54f"
    _C_LBL_GREY   = "#90a4ae"
    _C_LEGEND     = "#b0bec5"

    def __init__(self) -> None:
        super().__init__()
        self.title("HIT137 – Spot the Difference")
        self.configure(bg=self._C_BG)
        self.resizable(True, True)

        # The two objects that do all the real work
        self._processor = ImageProcessor()
        self._state     = GameState()

        # We need to hold onto PhotoImage objects or Python's GC will delete them
        # immediately and the canvases will show blank grey squares
        self._scale      = 1.0
        self._photo_orig = None
        self._photo_mod  = None

        self._build_ui()

    # --- Building the UI ---
    # Split into small methods so it's easy to find what you're looking for

    def _build_ui(self) -> None:
        self._build_title_bar()
        self._build_stats_bar()
        self._build_canvas_area()
        self._build_legend()

    def _build_title_bar(self) -> None:
        frame = tk.Frame(self, bg=self._C_BG, pady=10)
        frame.pack(fill="x")

        tk.Label(
            frame, text="Find the Differences",
            font=("Helvetica", 20, "bold"),
            bg=self._C_BG, fg="white",
        ).pack(side="left", padx=18)

        # Shared style for both buttons
        btn_kw = dict(font=("Helvetica", 11, "bold"),
                      relief="flat", padx=14, pady=7, cursor="hand2", bd=0)

        # Reveal is disabled until an image is loaded
        self._reveal_btn = tk.Button(
            frame, text="Reveal All",
            bg=self._C_REVEAL_BTN, fg="black", activebackground="#c96a2a",
            command=self._on_reveal, state="disabled", **btn_kw,
        )
        self._reveal_btn.pack(side="right", padx=8)

        tk.Button(
            frame, text="Load Image",
            bg=self._C_LOAD_BTN, fg="black", activebackground="#27ae60",
            command=self._on_load, **btn_kw,
        ).pack(side="right", padx=4)

    def _build_stats_bar(self) -> None:
        frame = tk.Frame(self, bg=self._C_PANEL, pady=8)
        frame.pack(fill="x")

        # StringVars so we can update label text without recreating widgets
        self._var_remaining = tk.StringVar(value="Remaining: –")
        self._var_mistakes  = tk.StringVar(value=f"Mistakes: 0 / {MAX_MISTAKES}")
        self._var_score     = tk.StringVar(value="Total Found: 0")
        self._var_status    = tk.StringVar(value="Load an image to begin!")

        lbl = dict(font=("Helvetica", 12), bg=self._C_PANEL)
        tk.Label(frame, textvariable=self._var_remaining,
                 fg=self._C_LBL_BLUE,  **lbl).pack(side="left",  padx=20)
        tk.Label(frame, textvariable=self._var_mistakes,
                 fg=self._C_LBL_RED,   **lbl).pack(side="left",  padx=20)
        tk.Label(frame, textvariable=self._var_score,
                 fg=self._C_LBL_GREEN, **lbl).pack(side="left",  padx=20)
        tk.Label(frame, textvariable=self._var_status,
                 font=("Helvetica", 11, "italic"),
                 bg=self._C_PANEL, fg=self._C_LBL_GOLD).pack(side="right", padx=20)

    def _build_canvas_area(self) -> None:
        frame = tk.Frame(self, bg=self._C_BG)
        frame.pack(fill="both", expand=True, padx=12, pady=8)

        hdr = dict(font=("Helvetica", 11, "bold"), bg=self._C_BG, pady=4)

        # Left side — original image, no click handler
        left = tk.Frame(frame, bg=self._C_BG)
        left.pack(side="left", padx=8, expand=True)
        tk.Label(left, text="Original  (reference – do not click)",
                 fg=self._C_LBL_GREY, **hdr).pack()
        self._orig_canvas = tk.Canvas(
            left, bg="#0d0d1a",
            width=CANVAS_MAX_W, height=CANVAS_MAX_H,
            highlightthickness=2, highlightbackground=self._C_BORDER,
        )
        self._orig_canvas.pack()

        # Right side — modified image, click handler attached
        right = tk.Frame(frame, bg=self._C_BG)
        right.pack(side="left", padx=8, expand=True)
        tk.Label(right, text="Modified  (click here to spot differences)",
                 fg=self._C_LBL_BLUE, **hdr).pack()
        self._mod_canvas = tk.Canvas(
            right, bg="#0d0d1a",
            width=CANVAS_MAX_W, height=CANVAS_MAX_H,
            highlightthickness=2, highlightbackground=self._C_LBL_BLUE,
            cursor="crosshair",
        )
        self._mod_canvas.pack()
        self._mod_canvas.bind("<Button-1>", self._on_canvas_click)

    def _build_legend(self) -> None:
        frame = tk.Frame(self, bg=self._C_PANEL, pady=5)
        frame.pack(fill="x")
        tk.Label(
            frame,
            text="  Red circle = found by player        Blue circle = revealed",
            font=("Helvetica", 10), bg=self._C_PANEL, fg=self._C_LEGEND,
        ).pack()

    # --- Event handlers ---

    def _on_load(self) -> None:
        """User clicked Load Image — open a file dialog and start a new round."""
        path = filedialog.askopenfilename(
            title="Choose an image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"),
                       ("All files",   "*.*")],
        )
        if not path:
            return   # user cancelled

        try:
            self._processor.load_image(path)
        except ValueError as exc:
            messagebox.showerror("Load Error", str(exc))
            return

        differences = self._processor.generate_differences()
        self._state.new_round(differences)

        self._scale = self._redraw_canvases()
        self._sync_stats()
        self._reveal_btn.config(state="normal")
        self._var_status.set(
            f"Find all {NUM_DIFFERENCES} differences!   "
            f"(max {MAX_MISTAKES} mistakes)"
        )

    def _on_canvas_click(self, event: tk.Event) -> None:
        """User clicked on the modified image — check if they hit a difference."""
        # Ignore clicks when there's nothing to click on
        if self._state.locked or self._processor.original is None:
            return
        if self._state.all_found():
            return

        # The canvas shows a scaled-down image, so we convert back to original coords
        orig_x = int(event.x / self._scale)
        orig_y = int(event.y / self._scale)

        hit = self._state.find_hit(orig_x, orig_y)

        if hit is not None:
            self._handle_correct_click(hit)
        else:
            self._handle_wrong_click()

    def _on_reveal(self) -> None:
        """User clicked Reveal All — show every unfound difference in blue."""
        if self._processor.original is None:
            return

        unfound = self._state.unfound()
        if not unfound:
            messagebox.showinfo("Nothing to reveal",
                                "You already found all the differences!")
            return

        for diff in unfound:
            diff.found = True   # mark as found but don't award score points
            self._draw_circle(diff, CIRCLE_REVEALED)

        self._state.force_lock()
        self._sync_stats()
        self._var_status.set("Differences revealed.  Load a new image to play again.")

    # --- What happens after a click ---

    def _handle_correct_click(self, diff: DifferenceRegion) -> None:
        """The player hit a difference patch."""
        self._state.register_find(diff)
        self._draw_circle(diff, CIRCLE_FOUND)
        self._sync_stats()

        if self._state.all_found():
            self._var_status.set("All differences found!")
            messagebox.showinfo(
                "Well done!",
                f"You found all {NUM_DIFFERENCES} differences this round!\n\n"
                f"Session total: {self._state.total_found} found.\n\n"
                "Load another image to keep playing.",
            )
        else:
            self._var_status.set(f"Correct!  {self._state.remaining()} left to find.")

    def _handle_wrong_click(self) -> None:
        """The player missed — add a mistake and lock them out if needed."""
        locked = self._state.register_mistake()
        self._sync_stats()

        if locked:
            found_this_round = NUM_DIFFERENCES - self._state.remaining()
            self._var_status.set(
                f"Too many mistakes!  {self._state.remaining()} difference(s) not found."
            )
            messagebox.showwarning(
                "Locked Out",
                f"You made {MAX_MISTAKES} mistakes.\n\n"
                f"You found {found_this_round} / {NUM_DIFFERENCES} "
                f"differences this round.\n\n"
                "Load a new image to restart.",
            )
        else:
            self._var_status.set(
                f"Wrong click!  {self._state.mistakes_remaining()} mistake(s) remaining."
            )

    # --- Display helpers ---

    def _redraw_canvases(self) -> float:
        """
        Scale both images to fit the canvas and draw them.
        Returns the scale factor so we can convert click coordinates later.
        """
        orig_scaled, scale = self._processor.scale_to_fit(self._processor.original)
        mod_scaled,  _     = self._processor.scale_to_fit(self._processor.modified)

        img_h, img_w = orig_scaled.shape[:2]
        for canvas in (self._orig_canvas, self._mod_canvas):
            canvas.config(width=img_w, height=img_h)
            canvas.delete("all")

        # Convert to Tkinter format and store the refs (GC will eat them otherwise)
        self._photo_orig = ImageProcessor.to_photoimage(orig_scaled)
        self._photo_mod  = ImageProcessor.to_photoimage(mod_scaled)

        self._orig_canvas.create_image(0, 0, anchor="nw", image=self._photo_orig)
        self._mod_canvas.create_image( 0, 0, anchor="nw", image=self._photo_mod)

        return scale

    def _draw_circle(self, diff: DifferenceRegion, colour: str) -> None:
        """
        Draw a circle around a patch on both canvases.
        The patch coordinates are in original-image pixels, so we scale them first.
        """
        cx = int((diff.x + diff.width  / 2) * self._scale)
        cy = int((diff.y + diff.height / 2) * self._scale)
        r  = int(max(diff.width, diff.height) / 2 * self._scale) + 7

        for canvas in (self._orig_canvas, self._mod_canvas):
            canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                               outline=colour, width=3)

    def _sync_stats(self) -> None:
        """Refresh the three stat labels at the top to match the current game state."""
        self._var_remaining.set(f"Remaining: {self._state.remaining()}")
        self._var_mistakes.set(f"Mistakes: {self._state.mistakes} / {MAX_MISTAKES}")
        self._var_score.set(f"Total Found: {self._state.total_found}")
