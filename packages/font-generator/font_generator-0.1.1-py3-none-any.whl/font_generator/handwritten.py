"""Module for adding handwritten effects to fonts using FontForge."""

import random

try:
    import fontforge
except ImportError:
    fontforge = None


def make_handwritten(input_font_path, output_font_path, jitter_amount=35, smoothing=15):
    """
    Add a handwritten effect to a font by adding random jitter to glyph points.

    Args:
        input_font_path (str): Path to the input TTF/OTF font file
        output_font_path (str): Path where the output font will be saved
        jitter_amount (int): Range of random movement for points (default: 35)
        smoothing (int): How much to smooth the jagged lines back into curves (default: 15)

    Raises:
        ImportError: If fontforge is not installed
        FileNotFoundError: If input font file doesn't exist
    """
    if fontforge is None:
        raise ImportError(
            "fontforge is required for handwritten font generation. "
            "Please install it: https://fontforge.org/en-US/downloads/"
        )

    print(f"Opening {input_font_path}...")
    font = fontforge.open(input_font_path)

    # 1. FORCE QUADRATIC (Standard for TTF)
    font.is_quadratic = True

    font.fontname += "Handwritten"
    font.familyname += " Handwritten"
    font.fullname += " Handwritten"

    print("Processing glyphs...")

    for glyph in font.glyphs():
        if glyph.foreground.isEmpty():
            continue

        # Unlink references so every character acts independently
        glyph.unlinkRef()

        # 2. POLYGONIZE (The Fix)
        # We turn every point into a "Corner" (On-Curve) point.
        # This effectively turns the letter into a jagged polygon.
        # This prevents "Cubic Spline" errors because lines don't need control points.

        layer = glyph.foreground
        new_layer = fontforge.layer()

        for contour in layer:
            new_contour = fontforge.contour()
            new_contour.closed = contour.closed

            for point in contour:
                dx = random.uniform(-jitter_amount, jitter_amount)
                dy = random.uniform(-jitter_amount, jitter_amount)

                # FIX IS HERE: Use 'True' (Boolean) for the 3rd argument.
                # True = "On Curve" point.
                new_point = fontforge.point(
                    point.x + dx,
                    point.y + dy,
                    True
                )
                new_contour += new_point

            new_layer += new_contour

        glyph.foreground = new_layer

        # 3. RE-SMOOTH
        # Turn the jagged polygon back into a nice curved font
        glyph.simplify(smoothing)

    print(f"Generating {output_font_path}...")
    font.generate(output_font_path)
    print("Done!")
