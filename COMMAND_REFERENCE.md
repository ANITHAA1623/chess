# Chess Reel Maker — Command Reference

Your personal cheat sheet. Keep this file open next to your terminal.

Every command below assumes you're already `cd`'d into the `chess_reel_maker`
folder and your venv is activated (`venv\Scripts\Activate.ps1`).

---

## 1. The absolute basics

```powershell
python main.py --pgn examples/opera_game.pgn
```
> Renders with every default setting. Output lands at `output/chess_reel.mp4`.

```powershell
python main.py --help
```
> Prints every flag this tool understands, straight from the code. Safe to
> run anytime — doesn't render anything or touch your files.

---

## 2. Using a DIFFERENT PGN (your own games)

**You never edit any code file for this.** Just:

1. Get your PGN text (Export Game → PGN, from chess.com/lichess/etc.)
2. Save it as a new file, e.g. `examples/my_game.pgn` (or anywhere in the folder)
3. Point `--pgn` at it:

```powershell
python main.py --pgn examples/my_game.pgn --theme tournament --piece-style icon --title "Sunday Blitz" --white "Me" --black "Rival123"
```
> `--title`, `--white`, `--black` are optional — if your PGN file already has
> proper `[White "..."]` / `[Black "..."]` / `[Event "..."]` header tags,
> the tool reads them automatically and you can leave these off.

---

## 3. Every theme, one at a time

```powershell
python main.py --pgn examples/opera_game.pgn --theme tournament -o output/tournament.mp4
```
> Walnut wood board, gold accents, warm broadcast look. **Default theme.**

```powershell
python main.py --pgn examples/opera_game.pgn --theme midnight -o output/midnight.mp4
```
> Marble board, cool blue tones. A calmer, moodier alternative.

```powershell
python main.py --pgn examples/opera_game.pgn --theme neon -o output/neon.mp4
```
> Dark glassy esports look — glowing pieces, rounded neon-lit board.

```powershell
python main.py --pgn examples/opera_game.pgn --theme royal_ivory -o output/royal_ivory.mp4
```
> Premium warm wood + ivory pieces, gold inlay, glossy gradient shading.

```powershell
python main.py --pgn examples/opera_game.pgn --theme royal_marble -o output/royal_marble.mp4
```
> Premium black/white marble + gold gloss treatment. Most dramatic/formal.

---

## 4. Piece style (independent of theme — mix any with any)

```powershell
python main.py --pgn examples/opera_game.pgn --piece-style glyph
```
> Classic Unicode chess symbols. **Default style.**

```powershell
python main.py --pgn examples/opera_game.pgn --piece-style icon
```
> Hand-drawn bold silhouette set (proper rook towers, horse-head knight,
> mitred bishop, pointed crowns). **Your confirmed favorite — pairs best
> with `--theme tournament`.**

---

## 5. Pacing — how fast the video feels

```powershell
python main.py --pgn examples/opera_game.pgn --seconds-per-move 1.1
```
> Default pace. Notable moves (captures, brilliancies, checkmate) automatically
> get extra time on top of this base number — you don't need to account for that.

```powershell
python main.py --pgn examples/opera_game.pgn --seconds-per-move 0.7
```
> Faster, punchier — good for a quick highlight-reel feel.

```powershell
python main.py --pgn examples/opera_game.pgn --seconds-per-move 1.6
```
> Slower — gives viewers more time to actually read each move.

```powershell
python main.py --pgn examples/opera_game.pgn --checkmate-hold 2.0
```
> Shortens the checkmate danger+celebration sequence (default is 3.4 seconds).
> Use a bigger number (e.g. `4.5`) to let the celebration breathe longer.

```powershell
python main.py --pgn examples/opera_game.pgn --fps 24
```
> Change frame rate. Default is 30 — rarely needs changing.

---

## 6. Sound

```powershell
python main.py --pgn examples/opera_game.pgn
```
> Built-in synthesized sound effects ON by default (clicks, thuds, checkmate
> fanfare) — no flag needed.

```powershell
python main.py --pgn examples/opera_game.pgn --no-sound-effects
```
> Turns OFF the built-in sound effects entirely (silent video, unless you
> also add `--audio`).

```powershell
python main.py --pgn examples/opera_game.pgn --effects-volume 1.0
```
> Makes the built-in sound effects louder. Default is `0.9`. Range is roughly
> `0.0` (silent) to `1.0`+ (max/louder).

```powershell
python main.py --pgn examples/opera_game.pgn --audio Test.mp3
```
> Layers your own mp3/wav music or narration on top of the built-in effects,
> mixed automatically.
> ⚠️ **Your audio file must be LONGER than the video, or the video gets cut
> short to match it.** See the "checking video length" note at the bottom.

```powershell
python main.py --pgn examples/opera_game.pgn --audio Test.mp3 --music-volume 0.4 --effects-volume 0.9
```
> Fine-tune the balance: quieter background music (`0.4`) so it doesn't
> compete with the sound effects (`0.9`).

```powershell
python main.py --pgn examples/opera_game.pgn --audio Test.mp3 --no-sound-effects
```
> Use ONLY your own mp3 — no synthesized clicks/thuds at all.

---

## 7. Board orientation

```powershell
python main.py --pgn examples/opera_game.pgn --flip
```
> Renders from Black's point of view instead of White's. Useful if you
> played Black and want the board to match your perspective.

---

## 8. Speed vs. quality (IMPORTANT while testing)

```powershell
python main.py --pgn examples/opera_game.pgn --fast
```
> Skips the heaviest effects (chromatic aberration, glitch, vortex/ripple/
> vertigo warps, motion blur) for a MUCH faster render (~1 min vs ~5-10 min).
> **Use this for every test/comparison render.** Drop it only for your final,
> real upload.

---

## 9. Other useful flags

```powershell
python main.py --pgn examples/opera_game.pgn -o output/my_custom_name.mp4
```
> Choose your own output filename/path instead of the default
> `output/chess_reel.mp4`. Useful so test renders don't overwrite each other.

```powershell
python main.py --pgn examples/opera_game.pgn --keep-frames
```
> Keeps every individual PNG frame on disk after rendering (for debugging /
> curiosity). Rarely needed day-to-day.

---

## 10. YOUR go-to final render command

Combining your confirmed favorites (`tournament` theme + `icon` pieces),
full quality, with your own PGN and names filled in:

```powershell
python main.py --pgn examples/my_game.pgn --theme tournament --piece-style icon --seconds-per-move 1.1 --title "My Game Title" --white "White Player" --black "Black Player" --audio Test.mp3 --music-volume 0.4 -o output/final.mp4
```

Just swap:
- `examples/my_game.pgn` → your actual PGN file
- `"My Game Title"`, `"White Player"`, `"Black Player"` → your real names
- `Test.mp3` → your actual audio file (or delete `--audio Test.mp3` and
  `--music-volume 0.4` entirely if you don't want music)

**Notice `--fast` is NOT in this command** — that's intentional. This is
your real, final, best-quality render.

---

## Quick troubleshooting

| Problem | Likely cause |
|---|---|
| Video cuts off early with music | Your mp3 is shorter than the video — use a longer track |
| Render taking 5-10+ minutes | Normal without `--fast` — that's full quality. Use `--fast` while testing |
| "Could not replay the game" error | PGN has a transcription error — double-check the moves |
| Pieces/theme didn't change | Double check spelling of `--theme`/`--piece-style` value — must match exactly (`tournament`, `icon`, etc.) |

---

## Checking a video's length (Windows)

Right-click the mp4 in File Explorer → **Properties** → **Details** tab →
look for "Length". Compare that to your mp3's length before using `--audio`.
