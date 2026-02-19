import pygame
import sys
import random
import math
import copy
import collections
import pickle  # <-- DO ZAPISYWANIA DANYCH
import os      # <-- DO SPRAWDZANIA CZY PLIK ISTNIEJE
import csv


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
GREEN = (0, 255, 0) # Kolor komunikatu o zapisie

TILE_SIZE = 30
PLAYER_SPEED = 3 # Szybka gra
UI_HEIGHT = 60 
SCARED_DURATION = 300 

LOG_FILE = "F:\\vs_code_workspace\\PacMan\\AI_pacman\\analisys\\pacman_stats.csv"

# Tworzymy nagłówki, jeśli plik jest nowy
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Episode", "Score", "Total_Reward", "Epsilon", "States_Discovered", "Dots_Left"])

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

GAME_MAP = copy.deepcopy(GAME_MAP_TEMPLATE)
WALLS = []
for r, row in enumerate(GAME_MAP):
    for c, tile in enumerate(row):
        if tile == 1:
            rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            WALLS.append(rect)

WIDTH_TILES = len(GAME_MAP[0])
HEIGHT_TILES = len(GAME_MAP)
GAME_WIDTH = WIDTH_TILES * TILE_SIZE
GAME_HEIGHT = HEIGHT_TILES * TILE_SIZE
SCREEN_WIDTH = GAME_WIDTH
SCREEN_HEIGHT = GAME_HEIGHT + (UI_HEIGHT * 2)

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man AI - Save/Load System")
clock = pygame.time.Clock()
font = pygame.font.SysFont('arial', 24, bold=True) 
big_font = pygame.font.SysFont('arial', 40, bold=True)
small_font = pygame.font.SysFont('arial', 16, bold=False)

game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT)).convert()
map_background = pygame.Surface((GAME_WIDTH, GAME_HEIGHT)).convert()

def pre_render_map():
    map_background.fill(BLACK)
    for r, row in enumerate(GAME_MAP):
        for c, tile in enumerate(row):
            x, y = c * TILE_SIZE, r * TILE_SIZE
            if tile == 1:
                pygame.draw.rect(map_background, BLUE, (x+2, y+2, TILE_SIZE-4, TILE_SIZE-4), 2)
pre_render_map()

# --- GPS (BFS) ---
def get_bfs_direction_to_food(start_pos, grid):
    start_x, start_y = start_pos
    if not (0 <= start_x < WIDTH_TILES and 0 <= start_y < HEIGHT_TILES): return None
    if grid[start_y][start_x] == 1: return None

    queue = collections.deque([(start_x, start_y, [])])
    visited = set()
    visited.add((start_x, start_y))
    deltas = [(0, -1, 0), (0, 1, 1), (-1, 0, 2), (1, 0, 3)]
    
    while queue:
        cx, cy, first_move = queue.popleft()
        if grid[cy][cx] in [0, 4]: 
            if not first_move: return None 
            return first_move[0]
        
        for dx, dy, move_idx in deltas:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < WIDTH_TILES and 0 <= ny < HEIGHT_TILES:
                if grid[ny][nx] != 1 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    next_move = list(first_move)
                    if not next_move: next_move.append(move_idx)
                    queue.append((nx, ny, next_move))
    return None

# --- AI AGENT (Z MODUŁEM PAMIĘCI) ---
class QLearningAgent:
    def __init__(self, actions):
        self.actions = actions
        self.q_table = {}
        self.epsilon = 1.0       # Startujemy od pełnej eksploracji
        self.epsilon_min = 0.05  # Zwiększamy do 20%  
        self.epsilon_decay = 0.9999 # Zmieniamy na wolniejszy decay
        self.alpha = 0.02         # Learning rate
        self.gamma = 0.86        # Bardziej patrzymy w przyszłość
        self.brain_file = "pacman_brain.pkl"

    def get_state(self, player, ghosts, bfs_suggested_action, is_scared_global):
        px, py = int(player.x // TILE_SIZE), int(player.y // TILE_SIZE)
        
        surroundings = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = px + dx, py + dy
            if 0 <= nx < WIDTH_TILES and 0 <= ny < HEIGHT_TILES:
                tile = GAME_MAP[ny][nx]
                if tile == 1:
                    surroundings.append(0) # ŚCIANA
                elif tile == 0 or tile == 4:
                    surroundings.append(2) # JEDZENIE
                else:
                    surroundings.append(1) # PUSTA DROGA
            else:
                surroundings.append(0) # Poza mapą = Ściana
        
        # Logika duchów (bez zmian)
        ghost_nearby = False
        if not is_scared_global:
            for g in ghosts:
                gx, gy = int(g.x // TILE_SIZE), int(g.y // TILE_SIZE)
                if abs(px - gx) + abs(py - gy) <= 3: 
                    ghost_nearby = True
                    break
        
        return (tuple(surroundings), bfs_suggested_action, ghost_nearby)

    def choose_action(self, state, valid_moves):
        # USUWAMY epsilon_decay STĄD (przenosimy do momentu zjedzenia kropki)
        if state not in self.q_table: self.q_table[state] = [0.0] * len(self.actions)
        
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
        # 1. Inicjalizacja stanu obecnego (jeśli go nie ma, np. po resetowaniu tabeli)
        if state not in self.q_table:
            self.q_table[state] = [0.0] * len(self.actions)
            
        # 2. Inicjalizacja stanu następnego
        if next_state not in self.q_table:
            self.q_table[next_state] = [0.0] * len(self.actions)
            
        # 3. Reszta logiki bez zmian
        old_v = self.q_table[state][action_idx]
        next_max = max(self.q_table[next_state])
        
        # Formuła Q-learning
        self.q_table[state][action_idx] = old_v + self.alpha * (reward + self.gamma * next_max - old_v)

    # --- NOWE FUNKCJE: ZAPIS I ODCZYT ---
    def save_brain(self):
        try:
            with open(self.brain_file, "wb") as f:
                pickle.dump(self.q_table, f)
            print("MÓZG ZAPISANY POMYŚLNIE!")
            return True
        except Exception as e:
            print(f"Błąd zapisu: {e}")
            return False

    def load_brain(self):
        if os.path.exists(self.brain_file):
            try:
                with open(self.brain_file, "rb") as f:
                    self.q_table = pickle.load(f)
                self.epsilon = 0.0 # Wyłączamy losowość - niech gra tym co umie!
                print("MÓZG WCZYTANY! TRYB PROFESJONALISTY (EPSILON = 0).")
                return True
            except Exception as e:
                print(f"Błąd odczytu: {e}")
                return False
        else:
            print("Brak zapisanego mózgu.")
            return False
            
    def reset_brain(self):
        self.q_table = {}
        self.epsilon = 0.5
        print("MÓZG ZRESETOWANY. NAUKA OD ZERA.")

# --- KLASY OBIEKTÓW ---
class Ghost:
    def __init__(self, grid_x, grid_y, color, start_delay=0):
        self.grid_x = grid_x; self.grid_y = grid_y; self.start_grid_x = grid_x; self.start_grid_y = grid_y
        self.x = grid_x * TILE_SIZE + 2; self.y = grid_y * TILE_SIZE + 2
        self.color = color; self.speed = 2; self.direction = (0, 0)
        self.rect = pygame.Rect(self.x, self.y, TILE_SIZE - 4, TILE_SIZE - 4)
        self.delay_timer = start_delay; self.is_scared = False 

    def move(self, player, mode):
        if self.delay_timer > 0:
            self.delay_timer -= 1
            base_y = self.start_grid_y * TILE_SIZE + 2
            if self.delay_timer % 40 < 20: self.y = base_y - 2
            else: self.y = base_y + 2
            self.rect.topleft = (self.x, self.y)
            return

        if self.rect.right < 0: self.x = GAME_WIDTH - self.rect.width
        elif self.rect.left > GAME_WIDTH: self.x = 0
        if self.rect.bottom < 0: self.y = GAME_HEIGHT - self.rect.height
        elif self.rect.top > GAME_HEIGHT: self.y = 0
        
        if 9 <= (self.y // TILE_SIZE) <= 11 and 8 * TILE_SIZE < self.x < 11 * TILE_SIZE:
            door_center_x = 9 * TILE_SIZE + 2
            if self.x < door_center_x: self.x += self.speed
            elif self.x > door_center_x: self.x -= self.speed
            if abs(self.x - door_center_x) <= self.speed:
                self.x = door_center_x; self.y -= self.speed; self.direction = (0, -1)
            self.rect.topleft = (self.x, self.y)
            return

        if self.x % TILE_SIZE == 2 and self.y % TILE_SIZE == 2:
            possible = []
            check = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for d in check:
                nx = int((self.x // TILE_SIZE) + d[0])
                ny = int((self.y // TILE_SIZE) + d[1])
                valid = True
                if 0 <= nx < WIDTH_TILES and 0 <= ny < HEIGHT_TILES:
                    if GAME_MAP[ny][nx] == 1: valid = False
                if valid:
                    if d[0] != -self.direction[0] or d[1] != -self.direction[1]:
                        possible.append(d)
            
            if not possible: 
                for d in check:
                    nx = int((self.x // TILE_SIZE) + d[0])
                    ny = int((self.y // TILE_SIZE) + d[1])
                    if 0 <= nx < WIDTH_TILES and 0 <= ny < HEIGHT_TILES:
                        if GAME_MAP[ny][nx] != 1: possible.append(d)
                    else: possible.append(d)

            if possible:
                tx, ty = None, None
                if self.is_scared: self.direction = random.choice(possible)
                elif mode == "SCATTER": self.direction = random.choice(possible)
                else:
                    if self.color == RED: tx, ty = player.x, player.y
                    elif self.color == PINK: tx = player.x + (player.direction[0]*TILE_SIZE*4); ty = player.y + (player.direction[1]*TILE_SIZE*4)
                    elif self.color == ORANGE:
                        if math.hypot(self.x-player.x, self.y-player.y) > 5*TILE_SIZE: tx, ty = player.x, player.y
                        else: self.direction = random.choice(possible)
                    elif self.color == CYAN: self.direction = random.choice(possible)

                    if tx is not None:
                        best = possible[0]; min_dist = float('inf')
                        for d in possible:
                            test_x = self.x + d[0] * TILE_SIZE; test_y = self.y + d[1] * TILE_SIZE
                            dist = abs(test_x - tx) + abs(test_y - ty)
                            if dist < min_dist: min_dist = dist; best = d
                        self.direction = best
                    elif self.color != ORANGE and self.color != CYAN: self.direction = random.choice(possible)

        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        self.rect.topleft = (self.x, self.y)

    def draw(self):
        c = SCARED_BLUE if self.is_scared else self.color
        pygame.draw.rect(game_surface, c, self.rect, border_radius=4)
            
class Player:
    def __init__(self):
        self.speed = PLAYER_SPEED; self.lives = 3; self.score = 0
        self.mouth_open_angle = 0; self.mouth_speed = 5; self.mouth_closing = False
        self.spawn_grid_x, self.spawn_grid_y = 0, 0
        for r, row in enumerate(GAME_MAP_TEMPLATE):
            for c, tile in enumerate(row):
                if tile == 3: self.spawn_grid_x, self.spawn_grid_y = c, r
        self.spawn()
    
    def spawn(self):
        self.x = self.spawn_grid_x * TILE_SIZE + 2; self.y = self.spawn_grid_y * TILE_SIZE + 2
        self.rect = pygame.Rect(self.x, self.y, 26, 26); self.direction = (0, 0); self.next_direction = (0, 0)

    def move(self):
        if self.direction != (0, 0):
            if self.mouth_closing:
                self.mouth_open_angle -= self.mouth_speed
                if self.mouth_open_angle <= 0: self.mouth_closing = False
            else:
                self.mouth_open_angle += self.mouth_speed
                if self.mouth_open_angle >= 45: self.mouth_closing = True

        if self.rect.right < 0: self.x = GAME_WIDTH - 26
        elif self.rect.left > GAME_WIDTH: self.x = -26
        if self.rect.bottom < 0: self.y = GAME_HEIGHT - 26
        elif self.rect.top > GAME_HEIGHT: self.y = 0

        if self.next_direction != (0, 0):
            cc, cr = round(self.x/30), round(self.y/30)
            tx, ty = cc*30+2, cr*30+2
            nx, ny = cc + self.next_direction[0], cr + self.next_direction[1]
            if 0 <= ny < HEIGHT_TILES and 0 <= nx < WIDTH_TILES:
                if GAME_MAP[int(ny)][int(nx)] != 1:
                    if (self.next_direction[0]==0 and abs(self.x-tx)<10) or (self.next_direction[1]==0 and abs(self.y-ty)<10):
                        self.x, self.y = tx, ty; self.direction = self.next_direction; self.next_direction = (0, 0)
        
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        test_rect = pygame.Rect(self.x, self.y, 26, 26)
        if test_rect.collidelist(WALLS) == -1: self.rect = test_rect
        else: self.x, self.y = self.rect.x, self.rect.y

        gx, gy = int((self.x+13)//30), int((self.y+13)//30)
        if 0 <= gx < WIDTH_TILES and 0 <= gy < HEIGHT_TILES:
            tile = GAME_MAP[gy][gx]
            if tile == 0:  # Zwykła kropka
                GAME_MAP[gy][gx] = 2; global score, dots_left; score += 10; dots_left -= 1
                
                # Decay przy każdej kropce - używamy wartości z agenta
                agent.epsilon = max(agent.epsilon_min, agent.epsilon * agent.epsilon_decay)
                
            elif tile == 4: # Duża kropka
                GAME_MAP[gy][gx] = 2; score += 50; dots_left -= 1
                
                # Duża kropka daje solidny skok pewności siebie (np. 5%)
                agent.epsilon = max(agent.epsilon_min, agent.epsilon * 0.95)
                
                global scared_mode, scared_timer; scared_mode = True; scared_timer = SCARED_DURATION 
                for g in ghosts: g.is_scared = True

    def draw(self):
        center = self.rect.center
        pygame.draw.circle(game_surface, YELLOW, center, 13)
        if self.direction == (0, 0): return
        cx, cy = center; offset = self.mouth_open_angle / 2
        if self.direction == (1, 0): p2, p3 = (cx+15, cy-offset), (cx+15, cy+offset)
        elif self.direction == (-1, 0): p2, p3 = (cx-15, cy-offset), (cx-15, cy+offset)
        elif self.direction == (0, -1): p2, p3 = (cx-offset, cy-15), (cx+offset, cy-15)
        elif self.direction == (0, 1): p2, p3 = (cx-offset, cy+15), (cx+offset, cy+15)
        else: return
        pygame.draw.polygon(game_surface, BLACK, [center, p2, p3])

def draw_pellets():
    for r, row in enumerate(GAME_MAP):
        for c, tile in enumerate(row):
            if tile == 0: pygame.draw.circle(game_surface, WHITE, (c*30+15, r*30+15), 3)
            elif tile == 4: pygame.draw.circle(game_surface, WHITE, (c*30+15, r*30+15), 8)

def draw_ui(last_msg=""):
    pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, UI_HEIGHT))
    pygame.draw.line(screen, BLUE, (0, UI_HEIGHT-1), (SCREEN_WIDTH, UI_HEIGHT-1), 2)
    
    # Górny pasek - Instrukcja
    instr = small_font.render("[S] Zapisz  [L] Wczytaj  [R] Reset Mózgu", True, WHITE)
    screen.blit(instr, (20, 10))
    if last_msg:
        msg = small_font.render(last_msg, True, GREEN)
        screen.blit(msg, (20, 35))

    # Dolny pasek
    bottom_y = SCREEN_HEIGHT - UI_HEIGHT
    pygame.draw.rect(screen, BLACK, (0, bottom_y, SCREEN_WIDTH, UI_HEIGHT))
    pygame.draw.line(screen, BLUE, (0, bottom_y), (SCREEN_WIDTH, bottom_y), 2)

    score_text = font.render(f"SCORE: {score}", True, WHITE)
    screen.blit(score_text, (20, bottom_y + 18))
    
    eps_text = font.render(f"EPS: {agent.epsilon:.4f}", True, CYAN)
    screen.blit(eps_text, (200, bottom_y + 18))
    
    rew_text = font.render(f"REW: {game_stats['total_reward']:.0f}", True, WHITE)
    screen.blit(rew_text, (400, bottom_y + 18))

    for i in range(player.lives):
        lx = SCREEN_WIDTH - 40 - (i * 30)
        ly = bottom_y + 30
        pygame.draw.circle(screen, YELLOW, (lx, ly), 10)

def reset_game_round():
    global score, GAME_MAP, ghosts, ghost_mode, mode_timer, scared_mode, scared_timer, dots_left, last_state, last_action_idx
    score = 0
    game_stats["total_reward"] = 0
    GAME_MAP = copy.deepcopy(GAME_MAP_TEMPLATE)
    dots_left = sum(r.count(0) + r.count(4) for r in GAME_MAP_TEMPLATE)
    player.spawn()
    gx, gy = 9, 10
    ghosts = [Ghost(gx, 9, RED, 0), Ghost(gx, 10, PINK, 60), Ghost(8, 10, CYAN, 120), Ghost(10, 10, ORANGE, 180)]
    ghost_mode = "CHASE"; mode_timer = 0; scared_mode = False; scared_timer = 0
    last_state = None; last_action_idx = None

def get_valid_moves(player):
    moves = []
    px, py = round(player.x / TILE_SIZE), round(player.y / TILE_SIZE)
    check_dirs = [(0, -1, 0), (0, 1, 1), (-1, 0, 2), (1, 0, 3)] 
    for dx, dy, idx in check_dirs:
        nx, ny = px + dx, py + dy
        if not (0 <= nx < WIDTH_TILES): moves.append(idx); continue
        if 0 <= ny < HEIGHT_TILES:
            if GAME_MAP[ny][nx] != 1: moves.append(idx)
    return moves

def log_to_csv(episode_num, score, total_reward, epsilon, q_table_size, dots_left):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([episode_num, score, round(total_reward, 2), round(epsilon, 4), q_table_size, dots_left])

# --- START ZMIENNYCH ---

game_stats = {"current_reward": 0, "total_reward": 0}
score = 0
episode_count = 0
dots_left = sum(r.count(0) + r.count(4) for r in GAME_MAP_TEMPLATE)

total_dots_start = sum(r.count(0) + r.count(4) for r in GAME_MAP_TEMPLATE)
best_dots_ever = total_dots_start
best_q_table = None

player = Player()
gx, gy = 9, 10
ghosts = [Ghost(gx, 9, RED, 0), Ghost(gx, 10, PINK, 60), Ghost(8, 10, CYAN, 120), Ghost(10, 10, ORANGE, 180)]
ghost_mode = "CHASE"; mode_timer = 0; CHANGE_MODE_TIME = 300
scared_mode = False; scared_timer = 0

actions = [(0, -1), (0, 1), (-1, 0), (1, 0)] 
agent = QLearningAgent(actions)
last_state = None; last_action_idx = None; old_score = 0
ui_message = "" # Komunikat o zapisie/odczycie

last_saved_q_size = 0
knowledge_milestone = 100

# --- PĘTLA GŁÓWNA ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                if agent.save_brain(): ui_message = "ZAPISANO MÓZG!"
            if event.key == pygame.K_l:
                if agent.load_brain(): ui_message = "WCZYTANO MÓZG (EPS=0)!"
            if event.key == pygame.K_r:
                agent.reset_brain(); ui_message = "RESET MÓZGU!"

    # 1. AI DECYZJA (Logika co 30 pikseli)
    if player.x % TILE_SIZE == 2 and player.y % TILE_SIZE == 2:
        cx, cy = int(player.x // 30), int(player.y // 30)
        bfs_hint = get_bfs_direction_to_food((cx, cy), GAME_MAP)
        current_state = agent.get_state(player, ghosts, bfs_hint, scared_mode)
        valid_moves = get_valid_moves(player)
        
        action_idx = agent.choose_action(current_state, valid_moves)
        player.next_direction = actions[action_idx]
        
        if last_state is not None:
            agent.learn(last_state, last_action_idx, game_stats["current_reward"], current_state)
        
        last_state = current_state
        last_action_idx = action_idx
    
    # 2. RUCH
    player.move()
    
    # 3. LOGIKA DUCHÓW
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
        g.move(player, ghost_mode)
        if player.rect.colliderect(g.rect):
            if g.is_scared:
                score += 200
                g.x = g.start_grid_x * TILE_SIZE + 2; g.y = g.start_grid_y * TILE_SIZE + 2
                g.rect.topleft = (g.x, g.y); g.delay_timer = 60
            else: hit = True
    
    # --- 4. NAGRODY ---
    score_diff = score - old_score

    # Definiujemy is_reversing TUTAJ, aby uniknąć błędu "not defined"
    is_reversing = False
    if last_action_idx is not None and 'action_idx' in locals():
        opposites = {0: 1, 1: 0, 2: 3, 3: 2}
        if action_idx == opposites.get(last_action_idx):
            is_reversing = True
    
    dots_left_ratio = dots_left / total_dots_start

    # Obliczamy nagrodę
    if hit:
        reward = -500
    elif score_diff > 0:
        reward = 35 + (60 * (1 - dots_left_ratio))
    else:
        reward = max(-2 * dots_left_ratio, -0.2)
        # Sprawdzamy czy zmienne AI istnieją w tej klatce
        if 'current_state' in locals() and 'action_idx' in locals():
            bfs_hint = current_state[1]
            if bfs_hint is not None and action_idx != bfs_hint:
                reward -= (4 * dots_left_ratio)
            if is_reversing and action_idx != bfs_hint:
                reward -= 10

    game_stats["current_reward"] = reward
    game_stats["total_reward"] += reward
    old_score = score
    
    # --- 5. LOGIKA KOŃCA RUNDY (Z NAPRAWIONĄ DIAGNOSTYKĄ) ---
    if hit or dots_left == 0:
        # A. NAUKA PRZED RESETEM
        if hit:
            if last_state: 
                agent.learn(last_state, last_action_idx, -500, agent.get_state(player, ghosts, None, scared_mode))
        else:
            if last_state: 
                agent.learn(last_state, last_action_idx, 1000, current_state)

        episode_count += 1
        current_q_size = len(agent.q_table)

        # B. LOGOWANIE
        log_to_csv(episode_count, score, game_stats["total_reward"], agent.epsilon, current_q_size, dots_left)

        # DIAGNOSTYKA (zobaczysz to po każdym zgonie)
        # print(f"DEBUG: Epizod: {episode_count}/50 | Q-Size: {current_q_size} | Last-Saved: {last_saved_q_size}")

        # C. WYMUSZENIE ZAPISU (ELITARYZM)
        should_save = False
        if dots_left == 0: # Zapis przy wygranej
            should_save = True
            print(">>> MISTRZ: Zapis za wygraną!")
        elif current_q_size >= last_saved_q_size + knowledge_milestone: # Zapis przy nowej wiedzy
            should_save = True
            last_saved_q_size = current_q_size
            print(f">>> MISTRZ: Nowa wiedza ({current_q_size} stanów). Zapisuję...")
        elif best_q_table is None: # Zapisz cokolwiek na start, żeby mieć punkt odniesienia
            should_save = True
            last_saved_q_size = current_q_size
            print(">>> MISTRZ: Pierwszy zapis bazy wiedzy.")

        if should_save:
            best_q_table = copy.deepcopy(agent.q_table)
            agent.save_brain()

        # D. MECHANIZM RATUNKOWY (POWRÓT DO MISTRZA)
        # Sprawdzamy co 50 epizodów
        if episode_count % 50 == 0:
            print(f"--- KONTROLA EPIZODU 50 (Rekord: {best_dots_ever}) ---")
            if best_q_table is not None:
                # Jeśli w tym 50-tym epizodzie poszło fatalnie (zostało dużo kropek)
                if dots_left > 150: 
                    print(f"--- POWRÓT DO MISTRZA: Słaby wynik ({dots_left} kropek). Wczytuję wiedzę... ---")
                    agent.q_table = copy.deepcopy(best_q_table)
                    agent.epsilon = min(0.4, agent.epsilon + 0.1)
                else:
                    print("--- KONTROLA: Wynik OK, nie wczytuję Mistrza. ---")
            else:
                print("--- KONTROLA: Brak zapisanego Mistrza w pamięci! ---")

        # Wydruk końcowy rundy
        status = "Zgon!" if hit else "WYGRANA!"
        print(f"{status} Epizod {episode_count} | Wynik: {score} | Kropki: {dots_left} | Tabela Q: {current_q_size}")

        reset_game_round()

    # RYSOWANIE
    screen.fill(BLACK)
    draw_ui(ui_message)
    game_surface.blit(map_background, (0, 0))
    draw_pellets()
    player.draw()
    for g in ghosts: g.draw()
    screen.blit(game_surface, (0, UI_HEIGHT))
    pygame.display.flip()
    clock.tick(0)

pygame.quit()
sys.exit()