# Skypix Image Processing API Documentation

Welcome to the Skypix Image Processing API! This API allows you to modify images by applying various transformations such as resizing, quality adjustment, rotation, and more.

## Documentation URL
For full documentation, visit the [Skypix Image Processing API Docs](https://skypix.om-mishra.com/docs).

## Overview
This API endpoint processes images based on a given URL and applies the requested modifications on the fly. You can resize, adjust quality, blur, rotate, and more!

## API Endpoints

### `GET /`

The base URL where the image processing happens. The API fetches an image from the given `image_url` and applies transformations based on the provided query parameters.

#### Query Parameters:
- `image_url` (optional): The URL of the image to process. Default is a placeholder image.
- `width` (optional): Set the width of the image.
- `height` (optional): Set the height of the image.
- `quality` (optional): Adjust the image quality (1-100).
- `blur` (optional): Apply a blur effect with the given intensity.
- `greyscale` (optional): Convert the image to greyscale.
- `flip` (optional): Flip the image horizontally.
- `rotate` (optional): Rotate the image by the given angle (in degrees).
- `remove-bg` (optional): Remove the background from the image.
- `watermark` (optional): Add a watermark with the given text.

## Example Requests

1. **Fetch and Resize an Image**  
   Resize the image to a width of 500px.
   ```bash
   /?image_url=https://example.com/image.png&width=500
   ```

2. **Apply a Blur Effect and Convert to Greyscale**  
   Apply a blur effect with intensity 5 and convert the image to greyscale.
   ```bash
   /?image_url=https://example.com/image.png&blur=5&greyscale=true
   ```

## Response Format

The API will return a modified image in the chosen format, directly in the response body.

### Example Error Response:
```json
{
  "status": "error",
  "message": "Invalid image URL"
}
```

## Error Handling

If an error occurs, the API will return a `JSON` response with a status code and an error message.

- `404` – Resource not found.
- `400` – Bad request (e.g., invalid parameters).
- `500` – Internal server error.

---

For any issues or questions, please refer to the support documentation or contact us at support@om-mishra.com.
