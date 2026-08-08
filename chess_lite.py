"""
chess_lite.py
=============

A minimal, dependency-free chess board that can replay a sequence of
Standard Algebraic Notation (SAN) moves, such as those found in a PGN
movetext. It does NOT implement full legal-move validation (pins,
discovered checks, etc.) — it trusts that the PGN it is given is
legal, which is true for the vast majority of real-world PGN files
(exported from chess.com, lichess, ChessBase, etc.).

What it *does* handle correctly:
    - Normal piece moves, including disambiguation (Nbd2, R1a3, Qh4e1)
    - Captures, including en passant
    - Castling (O-O / O-O-O, or 0-0 / 0-0-0)
    - Promotion (e8=Q, exd8=Q+)
    - Check ("+") and checkmate ("#") flags, read directly from SAN

This is intentionally small and readable so it's easy to extend.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

Square = str  # e.g. "e4"
Piece = Tuple[str, str]  # (color, type) e.g. ("w", "n")

FILES = "abcdefgh"
RANKS = "12345678"

KNIGHT_OFFSETS = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
KING_OFFSETS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
BISHOP_DIRS = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
ROOK_DIRS = [(1, 0), (-1, 0), (0, 1), (0, -1)]
QUEEN_DIRS = BISHOP_DIRS + ROOK_DIRS


def _sq(file_idx: int, rank_idx: int) -> Square:
    return f"{FILES[file_idx]}{RANKS[rank_idx]}"


def _idx(square: Square) -> Tuple[int, int]:
    return FILES.index(square[0]), RANKS.index(square[1])


def starting_board() -> Dict[Square, Piece]:
    board: Dict[Square, Piece] = {}
    back_rank = ["r", "n", "b", "q", "k", "b", "n", "r"]
    for f, piece_type in enumerate(back_rank):
        board[_sq(f, 0)] = ("w", piece_type)
        board[_sq(f, 7)] = ("b", piece_type)
    for f in range(8):
        board[_sq(f, 1)] = ("w", "p")
        board[_sq(f, 6)] = ("b", "p")
    return board


@dataclass
class MoveInfo:
    from_sq: Optional[Square]
    to_sq: Optional[Square]
    piece_type: str
    color: str
    san: str
    move_number: int
    capture: bool = False
    captured_piece_type: Optional[str] = None
    en_passant: bool = False
    castle: Optional[str] = None  # "kingside" | "queenside"
    rook_from: Optional[Square] = None
    rook_to: Optional[Square] = None
    promotion: Optional[str] = None
    check: bool = False
    checkmate: bool = False
    board_after: Dict[Square, Piece] = field(default_factory=dict)


class IllegalMoveError(Exception):
    pass


def _path_clear(board: Dict[Square, Piece], src: Square, dst: Square, direction: Tuple[int, int]) -> bool:
    fi, ri = _idx(src)
    df, dr = direction
    fi, ri = fi + df, ri + dr
    tf, tr = _idx(dst)
    while (fi, ri) != (tf, tr):
        if not (0 <= fi < 8 and 0 <= ri < 8):
            return False
        if _sq(fi, ri) in board:
            return False
        fi, ri = fi + df, ri + dr
    return True


def _can_reach(board: Dict[Square, Piece], piece_type: str, src: Square, dst: Square) -> bool:
    sf, sr = _idx(src)
    df, dr = _idx(dst)
    dx, dy = df - sf, dr - sr
    if piece_type == "n":
        return (abs(dx), abs(dy)) in [(1, 2), (2, 1)]
    if piece_type == "k":
        return max(abs(dx), abs(dy)) == 1
    if piece_type == "b":
        if abs(dx) != abs(dy) or dx == 0:
            return False
        direction = (1 if dx > 0 else -1, 1 if dy > 0 else -1)
        return _path_clear(board, src, dst, direction)
    if piece_type == "r":
        if dx != 0 and dy != 0:
            return False
        direction = (0 if dx == 0 else (1 if dx > 0 else -1), 0 if dy == 0 else (1 if dy > 0 else -1))
        return _path_clear(board, src, dst, direction)
    if piece_type == "q":
        if dx == 0 or dy == 0 or abs(dx) == abs(dy):
            direction = (0 if dx == 0 else (1 if dx > 0 else -1), 0 if dy == 0 else (1 if dy > 0 else -1))
            return _path_clear(board, src, dst, direction)
        return False
    return False


def _find_candidates(
    board: Dict[Square, Piece],
    piece_type: str,
    color: str,
    dst: Square,
    file_hint: Optional[str],
    rank_hint: Optional[str],
) -> List[Square]:
    out = []
    for sq, (c, t) in board.items():
        if c != color or t != piece_type:
            continue
        if file_hint and sq[0] != file_hint:
            continue
        if rank_hint and sq[1] != rank_hint:
            continue
        if _can_reach(board, piece_type, sq, dst):
            out.append(sq)
    return out


class Board:
    """Holds board state and applies one SAN move at a time."""

    def __init__(self):
        self.board: Dict[Square, Piece] = starting_board()
        self.fullmove_number = 1

    def snapshot(self) -> Dict[Square, Piece]:
        return dict(self.board)

    def push_san(self, color: str, raw_token: str) -> MoveInfo:
        token = raw_token.strip()
        check = token.endswith("+")
        checkmate = token.endswith("#")
        token = token.rstrip("+#!?")

        move_number = self.fullmove_number
        if color == "b":
            self.fullmove_number += 1

        # --- Castling ---
        if token in ("O-O", "0-0"):
            rank = "1" if color == "w" else "8"
            king_from, king_to = f"e{rank}", f"g{rank}"
            rook_from, rook_to = f"h{rank}", f"f{rank}"
            self.board[king_to] = self.board.pop(king_from)
            self.board[rook_to] = self.board.pop(rook_from)
            return MoveInfo(king_from, king_to, "k", color, raw_token, move_number,
                             castle="kingside", rook_from=rook_from, rook_to=rook_to,
                             check=check, checkmate=checkmate,
                             board_after=self.snapshot())

        if token in ("O-O-O", "0-0-0"):
            rank = "1" if color == "w" else "8"
            king_from, king_to = f"e{rank}", f"c{rank}"
            rook_from, rook_to = f"a{rank}", f"d{rank}"
            self.board[king_to] = self.board.pop(king_from)
            self.board[rook_to] = self.board.pop(rook_from)
            return MoveInfo(king_from, king_to, "k", color, raw_token, move_number,
                             castle="queenside", rook_from=rook_from, rook_to=rook_to,
                             check=check, checkmate=checkmate,
                             board_after=self.snapshot())

        # --- Promotion ---
        promotion = None
        if "=" in token:
            token, promo_letter = token.split("=")
            promotion = promo_letter.lower()

        capture = "x" in token
        token_wo_x = token.replace("x", "")

        # --- Piece move (N, B, R, Q, K) ---
        if token_wo_x[0] in "NBRQK":
            piece_type = token_wo_x[0].lower()
            rest = token_wo_x[1:]
            dst = rest[-2:]
            disamb = rest[:-2]
            file_hint = next((ch for ch in disamb if ch.isalpha()), None)
            rank_hint = next((ch for ch in disamb if ch.isdigit()), None)

            candidates = _find_candidates(self.board, piece_type, color, dst, file_hint, rank_hint)
            if len(candidates) != 1:
                raise IllegalMoveError(
                    f"Move '{raw_token}' is ambiguous or illegal given the current position "
                    f"(found {len(candidates)} candidate(s): {candidates})."
                )
            src = candidates[0]
            captured_piece = self.board.get(dst)
            self.board.pop(src)
            self.board[dst] = (color, piece_type)
            return MoveInfo(src, dst, piece_type, color, raw_token, move_number,
                             capture=bool(captured_piece),
                             captured_piece_type=captured_piece[1] if captured_piece else None,
                             check=check, checkmate=checkmate,
                             board_after=self.snapshot())

        # --- Pawn move ---
        dst = token_wo_x[-2:]
        dst_file, dst_rank = dst[0], int(dst[1])
        direction = 1 if color == "w" else -1

        en_passant = False
        captured_piece = self.board.get(dst)

        if capture:
            src_file = token_wo_x[0]
            src_rank = dst_rank - direction
            src = f"{src_file}{src_rank}"
            if captured_piece is None:
                # En passant: captured pawn sits beside the source square,
                # not on the destination square.
                ep_square = f"{dst_file}{src_rank}"
                if ep_square in self.board:
                    captured_piece = self.board.pop(ep_square)
                    en_passant = True
        else:
            one_back = f"{dst_file}{dst_rank - direction}"
            two_back = f"{dst_file}{dst_rank - 2 * direction}"
            if one_back in self.board and self.board[one_back] == (color, "p"):
                src = one_back
            else:
                src = two_back

        piece = self.board.pop(src)
        if promotion:
            self.board[dst] = (color, promotion)
        else:
            self.board[dst] = piece

        return MoveInfo(src, dst, "p", color, raw_token, move_number,
                         capture=bool(captured_piece),
                         captured_piece_type=captured_piece[1] if captured_piece else None,
                         en_passant=en_passant,
                         promotion=promotion, check=check, checkmate=checkmate,
                         board_after=self.snapshot())


def replay_pgn_moves(san_tokens: List[str]) -> List[MoveInfo]:
    """Apply a list of SAN tokens (in order, alternating white/black) and
    return the full move history, each with the resulting board snapshot."""
    board = Board()
    history: List[MoveInfo] = []
    color = "w"
    for token in san_tokens:
        info = board.push_san(color, token)
        history.append(info)
        color = "b" if color == "w" else "w"
    return history


def king_square(board: Dict[Square, Piece], color: str) -> Optional[Square]:
    for sq, (c, t) in board.items():
        if c == color and t == "k":
            return sq
    return None
