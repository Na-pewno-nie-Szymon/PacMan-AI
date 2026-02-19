import pandas as pd
import matplotlib.pyplot as plt

def plot_pacman_stats(csv_file='F:\\vs_code_workspace\\PacMan\\AI_pacman\\analisys\\pacman_stats.csv'):
    try:
        # Wczytanie danych
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"Błąd: Plik {csv_file} nie istnieje. Uruchom najpierw trening!")
        return

    # Kolory zdefiniowane przez użytkownika
    colors = {
        'Score': '#D8BFD8',             # Bladofioletowy
        'Total_Reward': '#AFEEEE',      # Blado cyjanowy
        'Epsilon': '#D2B48C',           # Blado kawowy
        'States_Discovered': '#98FB98', # Blado zielony
        'Dots_Left': '#FF1493'          # Neonowo różowy
    }

    # Stworzenie 5 subwykresów (jeden pod drugim)
    fig, axes = plt.subplots(5, 1, figsize=(12, 18), sharex=True)
    plt.subplots_adjust(hspace=0.4)
    
    # Ustawienie ciemnego motywu (pasuje do Pac-Mana)
    fig.patch.set_facecolor('#1a1a1a')
    
    metrics = ['Score', 'Total_Reward', 'Epsilon', 'States_Discovered', 'Dots_Left']
    
    for i, metric in enumerate(metrics):
        ax = axes[i]
        ax.set_facecolor('#262626')
        
        # Rysowanie linii
        ax.plot(df['Episode'], df[metric], color=colors[metric], linewidth=2, label=metric)
        
        # Stylizacja osi
        ax.set_ylabel(metric.replace('_', ' '), color='white', fontweight='bold', fontsize=12)
        ax.tick_params(axis='both', colors='white')
        ax.grid(True, linestyle='--', alpha=0.3, color='gray')
        
        # Dodanie legendy
        ax.legend(loc='upper left', frameon=False, labelcolor='white')

    # Ostatnia oś X
    axes[-1].set_xlabel('Episode', color='white', fontweight='bold', fontsize=14)
    
    plt.suptitle('PAC-MAN AI TRAINING PROGRESS', color='yellow', fontsize=20, fontweight='bold', y=0.92)
    
    # Wyświetlenie lub zapisanie
    plt.show()

if __name__ == "__main__":
    plot_pacman_stats()