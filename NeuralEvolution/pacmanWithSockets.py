import pygame
import sys
import random
import math
import copy
import socket 
import threading
import json

# --- KONFIGURACJA KOLORÓW ---
BLACK = (0, 0, 0)           # Tło
BLUE = (0, 0, 255)          # Ściany i ramki UI
SCARED_BLUE = (50, 50, 255) # Przestraszone duchy
YELLOW = (255, 255, 0)      # Pac-Man, Buźka, Życia, Zwycięstwo
WHITE = (255, 183, 174)     # Kropki i napisy UI (lekki róż)
RED = (255, 0, 0)           # Blinky, Wynik numeryczny, Game Over
PINK = (255, 105, 180)      # Pinky
CYAN = (0, 255, 255)        # Inky
ORANGE = (255, 165, 0)      # Clyde

TILE_SIZE = 30
PLAYER_SPEED = 3
UI_HEIGHT = 60 # Wysokość paska górnego
SCARED_DURATION = 300 

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


####### NETWORK
def send_msg(conn, data_dict):
    msg = json.dumps(data_dict).encode()
    conn.sendall(len(msg).to_bytes(4, "big") + msg)

def recv_msg(conn):
    length_bytes = conn.recv(4)
    if not length_bytes:
        return None
    length = int.from_bytes(length_bytes, "big")

    data = b""
    while len(data) < length:
        packet = conn.recv(length - len(data))
        if not packet:
            return None
        data += packet

    return json.loads(data.decode())


# --- ŚCIANY BEZ OFFSETU (Liczymy od 0,0) ---
WALLS = []
for r, row in enumerate(GAME_MAP):
    for c, tile in enumerate(row):
        if tile == 1:
            rect = pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            WALLS.append(rect)

WIDTH_TILES = len(GAME_MAP[0])
HEIGHT_TILES = len(GAME_MAP)

# Wymiary samej gry
GAME_WIDTH = WIDTH_TILES * TILE_SIZE
GAME_HEIGHT = HEIGHT_TILES * TILE_SIZE

# Wymiary całego okna (Gra + paski)
SCREEN_WIDTH = GAME_WIDTH
SCREEN_HEIGHT = GAME_HEIGHT + (UI_HEIGHT * 2)

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man Final")
clock = pygame.time.Clock()
font = pygame.font.SysFont('arial', 24, bold=True) 
big_font = pygame.font.SysFont('arial', 40, bold=True)

# --- WIRTUALNY EKRAN GRY ---
game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT)).convert()

# Zmienne globalne
scared_mode = False
scared_timer = 0
dots_left = 0
reset_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 25, 10, 50, 40)

# Statyczne tło mapy (ściany)
map_background = pygame.Surface((GAME_WIDTH, GAME_HEIGHT)).convert()

def pre_render_map():
    map_background.fill(BLACK)
    for r, row in enumerate(GAME_MAP):
        for c, tile in enumerate(row):
            x, y = c * TILE_SIZE, r * TILE_SIZE
            if tile == 1:
                pygame.draw.rect(map_background, BLUE, (x+2, y+2, TILE_SIZE-4, TILE_SIZE-4), 2)
pre_render_map()

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

    def move(self, player, mode):
        # 0. Respawn
        if self.delay_timer > 0:
            self.delay_timer -= 1
            base_y = self.start_grid_y * TILE_SIZE + 2
            if self.delay_timer % 40 < 20: self.y = base_y - 2
            else: self.y = base_y + 2
            self.rect.topleft = (self.x, self.y)
            return

        # --- 1. TUNEL (NAPRAWIONY) ---
        # Poziomy (Lewo/Prawo)
        if self.rect.right < 0: self.x = GAME_WIDTH - self.rect.width
        elif self.rect.left > GAME_WIDTH: self.x = 0
        
        # Pionowy (Góra/Dół) - TEGO BRAKOWAŁO!
        if self.rect.bottom < 0: self.y = GAME_HEIGHT - self.rect.height
        elif self.rect.top > GAME_HEIGHT: self.y = 0
        
        # 2. Wyjście z domu
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

        # 3. AI
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
                if self.is_scared:
                    self.direction = random.choice(possible)
                elif mode == "SCATTER":
                    self.direction = random.choice(possible)
                else:
                    if self.color == RED: tx, ty = player.x, player.y
                    elif self.color == PINK:
                        tx = player.x + (player.direction[0]*TILE_SIZE*4)
                        ty = player.y + (player.direction[1]*TILE_SIZE*4)
                    elif self.color == ORANGE:
                        if math.hypot(self.x-player.x, self.y-player.y) > 5*TILE_SIZE:
                            tx, ty = player.x, player.y
                        else: self.direction = random.choice(possible)
                    elif self.color == CYAN: self.direction = random.choice(possible)

                    if tx is not None:
                        best = possible[0]
                        min_dist = float('inf')
                        for d in possible:
                            test_x = self.x + d[0] * TILE_SIZE
                            test_y = self.y + d[1] * TILE_SIZE
                            dist = abs(test_x - tx) + abs(test_y - ty)
                            if dist < min_dist:
                                min_dist = dist
                                best = d
                        self.direction = best
                    elif self.color != ORANGE and self.color != CYAN:
                        self.direction = random.choice(possible)

        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        self.rect.topleft = (self.x, self.y)

    def draw(self):
        if self.is_scared:
            pygame.draw.rect(game_surface, SCARED_BLUE, self.rect, border_radius=4)
        else:
            pygame.draw.rect(game_surface, self.color, self.rect, border_radius=4)
            
class Player:
    def __init__(self):
        self.speed = PLAYER_SPEED
        self.lives = 3
        self.score = 0
        self.mouth_open_angle = 0 
        self.mouth_speed = 5
        self.mouth_closing = False
        
        self.spawn_grid_x, self.spawn_grid_y = 0, 0
        for r, row in enumerate(GAME_MAP_TEMPLATE):
            for c, tile in enumerate(row):
                if tile == 3: self.spawn_grid_x, self.spawn_grid_y = c, r
        self.spawn()
    
    def spawn(self):
        self.x = self.spawn_grid_x * TILE_SIZE + 2
        self.y = self.spawn_grid_y * TILE_SIZE + 2
        self.rect = pygame.Rect(self.x, self.y, 26, 26)
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.mouth_open_angle = 45

    def move(self):
        if self.direction != (0, 0):
            if self.mouth_closing:
                self.mouth_open_angle -= self.mouth_speed
                if self.mouth_open_angle <= 0: self.mouth_closing = False
            else:
                self.mouth_open_angle += self.mouth_speed
                if self.mouth_open_angle >= 45: self.mouth_closing = True

        # 1. Tunele
        if self.rect.right < 0: self.x = GAME_WIDTH - 26
        elif self.rect.left > GAME_WIDTH: self.x = -26
        if self.rect.bottom < 0: self.y = GAME_HEIGHT - 26
        elif self.rect.top > GAME_HEIGHT: self.y = 0

        # 2. Snapping
        if self.next_direction != (0, 0):
            cc, cr = round(self.x/30), round(self.y/30)
            tx, ty = cc*30+2, cr*30+2
            nx, ny = cc + self.next_direction[0], cr + self.next_direction[1]
            
            if 0 <= ny < HEIGHT_TILES and 0 <= nx < WIDTH_TILES:
                if GAME_MAP[int(ny)][int(nx)] != 1:
                    if (self.next_direction[0]==0 and abs(self.x-tx)<10) or \
                       (self.next_direction[1]==0 and abs(self.y-ty)<10):
                        self.x, self.y = tx, ty
                        self.direction = self.next_direction
                        self.next_direction = (0, 0)
        
        self.x += self.direction[0] * self.speed
        self.y += self.direction[1] * self.speed
        
        test_rect = pygame.Rect(self.x, self.y, 26, 26)
        if test_rect.collidelist(WALLS) == -1:
            self.rect = test_rect
        else:
            self.x, self.y = self.rect.x, self.rect.y

        # Jedzenie
        gx, gy = int((self.x+13)//30), int((self.y+13)//30)
        if 0 <= gx < WIDTH_TILES and 0 <= gy < HEIGHT_TILES:
            tile = GAME_MAP[gy][gx]
            if tile == 0:
                GAME_MAP[gy][gx] = 2
                global score, dots_left
                score += 10
                dots_left -= 1
            elif tile == 4:
                GAME_MAP[gy][gx] = 2
                score += 50
                dots_left -= 1
                global scared_mode, scared_timer
                scared_mode = True
                scared_timer = SCARED_DURATION 
                for g in ghosts: g.is_scared = True
            elif tile == 3: GAME_MAP[gy][gx] = 2

    def draw(self):
        center = self.rect.center
        pygame.draw.circle(game_surface, YELLOW, center, 13)
        if self.direction == (0, 0): return
        cx, cy = center
        mouth_size = 15
        p1 = (cx, cy)
        offset = self.mouth_open_angle / 2
        if self.direction == (1, 0): p2, p3 = (cx+15, cy-offset), (cx+15, cy+offset)
        elif self.direction == (-1, 0): p2, p3 = (cx-15, cy-offset), (cx-15, cy+offset)
        elif self.direction == (0, -1): p2, p3 = (cx-offset, cy-15), (cx+offset, cy-15)
        elif self.direction == (0, 1): p2, p3 = (cx-offset, cy+15), (cx+offset, cy+15)
        else: return
        pygame.draw.polygon(game_surface, BLACK, [p1, p2, p3])

def draw_pellets():
    for r, row in enumerate(GAME_MAP):
        for c, tile in enumerate(row):
            if tile == 0:
                pygame.draw.circle(game_surface, WHITE, (c*30+15, r*30+15), 3)
            elif tile == 4: 
                pygame.draw.circle(game_surface, WHITE, (c*30+15, r*30+15), 8)

def draw_ui():
    # Rysujemy UI bezpośrednio na SCREEN (głównym oknie)
    
    # Pasek Górny (Czarne tło, niebieska linia)
    pygame.draw.rect(screen, BLACK, (0, 0, SCREEN_WIDTH, UI_HEIGHT))
    pygame.draw.line(screen, BLUE, (0, UI_HEIGHT-1), (SCREEN_WIDTH, UI_HEIGHT-1), 2)
    
    # Pasek Dolny (Czarne tło, niebieska linia)
    pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - UI_HEIGHT, SCREEN_WIDTH, UI_HEIGHT))
    pygame.draw.line(screen, BLUE, (0, SCREEN_HEIGHT - UI_HEIGHT), (SCREEN_WIDTH, SCREEN_HEIGHT - UI_HEIGHT), 2)

    # Wynik
    score_label = font.render("SCORE:", True, WHITE) # Kolor kropek
    screen.blit(score_label, (20, 18))
    score_text = font.render(f"{score:05d}", True, RED) # Czerwone cyfry
    screen.blit(score_text, (110, 18))

    # Guzik Reset (Buźka na czarnym tle z niebieską ramką)
    pygame.draw.rect(screen, BLACK, reset_button_rect)
    pygame.draw.rect(screen, BLUE, reset_button_rect, 2) # Niebieska ramka

    center = reset_button_rect.center
    pygame.draw.circle(screen, YELLOW, center, 14) 
    pygame.draw.circle(screen, BLACK, center, 14, 1)
    
    eye_offset = 5
    pygame.draw.circle(screen, BLACK, (center[0]-eye_offset, center[1]-4), 2)
    pygame.draw.circle(screen, BLACK, (center[0]+eye_offset, center[1]-4), 2)
    
    if game_state == "GAME_OVER":
        pygame.draw.arc(screen, BLACK, (center[0]-7, center[1]+2, 14, 10), 0, 3.14, 2)
    else:
        pygame.draw.arc(screen, BLACK, (center[0]-7, center[1]-5, 14, 14), 3.4, 6.0, 2)

    # Życia
    for i in range(player.lives):
        lx = SCREEN_WIDTH - 40 - (i * 30)
        ly = 30
        pygame.draw.circle(screen, YELLOW, (lx, ly), 10)

def reset_game():
    global score, game_state, GAME_MAP, ghosts, ghost_mode, mode_timer, scared_mode, scared_timer, dots_left
    score = 0
    game_state = "PLAYING"
    GAME_MAP = copy.deepcopy(GAME_MAP_TEMPLATE)
    dots_left = sum(r.count(0) + r.count(4) for r in GAME_MAP_TEMPLATE)
    
    player.lives = 3
    player.spawn()
    
    gx, gy = 9, 10
    ghosts = [
        Ghost(gx, 9, RED, 0),
        Ghost(gx, 10, PINK, 60),
        Ghost(8, 10, CYAN, 120),
        Ghost(10, 10, ORANGE, 180)
    ]
    ghost_mode = "CHASE"
    mode_timer = 0
    scared_mode = False
    scared_timer = 0

# --- START ---
score = 0
game_state = "PLAYING"
dots_left = sum(r.count(0) + r.count(4) for r in GAME_MAP_TEMPLATE)

player = Player()
gx, gy = 9, 10
ghosts = [
    Ghost(gx, 9, RED, 0),
    Ghost(gx, 10, PINK, 60),
    Ghost(8, 10, CYAN, 120),
    Ghost(10, 10, ORANGE, 180)
]
ghost_mode = "CHASE"
mode_timer = 0
CHANGE_MODE_TIME = 300

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 5555

last_input = None
conn = None

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print("Waiting for client to connect...")
conn, addr = server.accept()
print("Client connected:", addr)


# --- PĘTLA ---
running = True
while running:

    #print("Game running?")
    data = conn.recv(1024).decode()
    #print("Game running? 2")
    if not data:
        break

    print("Data: ", data)
    if str(data) == "UP":
        player.next_direction = (0,-1)
    elif str(data) == "DOWN":
        player.next_direction = (0,1)
    elif str(data) == "LEFT":
        player.next_direction = (-1,0)
    elif str(data) == "RIGHT":
        player.next_direction = (1,0)


    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if reset_button_rect.collidepoint(event.pos):
                reset_game()
        if event.type == pygame.KEYDOWN:
            if game_state != "PLAYING":
                if event.key == pygame.K_UP: 
                    player.next_direction = (0, -1)
                elif event.key == pygame.K_DOWN: 
                    player.next_direction = (0, 1)
                elif event.key == pygame.K_LEFT: 
                    player.next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT: 
                    player.next_direction = (1, 0)   
                if event.key == pygame.K_SPACE: 
                    reset_game()
    

    if game_state == "PLAYING":
        player.move()
        
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
                    g.x = g.start_grid_x * TILE_SIZE + 2
                    g.y = g.start_grid_y * TILE_SIZE + 2
                    g.rect.topleft = (g.x, g.y)
                    g.delay_timer = 60
                else:
                    hit = True
        
        if hit:
            player.lives -= 1
            if player.lives > 0:
                player.spawn()
                ghosts[0].x, ghosts[0].y = 9*30+2, 9*30+2; ghosts[0].delay_timer=0
                ghosts[1].x, ghosts[1].y = 9*30+2, 10*30+2; ghosts[1].delay_timer=60
                ghosts[2].x, ghosts[2].y = 8*30+2, 10*30+2; ghosts[2].delay_timer=120
                ghosts[3].x, ghosts[3].y = 10*30+2, 10*30+2; ghosts[3].delay_timer=180
                for g in ghosts: g.rect.topleft = (g.x, g.y)
                pygame.time.delay(1000)
            else:
                game_state = "GAME_OVER"
        
        if dots_left == 0: game_state = "WON"

    # RYSOWANIE
    screen.fill(BLACK)
    draw_ui()

    # Rysujemy Grę na OSOBNEJ KARTCE
    game_surface.blit(map_background, (0, 0))
    draw_pellets()
    player.draw()
    for g in ghosts: g.draw()
    
    if game_state == "GAME_OVER":
        game_surface.blit(big_font.render("GAME OVER", True, RED), (GAME_WIDTH//2-100, GAME_HEIGHT//2))
    elif game_state == "WON":
        game_surface.blit(big_font.render("VICTORY!", True, YELLOW), (GAME_WIDTH//2-80, GAME_HEIGHT//2))

    # WKLEJAMY KARTKĘ Z GRĄ NA EKRAN GŁÓWNY
    screen.blit(game_surface, (0, UI_HEIGHT))
    send_mess = "u can go"
    conn.send(send_mess.encode())
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()