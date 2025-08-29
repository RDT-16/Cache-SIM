import random
from collections import deque

class CacheBlock:
    def __init__(self, tag):
        self.tag = tag
        self.timestamp = 0  # For LRU tracking

class BaseCache:
    def __init__(self, cache_size, block_size):
        self.cache_size = cache_size
        self.block_size = block_size
        self.num_blocks = cache_size // block_size
        self.hits = 0
        self.misses = 0

    def access(self, address):
        raise NotImplementedError("Override in subclasses")

    def hit_ratio(self):
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0

class DirectMappedCache(BaseCache):
    def __init__(self, cache_size, block_size):
        super().__init__(cache_size, block_size)
        self.cache = [None] * self.num_blocks

    def access(self, address):
        block_number = (address // self.block_size) % self.num_blocks
        tag = address // self.block_size

        if self.cache[block_number] == tag:
            self.hits += 1
            return "Hit", block_number, None
        else:
            replaced = self.cache[block_number]
            self.cache[block_number] = tag
            self.misses += 1
            return "Miss", block_number, replaced

    def get_cache_state(self):
        return self.cache

class FullyAssociativeCache(BaseCache):
    def __init__(self, cache_size, block_size, replacement_policy='LRU'):
        super().__init__(cache_size, block_size)
        self.cache = []
        self.replacement_policy = replacement_policy
        self.time = 0
        self.queue = deque()  # For FIFO

    def access(self, address):
        tag = address // self.block_size
        self.time += 1

        for i, block in enumerate(self.cache):
            if block.tag == tag:
                self.hits += 1
                if self.replacement_policy == 'LRU':
                    block.timestamp = self.time
                return "Hit", i, None

        self.misses += 1

        if len(self.cache) < self.num_blocks:
            new_block = CacheBlock(tag)
            if self.replacement_policy == 'LRU':
                new_block.timestamp = self.time
            self.cache.append(new_block)
            if self.replacement_policy == 'FIFO':
                self.queue.append(new_block)
            return "Miss", len(self.cache) -1, None

        # Replacement
        if self.replacement_policy == 'FIFO':
            old_block = self.queue.popleft()
            replaced_index = self.cache.index(old_block)
            self.cache.remove(old_block)
            new_block = CacheBlock(tag)
            self.cache.append(new_block)
            self.queue.append(new_block)
        elif self.replacement_policy == 'LRU':
            lru_block = min(self.cache, key=lambda b: b.timestamp)
            replaced_index = self.cache.index(lru_block)
            self.cache.remove(lru_block)
            new_block = CacheBlock(tag)
            new_block.timestamp = self.time
            self.cache.append(new_block)
        else:  # Random
            random_block = random.choice(self.cache)
            replaced_index = self.cache.index(random_block)
            self.cache.remove(random_block)
            new_block = CacheBlock(tag)
            self.cache.append(new_block)

        return "Miss", len(self.cache) -1, replaced_index

    def get_cache_state(self):
        # Pad with None if cache not full to maintain length
        return [block.tag for block in self.cache] + [None] * (self.num_blocks - len(self.cache))

class SetAssociativeCache(BaseCache):
    def __init__(self, cache_size, block_size, num_sets, replacement_policy='LRU'):
        super().__init__(cache_size, block_size)
        self.num_sets = num_sets
        self.set_size = self.num_blocks // num_sets
        self.replacement_policy = replacement_policy
        self.time = 0
        self.cache_sets = [[] for _ in range(num_sets)]
        self.fifo_queues = [deque() for _ in range(num_sets)]

    def access(self, address):
        tag = address // self.block_size
        set_index = (address // self.block_size) % self.num_sets
        current_set = self.cache_sets[set_index]
        fifo_queue = self.fifo_queues[set_index]
        self.time += 1

        for i, block in enumerate(current_set):
            if block.tag == tag:
                self.hits += 1
                if self.replacement_policy == 'LRU':
                    block.timestamp = self.time
                return "Hit", (set_index, i), None

        self.misses += 1

        if len(current_set) < self.set_size:
            new_block = CacheBlock(tag)
            if self.replacement_policy == 'LRU':
                new_block.timestamp = self.time
            current_set.append(new_block)
            if self.replacement_policy == 'FIFO':
                fifo_queue.append(new_block)
            return "Miss", (set_index, len(current_set) - 1), None

        # Replacement
        if self.replacement_policy == 'FIFO':
            old_block = fifo_queue.popleft()
            replaced_index = current_set.index(old_block)
            current_set.remove(old_block)
            new_block = CacheBlock(tag)
            current_set.append(new_block)
            fifo_queue.append(new_block)
        elif self.replacement_policy == 'LRU':
            lru_block = min(current_set, key=lambda b: b.timestamp)
            replaced_index = current_set.index(lru_block)
            current_set.remove(lru_block)
            new_block = CacheBlock(tag)
            new_block.timestamp = self.time
            current_set.append(new_block)
        else:  # Random
            random_block = random.choice(current_set)
            replaced_index = current_set.index(random_block)
            current_set.remove(random_block)
            new_block = CacheBlock(tag)
            current_set.append(new_block)

        return "Miss", (set_index, len(current_set) - 1), replaced_index

    def get_cache_state(self):
        state = []
        for current_set in self.cache_sets:
            state.extend([block.tag for block in current_set])
            state.extend([None]*(self.set_size - len(current_set)))
        return state
