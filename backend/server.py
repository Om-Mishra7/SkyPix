# Library imports

import os
import time
import requests
from io import BytesIO
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, send_file, redirect
from hashlib import sha256
import glob

# Load environment variables

load_dotenv()


# Make sure the cache directory exists

if not os.path.exists('cache'):
    os.makedirs('cache')
    

# Helper functions

def save_to_cache(image_url, image_request_response, image_format, max_files=100):

    # Generate a hash for the image URL to create a unique filename
    cache_file_path = f'cache/{sha256(image_url.encode()).hexdigest()}.{image_format}'

    # Save the image content to the cache file
    with open(cache_file_path, 'wb') as cache_image:
        cache_image.write(image_request_response.content)

    # Check if the number of cached files exceeds the max_files limit
    cached_files = glob.glob('cache/*')  # Get all files in the cache directory
    if len(cached_files) > max_files:
        # Sort files by their modification time (oldest first)
        cached_files.sort(key=os.path.getmtime)
        
        # Remove the oldest files until the count is within the limit
        for file_to_remove in cached_files[:-max_files]:
            try:
                os.remove(file_to_remove)
            except OSError as e:
                print(f"Error removing file {file_to_remove}: {e}")


# App configuration

app = Flask(__name__)

app_config = {
    'ENVIROMENT': os.environ.get('ENVIROMENT'),
    'SERVE_REQUESTS': os.environ.get('SERVE_REQUESTS'),
    'ALLOWED_ORIGINS': os.environ.get('ALLOWED_ORIGINS'),
    'NUMBER_OF_IMAGES_PROCESSED_THIS_SESSION': 0,
    'SIZE_OF_IMAGE_PROCESSED_THIS_SESSION': 0,
    'AVERAGE_RESPONSE_TIME_THIS_SESSION': 0
}

allowed_image_modification_parameters = ['width', 'height', 'quality', 'format', 'blur', 'greyscale', 'flip', 'rotate', 'watermark', 'remove-bg']

# After request middleware

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', app_config['ALLOWED_ORIGINS'])
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET')

    try:
        response.headers.add('X-Cache-Status', 'hit' if is_cached else 'miss')
    except NameError:
        pass
    
    response.headers.add('Server', 'SkyPix')

    return response



# Routes

@app.route('/docs')
def docs():
    return render_template('docs.html', NUMBER_OF_IMAGES_PROCESSED_THIS_SESSION=app_config['NUMBER_OF_IMAGES_PROCESSED_THIS_SESSION'], SIZE_OF_IMAGE_PROCESSED_THIS_SESSION=app_config['SIZE_OF_IMAGE_PROCESSED_THIS_SESSION'], AVERAGE_RESPONSE_TIME_THIS_SESSION=app_config['AVERAGE_RESPONSE_TIME_THIS_SESSION'])

@app.route('/favicon.ico')
def favicon():
    return redirect('https://cdn.om-mishra.com/favicon.ico', code=301)

@app.route('/')
def home():
    global image
    global is_cached
    from image_processing import Image_Editor

    app_config['NUMBER_OF_IMAGES_PROCESSED_THIS_SESSION'] += 1

    # Request start time 
    request_start_time = time.time()

    if app_config['SERVE_REQUESTS'] == 'false':
        return jsonify({'status': 'error', 'message': 'This service is currently disabled.'}), 503

    # Fetch image URL from request
    image_url = request.args.get('image_url', 'https://cdn.om-mishra.com/logo.png')

    # Check if the image URL is valid
    if not image_url.startswith('http') and not image_url.startswith('https'):
        return jsonify({'status': 'error', 'message': 'The requested image URL is invalid.'}), 400

    # Initialize image as None
    image = None

    # Check if the image is stored in the cache
    for file in os.listdir('cache'):
        if sha256(image_url.encode()).hexdigest() in file:
            with open(f'cache/{file}', 'rb') as cached_image:
                image = BytesIO(cached_image.read())
            is_cached = True
            break

    if image is None:  # If the image is not found in the cache, fetch it
        print('Image not found in cache, fetching from origin...')
        is_cached = False
        try:
            image_request_response = requests.get(
                image_url,
                allow_redirects=True,
                timeout=5,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36'
                },
            )

            if image_request_response.status_code != 200:
                return jsonify({'status': 'error', 'message': 'The requested image could not be fetched, from upstream origin.'}), 400

            image = BytesIO(image_request_response.content)
            
            # Find the image format from the response headers
            image_format = image_request_response.headers.get('content-type').split('/')[-1]
            
            if image_format not in ['jpeg', 'jpg', 'png', 'webp']:
                return jsonify({'status': 'error', 'message': 'The requested image is not in a supported format.'}), 400

            save_to_cache(image_url, image_request_response, image_format=image_format)

        except Exception as error:
            return jsonify({'status': 'error', 'message': 'The requested image could not be fetched, from upstream origin due to ' + str(error)}), 400

    # Create Image_Editor object
    image_editor = Image_Editor(image, image_url)

    if image_editor.image is None:
        return jsonify({'status': 'error', 'message': 'The requested image was not in a supported format.'}), 400

    # Apply image modifications based on request arguments
    for parameter in request.args:
        if parameter in allowed_image_modification_parameters:
            try:
                match parameter:
                    case 'width':
                        image_editor._width(int(request.args.get('width')))
                    case 'height':
                        image_editor._height(int(request.args.get('height')))
                    case 'quality':
                        image_editor._quality(int(request.args.get('quality')))
                    case 'blur':
                        image_editor._blur(int(request.args.get('blur')))
                    case 'greyscale':
                        image_editor._greyscale()
                    case 'flip':
                        image_editor._flip()
                    case 'rotate':
                        image_editor._rotate(int(request.args.get('rotate')))
                    case 'watermark':
                        image_editor._watermark(request.args.get('watermark'))
                    case _:
                        pass

            except Exception as error:
                return jsonify({'status': 'error', 'message': 'Error applying modification: ' + str(error)}), 400

    # Get the modified image as a BytesIO object
    serve_image = image_editor.get_image_bytes()

    # Calculate the ETag for the image
    etag = image_editor.get_etag()

    if request.headers.get('If-None-Match') == etag:
        return '', 304
    
    # Find image size
    image_size = len(serve_image.getvalue())

    # Calculate the response time
    response_time = round(time.time() - request_start_time, 3)  # Rounded to 3 decimal places

    # Update the session statistics
    app_config['SIZE_OF_IMAGE_PROCESSED_THIS_SESSION'] += image_size / 1024
    app_config['AVERAGE_RESPONSE_TIME_THIS_SESSION'] = (app_config['AVERAGE_RESPONSE_TIME_THIS_SESSION'] + response_time) / 2

    # Serve the image
    return send_file(serve_image, mimetype='image/webp', as_attachment=False, etag=etag, max_age=18000)


# Error handlers

@app.errorhandler(404)
def page_not_found(error):
    return jsonify({'status': 'error', 'message': 'The requested resource was not found.'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'status': 'error', 'message': 'An internal server error occurred.'}), 500

# Run the app

if __name__ == '__main__' and app_config['ENVIROMENT'] == 'development':
    app.run(debug=True)