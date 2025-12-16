"""
Generate icon files for Plumber Agent installer and system tray.

Creates .ico files with different colors for different agent states:
- plumber.ico (blue) - Main installer icon
- tray_running.ico (green) - Agent running status
- tray_stopped.ico (red) - Agent stopped status
- tray_starting.ico (yellow) - Agent starting/transitioning status

Dependencies:
    pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def create_icon(color, output_path, letter="P", size=256):
    """
    Create a circular icon with a letter in the center.

    Args:
        color: RGB tuple (r, g, b) for icon color
        output_path: Path to save the .ico file
        letter: Letter to display in center (default: "P")
        size: Icon size in pixels (default: 256)
    """
    # Create image with transparency
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Calculate dimensions
    margin = size // 8
    circle_bbox = [margin, margin, size - margin, size - margin]

    # Draw circle with white outline
    draw.ellipse(circle_bbox, fill=color, outline=(255, 255, 255, 255), width=size // 32)

    # Draw letter in center
    # Use default font (PIL's built-in font)
    font_size = size // 2
    try:
        # Try to use a TrueType font if available
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()

    # Get text bounding box for centering
    text_bbox = draw.textbbox((0, 0), letter, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Calculate position to center text
    text_x = (size - text_width) // 2
    text_y = (size - text_height) // 2 - size // 16  # Slight upward adjustment

    # Draw text
    draw.text((text_x, text_y), letter, fill=(255, 255, 255, 255), font=font)

    # Save as .ico with multiple sizes for Windows compatibility
    # Windows uses different icon sizes in different contexts
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
    images = []

    for icon_size in sizes:
        resized = img.resize(icon_size, Image.Resampling.LANCZOS)
        images.append(resized)

    # Save as .ico file with all sizes
    images[0].save(
        output_path,
        format='ICO',
        sizes=[(img.width, img.height) for img in images],
        append_images=images[1:]
    )

    print(f"✅ Created {output_path.name} ({len(images)} sizes)")


def main():
    """Generate all icon files."""
    print("Plumber Agent Icon Generator")
    print("=" * 50)

    # Create icons directory
    script_dir = Path(__file__).parent
    icons_dir = script_dir / "icons"
    icons_dir.mkdir(exist_ok=True)
    print(f"📁 Icons directory: {icons_dir}")
    print()

    # Define icon configurations
    icons = [
        {
            "name": "plumber.ico",
            "color": (59, 130, 246),  # blue-500 (main brand color)
            "description": "Main installer icon"
        },
        {
            "name": "tray_running.ico",
            "color": (34, 197, 94),  # green-500 (agent running)
            "description": "Agent running status"
        },
        {
            "name": "tray_stopped.ico",
            "color": (239, 68, 68),  # red-500 (agent stopped)
            "description": "Agent stopped status"
        },
        {
            "name": "tray_starting.ico",
            "color": (234, 179, 8),  # yellow-500 (agent starting)
            "description": "Agent starting status"
        }
    ]

    # Generate each icon
    for icon_config in icons:
        output_path = icons_dir / icon_config["name"]
        print(f"🎨 Generating {icon_config['name']}...")
        print(f"   Description: {icon_config['description']}")
        print(f"   Color: RGB{icon_config['color']}")

        create_icon(
            color=icon_config["color"],
            output_path=output_path,
            letter="P",
            size=256
        )
        print()

    print("=" * 50)
    print("✅ All icons generated successfully!")
    print(f"📂 Location: {icons_dir.absolute()}")
    print()
    print("Next steps:")
    print("1. Review icons by opening them in Windows Explorer")
    print("2. (Optional) Replace with professional icons from a designer")
    print("3. Continue with PyInstaller build specification")


if __name__ == "__main__":
    main()
