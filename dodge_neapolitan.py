"""
DODGE! à la neapolitan da cute one. 🍨
Falling scoops of ice cream, a strawberry hoverboard, sprinkle rain.
Same game, third flavor.

Run:  python dodge_neapolitan.py
Keys: A/D or arrows · P pause · R restart · Esc quit
"""

import math
import random
import sys

import pygame


WIDTH, HEIGHT = 480, 640
FPS = 60

PLAYER_W, PLAYER_H = 46, 16
PLAYER_SPEED = 340

SPAWN_EVERY_START = 0.9
SPAWN_EVERY_MIN = 0.22
FALL_SPEED_START = 160
FALL_SPEED_MAX = 520
RAMP_SECONDS = 75

# Palette — neapolitan 🍨
SKY_TOP = (255, 246, 233)        # vanilla cream
SKY_BOTTOM = (251, 221, 210)     # warm strawberry milk
CHOCOLATE = (74, 44, 33)
CHOCOLATE_SOFT = (138, 101, 82)
STRAWBERRY = (242, 126, 157)
STRAWBERRY_DARK = (217, 95, 129)
VANILLA = (246, 227, 180)
CREAM = (255, 253, 247)
CHERRY = (192, 57, 43)

SCOOP_FLAVORS = [CHOCOLATE_SOFT, STRAWBERRY, VANILLA]
SPRINKLE_COLORS = [STRAWBERRY, VANILLA, (168, 216, 185), (162, 184, 229)]


def ramp(t):
    return min(t / RAMP_SECONDS, 1.0)


def make_sky():
    sky = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        f = y / HEIGHT
        r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * f)
        g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * f)
        b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * f)
        pygame.draw.line(sky, (r, g, b), (0, y), (WIDTH, y))
    return sky


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("DODGE! à la neapolitan 🍨")
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("comicsansms,consolas", 44, bold=True)
    font = pygame.font.SysFont("comicsansms,consolas", 18, bold=True)
    font_small = pygame.font.SysFont("comicsansms,consolas", 14)

    sky = make_sky()
    world = pygame.Surface((WIDTH, HEIGHT))

    sprinkles = [(random.uniform(0, WIDTH), random.uniform(0, HEIGHT),
                  random.uniform(15, 50), random.choice(SPRINKLE_COLORS),
                  random.uniform(-0.6, 0.6))
                 for _ in range(60)]

    high_score = 0.0

    def reset():
        return {
            "player_x": WIDTH / 2 - PLAYER_W / 2,
            "scoops": [],           # [x, y, size, wobble_phase, color]
            "particles": [],
            "time_alive": 0.0,
            "spawn_timer": 0.0,
            "alive": True,
            "paused": False,
            "shake": 0.0,
        }

    state = reset()

    def burst(x, y, count=30, speed=240):
        for _ in range(count):
            ang = random.uniform(0, math.tau)
            spd = random.uniform(speed * 0.25, speed)
            state["particles"].append({
                "x": x, "y": y,
                "vx": math.cos(ang) * spd, "vy": math.sin(ang) * spd,
                "life": 0.0, "max": random.uniform(0.4, 0.9),
                "color": random.choice(SPRINKLE_COLORS + [CREAM]),
                "size": random.randint(2, 5),
            })

    while True:
        dt = clock.tick(FPS) / 1000.0

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

            state["time_alive"] += dt
            d = ramp(state["time_alive"])
            spawn_every = SPAWN_EVERY_START + (SPAWN_EVERY_MIN - SPAWN_EVERY_START) * d
            fall_speed = FALL_SPEED_START + (FALL_SPEED_MAX - FALL_SPEED_START) * d

            state["spawn_timer"] += dt
            while state["spawn_timer"] >= spawn_every:
                state["spawn_timer"] -= spawn_every
                size = random.randint(18, 44)
                state["scoops"].append(
                    [random.randint(0, WIDTH - size), -size, size,
                     random.uniform(0, math.tau), random.choice(SCOOP_FLAVORS)])

            # Player trail: little cream puffs
            px = state["player_x"] + PLAYER_W / 2
            py = HEIGHT - 60 + PLAYER_H / 2
            if moving != 0 and random.random() < 0.8:
                state["particles"].append({
                    "x": px - moving * PLAYER_W * 0.5,
                    "y": py + random.uniform(-4, 4),
                    "vx": -moving * random.uniform(30, 70),
                    "vy": random.uniform(-10, 10),
                    "life": 0.0, "max": random.uniform(0.25, 0.5),
                    "color": CREAM, "size": random.randint(2, 4),
                })

            player_rect = pygame.Rect(int(state["player_x"]), HEIGHT - 60, PLAYER_W, PLAYER_H)
            for sc in state["scoops"]:
                sc[1] += (fall_speed + sc[2] * 0.6) * dt
                sc[3] += dt * 4

            for sc in state["scoops"]:
                pad = sc[2] // 6  # circles are forgiving: shrink hitbox a touch
                scoop_rect = pygame.Rect(int(sc[0]) + pad, int(sc[1]) + pad,
                                         sc[2] - pad * 2, sc[2] - pad * 2)
                if scoop_rect.colliderect(player_rect):
                    state["alive"] = False
                    state["shake"] = 12.0
                    burst(px, py)
                    high_score = max(high_score, state["time_alive"])

            state["scoops"] = [s for s in state["scoops"] if s[1] < HEIGHT + 60]

        if not state["paused"]:
            for p in state["particles"]:
                p["life"] += dt
                p["x"] += p["vx"] * dt
                p["y"] += p["vy"] * dt
                p["vy"] += 60 * dt
            state["particles"] = [p for p in state["particles"] if p["life"] < p["max"]]

            sprinkles[:] = [(x, (y + spd * dt) % HEIGHT, spd, c, t)
                            for x, y, spd, c, t in sprinkles]
            state["shake"] = max(0.0, state["shake"] - 30 * dt)

        # ---------- Draw ----------
        world.blit(sky, (0, 0))

        # Sprinkle rain: tiny tilted capsules
        for x, y, spd, c, tilt in sprinkles:
            pygame.draw.line(world, c, (int(x), int(y)),
                             (int(x + tilt * 8), int(y + 7)), 3)

        for p in state["particles"]:
            fade = 1.0 - p["life"] / p["max"]
            size = max(1, int(p["size"] * fade))
            world.fill(p["color"], (int(p["x"]), int(p["y"]), size, size))

        # Scoops: round, outlined in chocolate, with a shine + drip wobble
        for sc in state["scoops"]:
            cx, cy, r = int(sc[0] + sc[2] / 2), int(sc[1] + sc[2] / 2), sc[2] // 2
            wob = int(math.sin(sc[3]) * 2)
            pygame.draw.circle(world, sc[4], (cx + wob, cy), r)
            pygame.draw.circle(world, CHOCOLATE, (cx + wob, cy), r, 3)
            pygame.draw.circle(world, CREAM, (cx + wob - r // 3, cy - r // 3), max(2, r // 5))

        # Player: strawberry board with chocolate outline and a cherry on top
        px = int(state["player_x"])
        py = HEIGHT - 60
        if state["alive"]:
            hover = math.sin(pygame.time.get_ticks() * 0.006) * 2
            board = pygame.Rect(px, int(py + hover), PLAYER_W, PLAYER_H)
            pygame.draw.rect(world, STRAWBERRY, board, border_radius=8)
            pygame.draw.rect(world, CHOCOLATE, board, 3, border_radius=8)
            pygame.draw.circle(world, CHERRY,
                               (px + PLAYER_W // 2, int(py + hover) - 4), 5)
            pygame.draw.circle(world, CHOCOLATE,
                               (px + PLAYER_W // 2, int(py + hover) - 4), 5, 2)

        # HUD: cream panel with chocolate text
        hud_bg = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
        hud_bg.fill((255, 253, 247, 170))
        world.blit(hud_bg, (0, 0))
        pygame.draw.line(world, CHOCOLATE, (0, 40), (WIDTH, 40), 2)
        world.blit(font.render(f"time {state['time_alive']:5.1f}s", True, CHOCOLATE), (14, 8))
        best = font.render(f"best {high_score:5.1f}s", True, STRAWBERRY_DARK)
        world.blit(best, (WIDTH - best.get_width() - 14, 8))

        if state["paused"] and state["alive"]:
            dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim.fill((255, 246, 233, 170))
            world.blit(dim, (0, 0))
            label = font_big.render("PAUSED", True, CHOCOLATE)
            world.blit(label, label.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        if not state["alive"]:
            dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim.fill((255, 246, 233, 190))
            world.blit(dim, (0, 0))
            over = font_big.render("PLOP!", True, STRAWBERRY_DARK)
            score = font.render(f"you lasted {state['time_alive']:.1f} seconds", True, CHOCOLATE)
            tip = font_small.render("press R for another scoop", True, CHOCOLATE_SOFT)
            world.blit(over, over.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 44)))
            world.blit(score, score.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 6)))
            world.blit(tip, tip.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 38)))

        ox = random.uniform(-state["shake"], state["shake"])
        oy = random.uniform(-state["shake"], state["shake"])
        screen.fill(SKY_TOP)
        screen.blit(world, (int(ox), int(oy)))
        pygame.display.flip()


if __name__ == "__main__":
    main()
