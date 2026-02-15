import heapq
import json
from collections import defaultdict

class Node:
    def __init__(self, char=None, freq=None):
        self.char = char  
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_frequency_table(text):
    freq = defaultdict(int)
    for char in text:
        freq[char] += 1
    return freq

def build_huffman_tree(freq_table):
    heap = [Node(char, freq) for char, freq in freq_table.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        n1 = heapq.heappop(heap)
        n2 = heapq.heappop(heap)
        merged = Node(freq=n1.freq + n2.freq)
        merged.left = n1
        merged.right = n2
        heapq.heappush(heap, merged)

    return heap[0] if heap else None

def generate_codes(root):
    codes = {}

    def traverse(node, current_code):
        if node:
            if node.char is not None:
                codes[node.char] = current_code
            traverse(node.left, current_code + "0")
            traverse(node.right, current_code + "1")

    traverse(root, "")
    return codes

def encode_text(text, code_map):
    return ''.join(code_map[char] for char in text)

def decode_text(encoded_text, code_map):
    reverse_map = {v: k for k, v in code_map.items()}
    current = ''
    decoded = ''
    for bit in encoded_text:
        current += bit
        if current in reverse_map:
            decoded += reverse_map[current]
            current = ''
    return decoded 