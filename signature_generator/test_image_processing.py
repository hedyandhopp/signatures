from PIL import Image, ImageDraw

def process_image(image_path, output_path):
    with Image.open(image_path).convert("RGBA") as img:
        img = img.resize((120, 120))
        corner_radius = 45

        # Create a white background image
        background = Image.new("RGBA", img.size, (255, 255, 255, 255))

        # Create a mask for the bottom-right corner
        mask = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(mask)

        # Draw the rectangle for the entire image (filled) and the rounded corner on bottom-right
        draw.rectangle([0, 0, img.size[0], img.size[1]], fill=255)
        draw.pieslice([img.size[0] - 2 * corner_radius, img.size[1] - 2 * corner_radius, img.size[0], img.size[1]],
                      start=270, end=360, fill=0)  # Transparent slice on bottom-right

        # Apply the mask to the image and paste onto background
        img.putalpha(mask)
        background.paste(img, (0, 0), img)

        # Save the processed image
        background.save(output_path, "PNG")

# Example usage with your image
process_image('/Users/suzieschmitt/Downloads/headshot.png', '/Users/suzieschmitt/Downloads/output_headshot.png')
