import pygame
import random
import math
import copy
import collections
import pickle 
import os 
import csv
import multiprocessing  

# --- KONFIGURACJA KOLORÓW ---
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
SCARED_BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 183, 174)
RED = (255, 0, 0)
PINK = (255, 105, 180)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
GREEN = (0, 255, 0)

# --- STAŁE ---
TILE_SIZE = 30
PLAYER_SPEED = 3 
UI_HEIGHT = 60 
SCARED_DURATION = 300

# MAPA (Zostawiamy tylko szablon, kopie będą tworzone wewnątrz procesów)
GAME_MAP_TEMPLATE = [
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 4, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 4, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 2, 1, 1, 0, 1, 0, 1, 1, 1, 1], 
    [0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0], 
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 4, 0, 1, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 1, 0, 4, 1],
    [1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1],
]

# --- PARAMETRY OKNA I MAPY ---
WIDTH_TILES = len(GAME_MAP_TEMPLATE[0])
HEIGHT_TILES = len(GAME_MAP_TEMPLATE)
GAME_WIDTH = WIDTH_TILES * TILE_SIZE
GAME_HEIGHT = HEIGHT_TILES * TILE_SIZE
SCREEN_WIDTH = GAME_WIDTH
SCREEN_HEIGHT = GAME_HEIGHT + (UI_HEIGHT * 2)

# --- PARAMETRY AI PACMAN ---
EPSILON_DECAY = 0.9999  
MAX_DEPTH = 5

def pre_render_map(surface, grid):
    """Renderuje ściany na podanej powierzchni na podstawie dostarczonej mapy."""
    surface.fill(BLACK)
    for r, row in enumerate(grid):
        for c, tile in enumerate(row):
            x, y = c * TILE_SIZE, r * TILE_SIZE
            if tile == 1:
                # Rysujemy niebieskie obramowania ścian
                pygame.draw.rect(surface, BLUE, (x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4), 2)

def get_bfs_direction_to_food(start_pos, grid):
    """
    Znajduje najkrótszą drogę do najbliższej kropki i zwraca 
    indeks pierwszego ruchu (0: góra, 1: dół, 2: lewo, 3: prawo).
    """
    start_x, start_y = start_pos

    # Podstawowe sprawdzenie bezpieczeństwa
    if not (0 <= start_x < WIDTH_TILES and 0 <= start_y < HEIGHT_TILES): 
        return None
    if grid[start_y][start_x] == 1: # Jeśli Pac-Man utknął w ścianie (bug)
        return None

    queue = collections.deque([(start_x, start_y, [])])
    visited = set()
    visited.add((start_x, start_y))

    # Deltas zgodne z Twoją listą actions: 0: Up, 1: Down, 2: Left, 3: Right
    deltas = [(0, -1, 0), (0, 1, 1), (-1, 0, 2), (1, 0, 3)]
    
    while queue:
        cx, cy, path = queue.popleft()

        # Sprawdzamy, czy tu jest jedzenie (0: mała kropka, 4: duża kropka)
        if grid[cy][cx] in [0, 4]: 
            if not path: 
                return None # Już stoimy na kropce
            return path[0] # Zwracamy indeks pierwszego ruchu na ścieżce
        
        for dx, dy, move_idx in deltas:
            nx = (cx + dx) % WIDTH_TILES
            ny = (cy + dy) % HEIGHT_TILES

            # Sprawdzamy granice mapy i czy nie wchodzimy w ścianę (1)
            if 0 <= nx < WIDTH_TILES and 0 <= ny < HEIGHT_TILES:
                if grid[ny][nx] != 1 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    new_path = list(path)
                    new_path.append(move_idx)
                    queue.append((nx, ny, new_path))
    return None

# --- AI AGENT (Z MODUŁEM PAMIĘCI) ---
class QLearningAgent:
    def __init__(self, actions, sim_id=0):
        self.actions = actions
        self.q_table = {}
        self.epsilon = 1.0           # Początkowa eksploracja
        self.epsilon_min = 0.05      # Minimalna losowość
        self.alpha = 0.3            # Współczynnik uczenia (learning rate)
        self.gamma = 0.97            # Współczynnik dyskontowania (patrzenie w przyszłość)
        
        # Unikalna ścieżka dla każdego procesu
        self.brain_file = f"AI_pacman\\brain_{sim_id}.pkl"

    def get_true_distance(self, pacman_pos, target_pos, current_map, max_depth=5):
        """
        Zoptymalizowany pod Twój current_map BFS.
        """
        # 1. Toroidal Manhattan (uwzględnia tunele!)
        # Liczymy krótszy dystans: albo normalnie w poprzek mapy, albo przez tunel na zewnątrz.
        dx = abs(pacman_pos[0] - target_pos[0])
        dy = abs(pacman_pos[1] - target_pos[1])
        wrap_dx = min(dx, WIDTH_TILES - dx)
        wrap_dy = min(dy, HEIGHT_TILES - dy)

        # Szybki test Manhattana
        manhattan_dist = wrap_dx + wrap_dy

        if manhattan_dist > max_depth:
            return 999 

        queue = collections.deque([(pacman_pos, 0)])
        visited = set()
        visited.add(pacman_pos)
        
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        while queue:
            current_pos, dist = queue.popleft()

            if current_pos == target_pos:
                return dist

            if dist >= max_depth:
                continue 

            for dx, dy in directions:
                nx = (current_pos[0] + dx) % WIDTH_TILES
                ny = (current_pos[1] + dy) % HEIGHT_TILES
                
                # Używamy Twojej tablicy current_map (1 to ściana) - ultraszybkie!
                if current_map[ny][nx] != 1 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), dist + 1))
                        
        return 999 

    def get_state(self, player, ghosts, is_scared_global, bfs_suggested_action, current_map):
        """
        Ultra-prosty mózg nastawiony TYLKO na żarcie. Max 64 stany.
        """
        px, py = int(player.x // TILE_SIZE), int(player.y // TILE_SIZE)
        
        # 1. ŚCIANY (Z obsługą tuneli)
        walls = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = (px + dx) % WIDTH_TILES, (py + dy) % HEIGHT_TILES
            walls.append(current_map[ny][nx] == 1)
        
        wall_state = tuple(walls)

        # 2. GPS DO JEDZENIA (Zwraca indeks 0-3, albo -1 jak nie ma jedzenia)
        food_dir = bfs_suggested_action if bfs_suggested_action is not None else -1

        # 3. RADAR ZAGROŻENIA (BFS z obsługą tuneli)
        threat_up = 0
        threat_down = 0
        threat_left = 0
        threat_right = 0

        for g in ghosts:
            gx, gy = int(g.x // TILE_SIZE), int(g.y // TILE_SIZE)
            dist = self.get_true_distance((px, py), (gx, gy), current_map, max_depth=MAX_DEPTH)

            if dist <= 4:
                threat_level = 2 if dist <= 2 else 1

                dx = gx - px
                dy = gy - py

                if dx > WIDTH_TILES / 2: dx -= WIDTH_TILES
                elif dx < -WIDTH_TILES / 2: dx += WIDTH_TILES

                if dy > HEIGHT_TILES / 2: dy -= HEIGHT_TILES
                elif dy < -HEIGHT_TILES / 2: dy += HEIGHT_TILES

                # Zapalamy odpowiednią lampkę alarmową
                if abs(dx) > abs(dy):
                    if dx > 0: threat_right = max(threat_right, threat_level)
                    else: threat_left = max(threat_left, threat_level)
                else:
                    if dy > 0: threat_down = max(threat_left, threat_level)
                    else: threat_up = max(threat_left, threat_level)

        danger_zone = (threat_up, threat_down, threat_left, threat_right)

        return (wall_state, food_dir, danger_zone, is_scared_global)

    def choose_action(self, state, valid_moves):
        if state not in self.q_table:
            self.q_table[state] = [0.0] * len(self.actions)
        
        if random.random() < self.epsilon: 
            return random.choice(valid_moves)

        q_values = self.q_table[state]
        best_val = -float('inf')
        best_action = random.choice(valid_moves)

        for idx in valid_moves:
            if q_values[idx] > best_val:
                best_val = q_values[idx]
                best_action = idx
        return best_action

    def learn(self, state, action_idx, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = [0.0] * len(self.actions)
        if next_state not in self.q_table:
            self.q_table[next_state] = [0.0] * len(self.actions)
            
        old_v = self.q_table[state][action_idx]
        next_max = max(self.q_table[next_state])
        
        self.q_table[state][action_idx] = old_v + self.alpha * (reward + self.gamma * next_max - old_v)

    def save_brain(self):
        try:
            folder = os.path.dirname(self.brain_file)
            if folder:
                os.makedirs(folder, exist_ok=True)

            with open(self.brain_file, "wb") as f:
                pickle.dump(self.q_table, f)
            return True
        except Exception as e:
            print(f"Błąd zapisu: {e}")
            return False

    def load_brain(self):
        if os.path.exists(self.brain_file):
            try:
                with open(self.brain_file, "rb") as f:
                    self.q_table = pickle.load(f)
                self.epsilon = 0.05 
                return True
            except Exception as e:
                print(f"Błąd odczytu mózgu: {e}")
                return False
        return False
            
    def reset_brain(self):
        self.q_table = {}
        self.epsilon = 1

# --- KLASY OBIEKTÓW ---
class Ghost:
    def __init__(self, grid_x, grid_y, color, start_delay=0):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.start_grid_x = grid_x
        self.start_grid_y = grid_y
        self.x = grid_x * TILE_SIZE + 2
        self.y = grid_y * TILE_SIZE + 2
        self.color = color
        self.speed = 2
        self.direction = (0, 0)
        self.rect = pygame.Rect(self.x, self.y, TILE_SIZE - 4, TILE_SIZE - 4)
        self.delay_timer = start_delay
        self.is_scared = False 

    def move(self, player, mode, current_map):
        # 1. Logika oczekiwania w "domku"
        if self.delay_timer > 0:
            self.delay_timer -= 1
            base_y = self.start_grid_y * TILE_SIZE + 2
            if self.delay_timer % 40 < 20: self.y = base_y - 2
            else: self.y = base_y + 2
            self.rect.topleft = (self.x, self.y)
            return

        # 2. Obsługa tuneli (przechodzenie przez krawędzie)
        if self.rect.right < 0: self.x = GAME_WIDTH - self.rect.width
        elif self.rect.left > GAME_WIDTH: self.x = 0
        if self.rect.bottom < 0: self.y = GAME_HEIGHT - self.rect.height
        elif self.rect.top > GAME_HEIGHT: self.y = 0
        
        if 9 <= (self.y // TILE_SIZE) <= 11 and 8 * TILE_SIZE < self.x < 11 * TILE_SIZE:
            door_center_x = 9 * TILE_SIZE + 2
            if self.x < door_center_x: self.x += self.speed
            elif self.x > door_center_x: self.x -= self.speed
            if abs(self.x - door_center_x) <= self.speed:
                self.x = door_center_x
                self.y -= self.speed
                self.direction = (0, -1)
            self.rect.topleft = (self.x, self.y)
            return

        # 4. Wybór kierunku na skrzyżowaniach (centrum kafelka)
        if self.x % TILE_SIZE == 2 and self.y % TILE_SIZE == 2:
            possible = []
            check = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for d in check:
                nx = int((self.x // TILE_SIZE) + d[0])
                ny = int((self.y // TILE_SIZE) + d[1])

                if 0 <= nx < WIDTH_TILES and 0 <= ny < HEIGHT_TILES:
                    if current_map[ny][nx] != 1: # Jeśli nie ściana
                        if d[0] != -self.direction[0] or d[1] != -self.direction[1]:
                            possible.append(d)

            if not possible: possible = check

            if possible:
                target_x, target_y = None, None

                if self.is_scared:
                    self.direction = random.choice(possible)
                elif mode == "SCATTER":
                    self.direction = random.choice(possible)
                else:
                    if self.color == RED: 
                        target_x, target_y = player.x, player.y
                    elif self.color == PINK: 
                        target_x = player.x + (player.direction[0] * TILE_SIZE * 4)
                        target_y = player.y + (player.direction[1] * TILE_SIZE * 4)
                    elif self.color == ORANGE:
                        if math.hypot(self.x-player.x, self.y-player.y) > 5*TILE_SIZE:
                            target_x, target_y = player.x, player.y
                        else: self.direction = random.choice(possible)
                    elif self.color == CYAN: 
                        self.direction = random.choice(possible)

                    if target_x is not None:
                        best_move = possible[0]
                        min_dist = float('inf')
                        for d in possible:
                            test_x = self.x + d[0] * TILE_SIZE
                            test_y = self.y + d[1] * TILE_SIZE
                            dist = abs(test_x - target_x) + abs(test_y - target_y)
                            if dist < min_dist:
                                min_dist = dist
                                best_move = d
                        self.direction = best_move

        # 5. Wykonanie ruchu
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        c = SCARED_BLUE if self.is_scared else self.color
        pygame.draw.rect(surface, c, self.rect, border_radius=4)
            
class Player:
    def __init__(self, map_template):
        self.speed = PLAYER_SPEED
        self.lives = 3
        self.score = 0
        self.mouth_open_angle = 0
        self.mouth_speed = 5
        self.mouth_closing = False

        # Szukanie punktu spawnu (3) w szablonie mapy
        self.spawn_grid_x, self.spawn_grid_y = 0, 0
        for r, row in enumerate(map_template):
            for c, tile in enumerate(row):
                if tile == 3:
                    self.spawn_grid_x, self.spawn_grid_y = c, r
        self.spawn()
    
    def spawn(self):
        self.x = self.spawn_grid_x * TILE_SIZE + 2
        self.y = self.spawn_grid_y * TILE_SIZE + 2
        self.rect = pygame.Rect(self.x, self.y, 26, 26)
        self.direction = (0, 0)
        self.next_direction = (0, 0)

    def move(self, current_map, walls_list):
        """
        Zwraca: (score_gain, dots_eaten, scared_trigger)
        """
        score_gain = 0
        dots_eaten = 0
        scared_trigger = False

        # 1. Animacja buzi
        if self.direction != (0, 0):
            if self.mouth_closing:
                self.mouth_open_angle -= self.mouth_speed
                if self.mouth_open_angle <= 0: self.mouth_closing = False
            else:
                self.mouth_open_angle += self.mouth_speed
                if self.mouth_open_angle >= 45: self.mouth_closing = True

        # 2. Tunele (wrap around)
        if self.rect.right < 0: self.x = GAME_WIDTH - 26
        elif self.rect.left > GAME_WIDTH: self.x = -26
        if self.rect.bottom < 0: self.y = GAME_HEIGHT - 26
        elif self.rect.top > GAME_HEIGHT: self.y = 0

        # 3. Logika skręcania (próba zmiany kierunku w centrum kafelka)
        if self.next_direction != (0, 0):
            cc, cr = round(self.x / TILE_SIZE), round(self.y / TILE_SIZE)
            tx, ty = cc * TILE_SIZE + 2, cr * TILE_SIZE + 2
            nx, ny = cc + self.next_direction[0], cr + self.next_direction[1]
            
            if 0 <= ny < HEIGHT_TILES and 0 <= nx < WIDTH_TILES:
                if current_map[ny][nx] != 1: # Jeśli nie ściana
                    # Snapping do kafelka przy skręcie
                    if (self.next_direction[0] == 0 and abs(self.x - tx) < 10) or \
                       (self.next_direction[1] == 0 and abs(self.y - ty) < 10):
                        self.x, self.y = tx, ty
                        self.direction = self.next_direction
                        self.next_direction = (0, 0)
        
        # 4. Fizyczny ruch i kolizje ze ścianami
        old_pos = (self.x, self.y)
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        
        self.rect.topleft = (self.x, self.y)
        if self.rect.collidelist(walls_list) != -1:
            self.x, self.y = old_pos
            self.rect.topleft = (self.x, self.y)

        # 5. Zjadanie kropek
        gx, gy = int((self.x + 13) // 30), int((self.y + 13) // 30)
        if 0 <= gx < WIDTH_TILES and 0 <= gy < HEIGHT_TILES:
            tile = current_map[gy][gx]
            
            if tile == 0:  # Zwykła kropka
                current_map[gy][gx] = 2 # Zmieniamy na "puste"
                score_gain = 10
                dots_eaten = 1
                # Epsilon decay przy każdej kropce
                # agent.epsilon = max(agent.epsilon_min, agent.epsilon * agent.epsilon_decay)
                
            elif tile == 4: # Duża kropka (Power Pellet)
                current_map[gy][gx] = 2
                score_gain = 50
                dots_eaten = 1
                scared_trigger = True
                # Duży skok pewności siebie (zmniejszenie losowości)
                # agent.epsilon = max(agent.epsilon_min, agent.epsilon * 0.95)

        return score_gain, dots_eaten, scared_trigger

    def draw(self, surface):
        center = self.rect.center
        pygame.draw.circle(surface, YELLOW, center, 13)

        if self.direction == (0, 0): return

        cx, cy = center
        offset = self.mouth_open_angle / 2

        if self.direction == (1, 0): p2, p3 = (cx+15, cy-offset), (cx+15, cy+offset)
        elif self.direction == (-1, 0): p2, p3 = (cx-15, cy-offset), (cx-15, cy+offset)
        elif self.direction == (0, -1): p2, p3 = (cx-offset, cy-15), (cx+offset, cy-15)
        elif self.direction == (0, 1): p2, p3 = (cx-offset, cy+15), (cx+offset, cy+15)
        else: return
        pygame.draw.polygon(surface, BLACK, [center, p2, p3])

def draw_pellets(surface, current_map):
    """Rysuje małe i duże kropki na podstawie aktualnego stanu mapy."""
    for r, row in enumerate(current_map):
        for c, tile in enumerate(row):
            # Obliczamy środek kafelka
            pos = (c * TILE_SIZE + 15, r * TILE_SIZE + 15)

            if tile == 0:
                # Mała kropka
                pygame.draw.circle(surface, WHITE, pos, 3)
            elif tile == 4:
                # Duża kropka (Power Pellet)
                pygame.draw.circle(surface, WHITE, pos, 8)

def draw_ui(screen, sim_id, score, epsilon, total_reward, lives, ui_message, font, small_font):
    """Rysuje górny i dolny pasek interfejsu z unikalnymi danymi dla danej symulacji."""
    
    # 1. Górny pasek - Tło i separator
    pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, UI_HEIGHT))
    pygame.draw.line(screen, BLUE, (0, UI_HEIGHT-1), (SCREEN_WIDTH, UI_HEIGHT-1), 2)
    
    # Informacje o symulacji i instrukcje
    id_txt = f"SIM ID: {sim_id} | [S] Save [L] Load [R] Reset"
    instr = small_font.render(id_txt, True, WHITE)
    screen.blit(instr, (20, 10))

    # Komunikaty systemowe (np. "Zapisano mózg")
    if ui_message:
        msg = small_font.render(ui_message, True, GREEN)
        screen.blit(msg, (20, 35))

    # 2. Dolny pasek - Tło i separator
    bottom_y = SCREEN_HEIGHT - UI_HEIGHT
    pygame.draw.rect(screen, BLACK, (0, bottom_y, SCREEN_WIDTH, UI_HEIGHT))
    pygame.draw.line(screen, BLUE, (0, bottom_y), (SCREEN_WIDTH, bottom_y), 2)

    # Statystyki AI
    score_text = font.render(f"SCORE: {score}", True, WHITE)
    screen.blit(score_text, (20, bottom_y + 18))
    
    eps_text = font.render(f"EPS: {epsilon:.4f}", True, CYAN)
    screen.blit(eps_text, (200, bottom_y + 18))
    
    rew_text = font.render(f"REW: {total_reward:.0f}", True, WHITE)
    screen.blit(rew_text, (400, bottom_y + 18))

    # Życia (żółte kółka)
    for i in range(lives):
        lx = SCREEN_WIDTH - 40 - (i * 30)
        ly = bottom_y + 30
        pygame.draw.circle(screen, YELLOW, (lx, ly), 10)

def get_valid_moves(player, current_map):
    """
    Zwraca listę indeksów ruchów (0-3), które nie prowadzą w ścianę.
    """
    moves = []
    # Wyliczamy aktualną pozycję na siatce
    px, py = round(player.x / TILE_SIZE), round(player.y / TILE_SIZE)

    # Kierunki: 0: Góra, 1: Dół, 2: Lewo, 3: Prawo
    check_dirs = [(0, -1, 0), (0, 1, 1), (-1, 0, 2), (1, 0, 3)]

    for dx, dy, idx in check_dirs:
        nx, ny = (px + dx) % WIDTH_TILES, (py + dy) % HEIGHT_TILES

        # 1. Obsługa tunelu: jeśli wyjdzie poza szerokość, pozwól na ruch (teleportacja)
        if not (0 <= nx < WIDTH_TILES):
            moves.append(idx)
            continue

        # 2. Sprawdzenie ścian na lokalnej mapie procesu
        if 0 <= ny < HEIGHT_TILES:
            if current_map[ny][nx] != 1:
                moves.append(idx)
    return moves

def log_to_csv(sim_id, episode_num, score, total_reward, epsilon, q_table_size, dots_left):
    """
    Zapisuje statystyki epizodu do osobnego pliku CSV dla każdej symulacji.
    """
    file_path = f"AI_pacman\\analysis\\stats_sim_{sim_id}.csv"
    
    # Sprawdzamy czy plik istnieje, aby wiedzieć czy dopisać nagłówek
    # file_exists = os.path.isfile(file_path)

    try:
        with open(file_path, "a", newline="") as f:
            writer = csv.writer(f)


            # if not file_exists:
            #     writer.writerow(["Episode", "Score", "Total Reward", "Epsilon", "States_Discovered", "Dots Left"])
            # Zapisujemy dane (zaokrąglamy dla czytelności pliku)
            writer.writerow([
                episode_num, 
                score, 
                round(total_reward, 2), 
                round(epsilon, 4), 
                q_table_size, 
                dots_left
            ])
    except Exception as e:
        print(f"[SIM {sim_id}] Błąd zapisu CSV: {e}")

def start_sim(sim_id, use_graphics=False):
    # --- LOGIKA I PUNKTACJA ---
    score = 0                     # Bieżący wynik punktowy w danej rundzie
    old_score = 0                 # Wynik z poprzedniej klatki (potrzebny do obliczania różnicy nagrody)
    game_stats = {                # Słownik przechowujący dane o nagrodach dla Agenta
        "current_reward": 0, 
        "total_reward": 0
    }
    
    # --- ŚWIAT GRY ---
    current_map = copy.deepcopy(GAME_MAP_TEMPLATE) # Indywidualna kopia mapy dla tego procesu
    dots_left = 0                 # Licznik kropek pozostałych na planszy (cel: 0)
    walls_list = []               # Lista obiektów Rect ścian do wykrywania kolizji
    
    # --- DUCHY ---
    ghosts = []                   # Lista przechowująca obiekty klasy Ghost
    ghost_mode = "CHASE"          # Aktualny tryb zachowania duchów (CHASE lub SCATTER)
    mode_timer = 0                # Licznik klatek do następnej zmiany trybu duchów
    scared_mode = False           # Flaga: czy duchy są obecnie niebieskie (można je jeść)
    scared_timer = 0              # Czas pozostały do końca trybu "przestraszonych" duchów
    
    # --- PAMIĘĆ AGENTA (Q-LEARNING) ---
    last_state = None             # Stan, w którym Agent był przed podjęciem ostatniego ruchu
    last_action_idx = None        # Indeks akcji (0-3), którą Agent właśnie wykonał
    
    # --- SYSTEMY MONITORINGU I REKORDÓW ---
    ui_message = ""               # Tekst wyświetlany w UI (np. "ZAPISANO MÓZG!")
    episode_count = 0             # Numer aktualnej gry (epizodu) w tej symulacji
    wins_count = 0                # # Inicjalizacja licznika wygranych dla konkretnego SIM-a
    last_saved_q_size = 0         # Rozmiar tabeli Q podczas ostatniego autozapisu
    dots_history = collections.deque(maxlen=500) # Tu trzymamy ostatnie 500 wyników
    avg_dots = 999
    knowledge_milestone = 20      # Próg nowych stanów, po którym następuje zapis mózgu
    best_q_table = None           # Kopia tabeli Q z najlepszej dotychczasowej próby
    best_dots_ever = 999          # Najmniejsza liczba kropek, jaka została na mapie (rekord sim)

    # 2. KONFIGURACJA GRAFIKI (Tylko jeśli use_graphics=True)
    screen = None
    clock = None
    font = None
    small_font = None
    map_bg_surface = None
    game_surface = None

    if use_graphics:
        pygame.init()
        pygame.font.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"Pac-Man AI | SIM ID: {sim_id}")
        clock = pygame.time.Clock()
        font = pygame.font.SysFont('arial', 24, bold=True)
        small_font = pygame.font.SysFont('arial', 16, bold=False)
        
        # Powierzchnie do rysowania
        map_bg_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT)).convert()
        game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT)).convert()

    # 3. OBIEKTY AGENTA I GRACZA
    actions = [(0, -1), (0, 1), (-1, 0), (1, 0)] 
    agent = QLearningAgent(actions, sim_id)
    player = Player(GAME_MAP_TEMPLATE)

    # 4. DEFINICJA RESETU (Twoja funkcja z obrazka, teraz już poprawna)
    def reset_game_round():
        nonlocal score, current_map, ghosts, ghost_mode, mode_timer
        nonlocal scared_mode, scared_timer, dots_left, last_state, last_action_idx
        nonlocal walls_list, game_stats, old_score

        score = 0
        old_score = 0
        game_stats["total_reward"] = 0
        current_map = copy.deepcopy(GAME_MAP_TEMPLATE)
        dots_left = sum(r.count(0) + r.count(4) for r in current_map)
        
        player.spawn()
        
        # Budujemy listę ścian dla tego konkretnego procesu
        walls_list = []
        for r, row in enumerate(current_map):
            for c, tile in enumerate(row):
                if tile == 1:
                    rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    walls_list.append(rect)
        
        if use_graphics:
            pre_render_map(map_bg_surface, current_map)

        gx, gy = 9, 10
        ghosts = [
            Ghost(gx, 9, RED, 0), 
            Ghost(gx, 10, PINK, 60),
            Ghost(8, 10, CYAN, 120)
            #Ghost(10, 10, ORANGE, 180)
        ]
        ghost_mode = "CHASE"
        mode_timer = 0
        scared_mode = False
        scared_timer = 0
        last_state = None
        last_action_idx = None

    # PIERWSZE URUCHOMIENIE RESETU
    reset_game_round()

    # 5. PARAMETRY CZASOWE (Lokalne dla procesu)
    CHANGE_MODE_TIME = 300
    total_dots_start = dots_left # Zapamiętujemy ile było kropek na początku


    # Nadpisywanie plików co kolejne odpalenie programu
    file_path = f"AI_pacman\\analysis\\stats_sim_{sim_id}.csv"

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Episode", "Score", "Total Reward", "Epsilon", "States_Discovered", "Dots Left"])

    running = True
    while running:
        # A. OBSŁUGA ZDARZEŃ
        if use_graphics:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        if agent.save_brain(): ui_message = "ZAPISANO MÓZG!"
                    if event.key == pygame.K_l:
                        if agent.load_brain(): ui_message = "WCZYTANO MÓZG!"
                    if event.key == pygame.K_r:
                        agent.reset_brain(); ui_message = "RESET MÓZGU!"
        else:
            # Procesy w tle nie sprawdzają klawiatury, żeby nie marnować czasu
            pass

        # B. LOGIKA AI (Co 30 pikseli - środek kafelka)
        if player.x % TILE_SIZE == 2 and player.y % TILE_SIZE == 2:
            cx, cy = int(player.x // 30), int(player.y // 30)
            bfs_hint = get_bfs_direction_to_food((cx, cy), current_map)
            
            # Pobieramy stan i wybieramy akcję
            curr_state = agent.get_state(player, ghosts, scared_mode, bfs_hint, current_map)
            valid_moves = get_valid_moves(player, current_map)
            action_idx = agent.choose_action(curr_state, valid_moves)
            
            player.next_direction = actions[action_idx]

            # Nauka na podstawie poprzedniego ruchu
            if last_state is not None:
                agent.learn(last_state, last_action_idx, game_stats["current_reward"], curr_state)
            
            last_state = curr_state
            last_action_idx = action_idx

        # C. RUCH PAC-MANA
        s_gain, d_eaten, s_trigger = player.move(current_map, walls_list)
        score += s_gain
        dots_left -= d_eaten
        if s_trigger:
            scared_mode = True
            scared_timer = SCARED_DURATION
            for g in ghosts: g.is_scared = True

        # D. LOGIKA DUCHÓW I KOLIZJE
        if scared_mode:
            scared_timer -= 1
            if scared_timer <= 0:
                scared_mode = False
                for g in ghosts: g.is_scared = False
        else:
            mode_timer += 1
            if mode_timer >= CHANGE_MODE_TIME:
                mode_timer = 0
                ghost_mode = "SCATTER" if ghost_mode == "CHASE" else "CHASE"

        hit = False
        for g in ghosts:
            g.move(player, ghost_mode, current_map)
            if player.rect.colliderect(g.rect):
                if g.is_scared:
                    score += 250
                    g.x, g.y = g.start_grid_x * TILE_SIZE + 2, g.start_grid_y * TILE_SIZE + 2
                    g.delay_timer = 60
                else:
                    hit = True

        # E. OBLICZANIE NAGRODY (REWARD)
        score_diff = score - old_score
        reward = 0
        
        if hit:
            reward -= 1650
        elif score_diff > 0: 
            reward += 10
        # else: 
        #     # Jeśli nie je, to musi chociaż iść w stronę jedzenia
        #     if bfs_hint is not None and player.direction == actions[bfs_hint]:
        #         reward += 2   # Głaskanie po głowie: "dobrze idziesz, kontynuuj"
        #     else:
        #         reward = -5  # Bolesna kara: "nie stój, nie błądź, czas to pieniądz!"
        
        game_stats["current_reward"] = reward
        game_stats["total_reward"] += reward
        old_score = score

        # F. KONIEC RUNDY (LOGIKA MISTRZA)
        if hit or dots_left == 0:
            episode_count += 1
            dots_history.append(dots_left) # Dodajemy wynik do historii

            if hit:
                if last_state: 
                    dead_state = agent.get_state(player, ghosts, scared_mode, None, current_map)
                    agent.learn(last_state, last_action_idx, -500, dead_state)
            else:
                wins_count += 1
                if last_state: agent.learn(last_state, last_action_idx, 1000, last_state)
                #print(f">>> [SIM {sim_id}] WYGRANA nr {wins_count}! Epizod: {episode_count}")    

            # System rekordów i zapisu
            if dots_left < best_dots_ever:
                best_dots_ever = dots_left
                best_q_table = copy.deepcopy(agent.q_table)
                agent.save_brain()
                if dots_left > 0:
                    print(f">>> [SIM {sim_id}] Nowy rekord: zostało tylko {dots_left} kropek!")   

            # 3. Raportowanie co 250 gier
            if episode_count % 250 == 0:
                print(f">>> [SIM {sim_id}] Gra: {episode_count} | EPS: {agent.epsilon:.3f} | States: {len(agent.q_table)}")

            # 4. JEDEN spadek epsilonu
            agent.epsilon = max(agent.epsilon_min, agent.epsilon * EPSILON_DECAY) 

            # 5. Logika ratunkowa
            # Lekki restart: powrót do Mistrza i EPS 0.5
            
            # if episode_count >= 1000 and episode_count % 500 == 0:
            #     if episode_count % 1000 == 0:
            #         agent.alpha = max(0.01, agent.alpha * 0.9999)
            #     old_avg_dots = avg_dots
            #     avg_dots = sum(dots_history) / len(dots_history)

            #     if episode_count % 2500 == 0 and avg_dots > 155:
            #             agent.epsilon = 0.8
            #             print(f"🔥 [SIM {sim_id}] HARD RESET (Epizod {episode_count})! Średnia {avg_dots:.1f} to dramat. Szukamy wszystkiego od zera.")

            #     should_reset = avg_dots > 152 or (avg_dots >= old_avg_dots and avg_dots > 50)
                
            #     # if should_reset:
            #     #     print(f">>> [SIM {sim_id}] KRYZYS STATYSTYCZNY! Średnia: {avg_dots:.1f} dots.")
                    
            #     #     if best_q_table is not None:
            #     #         # Wracamy do mistrza, bo obecna ścieżka ewolucji to ślepy zaułek
            #     #         agent.q_table = copy.deepcopy(best_q_table)
            #     #         agent.epsilon = 0.3
            #     #         print(f"   -> Przywrócono Mistrza i podbito EPS do 0.3")
            #     #     else:
            #     #         # Jeśli nie ma mistrza, po prostu dajemy potężną dawkę losowości
            #     #         agent.epsilon = 0.7
            #     #         print(f"   -> Brak Mistrza. Hard Reset EPS do 0.7")
                
            #     # else:
            #         # Progres jest OK, nie przeszkadzamy mu
            #     print(f">>> [SIM {sim_id}] Kontrola: Średnia {avg_dots:.1f} - uczy się poprawnie.")

            # 6. Zapisywanie milestone'ów wiedzy
            q_size = len(agent.q_table)
            if q_size >= last_saved_q_size + 100:
                last_saved_q_size = q_size
                agent.save_brain()

            log_to_csv(sim_id, episode_count, score, game_stats["total_reward"], agent.epsilon, q_size, dots_left)

            reset_game_round()

        # G. RYSOWANIE (Tylko dla głównego procesu)
        if use_graphics:
            game_surface.blit(map_bg_surface, (0, 0))
            draw_pellets(game_surface, current_map)
            player.draw(game_surface)
            for g in ghosts: g.draw(game_surface)
            
            screen.fill(BLACK)
            draw_ui(screen, sim_id, score, agent.epsilon, game_stats["total_reward"], player.lives, ui_message, font, small_font)
            screen.blit(game_surface, (0, UI_HEIGHT))
            pygame.display.flip()
            clock.tick(1200) # Wizualna symulacja w 60 FPS

    if use_graphics: pygame.quit()


if __name__ == "__main__":
    import multiprocessing
    
    # Ile kopii agenta chcesz puścić (np. 6 lub 10)
    num_sims = 6  
    processes = []
    
    print(f"Odpalam {num_sims} niezależnych światów Pac-Mana...")
    
    for i in range(num_sims):
        # Tylko pierwsza symulacja (ID 0) ma okno (True)
        p = multiprocessing.Process(target=start_sim, args=(i, i==0))
        p.start()
        processes.append(p)
        
    for p in processes:
        p.join()