import pygame
import pickle
import os
import copy
# Importujemy funkcje i klasy z Twojego głównego pliku
# Załóżmy, że Twój główny plik nazywa się main.py
from q_learn_pacman import (
    QLearningAgent, Player, Ghost, GAME_MAP_TEMPLATE, 
    get_bfs_direction_to_food, get_valid_moves, pre_render_map,
    draw_pellets, draw_ui, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT,
    GAME_WIDTH, GAME_HEIGHT, UI_HEIGHT, BLACK, WHITE, YELLOW, CYAN, 
    RED, PINK, ORANGE, SCARED_DURATION, PLAYER_SPEED
)

# --- KONFIGURACJA TESTU ---
BRAIN_ID = 1  # <--- WPISZ ID SYMULACJI, KTÓRA WYGRAŁA
ACTIONS = [(0, -1), (0, 1), (-1, 0), (1, 0)]

def run_test():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f"TEST MÓZGU - SIM {BRAIN_ID}")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('arial', 24, bold=True)
    small_font = pygame.font.SysFont('arial', 16, bold=False)

    # Inicjalizacja Agenta i wczytanie mózgu
    agent = QLearningAgent(ACTIONS, BRAIN_ID)
    if agent.load_brain():
        print(f"Pomyślnie wczytano mózg sim_{BRAIN_ID}.pkl")
    else:
        print("Nie znaleziono pliku mózgu! Sprawdź ścieżkę.")
        return

    # WYŁĄCZAMY LOSOWOŚĆ - Pac-Man ma grać najlepiej jak umie
    agent.epsilon = 0 
    
    # Inicjalizacja gry
    current_map = copy.deepcopy(GAME_MAP_TEMPLATE)
    player = Player(GAME_MAP_TEMPLATE)
    ghosts = [
        Ghost(9, 9, RED, 0), Ghost(9, 10, PINK, 60), 
        Ghost(8, 10, CYAN, 120), Ghost(10, 10, ORANGE, 180)
    ]
    
    map_bg_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT)).convert()
    pre_render_map(map_bg_surface, current_map)
    game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT)).convert()

    walls_list = []
    for r, row in enumerate(current_map):
        for c, tile in enumerate(row):
            if tile == 1:
                walls_list.append(pygame.Rect(c*30, r*30, 30, 30))

    running = True
    score = 0
    scared_mode = False
    scared_timer = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

        # LOGIKA AI (bez uczenia)
        if player.x % TILE_SIZE == 2 and player.y % TILE_SIZE == 2:
            cx, cy = int(player.x // 30), int(player.y // 30)
            bfs_hint = get_bfs_direction_to_food((cx, cy), current_map)
            
            # Agent wybiera akcję tylko na podstawie wiedzy (epsilon=0)
            curr_state = agent.get_state(player, ghosts, bfs_hint, scared_mode, current_map)
            valid_moves = get_valid_moves(player, current_map)
            action_idx = agent.choose_action(curr_state, valid_moves)
            player.next_direction = ACTIONS[action_idx]

        # RUCHY
        s_gain, d_eaten, s_trigger = player.move(current_map, walls_list, agent)
        score += s_gain
        if s_trigger:
            scared_mode = True
            scared_timer = SCARED_DURATION
            for g in ghosts: g.is_scared = True

        if scared_mode:
            scared_timer -= 1
            if scared_timer <= 0:
                scared_mode = False
                for g in ghosts: g.is_scared = False

        for g in ghosts:
            g.move(player, "CHASE", current_map)
            if player.rect.colliderect(g.rect):
                if g.is_scared:
                    score += 250
                    g.x, g.y = g.start_grid_x * TILE_SIZE + 2, g.start_grid_y * TILE_SIZE + 2
                    g.delay_timer = 60
                else:
                    print(f"Koniec testu! Wynik: {score}")
                    running = False

        # RYSOWANIE
        game_surface.blit(map_bg_surface, (0, 0))
        draw_pellets(game_surface, current_map)
        player.draw(game_surface)
        for g in ghosts: g.draw(game_surface)
        
        screen.fill(BLACK)
        draw_ui(screen, f"TEST_{BRAIN_ID}", score, 0.0, 0, 3, "TRYB TESTOWY", font, small_font)
        screen.blit(game_surface, (0, UI_HEIGHT))
        pygame.display.flip()
        clock.tick(60) # Stałe 60 FPS, żebyś widział każdy ruch

    pygame.quit()

if __name__ == "__main__":
    run_test()