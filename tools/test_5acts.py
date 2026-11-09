#!/usr/bin/env python3
import sys
sys.path.append("/tmp")
from render_full_film_4k import render_frame_4k

print("Testing 5 frames across all 5 acts...")
for f in [100, 1100, 1800, 2600, 3400]:
    path = render_frame_4k(f)
    print(f"Rendered: {path}")
print("ALL 5 ACTS VERIFIED!")
