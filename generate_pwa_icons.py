import os
from PIL import Image, ImageDraw, ImageFont

public_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard", "public")
os.makedirs(public_dir, exist_ok=True)

def create_icon(size):
    # Create dark blueprint background image
    img = Image.new("RGBA", (size, size), (10, 14, 23, 255))
    draw = ImageDraw.Draw(img)

    # Rounded rectangle background
    corner_radius = int(size * 0.22)
    draw.rounded_rectangle(
        [(int(size * 0.03), int(size * 0.03)), (int(size * 0.97), int(size * 0.97))],
        radius=corner_radius,
        fill=(24, 34, 52, 255),
        outline=(56, 189, 248, 120),
        width=max(2, int(size * 0.015))
    )

    # 3D isometric cube coordinates
    cx = size // 2
    cy = size // 2
    r = int(size * 0.32)
    h = int(r * 0.58)

    # Top face (cyan)
    p_top = [(cx, cy - r), (cx + int(r * 0.86), cy - r + h), (cx, cy - r + 2 * h), (cx - int(r * 0.86), cy - r + h)]
    draw.polygon(p_top, fill=(2, 132, 199, 240), outline=(56, 189, 248, 255))

    # Left face (dark blue)
    p_left = [(cx - int(r * 0.86), cy - r + h), (cx, cy - r + 2 * h), (cx, cy + r), (cx - int(r * 0.86), cy + r - h)]
    draw.polygon(p_left, fill=(3, 105, 161, 240), outline=(56, 189, 248, 180))

    # Right face (emerald/cyan)
    p_right = [(cx, cy - r + 2 * h), (cx + int(r * 0.86), cy - r + h), (cx + int(r * 0.86), cy + r - h), (cx, cy + r)]
    draw.polygon(p_right, fill=(16, 185, 129, 240), outline=(52, 211, 153, 255))

    # Center sensor dot
    dot_r = max(4, int(size * 0.035))
    draw.ellipse([(cx - dot_r, cy - dot_r + h), (cx + dot_r, cy + dot_r + h)], fill=(248, 250, 252, 255))

    # 4D Pill Badge
    badge_w = int(size * 0.32)
    badge_h = int(size * 0.14)
    bx = int(size * 0.60)
    by = int(size * 0.72)
    draw.rounded_rectangle([(bx, by), (bx + badge_w, by + badge_h)], radius=int(badge_h * 0.3), fill=(2, 132, 199, 255), outline=(56, 189, 248, 255), width=2)

    out_path = os.path.join(public_dir, f"pwa-{size}x{size}.png")
    img.save(out_path, "PNG")
    print(f"Created {out_path}")

create_icon(192)
create_icon(512)
create_icon(180) # Apple touch icon
