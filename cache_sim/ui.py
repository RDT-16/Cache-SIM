import tkinter as tk
from multiprocessing import Process
from cache_sim.simulation import DirectMappedCache, FullyAssociativeCache, SetAssociativeCache
from cache_sim.visualization import CacheVisualizer
import pygame
import sys

def run_pygame_simulation(cache_size, block_size, addresses, mapping, policy, num_sets=2):
    pygame.init()
    visualizer = CacheVisualizer(cache_size, block_size, num_sets=num_sets)

    if mapping == "Direct Mapped":
        cache = DirectMappedCache(cache_size, block_size)
    elif mapping == "Fully Associative":
        cache = FullyAssociativeCache(cache_size, block_size, replacement_policy=policy)
    else:
        cache = SetAssociativeCache(cache_size, block_size, num_sets=num_sets, replacement_policy=policy)

    clock = pygame.time.Clock()
    running = True
    paused = False
    index = 0
    flash_duration = 1500  # milliseconds
    last_step_time = pygame.time.get_ticks()

    last_access = None
    last_hit = None
    replaced = None

    visualizer.start_highlight()

    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = not paused

        current_time = pygame.time.get_ticks()

        if not paused and index < len(addresses) and (current_time - last_step_time) > flash_duration:
            addr = addresses[index]
            result, access_idx, replaced_idx = cache.access(addr)

            last_hit = (result == "Hit")
            if isinstance(access_idx, tuple):
                last_access = access_idx[0] * (cache_size // block_size // num_sets) + access_idx[1]
            else:
                last_access = access_idx

            if replaced_idx is not None:
                if isinstance(replaced_idx, tuple):
                    replaced = replaced_idx[0] * (cache_size // block_size // num_sets) + replaced_idx[1]
                else:
                    replaced = replaced_idx

            last_step_time = current_time
            visualizer.start_highlight()
            index += 1

        if (current_time - last_step_time) > flash_duration:
            last_access = None
            replaced = None

        visualizer.update_highlight(dt)
        visualizer.update_cache(cache.get_cache_state())
        visualizer.draw_cache(cache.hits, cache.misses, last_access, last_hit, replaced)

    visualizer.close()
    pygame.quit()
    sys.exit()

class CacheSimulatorUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cache Simulator")

        tk.Label(root, text="Cache Size (bytes):").grid(row=0, column=0)
        self.cache_size_entry = tk.Entry(root)
        self.cache_size_entry.grid(row=0, column=1)
        self.cache_size_entry.insert(0, "16")

        tk.Label(root, text="Block Size (bytes):").grid(row=1, column=0)
        self.block_size_entry = tk.Entry(root)
        self.block_size_entry.grid(row=1, column=1)
        self.block_size_entry.insert(0, "4")

        tk.Label(root, text="Memory Addresses (comma-separated):").grid(row=2, column=0, columnspan=2)
        self.addresses_entry = tk.Entry(root, width=40)
        self.addresses_entry.grid(row=3, column=0, columnspan=2)
        self.addresses_entry.insert(0, "0,4,8,0,16,4,20,0")

        tk.Label(root, text="Mapping Technique:").grid(row=4, column=0)
        self.mapping_var = tk.StringVar(root)
        self.mapping_var.set("Direct Mapped")
        mapping_options = ["Direct Mapped", "Fully Associative", "Set Associative"]
        self.mapping_menu = tk.OptionMenu(root, self.mapping_var, *mapping_options)
        self.mapping_menu.grid(row=4, column=1)

        tk.Label(root, text="Replacement Policy:").grid(row=5, column=0)
        self.policy_var = tk.StringVar(root)
        self.policy_var.set("LRU")
        policy_options = ["LRU", "FIFO", "Random"]
        self.policy_menu = tk.OptionMenu(root, self.policy_var, *policy_options)
        self.policy_menu.grid(row=5, column=1)

        tk.Label(root, text="Number of Sets (For Set Associative):").grid(row=6, column=0)
        self.sets_entry = tk.Entry(root)
        self.sets_entry.grid(row=6, column=1)
        self.sets_entry.insert(0, "2")

        self.result_text = tk.Text(root, height=10, width=50)
        self.result_text.grid(row=8, column=0, columnspan=2)

        tk.Button(root, text="Run Simulation", command=self.run_simulation).grid(row=7, column=0, columnspan=2)

    def run_simulation(self):
        try:
            cache_size = int(self.cache_size_entry.get())
            block_size = int(self.block_size_entry.get())
            addresses = list(map(int, self.addresses_entry.get().split(',')))
            mapping = self.mapping_var.get()
            policy = self.policy_var.get()
            num_sets = int(self.sets_entry.get())
            if mapping != "Set Associative":
                num_sets = 1
        except ValueError:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "Invalid input. Please enter integers correctly.")
            return

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Launching animation window...\n")

        p = Process(target=run_pygame_simulation, args=(cache_size, block_size, addresses, mapping, policy, num_sets))
        p.start()
