# game_state.py
# Keeps track of everything that changes while the game is being played —
# mistakes, score, which differences have been found, and whether the round is locked.
#
# The GUI never reads or changes these values directly.
# It just calls methods here and lets this class decide what changes.

from .difference import DifferenceRegion
from .constants  import MAX_MISTAKES, NUM_DIFFERENCES


class GameState:
    """
    All the live state for a play session lives here.

    One thing worth noting: total_found is cumulative across all images
    loaded in the same session, while mistakes and locked reset each round.
    """

    def __init__(self) -> None:
        self._differences = []    # the patches for the current image
        self._mistakes    = 0
        self._total_found = 0     # keeps going up across multiple images
        self._locked      = False

    # --- Read-only properties so the GUI can see values but not set them directly ---

    @property
    def mistakes(self) -> int:
        return self._mistakes

    @property
    def total_found(self) -> int:
        return self._total_found

    @property
    def locked(self) -> bool:
        return self._locked

    # --- Round management ---

    def new_round(self, differences: list) -> None:
        """
        Call this when a new image is loaded.
        Resets per-round stuff but keeps the cumulative score going.
        """
        self._differences = differences
        self._mistakes    = 0
        self._locked      = False
        # total_found stays as-is on purpose

    # --- Things that happen during play ---

    def register_find(self, diff: DifferenceRegion) -> None:
        """Player clicked the right spot — mark it found and add to the score."""
        diff.found         = True
        self._total_found += 1

    def register_mistake(self) -> bool:
        """
        Player clicked the wrong spot.
        Returns True if they've hit the mistake limit and we need to lock them out.
        """
        self._mistakes += 1
        if self._mistakes >= MAX_MISTAKES:
            self._locked = True
        return self._locked

    def force_lock(self) -> None:
        """Lock the round without counting a mistake — used when Reveal is pressed."""
        self._locked = True

    # --- Queries the GUI uses to update labels ---

    def remaining(self) -> int:
        """How many differences are still hiding."""
        return sum(1 for d in self._differences if not d.found)

    def unfound(self) -> list:
        """The patch objects the player hasn't found yet."""
        return [d for d in self._differences if not d.found]

    def all_found(self) -> bool:
        """True once every difference has been found."""
        return all(d.found for d in self._differences)

    def find_hit(self, orig_x: int, orig_y: int):
        """
        Check if a click landed on any unfound patch.
        Returns the matching patch, or None if it was a miss.
        """
        for diff in self.unfound():
            if diff.hit_test(orig_x, orig_y):
                return diff
        return None

    def mistakes_remaining(self) -> int:
        """How many more wrong clicks the player is allowed."""
        return MAX_MISTAKES - self._mistakes
