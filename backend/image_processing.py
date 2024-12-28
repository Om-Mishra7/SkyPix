from rembg import remove
from PIL import Image, ImageFilter, ImageOps, ImageDraw, ImageFont
from io import BytesIO
from hashlib import sha1
import os

class Image_Editor:
    def __init__(self, image, image_url):
        # Load the image once and prepare it in the optimal mode
        self.image = Image.open(image)

        try:
            if self.image.mode in ("RGBA", "LA") or (self.image.mode == "P" and "transparency" in self.image.info):
                self.image = self.image.convert("RGBA")  # Ensure image has RGBA support
            else:
                self.image = self.image.convert("RGB")  # Convert to RGB if no transparency
        except Exception as error:
            self.image = None
            self.error = str(error)

        # Add metadata to the image
        self.image.info['author'] = 'SkyPix - sykpix.om-mishra.com'
        self.image.info['original_image_url'] = image_url

        # Cache the font for watermarking to avoid reloading it each time
        self.font_cache = {}

    def _height(self, height):
        """Resize the image by height, maintaining the width."""
        if height is None:
            return self
        self.image = self.image.resize((self.image.width, int(height)), Image.Resampling.LANCZOS)
        return self

    def _width(self, width):
        """Resize the image by width, maintaining the height."""
        if width is None:
            return self
        self.image = self.image.resize((int(width), self.image.height), Image.Resampling.LANCZOS)
        return self

    def _quality(self, quality):
        """Apply quality compression to the image."""
        if quality is None:
            quality = 50

        quality = min(max(int(quality), 0), 100)

        # If the image is in RGBA or other format, convert it to RGB
        if self.image.mode == "RGBA":
            self.image = self.image.convert("RGB")

        img_byte_arr = BytesIO()
        self.image.save(img_byte_arr, format="JPEG", quality=quality)  # Apply JPEG compression
        img_byte_arr.seek(0)

        # Reopen the image from the BytesIO object to update the image
        self.image = Image.open(img_byte_arr)

        return self

    def _blur(self, radius):
        """Apply a Gaussian blur to the image."""
        if radius is None:
            return self
        self.image = self.image.filter(ImageFilter.GaussianBlur(radius))
        return self

    def _greyscale(self):
        """Convert the image to greyscale."""
        self.image = ImageOps.grayscale(self.image)
        return self

    def _flip(self):
        """Flip the image vertically."""
        self.image = ImageOps.flip(self.image)
        return self

    def _rotate(self, angle):
        """Rotate the image by the specified angle."""
        if angle is None:
            return self
        self.image = self.image.rotate(angle, expand=True)
        return self

    def _watermark(self, text, font_size=12):
        """Add a watermark to the image at the lower right with white color."""
        if text is None:
            return self

        # Ensure the image has an alpha channel for transparency
        self.image = self.image.convert("RGBA")

        # Cache the font to avoid reloading it each time
        if font_size not in self.font_cache:
            font_path = "backend/fonts/roboto.ttf"  # Adjust this path if needed
            self.font_cache[font_size] = ImageFont.truetype(font_path, font_size)

        font = self.font_cache[font_size]

        # Create a watermark (transparent) image with the same size as the original image
        watermark = Image.new("RGBA", self.image.size, (255, 255, 255, 0))

        # Prepare to draw the watermark text
        draw = ImageDraw.Draw(watermark)

        # Get the bounding box of the text to center it
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Position the watermark at the lower right corner with padding
        padding = 10  # Adjust padding as necessary
        text_x = watermark.width - text_width - padding
        text_y = watermark.height - text_height - padding

        # Draw the watermark text in white with transparency (128 alpha value)
        draw.text((text_x, text_y), text, font=font, fill=(255, 255, 255, 128))

        # Composite the watermark on top of the original image
        self.image = Image.alpha_composite(self.image, watermark)

        return self

    def _remove_bg(self):
        """Remove the background from the image using the remove.bg API."""
        self.image = remove(self.image)
        return self

    def get_image_bytes(self, format="PNG"):
        """Returns the image as a transparent PNG BytesIO object."""
        # If the image is not in RGBA format, convert it once
        if self.image.mode != 'RGBA':
            self.image = self.image.convert('RGBA')

        # Create a BytesIO object to save the image in memory
        img_byte_arr = BytesIO()
        self.image.save(img_byte_arr, format=format)
        img_byte_arr.seek(0)  # Reset the pointer to the beginning of the BytesIO object
        return img_byte_arr

    def get_etag(self, format="PNG"):
        """Returns the ETag for the image."""
        img_byte_arr = self.get_image_bytes(format)
        return sha1(img_byte_arr.getvalue()).hexdigest()