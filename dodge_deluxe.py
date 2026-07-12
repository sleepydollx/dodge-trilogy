"""
DODGE! deluxe — same game, dressed up.
Gradient night sky, drifting stars, glowing player with a particle trail,
screen shake and a burst when you get hit.

Run:  python dodge_deluxe.py
Keys: A/D or arrows · P pause · R restart · Esc quit
"""

import math
import random
import sys

import pygame

# ---------- Config ----------
WIDTH, HEIGHT = 480, 640
FPS = 60

PLAYER_W, PLAYER_H = 46, 16
PLAYER_SPEED = 340

SPAWN_EVERY_START = 0.9
SPAWN_EVERY_MIN = 0.22
FALL_SPEED_START = 160
FALL_SPEED_MAX = 520
RAMP_SECONDS = 75

# Palette — neon night
SKY_TOP = (10, 8, 24)
SKY_BOTTOM = (38, 16, 52)
PLAYER_CORE = (140, 240, 255)
PLAYER_GLOW = (60, 160, 220)
ROCK_CORE = (255, 92, 120)
ROCK_GLOW = (160, 40, 80)
STAR = (200, 200, 230)
HUD_TEXT = (255, 200, 120)
WHITE = (240, 240, 245)


def ramp(t):
    return min(t / RAMP_SECONDS, 1.0)


def make_sky():
    """Pre-render the vertical gradient once."""
    sky = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        f = y / HEIGHT
        r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * f)
        g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * f)
        b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * f)
        pygame.draw.line(sky, (r, g, b), (0, y), (WIDTH, y))
    return sky


def glow_circle(surface, color, center, radius):
    """Cheap glow: stacked translucent circles."""
    glow = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
    for i, alpha in ((3.0, 25), (2.2, 45), (1.5, 70)):
        pygame.draw.circle(glow, (*color, alpha),
                           (radius * 2, radius * 2), int(radius * i))
    surface.blit(glow, (center[0] - radius * 2, center[1] - radius * 2))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("DODGE! deluxe")
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("consolas", 46, bold=True)
    font = pygame.font.SysFont("consolas", 19)
    font_small = pygame.font.SysFont("consolas", 15)

    sky = make_sky()
    world = pygame.Surface((WIDTH, HEIGHT))  # we draw here, then blit with shake offset

    # Parallax stars: (x, y, speed, size)
    stars = [(random.uniform(0, WIDTH), random.uniform(0, HEIGHT),
              random.uniform(12, 45), random.choice((1, 1, 2)))
             for _ in range(70)]

    high_score = 0.0

    def reset():
        return {
            "player_x": WIDTH / 2 - PLAYER_W / 2,
            "rocks": [],            # [x, y, size, spin]
            "particles": [],        # {x, y, vx, vy, life, max, color, size}
            "time_alive": 0.0,
            "spawn_timer": 0.0,
            "alive": True,
            "paused": False,
            "shake": 0.0,
        }

    state = reset()

    def burst(x, y, color, count=26, speed=260):
        for _ in range(count):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(speed * 0.25, speed)
            state["particles"].append({
                "x": x, "y": y,
                "vx": math.cos(ang) * spd, "vy": math.sin(ang) * spd,
                "life": 0.0, "max": random.uniform(0.4, 0.9),
                "color": color, "size": random.randint(2, 5),
            })

    while True:
        dt = clock.tick(FPS) / 1000.0

        # ---------- Events ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_p and state["alive"]:
                    state["paused"] = not state["paused"]
                if event.key == pygame.K_r and not state["alive"]:
                    state = reset()

        moving = 0
        if state["alive"] and not state["paused"]:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                moving -= 1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                moving += 1
            state["player_x"] += moving * PLAYER_SPEED * dt
            state["player_x"] = max(0, min(WIDTH - PLAYER_W, state["player_x"]))

            # Difficulty
            state["time_alive"] += dt
            d = ramp(state["time_alive"])
            spawn_every = SPAWN_EVERY_START + (SPAWN_EVERY_MIN - SPAWN_EVERY_START) * d
            fall_speed = FALL_SPEED_START + (FALL_SPEED_MAX - FALL_SPEED_START) * d

            # Spawn
            state["spawn_timer"] += dt
            while state["spawn_timer"] >= spawn_every:
                state["spawn_timer"] -= spawn_every
                size = random.randint(16, 42)
                state["rocks"].append(
                    [random.randint(0, WIDTH - size), -size, size,
                     random.uniform(-2.5, 2.5)])

            # Player trail
            px = state["player_x"] + PLAYER_W / 2
            py = HEIGHT - 60 + PLAYER_H / 2
            if moving != 0 and random.random() < 0.85:
                state["particles"].append({
                    "x": px - moving * PLAYER_W * 0.5,
                    "y": py + random.uniform(-4, 4),
                    "vx": -moving * random.uniform(30, 80),
                    "vy": random.uniform(-15, 15),
                    "life": 0.0, "max": random.uniform(0.25, 0.5),
                    "color": PLAYER_GLOW, "size": random.randint(2, 4),
                })

            # Rocks
            player_rect = pygame.Rect(int(state["player_x"]), HEIGHT - 60, PLAYER_W, PLAYER_H)
            for rock in state["rocks"]:
                rock[1] += (fall_speed + rock[2] * 0.6) * dt
                rock[3] += dt  # spin phase

            for rock in state["rocks"]:
                rock_rect = pygame.Rect(int(rock[0]), int(rock[1]), rock[2], rock[2])
                if rock_rect.colliderect(player_rect):
                    state["alive"] = False
                    state["shake"] = 14.0
                    burst(px, py, PLAYER_CORE)
                    burst(px, py, ROCK_CORE, count=14)
                    high_score = max(high_score, state["time_alive"])

            state["rocks"] = [r for r in state["rocks"] if r[1] < HEIGHT + 60]

        # ---------- Always-on updates (particles, stars, shake decay) ----------
        if not state["paused"]:
            for p in state["particles"]:
                p["life"] += dt
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                p["vy"] += 60 * dt  # slight gravity
            state["particles"] = [p for p in state["particles"] if p["life"] < p["max"]]

            stars[:] = [(x, (y + spd * dt) % HEIGHT, spd, s) for x, y, spd, s in stars]
            state["shake"] = max(0.0, state["shake"] - 30 * dt)

        # ---------- Draw ----------
        world.blit(sky, (0, 0))

        for x, y, spd, s in stars:
            world.fill(STAR, (int(x), int(y), s, s))

        # Particles (under everything else)
        for p in state["particles"]:
            fade = 1.0 - p["life"] / p["max"]
            c = tuple(int(ch * fade) for ch in p["color"])
            size = max(1, int(p["size"] * fade))
            world.fill(c, (int(p["x"]), int(p["y"]), size, size))

        # Rocks: glow + core with a wobble
        for rock in state["rocks"]:
            cx = rock[0] + rock[2] / 2
            cy = rock[1] + rock[2] / 2
            glow_circle(world, ROCK_GLOW, (int(cx), int(cy)), int(rock[2] * 0.55))
            wob = math.sin(rock[3] * 4) * 2
            pygame.draw.rect(world, ROCK_CORE,
                             (int(rock[0] + wob), int(rock[1]), rock[2], rock[2]),
                             border_radius=6)

        # Player: glow + hovering board + light dot
        px = int(state["player_x"])
        py = HEIGHT - 60
        if state["alive"]:
            glow_circle(world, PLAYER_GLOW, (px + PLAYER_W // 2, py + PLAYER_H // 2), 26)
            hover = math.sin(pygame.time.get_ticks() * 0.006) * 2
            pygame.draw.rect(world, PLAYER_CORE,
                             (px, int(py + hover), PLAYER_W, PLAYER_H), border_radius=8)
            pygame.draw.circle(world, WHITE,
                               (px + PLAYER_W // 2, int(py + hover) + PLAYER_H // 2), 3)

        # HUD panel
        hud_bg = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
        hud_bg.fill((0, 0, 0, 110))
        world.blit(hud_bg, (0, 0))
        world.blit(font.render(f"time {state['time_alive']:6.1f}s", True, HUD_TEXT), (14, 10))
        best = font.render(f"best {high_score:5.1f}s", True, HUD_TEXT)
        world.blit(best, (WIDTH - best.get_width() - 14, 10))

        # Overlays
        if state["paused"] and state["alive"]:
            dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim.fill((0, 0, 0, 140))
            world.blit(dim, (0, 0))
            label = font_big.render("PAUSED", True, WHITE)
            world.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        if not state["alive"]:
            dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim.fill((20, 0, 10, 150))
            world.blit(dim, (0, 0))
            over = font_big.render("SPLAT.", True, ROCK_CORE)
            score = font.render(f"you lasted {state['time_alive']:.1f} seconds", True, HUD_TEXT)
            tip = font_small.render("press R to try again", True, WHITE)
            world.blit(over, over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 44)))
            world.blit(score, score.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 6)))
            world.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 38)))

        # Screen shake: blit the world with a decaying random offset
        ox = random.uniform(-state["shake"], state["shake"])
        oy = random.uniform(-state["shake"], state["shake"])
        screen.fill((0, 0, 0))
        screen.blit(world, (int(ox), int(oy)))
        pygame.display.flip()


if __name__ == "__main__":
    main()
