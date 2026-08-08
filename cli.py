"""
cli.py
======

Command-line entry point.

Examples
--------
    python main.py --pgn examples/opera_game.pgn --title "A Night at the Opera"

    python main.py --pgn-text "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6" \
                    --white "Kasparov" --black "Karpov" --seconds-per-move 1.4

    python main.py --pgn game.pgn --audio music.mp3 --theme midnight -o my_reel.mp4

    # A file with several games concatenated together (e.g. exported
    # from chess.com/lichess) automatically renders one video per game:
    python main.py --pgn my_games.pgn -o output/game.mp4
    #   -> output/game_1.mp4, output/game_2.mp4, ...
"""

import argparse
import os
import re
import sys
import time

from .chess_lite import replay_pgn_moves, IllegalMoveError
from .pgn_parser import extract_san_tokens, read_pgn_file, split_games
from .themes import THEMES
from .video_builder import ReelOptions, build_video


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="chess-reel",
        description="Turn a PGN chess game into a vertical short-form video with cinematic effects.",
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--pgn", metavar="FILE", help="Path to a .pgn file (may contain one or many games)")
    src.add_argument("--pgn-text", metavar="TEXT", help="PGN movetext given directly on the command line")

    p.add_argument("-o", "--output", default="output/chess_reel.mp4",
                    help="Output video path (default: output/chess_reel.mp4). "
                         "If the PGN has multiple games, this is used as a base name.")
    p.add_argument("--title", default=None, help="Title shown at the top of the video (default: derived from PGN headers)")
    p.add_argument("--white", default=None, help="White player's name (default: read from PGN header if present)")
    p.add_argument("--black", default=None, help="Black player's name (default: read from PGN header if present)")
    p.add_argument("--theme", default="tournament", choices=list(THEMES.keys()), help="Visual theme")
    p.add_argument("--seconds-per-move", type=float, default=1.1, help="Base screen time per move (notable moves get more automatically)")
    p.add_argument("--fps", type=int, default=30, help="Frames per second")
    p.add_argument("--flip", action="store_true", help="Render the board from Black's perspective")
    p.add_argument("--audio", metavar="FILE", help="Optional background music/narration file to mix in")
    p.add_argument("--music-volume", type=float, default=0.5, help="Volume multiplier for --audio (default 0.5)")
    p.add_argument("--no-sound-effects", action="store_true", help="Disable the synthesized capture/check/checkmate sound effects")
    p.add_argument("--effects-volume", type=float, default=0.9, help="Volume multiplier for sound effects (default 0.9)")
    p.add_argument("--checkmate-hold", type=float, default=3.4, help="How long the checkmate danger+celebration sequence lasts, in seconds")
    p.add_argument("--keep-frames", action="store_true", help="Keep the intermediate PNG frames on disk for inspection")
    p.add_argument("--fast", action="store_true", help="Skip the heavier per-pixel warp effects (chromatic aberration, glitch, vortex/ripple/vertigo) for a much quicker draft render")
    p.add_argument("--piece-style", default="glyph", choices=["glyph", "icon"], help="'glyph' = classic Unicode chess symbols, 'icon' = hand-drawn bold silhouette set (works with any --theme)")

    return p


def _extract_pgn_header(pgn_text: str, tag: str) -> str:
    m = re.search(rf'\[{tag}\s+"([^"]*)"\]', pgn_text)
    return m.group(1) if m else ""


def _derive_output_path(base_output: str, index: int, total: int) -> str:
    if total <= 1:
        return base_output
    root, ext = os.path.splitext(base_output)
    return f"{root}_{index}{ext}"


def _render_one_game(pgn_text: str, args, output_path: str) -> bool:
    tokens = extract_san_tokens(pgn_text)
    if not tokens:
        print("  No moves found in this game, skipping.", file=sys.stderr)
        return False

    try:
        history = replay_pgn_moves(tokens)
    except IllegalMoveError as e:
        print(f"  Could not replay this game: {e}", file=sys.stderr)
        return False

    white = args.white or _extract_pgn_header(pgn_text, "White") or "White"
    black = args.black or _extract_pgn_header(pgn_text, "Black") or "Black"
    title = args.title or _extract_pgn_header(pgn_text, "Event") or f"{white} vs {black}"

    opts = ReelOptions(
        title=title,
        white=white,
        black=black,
        theme=args.theme,
        seconds_per_move=args.seconds_per_move,
        checkmate_hold_seconds=args.checkmate_hold,
        fps=args.fps,
        flipped=args.flip,
        audio_path=args.audio,
        music_volume=args.music_volume,
        sound_effects=not args.no_sound_effects,
        effects_volume=args.effects_volume,
        keep_frames=args.keep_frames,
        fx_quality="fast" if args.fast else "full",
        piece_style=args.piece_style,
    )

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    def progress(done, total):
        print(f"  rendered move {done}/{total}", end="\r")

    start = time.time()
    build_video(history, opts, output_path, progress_cb=progress)
    elapsed = time.time() - start
    print(f"\n  Done in {elapsed:.1f}s -> {output_path}")
    return True


def main(argv=None):
    args = build_arg_parser().parse_args(argv)

    pgn_text = read_pgn_file(args.pgn) if args.pgn else args.pgn_text
    games = split_games(pgn_text)

    if len(games) > 1:
        print(f"Found {len(games)} games in this PGN — rendering one video per game.\n")

    ok_count = 0
    for i, game_text in enumerate(games, start=1):
        if len(games) > 1:
            print(f"[Game {i}/{len(games)}]")
        output_path = _derive_output_path(args.output, i, len(games))
        if _render_one_game(game_text, args, output_path):
            ok_count += 1

    if ok_count == 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
