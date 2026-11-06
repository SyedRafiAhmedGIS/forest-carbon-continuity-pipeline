import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

print("🎬 Generating 5-Frame Pipeline Workflow GIF...")
fig, ax = plt.subplots(figsize=(6, 6))
ax.axis('off')

frames_data = [
    ("1. Raw Sentinel-1/2 Data", 'gray', "Cloud Obstructed"),
    ("2. SAR Cloud-Proof Masking", 'binary', "VH/VV Ratio Applied"),
    ("3. Species Classification", 'terrain', "Spruce | Pine | Mixed"),
    ("4. Carbon Stock (t/ha)", 'YlOrRd', "±95% CI Uncertainty"),
    ("5. Density & LULC Layers", 'tab20', "VDF | MDF | Nursery | Office")
]

def update(frame_idx):
    ax.clear()
    ax.axis('off')
    title, cmap, subtitle = frames_data[frame_idx]
    data = np.random.rand(50, 50)
    if frame_idx == 1: data = np.where(data > 0.5, 1, 0)
    if frame_idx == 2: data = np.random.randint(0, 4, (50, 50))
    if frame_idx == 3: data = np.random.rand(50, 50) * 400
    if frame_idx == 4: data = np.random.randint(1, 9, (50, 50))
    
    ax.imshow(data, cmap=cmap)
    ax.set_title(f"{title}\n{subtitle}", fontsize=12, fontweight='bold')
    return []

ani = animation.FuncAnimation(fig, update, frames=len(frames_data), interval=1500)
output_path = os.path.join(os.path.dirname(__file__), 'pipeline_demo.gif')
ani.save(output_path, writer='pillow')
print(f"✅ SUCCESS: 5-Frame GIF saved to {output_path}")
