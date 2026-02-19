# Pac-Man Reinforcement Learning: The Ghost Hunter

Projekt agenta sztucznej inteligencji uczącego się gry w Pac-Mana od zera przy użyciu algorytmu **Q-Learning**. System został zaprojektowany pod kątem stabilnego treningu długofalowego z wykorzystaniem statystycznej analizy postępów.



## 🧠 Kluczowe Funkcje (The Essentials)

* **Multi-Sim Engine:** Obsługa wielu równoległych symulacji przyspieszająca zbieranie doświadczeń.
* **Headless Mode:** Tryb ultra-szybkiego treningu (wyłączona grafika), pozwalający na przeliczenie tysięcy gier w krótkim czasie.
* **Statistical Rescue Logic:** System zapobiegający stagnacji – resetuje parametry tylko wtedy, gdy średnia z ostatnich 500 gier nie wykazuje poprawy.
* **Q-Table Persistence:** Automatyczny zapis i odczyt "mózgu" z plików `.pkl`.
* **Live Metrics:** Eksport danych do CSV (Reward, Epsilon, Dots Left, Q-Table Size).

---

## 🚀 Szybki Start

Postępuj zgodnie z poniższymi krokami, aby uruchomić projekt na nowym urządzeniu:

### 1. Przygotowanie środowiska (VENV)
```bash
# Stworzenie wirtualnego środowiska
python -m venv venv

# Aktywacja (Windows)
venv\Scripts\activate

# Aktywacja (Linux/Mac)
source venv/bin/activate
```
### 2. Instalacja Bibliotek 
```bash
pip install -r requirements.txt
```

### 3. Uruchomienie treningu
W pliku `q_learn_pacman.py` ustaw parametry symulacji, następnie uruchom:
```bash
python q_learn_pacman.py
```

## Matematyka i Logika
Agent optymalizuje swoje decyzje w oparciu o równanie Bellmana dla funkcji $Q(s, a)$:

$$Q(s, a) \leftarrow Q(s, a) + \alpha [r + \gamma \max_{a'} Q(s', a') - Q(s, a)]$$

Zastosowane hiperparametry:
* **Alpha** (Learning Rate): 0.2
* **Gamma** (Discount Factor): 0.99
* **Epsilon** (Exploration): Spadek od 1.0 do 0.05 (mnożnik 0.9997-0.9998).

## Struktura Projektu
| Plik | Opis |
| :--- | :--- |
| PacMan/ | Całe repo |
| pacman.py | Gra pacman - stworzona do faktycznego grania |
| graphics/ | Stworzone pierwsze grafiki duszków (jeszcze nie zaimplementowane) |
| AI_pacman/ | Cała magia samogrającego PacMan'a |
| q_learn_pacman.py | Główny silnik gry, logika AI i pętla treningowa |
| Brain_test.py | Skrypt fo testowania wyuczonego mózgu (epsilon = 0) |
| analysis/ | Tam trafiają wszyskie zapisane kroki w plikach csv |
| plotter.py | Narzędzie diagnostyczne - wypluwa wykresy |

## Sterowanie (Tryb Graficzny)
W oknie głównym (Sim 0) dostępne są komendy:

* **S** – Ręczny zapis aktualnego mózgu.
* **L** – Wczytanie mózgu z pliku.
* **R** – Całkowity reset tabeli Q.

Uwaga: Dla maksymalnej wydajności podczas długich sesji treningowych zaleca się ustawienie `use_graphics=False` w funkcji `start_sim`.