# DODGE! Trilogy 🎮

A tiny falling-object dodge game, made three times over — same core mechanic, three completely different looks and feels.

Move left and right, survive as long as you can, and try not to get hit. It gets harder the longer you last. It always gets harder.

## The three flavors

| File | Vibe | What's different |
|---|---|---|
| `dodge.py` | **Classic** | Minimal, moody, bone-and-rust color palette. No frills — just the core game. |
| `dodge_deluxe.py` | **Neon** | Gradient night sky, drifting parallax stars, a glowing player with a particle trail, and screen shake + a burst effect on death. |
| `dodge_neapolitan.py` | **Cute** 🍨 | Vanilla-strawberry color palette, falling ice cream scoops instead of rocks, a strawberry hoverboard with a cherry on top, and sprinkle rain in the background. |

All three share the same underlying rules — only the presentation changes.

## How to play

- **A/D** or **Arrow keys** — move left/right
- **P** — pause
- **R** — restart after game over
- **Esc** — quit

Survive as long as you can. Things fall faster and more often the longer you last.

## Running it

You'll need Python 3 and [Pygame](https://www.pygame.org/) installed.

```bash
pip install pygame
```

Then run whichever version you want:

```bash
python dodge.py              # classic
python dodge_deluxe.py       # neon
python dodge_neapolitan.py   # cute
```

## Why three versions?

Same game logic, three different art directions — a fun way to explore how far a re-skin can change the feel of something without touching the core mechanics.
