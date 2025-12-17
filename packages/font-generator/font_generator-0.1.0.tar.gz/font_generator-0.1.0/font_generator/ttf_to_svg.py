"""Module for converting TTF fonts to SVG format."""

import os
import json

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont


def ttf_to_svg(font_path, output_dir):
    """
    Convert a TTF/OTF font file to individual SVG files for each glyph.

    Args:
        font_path (str): Path to the input TTF/OTF font file
        output_dir (str): Directory where SVG files will be saved

    Raises:
        FileNotFoundError: If font file doesn't exist
        ValueError: If file is not a valid font file
        IOError: If there's an error reading the font file
    """
    # Check if file exists
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font file not found: {font_path}")

    # Check if file is actually a font file by reading first few bytes
    try:
        with open(font_path, 'rb') as f:
            header = f.read(4)
            # TTF files start with specific signatures
            # TrueType: 0x00010000 or 'OTTO' for OpenType
            # Check for ZIP signature (PK) which indicates it's not a valid font
            if header[:2] == b'PK':
                raise ValueError(
                    f"File '{font_path}' appears to be a ZIP archive, not a font file. "
                    f"Please ensure you have a valid TTF or OTF font file."
                )
            # Check for valid font signatures
            if header != b'\x00\x01\x00\x00' and header != b'OTTO':
                # Try to read more to check for other formats
                f.seek(0)
                more_data = f.read(12)
                if more_data[:4] != b'\x00\x01\x00\x00' and more_data[:4] != b'OTTO':
                    raise ValueError(
                        f"File '{font_path}' does not appear to be a valid TrueType or OpenType font. "
                        f"Expected font signature, but found: {header.hex()}"
                    )
    except (IOError, OSError) as e:
        raise IOError(f"Error reading font file '{font_path}': {e}")

    # Load the font
    try:
        font = TTFont(font_path)
    except Exception as e:
        raise ValueError(
            f"Failed to load font from '{font_path}'. "
            f"The file may be corrupted or not a valid font file. "
            f"Original error: {e}"
        )
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Invert mapping to find glyph name by character code
    cmap_reversed = {v: k for k, v in cmap.items()}

    print(f"Extracting glyphs from {font_path}...")

    extracted_count = 0
    skipped_count = 0
    units_per_em = font['head'].unitsPerEm
    # Reasonable max width (typically fonts have widths < 2000 units)
    max_reasonable_width = units_per_em * 3

    # Initialize metadata dictionary to store font info and glyph metrics
    metadata = {
        'fontname': 'Unknown',
        'familyname': 'Unknown',
        'fullname': 'Unknown',
        'version': 'Version 1.0',
        'units_per_em': units_per_em,
        'ascent': units_per_em * 0.8,
        'descent': -units_per_em * 0.2,
        'linegap': 0,
        'glyph_metrics': {}
    }

    # Extract metrics from hhea table
    if 'hhea' in font:
        metadata['ascent'] = font['hhea'].ascent
        metadata['descent'] = font['hhea'].descent
        metadata['linegap'] = font['hhea'].lineGap

    for glyph_name in font.getGlyphOrder():
        # Skip empty glyphs
        if glyph_name not in glyph_set:
            skipped_count += 1
            continue

        # Check glyph advance width - skip invalid/abnormal widths
        try:
            # Get advance width from hmtx table if available
            if 'hmtx' in font:
                advance_width = font['hmtx'].metrics.get(glyph_name, (0, 0))[0]
                # Skip glyphs with invalid widths:
                # - 65535 (0xFFFF) is often used as error/invalid marker (unsigned -1)
                # - Very large widths are likely errors
                if advance_width >= 65535 or advance_width > max_reasonable_width:
                    skipped_count += 1
                    continue
        except (KeyError, AttributeError, IndexError):
            # If we can't check width, continue anyway (glyph might be valid)
            pass

        # Create SVG Path
        pen = SVGPathPen(glyph_set)

        # Mukta/Devanagari glyphs might need scaling/flipping depending on the tool
        # This grabs the raw outline
        try:
            glyph_set[glyph_name].draw(pen)
        except Exception as e:
            print(f"Skipping {glyph_name}: {e}")
            skipped_count += 1
            continue

        path_data = pen.getCommands()

        if not path_data:
            skipped_count += 1
            continue

        # Save glyph metrics (width, bearings) before determining filename
        glyph_width = 0
        left_bearing = 0
        if 'hmtx' in font:
            metrics = font['hmtx'].metrics.get(glyph_name, (0, 0))
            glyph_width = metrics[0]
            left_bearing = metrics[1]
            metadata['glyph_metrics'][glyph_name] = {
                'width': glyph_width,
                'left_bearing': left_bearing
            }

        # Determine filename (use Unicode char if available, else glyph name)
        unicode_val = cmap_reversed.get(glyph_name)
        if unicode_val:
            # Use 4-digit hex for standard Unicode, but handle longer sequences
            filename = f"uni{unicode_val:04X}_{glyph_name}.svg"
            # Also store Unicode mapping for metrics lookup
            if glyph_name not in metadata['glyph_metrics']:
                metadata['glyph_metrics'][glyph_name] = {'width': glyph_width, 'left_bearing': left_bearing}
            metadata['glyph_metrics'][f'U+{unicode_val:04X}'] = metadata['glyph_metrics'][glyph_name]
        else:
            # For glyphs without Unicode mapping, use the glyph name
            # Ensure filename is safe (no special characters)
            safe_name = glyph_name.replace(".", "_").replace(" ", "_")
            filename = f"{safe_name}.svg"

        # Create SVG content
        # ViewBox logic usually requires analyzing font metrics (unitsPerEm)
        # For Mukta, typical upm is 1000 or 2048. We set a standard viewbox.
        # Note: TTF coordinates have (0,0) at bottom-left, SVG is top-left.
        # Simple extraction puts it upside down without a transform flip.
        # This output keeps raw path data which might look flipped in standard viewers
        # until imported back into a font editor.

        svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -{units_per_em} {units_per_em} {2 * units_per_em}">
  <path d="{path_data}" transform="scale(1, -1)" fill="black" />
</svg>"""

        try:
            with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
                f.write(svg_content)
            extracted_count += 1
        except Exception as e:
            print(f"Error writing {filename}: {e}")
            skipped_count += 1

    # Extract name table entries (after loop, so we have all glyph metrics)
    try:
        name_table = font.get('name')
        if name_table:
            for record in name_table.names:
                if record.nameID == 1:  # Family name
                    metadata['familyname'] = record.toUnicode()
                elif record.nameID == 4:  # Full name
                    metadata['fullname'] = record.toUnicode()
                elif record.nameID == 6:  # PostScript name
                    metadata['fontname'] = record.toUnicode()
                elif record.nameID == 5:  # Version
                    metadata['version'] = record.toUnicode()
    except Exception as e:
        print(f"Warning: Could not extract all name table entries: {e}")

    # Save OpenType feature tables (GSUB/GPOS) - these are critical for Devanagari
    # We'll save the original font file path so we can copy these tables later
    metadata['original_font_path'] = font_path

    # Check if GSUB/GPOS tables exist
    has_gsub = 'GSUB' in font
    has_gpos = 'GPOS' in font
    metadata['has_gsub'] = has_gsub
    metadata['has_gpos'] = has_gpos

    print(f"\nOpenType features: GSUB={has_gsub}, GPOS={has_gpos}")

    # Save metadata to JSON file
    metadata_file = os.path.join(output_dir, '_font_metadata.json')
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\nExtraction complete!")
    print(f"Extracted: {extracted_count} glyphs")
    print(f"Skipped: {skipped_count} glyphs")
    print(f"Font metadata saved to: {metadata_file}")
    print(f"Check the '{output_dir}' folder.")
