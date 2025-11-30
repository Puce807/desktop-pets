import os
from PIL import Image, ImageSequence

# Change this to your folder path
DIRECTORY = r"C:\Users\lrgc1\PycharmProject\desktop-pets\assets\cat"

for filename in os.listdir(DIRECTORY):
    if filename.lower().endswith(".gif"):
        full_path = os.path.join(DIRECTORY, filename)
        print(f"Flipping {filename}...")

        # Load GIF
        original = Image.open(full_path)

        # Flip all frames horizontally
        frames = [
            frame.transpose(Image.FLIP_LEFT_RIGHT)
            for frame in ImageSequence.Iterator(original)
        ]

        # Build new filename
        new_name = filename.rsplit(".", 1)[0] + "_FLIPPED.gif"
        new_path = os.path.join(DIRECTORY, new_name)

        # Save flipped GIF
        frames[0].save(
            new_path,
            save_all=True,
            append_images=frames[1:],
            duration=original.info.get("duration", 100),
            loop=original.info.get("loop", 0),
            disposal=original.info.get("disposal", 2)
        )

        print(f"Saved: {new_name}")

print("Done!")
