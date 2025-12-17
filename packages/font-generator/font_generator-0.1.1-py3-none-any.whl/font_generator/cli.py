"""Command-line interface for font-generator."""

import argparse
import sys


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description='Font Generator - Tools for font manipulation and conversion',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
          # Convert TTF to SVG
          font-generator ttf-to-svg input.ttf output_dir/
        
          # Convert SVG to TTF
          font-generator svg-to-ttf svg_dir/ base.ttf output.ttf
        
          # Add handwritten effect to font
          font-generator handwritten input.ttf output.ttf --jitter 50 --smoothing 20
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # TTF to SVG command
    ttf_svg_parser = subparsers.add_parser(
        'ttf-to-svg',
        help='Convert TTF/OTF font to SVG files'
    )
    ttf_svg_parser.add_argument(
        'input_font',
        help='Path to input TTF/OTF font file'
    )
    ttf_svg_parser.add_argument(
        'output_dir',
        help='Output directory for SVG files'
    )

    # SVG to TTF command
    svg_ttf_parser = subparsers.add_parser(
        'svg-to-ttf',
        help='Convert SVG files to TTF font'
    )
    svg_ttf_parser.add_argument(
        'input_folder',
        help='Directory containing SVG files'
    )
    svg_ttf_parser.add_argument(
        'base_font',
        help='Path to base font file to use as template'
    )
    svg_ttf_parser.add_argument(
        'output_font',
        help='Path for output TTF font file'
    )
    svg_ttf_parser.add_argument(
        '--width',
        type=int,
        default=800,
        help='Default glyph width (default: 800)'
    )

    # Handwritten command
    handwritten_parser = subparsers.add_parser(
        'handwritten',
        help='Add handwritten effect to a font'
    )
    handwritten_parser.add_argument(
        'input_font',
        help='Path to input TTF/OTF font file'
    )
    handwritten_parser.add_argument(
        'output_font',
        help='Path for output font file'
    )
    handwritten_parser.add_argument(
        '--jitter',
        type=int,
        default=35,
        help='Amount of random jitter to apply (default: 35)'
    )
    handwritten_parser.add_argument(
        '--smoothing',
        type=int,
        default=15,
        help='Smoothing amount for curves (default: 15)'
    )

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == 'ttf-to-svg':
            from .ttf_to_svg import ttf_to_svg
            ttf_to_svg(args.input_font, args.output_dir)

        elif args.command == 'svg-to-ttf':
            from .svg_to_ttf import svg_to_ttf
            svg_to_ttf(args.input_folder, args.base_font, args.output_font, default_width=args.width)

        elif args.command == 'handwritten':
            from .handwritten import make_handwritten
            make_handwritten(
                args.input_font,
                args.output_font,
                jitter_amount=args.jitter,
                smoothing=args.smoothing
            )

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
