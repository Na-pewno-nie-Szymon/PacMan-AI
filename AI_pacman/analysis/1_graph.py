import pandas as pd
import matplotlib.pyplot as plt

def plot_unified_stats(csv_file='F:\\vs_code_workspace\\PacMan\\AI_pacman\\analisys\\pacman_stats.csv'):
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print("Błąd: Brak pliku CSV. Upewnij się, że ścieżka jest poprawna.")
        return

    # Funkcja do normalizacji ręcznej (0-100%)
    def normalize(column):
        low, high = column.min(), column.max()
        if high == low: return column * 0 # Unikamy dzielenia przez zero
        return 100 * (column - low) / (high - low)

    # Kolory (zgodnie z Twoim wyborem)
    colors = {
        'Score': '#D8BFD8',             # Bladofioletowy
        'Total_Reward': '#AFEEEE',      # Blado cyjanowy
        'Epsilon': '#D2B48C',           # Blado kawowy
        'States_Discovered': '#98FB98', # Blado zielony
        'Dots_Left': '#FF1493'          # Neonowo różowy
    }

    # Przygotowanie wykresu
    plt.figure(figsize=(15, 8))
    
    # Ustawienie jednolitego tła
    background_color = '#0D0D0D'
    plt.gcf().set_facecolor(background_color)
    plt.gca().set_facecolor(background_color)

    metrics = ['Score', 'Total_Reward', 'Epsilon', 'States_Discovered', 'Dots_Left']

    # Rysowanie linii
    for metric in metrics:
        # Normalizujemy dane, aby wszystkie serie zmieściły się na jednym wykresie
        y_values = normalize(df[metric])
        
        # Cieńsze linie (linewidth=1.2)
        plt.plot(df['Episode'], y_values, 
                 color=colors[metric], 
                 label=metric.replace('_', ' '), 
                 linewidth=1.2, 
                 alpha=0.9)

    # Legenda
    leg = plt.legend(loc='upper right', facecolor=background_color, edgecolor='gray', labelcolor='white')
    
    # Stylizacja osi
    plt.title('PAC-MAN AI: ZBIORCZA ANALIZA TRENINGU', color='yellow', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('Epizod (Śmierć/Reset)', color='white', fontsize=12)
    plt.ylabel('Postęp Relatywny (0-100%)', color='white', fontsize=12)
    
    plt.tick_params(colors='white')
    plt.grid(True, linestyle='--', alpha=0.15, color='white')

    # Usunięcie zbędnych ramek dla czystego wyglądu
    for spine in plt.gca().spines.values():
        spine.set_visible(False)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    plot_unified_stats()