# constants.py
# Centralised configuration for the Spot the Difference game.
# Change values here to tune gameplay without touching any other file.

# Gameplay 
NUM_DIFFERENCES = 5     # number of differences injected per image
MAX_MISTAKES    = 3     # wrong clicks allowed before the round is locked

# Difference patch size (original-image pixels) 
PATCH_W         = 72
PATCH_H         = 72

# Placement constraints (original-image pixels) 
OVERLAP_MARGIN  = 18    # minimum gap between any two patch edges
EDGE_MARGIN     = 25    # minimum gap between a patch and the image border

# Click detection 
CLICK_TOLERANCE = 46    # hit-radius (px) around the centre of a patch

#Display 
CANVAS_MAX_W    = 560   # maximum canvas width  (display pixels)
CANVAS_MAX_H    = 520   # maximum canvas height (display pixels)

#Colours (Tkinter hex strings)
CIRCLE_FOUND    = "#ff4444"   # red   - player found this difference
CIRCLE_REVEALED = "#4499ff"   # blue  - revealed by the Reveal button
