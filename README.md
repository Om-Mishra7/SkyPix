# SkyPix Documentation

### Overview
SkyPix is a real-time image processing API that allows you to modify images by simply passing the URL of the image and the desired modifications as query parameters. It's perfect for resizing, applying effects, and enhancing images on the fly.

---

### Base URL
**https://skypix.om-mishra.com**

This is the single endpoint for the API. All requests should be made to this URL with the appropriate query parameters.

---

### Query Parameters
- **`image_url`** (optional): URL of the image to process. Default is a placeholder image.
- **`width`** (optional): Set the width of the image (in pixels).
- **`height`** (optional): Set the height of the image (in pixels).
- **`quality`** (optional): Adjust the quality of the image (1-100).
- **`blur`** (optional): Apply a blur effect with the given intensity.
- **`greyscale`** (optional): Convert the image to greyscale.
- **`flip`** (optional): Flip the image horizontally.
- **`rotate`** (optional): Rotate the image by the given angle (in degrees).
- **`watermark`** (optional): Add a watermark to the image with the specified text.

---

### Example Requests

1. **Resize an image:**

   URL:
   ```
   https://skypix.om-mishra.com?image_url=https://cdn.om-mishra.com/logo.png&width=50&height=50
   ```
   ![Resized Imag](https://skypix.om-mishra.com?image_url=https://cdn.om-mishra.com/logo.png&width=100&height=100)

2. **Apply a blur effect and greyscale:**

   URL:
   ```
   https://skypix.om-mishra.com?image_url=https://cdn.om-mishra.com/logo.png&blur=5&greyscale=true&width=100&height=100
   ```
   ![Blur and Greyscale](https://skypix.om-mishra.com?image_url=https://cdn.om-mishra.com/logo.png&blur=5&greyscale=true&width=100&height=100)

3. **Reduce image quality and rotate:**

   URL:
   ```
   https://skypix.om-mishra.com?image_url=https://cdn.om-mishra.com/logo.png&quality=10&rotate=90&width=100&height=100
   ```
   ![Quality Reduced and Rotated](https://skypix.om-mishra.com?image_url=https://cdn.om-mishra.com/logo.png&quality=10&rotate=90&width=100&height=100)

4. **Add a watermark:**

   URL:
   ```
   https://skypix.om-mishra.com?image_url=https://cdn.om-mishra.com/logo.png&watermark=SkyPix&width=100&height=100
   ```
   ![Watermark](https://skypix.om-mishra.com?image_url=https://cdn.om-mishra.com/logo.png&watermark=SkyPix&width=100&height=100)

---

### Response Format
The API directly serves the modified image in the response body. Ensure your application can handle image responses.

---

### Error Handling
If an error occurs, the API will return a JSON response with a status code and error message:

```json
{
  "status": "error",
  "message": "Invalid image URL"
}
```

---

### Fair Use Policy
SkyPix is provided free of charge for personal and non-commercial use. Please adhere to the following guidelines:

1. Do not process large batches of images.
2. Do not use the service for commercial purposes.
3. Ensure you have permission to process the images.

---

### License
**© 2024 SkyPix**

All Rights Reserved | A service by Om Mishra
