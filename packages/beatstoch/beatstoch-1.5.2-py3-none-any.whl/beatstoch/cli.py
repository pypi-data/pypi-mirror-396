# filename: src/beatstoch/cli.py
import argparse
import re
import sys

from .generator import generate_from_song, generate_stochastic_pattern

EXAMPLES = """\
Examples:
  # Generate from song title (BPM auto-detected)
  beatstoch generate "Billie Jean" --artist "Michael Jackson"
  beatstoch generate "1979" --artist "Smashing Pumpkins" --bars 16

  # Generate with explicit BPM - various styles
  beatstoch generate-bpm 128 --style house                 # Four-on-the-floor EDM
  beatstoch generate-bpm 140 --style breaks --bars 16      # Syncopated breakbeat
  beatstoch generate-bpm 120 --style rock                  # Driving rock beat
  beatstoch generate-bpm 85 --style blues                  # Shuffle blues
  beatstoch generate-bpm 110 --style indie                 # Loose indie rock
  beatstoch generate-bpm 140 --style jazz                  # Jazz ride pattern

  # Different time signatures
  beatstoch generate-bpm 90 --meter 3/4 --style generic    # Waltz
  beatstoch generate-bpm 110 --meter 2/4                   # March

  # Humanized patterns (ghost notes + timing variation)
  beatstoch generate-bpm 120 --humanize 0.5                # Medium humanization
  beatstoch generate-bpm 128 --humanize 0.8 --style breaks # Heavy humanization

  # Control randomness with --predictability
  beatstoch generate-bpm 128 --predictability 1.0          # Fully predictable (mechanical)
  beatstoch generate-bpm 128 --predictability 0.5          # More variation/surprises

  # Combine features
  beatstoch generate-bpm 120 --style rock --humanize 0.6 --groove-intensity 0.8
  beatstoch generate "Take Five" --artist "Dave Brubeck" --style jazz --fallback-bpm 174
"""

GENERATE_EXAMPLES = """\
Examples:
  beatstoch generate "Billie Jean" --artist "Michael Jackson"
  beatstoch generate "1979" --artist "Smashing Pumpkins" --bars 16 --style house
  beatstoch generate "Blue Monday" --artist "New Order" --humanize 0.6
  beatstoch generate "Take Five" --artist "Dave Brubeck" --meter 3/4 --humanize 0.8 --fallback-bpm 174
  beatstoch generate "Around the World" --artist "Daft Punk" --predictability 1.0  # Mechanical
  beatstoch generate "Amen Brother" --artist "The Winstons" --predictability 0.5   # More variation
"""

GENERATE_BPM_EXAMPLES = """\
Examples:
  beatstoch generate-bpm 128                               # Basic house at 128 BPM
  beatstoch generate-bpm 140 --style breaks --bars 16      # 16 bars of breakbeat
  beatstoch generate-bpm 120 --style rock                  # Classic rock beat
  beatstoch generate-bpm 85 --style blues --humanize 0.6   # Shuffle blues with feel
  beatstoch generate-bpm 110 --style indie                 # Indie rock groove
  beatstoch generate-bpm 140 --style jazz                  # Jazz ride pattern
  beatstoch generate-bpm 90 --meter 3/4 --style generic    # Waltz in 3/4
  beatstoch generate-bpm 128 --predictability 1.0          # Fully predictable/mechanical
  beatstoch generate-bpm 128 --predictability 0.5          # More stochastic variation
"""


def parse_meter(value: str) -> tuple:
    """Parse time signature string like '4/4', '3/4', '2/4' into tuple."""
    try:
        parts = value.split("/")
        if len(parts) != 2:
            raise ValueError
        return (int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        raise argparse.ArgumentTypeError(
            f"Invalid meter '{value}'. Use format like '4/4', '3/4', or '2/4'"
        )


def main():
    """
    CLI for BPM-aware stochastic drum MIDI generator.
    """
    parser = argparse.ArgumentParser(
        prog="beatstoch",
        description="BPM-aware stochastic drum MIDI generator with psychoacoustic grooves.",
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd")

    # --- generate command ---
    gsong = sub.add_parser(
        "generate",
        help="Generate from song title/artist (BPM auto-detected from BPMDatabase)",
        description="Generate drum pattern by looking up song BPM from BPMDatabase.com",
        epilog=GENERATE_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    gsong.add_argument("title", help="Song title to look up")
    gsong.add_argument("--artist", help="Artist name (improves BPM lookup accuracy)")
    gsong.add_argument(
        "--bars", type=int, default=8, help="Number of bars (default: 8)"
    )
    gsong.add_argument(
        "--style",
        default="house",
        choices=["house", "breaks", "rock", "blues", "indie", "jazz", "generic"],
        help="Drum style (default: house)",
    )
    gsong.add_argument(
        "--meter",
        type=parse_meter,
        default=(4, 4),
        metavar="X/Y",
        help="Time signature: 4/4, 3/4, or 2/4 (default: 4/4)",
    )
    gsong.add_argument(
        "--humanize",
        type=float,
        default=0.0,
        metavar="0.0-1.0",
        help="Add ghost notes and timing variation (default: 0.0)",
    )
    gsong.add_argument(
        "--steps-per-beat",
        type=int,
        default=4,
        help="Resolution (default: 4 = 16th notes)",
    )
    gsong.add_argument(
        "--swing", type=float, default=0.10, help="Swing amount 0.0-1.0 (default: 0.10)"
    )
    gsong.add_argument(
        "--intensity",
        type=float,
        default=0.9,
        help="Pattern density 0.0-1.0 (default: 0.9)",
    )
    gsong.add_argument(
        "--groove-intensity",
        type=float,
        default=0.7,
        metavar="0.0-1.0",
        help="Psychoacoustic groove strength (default: 0.7)",
    )
    gsong.add_argument(
        "--predictability",
        type=float,
        default=0.85,
        metavar="0.0-1.0",
        help="Pattern predictability: 1.0=mechanical, 0.0=chaotic (default: 0.85)",
    )
    gsong.add_argument("--seed", type=int, help="Random seed for reproducible patterns")
    gsong.add_argument("--fallback-bpm", type=float, help="BPM to use if lookup fails")
    gsong.add_argument("--verbose", action="store_true", help="Show BPM lookup details")

    # --- generate-bpm command ---
    gbpm = sub.add_parser(
        "generate-bpm",
        help="Generate with explicit BPM (no lookup)",
        description="Generate drum pattern with specified BPM (no database lookup)",
        epilog=GENERATE_BPM_EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    gbpm.add_argument("bpm", type=float, help="Target BPM (e.g., 120, 128, 140)")
    gbpm.add_argument("--bars", type=int, default=8, help="Number of bars (default: 8)")
    gbpm.add_argument(
        "--style",
        default="house",
        choices=["house", "breaks", "rock", "blues", "indie", "jazz", "generic"],
        help="Drum style (default: house)",
    )
    gbpm.add_argument(
        "--meter",
        type=parse_meter,
        default=(4, 4),
        metavar="X/Y",
        help="Time signature: 4/4, 3/4, or 2/4 (default: 4/4)",
    )
    gbpm.add_argument(
        "--humanize",
        type=float,
        default=0.0,
        metavar="0.0-1.0",
        help="Add ghost notes and timing variation (default: 0.0)",
    )
    gbpm.add_argument(
        "--steps-per-beat",
        type=int,
        default=4,
        help="Resolution (default: 4 = 16th notes)",
    )
    gbpm.add_argument(
        "--swing", type=float, default=0.10, help="Swing amount 0.0-1.0 (default: 0.10)"
    )
    gbpm.add_argument(
        "--intensity",
        type=float,
        default=0.9,
        help="Pattern density 0.0-1.0 (default: 0.9)",
    )
    gbpm.add_argument(
        "--groove-intensity",
        type=float,
        default=0.7,
        metavar="0.0-1.0",
        help="Psychoacoustic groove strength (default: 0.7)",
    )
    gbpm.add_argument(
        "--predictability",
        type=float,
        default=0.85,
        metavar="0.0-1.0",
        help="Pattern predictability: 1.0=mechanical, 0.0=chaotic (default: 0.85)",
    )
    gbpm.add_argument("--seed", type=int, help="Random seed for reproducible patterns")

    args = parser.parse_args()

    # If no command provided, print help and exit cleanly
    if args.cmd is None:
        parser.print_help()
        sys.exit(0)

    if args.cmd == "generate":
        try:
            mid, bpm_used = generate_from_song(
                song_title=args.title,
                artist=args.artist,
                bars=args.bars,
                style=args.style,
                meter=args.meter,
                steps_per_beat=args.steps_per_beat,
                swing=args.swing,
                intensity=args.intensity,
                groove_intensity=args.groove_intensity,
                humanize=args.humanize,
                predictability=args.predictability,
                seed=args.seed,
                fallback_bpm=args.fallback_bpm,
                verbose=args.verbose,
            )
        except Exception as e:
            print(f"beatstoch: {e}", file=sys.stderr)
            sys.exit(2)

        safe_title = re.sub(r"[^a-zA-Z0-9]+", "_", args.title).strip("_").lower()
        safe_artist = (
            re.sub(r"[^a-zA-Z0-9]+", "_", args.artist).strip("_").lower()
            if args.artist
            else "unknown"
        )
        meter_str = f"{args.meter[0]}{args.meter[1]}"
        humanize_str = "_humanized" if args.humanize > 0 else ""
        out_path = f"stoch_{safe_artist}_{safe_title}_{int(bpm_used)}bpm_{meter_str}{humanize_str}.mid"
        mid.save(out_path)
        print(
            f"Wrote {out_path} (BPM={bpm_used}, meter={args.meter[0]}/{args.meter[1]}, humanize={args.humanize})"
        )
    else:
        mid = generate_stochastic_pattern(
            bpm=args.bpm,
            bars=args.bars,
            meter=args.meter,
            steps_per_beat=args.steps_per_beat,
            swing=args.swing,
            intensity=args.intensity,
            groove_intensity=args.groove_intensity,
            humanize=args.humanize,
            predictability=args.predictability,
            seed=args.seed if args.seed is not None else 42,
            style=args.style,
        )
        meter_str = f"{args.meter[0]}{args.meter[1]}"
        humanize_str = "_humanized" if args.humanize > 0 else ""
        out_path = f"stoch_{int(args.bpm)}bpm_{meter_str}{humanize_str}.mid"
        mid.save(out_path)
        print(
            f"Wrote {out_path} (meter={args.meter[0]}/{args.meter[1]}, humanize={args.humanize})"
        )


if __name__ == "__main__":
    main()
