import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

# --- KONFIGURACJA ---
LOG_DIR = r"F:\vs_code_workspace\PacMan\AI_pacman\analysis"
SMOOTHING_WINDOW = 50  # Zwiększyłem wygładzanie, żeby lepiej widzieć trendy

def plot_results():
    files = glob.glob(os.path.join(LOG_DIR, "stats_sim_*.csv"))
    
    if not files:
        print(f"Błąd: Nie znaleziono plików CSV w {LOG_DIR}")
        return

    # Zmieniamy na siatkę 2x2
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    ((ax1, ax2), (ax3, ax4)) = axes
    
    fig.suptitle('Szczegółowa Analiza Postępów AI (w tym Epsilon)', fontsize=16)

    for file in files:
        sim_id = os.path.basename(file).split('_')[-1].split('.')[0]
        try:
            df = pd.read_csv(file)
            if df.empty: continue
        except Exception:
            continue

        # 1. Nagroda (Total Reward)
        reward_smooth = df['Total Reward'].rolling(window=SMOOTHING_WINDOW).mean()
        ax1.plot(df['Episode'], reward_smooth, label=f'Sim {sim_id}')
        ax1.set_title('Suma Nagród (Reward)')
        ax1.set_ylabel('Wartość wygładzona')

        # 2. Cel (Dots Left)
        dots_smooth = df['Dots Left'].rolling(window=SMOOTHING_WINDOW).mean()
        ax2.plot(df['Episode'], dots_smooth, label=f'Sim {sim_id}')
        # Dodaj surowe dane (kropki) z dużą przezroczystością, żeby widzieć "szczyty" sukcesu
        ax2.scatter(df['Episode'], df['Dots Left'], color='gray', alpha=0.1, s=1)
        ax2.set_title('Pozostałe Kropki (Im mniej, tym lepiej)')
        ax2.invert_yaxis()

        # 3. Wiedza (States Discovered)
        ax3.plot(df['Episode'], df['States_Discovered'], label=f'Sim {sim_id}')
        ax3.set_title('Rozmiar Tabeli Q (Liczba stanów)')
        ax3.set_ylabel('Unikalne sytuacje')

        # 4. Eksploracja (EPSILON) - NOWY WYKRES
        ax4.plot(df['Episode'], df['Epsilon'], label=f'Sim {sim_id}', alpha=0.8)
        ax4.set_title('Współczynnik Eksploracji (Epsilon)')
        ax4.set_ylabel('Prawdopodobieństwo losowego ruchu')
        ax4.set_ylim(0, 1.05) # Zawsze od 0 do 1

    for ax in axes.flat:
        ax.legend(fontsize='small', ncol=2)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.set_xlabel('Epizod')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.show()

if __name__ == "__main__":
    plot_results()