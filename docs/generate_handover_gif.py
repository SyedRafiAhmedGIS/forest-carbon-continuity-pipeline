import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

print("🎬 Generating Handover & Continuity Philosophy GIF...")
fig, ax = plt.subplots(figsize=(8, 5))
ax.axis('off')

# 5 Frames illustrating the "If I Leave Tomorrow" philosophy
frames_data = [
    ("Hour 1: Quickstart", "Clone -> Run -> Map in <60 mins", "#2ecc71"),
    ("Fail-Loud: Quarantine", "Bad data -> /quarantine/ (JSON logs)", "#e74c3c"),
    ("Deterministic Replay", "GeoTIFF embeds SHA & INPUT_HASH", "#3498db"),
    ("Week 1: Guardrails", "PR -> Tests -> Golden Image Diff", "#f39c12"),
    ("Guaranteed Continuity", "Byte-level reproducibility. Zero downtime.", "#9b59b6")
]

def update(frame_idx):
    ax.clear()
    ax.axis('off')
    title, subtitle, color = frames_data[frame_idx]

    # Draw a clean conceptual card
    ax.add_patch(plt.Rectangle((0.1, 0.2), 0.8, 0.6, facecolor=color, alpha=0.2, edgecolor=color, linewidth=2))
    ax.text(0.5, 0.65, title, ha='center', va='center', fontsize=16, fontweight='bold', color=color)
    ax.text(0.5, 0.35, subtitle, ha='center', va='center', fontsize=12, color='black')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    return []

ani = animation.FuncAnimation(fig, update, frames=len(frames_data), interval=2000)
output_path = os.path.join(os.path.dirname(__file__), 'handover_continuity_demo.gif')
ani.save(output_path, writer='pillow')
print(f"✅ SUCCESS: Handover GIF saved to {output_path}")
