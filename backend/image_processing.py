from PIL import Image
from io import BytesIO
from hashlib import sha1

class Image_Editor:
    def __init__(self, image, image_url):
        self.image = Image.open(image)

        try:
            # Convert the image to RGBA to preserve transparency (if needed)
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

    def _height(self, height):
        """Resize the image by height, maintaining the width."""
        if height is None:
            return self
        self.image = self.image.resize((self.image.width, int(height)), Image.Resampling.LANCZOS)  # Use LANCZOS instead of ANTIALIAS
        return self

    def _width(self, width):
        """Resize the image by width, maintaining the height."""
        if width is None:
            return self
        self.image = self.image.resize((int(width), self.image.height), Image.Resampling.LANCZOS)
        return self

    def _quality(self, quality):
      if quality is None:
              return self

          # Ensure the quality is between 0 and 100 for JPEG
      quality = min(max(int(quality), 0), 100)

      # If the image is in RGBA or other format, convert it to RGB
      if self.image.mode == "RGBA":
          self.image = self.image.convert("RGB")  # Convert to RGB to save as JPEG
      
      # Save the image to a BytesIO object with lossy JPEG compression
      img_byte_arr = BytesIO()
      self.image.save(img_byte_arr, format="JPEG", quality=quality)  # Apply lossy compression (JPEG)
      img_byte_arr.seek(0)
      
      # Reopen the image from the BytesIO object to update the image
      self.image = Image.open(img_byte_arr)

      return self

    def get_image_bytes(self, format="PNG"):
        """Returns the image as a BytesIO object."""
        img_byte_arr = BytesIO()
        self.image.save(img_byte_arr, format=format)
        img_byte_arr.seek(0)
        return img_byte_arr

    def get_etag(self, format="PNG"):
        """Returns the ETag for the image."""
        img_byte_arr = self.get_image_bytes(format)
        return sha1(img_byte_arr.getvalue()).hexdigest()
