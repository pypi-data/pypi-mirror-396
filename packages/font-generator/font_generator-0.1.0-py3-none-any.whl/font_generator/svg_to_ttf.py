"""Module for converting SVG files back to TTF font format."""

import os

from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from svgpathtools import svg2paths


def svg_to_ttf(input_folder, base_font_path, output_font, unicode_map=None, default_width=800):
    """
    Convert SVG files back to TTF font format.

    Args:
        input_folder (str): Directory containing SVG files to convert
        base_font_path (str): Path to base font file to use as template
        output_font (str): Path where the output font will be saved
        unicode_map (dict): Optional mapping of glyph names to Unicode values.
                           If None, will use default A-Z mapping.
        default_width (int): Default glyph width for new glyphs (default: 800)

    Raises:
        FileNotFoundError: If input folder or base font doesn't exist
        ValueError: If base font is not valid
    """
    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"Input folder not found: {input_folder}")

    if not os.path.exists(base_font_path):
        raise FileNotFoundError(f"Base font file not found: {base_font_path}")

    # Default Unicode map for A-Z if not provided
    if unicode_map is None:
        unicode_map = {
            "A": 0x0041, "B": 0x0042, "C": 0x0043, "D": 0x0044, "E": 0x0045,
            "F": 0x0046, "G": 0x0047, "H": 0x0048, "I": 0x0049, "J": 0x004A,
            "K": 0x004B, "L": 0x004C, "M": 0x004D, "N": 0x004E, "O": 0x004F,
            "P": 0x0050, "Q": 0x0051, "R": 0x0052, "S": 0x0053, "T": 0x0054,
            "U": 0x0055, "V": 0x0056, "W": 0x0057, "X": 0x0058, "Y": 0x0059,
            "Z": 0x005A,
        }

    # Load base font
    try:
        font = TTFont(base_font_path)
    except Exception as e:
        raise ValueError(f"Failed to load base font: {e}")

    glyf = font["glyf"]
    cmap = font["cmap"].tables[0].cmap
    hmtx = font["hmtx"]

    def svg_to_glyph(svg_path):
        """Convert a single SVG file to a glyph."""
        paths, attributes = svg2paths(svg_path)

        pen = TTGlyphPen(None)

        for path in paths:
            for segment in path:
                start = segment.start
                end = segment.end

                if segment.__class__.__name__ == "Line":
                    pen.lineTo((end.real, end.imag))

                elif segment.__class__.__name__ == "CubicBezier":
                    pen.curveTo(
                        (segment.control1.real, segment.control1.imag),
                        (segment.control2.real, segment.control2.imag),
                        (end.real, end.imag),
                    )

            pen.endPath()

        return pen.glyph()

    # Convert all SVG files into glyphs
    processed_count = 0
    skipped_count = 0

    for filename in os.listdir(input_folder):
        if not filename.endswith(".svg") or filename.startswith("_"):
            continue

        # Extract letter/glyph name from filename
        # Handle formats like "uni0041_A.svg" or "A.svg"
        base_name = filename.replace(".svg", "")
        if "_" in base_name:
            parts = base_name.split("_")
            letter = parts[-1].upper()
        else:
            letter = base_name.upper()

        svg_path = os.path.join(input_folder, filename)

        if letter not in unicode_map:
            print(f"Skipping {filename} (not in Unicode map)")
            skipped_count += 1
            continue

        try:
            print(f"Processing {filename} → Letter: {letter}")
            new_glyph = svg_to_glyph(svg_path)

            glyph_name = letter

            # Insert into glyf table
            glyf[glyph_name] = new_glyph

            # Store width
            hmtx[glyph_name] = (default_width, 0)

            # Map Unicode
            cmap[unicode_map[letter]] = glyph_name
            processed_count += 1
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            skipped_count += 1

    # Save new font
    font.save(output_font)
    print(f"\nFont created successfully!")
    print(f"Processed: {processed_count} glyphs")
    print(f"Skipped: {skipped_count} glyphs")
    print(f"Saved as: {output_font}")
