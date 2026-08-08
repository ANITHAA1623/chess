"""
chess_reel
==========

A small, dependency-light toolkit that turns a PGN chess game into a
vertical short-form video (YouTube Shorts / Instagram Reels / TikTok)
with cinematic zoom, pan, capture-flash and checkmate effects.

No internet access and no heavy chess engine required: the PGN mover
in `chess_lite.py` is a self-contained SAN interpreter written from
scratch, and rendering is done with Pillow. The only external binary
required is ffmpeg (used to stitch frames into an mp4).
"""

__version__ = "1.0.0"
