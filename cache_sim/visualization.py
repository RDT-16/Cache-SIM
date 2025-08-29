import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 400
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
YELLOW = (255, 255, 0)
GREY = (220, 220, 220)

FONT = pygame.font.SysFont('Arial', 20)

def lerp_color(color_start, color_end, t):
    return tuple(
        int(color_start[i] + (color_end[i] - color_start[i]) * t)
        for i in range(3)
    )

class CacheVisualizer:
    def __init__(self, cache_size, block_size, num_sets=1):
        self.cache_size = cache_size
        self.block_size = block_size
        self.num_sets = num_sets
        self.num_blocks = cache_size // block_size
        self.set_size = self.num_blocks // num_sets
        self.cache_state = [None] * self.num_blocks

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Cache Memory Visualization')

        self.highlight_duration = 1500  # ms
        self.highlight_timer = 0
        self.highlighting = False

    def start_highlight(self):
        self.highlight_timer = 0
        self.highlighting = True

    def update_highlight(self, dt):
        if self.highlighting:
            self.highlight_timer += dt
            if self.highlight_timer > self.highlight_duration:
                self.highlighting = False
                self.highlight_timer = 0

    def update_cache(self, cache_state):
        self.cache_state = list(cache_state)

    def draw_cache(self, hits, misses, last_access=None, last_hit=None, replaced=None):
        self.screen.fill(WHITE)

        t = min(1.0, self.highlight_timer / self.highlight_duration) if self.highlighting else 0

        block_width = WIDTH // (self.set_size * self.num_sets)
        block_height = 50
        y_spacing = 70

        for set_i in range(self.num_sets):
            y = 50 + set_i * y_spacing
            set_label = FONT.render(f"Set {set_i}", True, BLACK)
            self.screen.blit(set_label, (5, y))

            for block_i in range(self.set_size):
                idx = set_i * self.set_size + block_i
                x = 50 + block_i * block_width
                color = GREY

                if replaced == idx:
                    color = lerp_color(YELLOW, GREY, t)
                elif last_access == idx:
                    target_color = GREEN if last_hit else RED
                    color = lerp_color(target_color, GREY, t)

                pygame.draw.rect(self.screen, color, (x, y, block_width - 4, block_height))

                tag = self.cache_state[idx]
                if tag is not None:
                    text = FONT.render(str(tag), True, BLACK)
                    self.screen.blit(text, (x + block_width // 3, y + block_height // 3))

        hit_text = FONT.render(f'Hits: {hits}', True, GREEN)
        miss_text = FONT.render(f'Misses: {misses}', True, RED)
        self.screen.blit(hit_text, (10, HEIGHT - 60))
        self.screen.blit(miss_text, (10, HEIGHT - 30))

        pygame.display.flip()

    def close(self):
        pygame.quit()
        sys.exit()
