import os
from rembg import remove
from PIL import Image

def process_image(input_path, output_path):
    print(f"Processing {input_path}...")
    
    # Check if input file exists
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    # Backup the original file
    backup_path = input_path + ".bak"
    if not os.path.exists(backup_path):
        print(f"Creating backup at {backup_path}")
        with open(input_path, 'rb') as f_in:
            with open(backup_path, 'wb') as f_out:
                f_out.write(f_in.read())
    else:
        print(f"Backup already exists at {backup_path}")

    # Read image
    input_image = Image.open(input_path)

    # Remove background
    print("Removing background...")
    output_image = remove(input_image)

    # Trim whitespace
    print("Trimming whitespace...")
    bbox = output_image.getbbox()
    if bbox:
        output_image = output_image.crop(bbox)
        print(f"Cropped to {bbox}")
    else:
        print("Warning: No content found (empty image?)")

    # Save result
    print(f"Saving to {output_path}...")
    output_image.save(output_path)
    print("Done!")

if __name__ == "__main__":
    input_file = "static/img/hero_tooth_3d.png"
    # Overwrite the same file
    process_image(input_file, input_file)
