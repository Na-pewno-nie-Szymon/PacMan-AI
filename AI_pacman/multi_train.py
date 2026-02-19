import multiprocessing
from q_learn_pacman import start_sim

if __name__ == "__main__":
    # --- TUTAJ USTALASZ ILE KOPII CHCESZ ---
    num_processes = 4  # Zmień na 10 jak będziesz gotowy na ogień
    processes = []

    print(f"Odpalam {num_processes} symulacji...")

    for i in range(num_processes):
        # Pierwsza symulacja (i=0) ma okno (True), reszta pracuje po cichu (False)
        show_gui = (i == 0) 
        
        p = multiprocessing.Process(target=start_sim, args=(i, show_gui))
        p.start()
        processes.append(p)

    # To sprawia, że program główny czeka na zamknięcie procesów
    for p in processes:
        p.join()