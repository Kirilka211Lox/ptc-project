import pygame
import sys
import random
import math

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Protect the Core")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 22, bold=True)
title_font = pygame.font.SysFont("consolas", 44, bold=True)

COLOR_BG = (18, 22, 28)
COLOR_CORE = (34, 39, 82)
COLOR_CORE_INNER = (50, 23, 173)
COLOR_LASER_TOWER = (74, 15, 20)
COLOR_LASER = (181, 0, 15)
COLOR_ENEMY = (45, 160, 90)
COLOR_WALL = (110, 120, 135)

coins = 0
health_core = 100
max_laser_range = 200
laser_towers = []
weak_enemies = []
walls = []
wall_mode = False
in_main_menu = True

core_rect = pygame.Rect(360, 250, 60, 60)
play_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 - 20, 220, 54)


def add_laser_tower(x, y, health=100):
    tower_info = {
        "rect": pygame.Rect(x, y, 15, 15),
        "health": health
    }
    laser_towers.append(tower_info)


def spawn_weak_enemy(x, y, health=50, speed=1.5):
    enemy_info = {
        "rect": pygame.Rect(x - 10, y - 10, 10, 10),
        "x": float(x - 10),
        "y": float(y - 10),
        "health": health,
        "speed": speed
    }
    weak_enemies.append(enemy_info)


def add_wall(x, y, health=1000):
    wall_info = {
        "rect": pygame.Rect(x - 15, y - 15, 30, 30),
        "health": health
    }
    walls.append(wall_info)


def handle_menu_event(event):
    global in_main_menu
    if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
        in_main_menu = False
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if play_btn_rect.collidepoint(event.pos):
            in_main_menu = False


def handle_game_event(event):
    global wall_mode, in_main_menu
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_e:
            mx, my = pygame.mouse.get_pos()
            spawn_weak_enemy(mx, my)
        elif event.key == pygame.K_w:
            wall_mode = not wall_mode
        elif event.key == pygame.K_ESCAPE:
            in_main_menu = True
    elif event.type == pygame.MOUSEBUTTONDOWN:
        if event.button == 1:
            if wall_mode:
                add_wall(event.pos[0], event.pos[1])
            else:
                add_laser_tower(event.pos[0], event.pos[1])
        elif event.button == 3:
            removed = False
            for wall in walls[:]:
                if wall["rect"].collidepoint(event.pos):
                    walls.remove(wall)
                    removed = True
                    break
            if not removed:
                for tower in laser_towers[:]:
                    if tower["rect"].collidepoint(event.pos):
                        laser_towers.remove(tower)
                        break


def update_game():
    global coins, health_core

    for enemy in weak_enemies[:]:
        angle = math.atan2(core_rect.centery - enemy["rect"].centery,
                           core_rect.centerx - enemy["rect"].centerx)
        #wallhitx
        enemy["x"] += math.cos(angle) * enemy["speed"]
        enemy["rect"].x = round(enemy["x"])
        for wall in walls[:]:
            if enemy["rect"].colliderect(wall["rect"]):
                if math.cos(angle) > 0:
                    enemy["rect"].right = wall["rect"].left
                elif math.cos(angle) < 0:
                    enemy["rect"].left = wall["rect"].right
                enemy["x"] = float(enemy["rect"].x)
                wall["health"] -= 1
                if wall["health"] <= 0:
                    walls.remove(wall)
                break

        #wallhity
        enemy["y"] += math.sin(angle) * enemy["speed"]
        enemy["rect"].y = round(enemy["y"])
        for wall in walls[:]:
            if enemy["rect"].colliderect(wall["rect"]):
                if math.sin(angle) > 0:
                    enemy["rect"].bottom = wall["rect"].top
                elif math.sin(angle) < 0:
                    enemy["rect"].top = wall["rect"].bottom
                enemy["y"] = float(enemy["rect"].y)
                wall["health"] -= 1
                if wall["health"] <= 0:
                    walls.remove(wall)
                break

        if enemy["rect"].colliderect(core_rect):
            health_core -= 10
            weak_enemies.remove(enemy)
            continue

        for tower in laser_towers[:]:
            if enemy["rect"].colliderect(tower["rect"]):
                tower["health"] -= 1
                enemy["x"] -= math.cos(angle) * enemy["speed"] * 2
                enemy["y"] -= math.sin(angle) * enemy["speed"] * 2
                enemy["rect"].topleft = (round(enemy["x"]), round(enemy["y"]))
                if tower["health"] <= 0:
                    laser_towers.remove(tower)
                break
#awfully done enemy separation i'll never do it again i spent like 2 hours on this :cry:
    cell_size = 40
    grid = {}
    for idx, enemy in enumerate(weak_enemies):
        cx = int(enemy["rect"].centerx // cell_size)
        cy = int(enemy["rect"].centery // cell_size)
        grid.setdefault((cx, cy), []).append(idx)

    min_spacing = 10
    checked_pairs = set()
    for (cx, cy), indices in grid.items():
        neighbor_indices = []
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                neighbor_indices.extend(grid.get((cx + ox, cy + oy), ()))

        for i in indices:
            a = weak_enemies[i]
            for j in neighbor_indices:
                if i == j:
                    continue
                pair = (i, j) if i < j else (j, i)
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)

                b = weak_enemies[j]
                dx = b["x"] - a["x"]
                dy = b["y"] - a["y"]
                dist_sq = dx * dx + dy * dy
                if 0 < dist_sq < min_spacing * min_spacing:
                    dist = math.sqrt(dist_sq)
                    overlap = (min_spacing - dist) * 0.5
                    nx = dx / dist
                    ny = dy / dist
                    a["x"] -= nx * overlap
                    a["y"] -= ny * overlap
                    b["x"] += nx * overlap
                    b["y"] += ny * overlap
                    a["rect"].topleft = (round(a["x"]), round(a["y"]))
                    b["rect"].topleft = (round(b["x"]), round(b["y"]))
                elif dist_sq == 0:
                    a["x"] -= 0.5
                    b["x"] += 0.5
                    a["rect"].topleft = (round(a["x"]), round(a["y"]))
                    b["rect"].topleft = (round(b["x"]), round(b["y"]))

    if health_core < 0:
        health_core = 0


def draw_menu():
    screen.fill(COLOR_BG)
    pygame.draw.rect(screen, COLOR_CORE, core_rect, border_radius=5)
    pygame.draw.rect(screen, COLOR_CORE_INNER, (370, 260, 40, 40), border_radius=5)

    title_surf = title_font.render("PROTECT THE CORE", True, (235, 240, 250))
    screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 145)))

    hover = play_btn_rect.collidepoint(pygame.mouse.get_pos())
    btn_color = (65, 85, 130) if hover else (42, 54, 82)
    pygame.draw.rect(screen, btn_color, play_btn_rect, border_radius=8)
    pygame.draw.rect(screen, (130, 155, 205), play_btn_rect, 2, border_radius=8)

    label_surf = font.render("PLAY (ENTER)", True, (245, 248, 255))
    screen.blit(label_surf, label_surf.get_rect(center=play_btn_rect.center))


def draw_game():
    global coins

    screen.fill(COLOR_BG)

    #something odd range draw
    if len(laser_towers) % 2 == 1:
        last_tower_center = laser_towers[-1]["rect"].center
        pygame.draw.circle(screen, (60, 70, 85), last_tower_center, max_laser_range, 1)

    #testinglasertowers ok now its drawing stuff not only lasertowers

    for enemy in weak_enemies:
        pygame.draw.rect(screen, COLOR_ENEMY, enemy["rect"])

    for wall in walls:
        pygame.draw.rect(screen, COLOR_WALL, wall["rect"])

    for tower in laser_towers:
        pygame.draw.rect(screen, COLOR_LASER_TOWER, tower["rect"])

    #laser draw
    connections = [0] * len(laser_towers)
    for i in range(len(laser_towers)):
        #keep going if not second guy
        if connections[i] >= 2:
            continue
        for j in range(i + 1, len(laser_towers)):
            #stop if second guy
            if connections[i] >= 3:
                break
            if connections[j] >= 3:
                continue
            start_pos = laser_towers[i]["rect"].center
            end_pos = laser_towers[j]["rect"].center
            if math.dist(start_pos, end_pos) <= max_laser_range:
                connections[i] += 1
                connections[j] += 1
                #draw laser yay difficult part done
                #outlaser
                pygame.draw.line(screen, COLOR_LASER, start_pos, end_pos, random.randint(3, 6))
                #inlasesr
                pygame.draw.line(screen, (255, 200, 200), start_pos, end_pos, 1)
                #---_rect.clipline - clippin with enemis
                for enemy in weak_enemies[:]:
                    if enemy["rect"].clipline(start_pos, end_pos):
                        enemy["health"] -= 3
                        if enemy["health"] <= 0:
                            weak_enemies.remove(enemy)
                            coins += 5
    if health_core <= 0:
        win_surf = font.render("lost", True, COLOR_LASER)
        banner_rect = win_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
        pygame.draw.rect(screen, (20, 30, 40), banner_rect.inflate(20, 10), border_radius=6)
        screen.blit(win_surf, banner_rect)

    hp_core_surf = font.render(str(health_core), True, COLOR_LASER)
    banner2_rect = hp_core_surf.get_rect(center=(390, 240))
    pygame.draw.rect(screen, COLOR_BG, banner2_rect.inflate(20, 10))
    screen.blit(hp_core_surf, banner2_rect)

    pygame.draw.rect(screen, COLOR_CORE, (360, 250, 60, 60), border_radius=5)
    pygame.