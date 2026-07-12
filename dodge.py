"""
DODGE! — a tiny falling-things game.
Move with A/D or arrow keys. Survive. It gets worse. It always gets worse.

Run:  python dodge.py
Keys: A/D or arrows to move · P pause · R restart after game over · Esc quit
"""

import random
import sys

import pygame

# ---------- Config ----------
WIDTH, HEIGHT = 480, 640
FPS = 60

PLAYER_W, PLAYER_H = 46, 18
PLAYER_SPEED = 340            # px per second

SPAWN_EVERY_START = 0.9       # seconds between spawns at the start
SPAWN_EVERY_MIN = 0.22        # fastest spawn rate it can reach
FALL_SPEED_START = 160        # px per second
FALL_SPEED_MAX = 520
RAMP_SECONDS = 75             # how long until difficulty maxes out

BG = (12, 13, 18)
FG = (233, 228, 218)          # bone, of course
FG_DIM = (233, 228, 218)
ACCENT = (185, 136, 75)
DANGER = (196, 90, 74)


def ramp(t):
    """0..1 difficulty over time."""
    return min(t / RAMP_SECONDS, 1.0)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("DODGE!")
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("consolas", 44, bold=True)
    font = pygame.font.SysFont("consolas", 20)

    high_score = 0.0

    def reset():
        return {
            "player_x": WIDTH / 2 - PLAYER_W / 2,
            "rocks": [],          # each rock: [x, y, size]
            "time_alive": 0.0,
            "spawn_timer": 0.0,
            "alive": True,
            "paused": False,
        }

    state = reset()

    while True:
        dt = clock.tick(FPS) / 1000.0

        # ---------- Input / events ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_p and state["alive"]:
                    state["paused"] = not state["paused"]
                if event.key == pygame.K_r and not state["alive"]:
                    state = reset()

        if state["alive"] and not state["paused"]:
            keys = pygame.key.get_pressed()
            move = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                move -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                move += 1
            state["player_x"] += move * PLAYER_SPEED * dt
            state["player_x"] = max(0, min(WIDTH - PLAYER_W, state["player_x"]))

            # ---------- Difficulty & spawning ----------
            state["time_alive"] += dt
            d = ramp(state["time_alive"])
            spawn_every = SPAWN_EVERY_START + (SPAWN_EVERY_MIN - SPAWN_EVERY_START) * d
            fall_speed = FALL_SPEED_START + (FALL_SPEED_MAX - FALL_SPEED_START) * d

            state["spawn_timer"] += dt
            while state["spawn_timer"] >= spawn_every:
                state["spawn_timer"] -= spawn_every
                size = random.randint(16, 42)
                x = random.randint(0, WIDTH - size)
                state["rocks"].append([x, -size, size])

            # ---------- Move rocks & collide ----------
            player_rect = pygame.Rect(int(state["player_x"]), HEIGHT - 60, PLAYER_W, PLAYER_H)
            for rock in state["rocks"]:
                rock[1] += fall_speed * dt
                # bigger rocks fall a touch faster — feels natural
                rock[1] += rock[2] * 0.6 * dt

            for rock in state["rocks"]:
                rock_rect = pygame.Rect(int(rock[0]), int(rock[1]), rock[2], rock[2])
                if rock_rect.colliderect(player_rect):
                    state["alive"] = False
                    high_score = max(high_score, state["time_alive"])

            state["rocks"] = [r for r in state["rocks"] if r[1] < HEIGHT + 50]

        # ---------- Draw ----------
        screen.fill(BG)

        # rocks
        for rock in state["rocks"]:
            pygame.draw.rect(screen, DANGER, (int(rock[0]), int(rock[1]), rock[2], rock[2]), border_radius=4)

        # player
        py = HEIGHT - 60
        color = FG if state["alive"] else (90, 60, 55)
        pygame.draw.rect(screen, color, (int(state["player_x"]), py, PLAYER_W, PLAYER_H), border_radius=6)

        # HUD
        secs = state["time_alive"]
        hud = font.render(f"{secs:6.1f}s   best {high_score:5.1f}s", True, ACCENT)
        screen.blit(hud, (12, 10))

        if state["paused"] and state["alive"]:
            label = font_big.render("PAUSED", True, FG)
            screen.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        if not state["alive"]:
            over = font_big.render("SPLAT.", True, DANGER)
            tip = font.render("press R to try again", True, FG)
            score = font.render(f"you lasted {secs:.1f} seconds", True, ACCENT)
            screen.blit(over, over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
            screen.blit(score, score.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 8)))
            screen.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

        pygame.display.flip()


if __name__ == "__main__":
    main()
