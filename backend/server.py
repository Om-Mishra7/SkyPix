# Library imports

import os
import requests
from io import BytesIO
from hashlib import sha1
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, send_file

# Local imports 

from image_processing import Image_Editor


# Load environment variables

load_dotenv()


# App configuration

app = Flask(__name__)

app_config = {
    'ENVIROMENT': os.environ.get('ENVIROMENT'),
    'SERVE_REQUESTS': os.environ.get('SERVE_REQUESTS'),
    'ALLOWED_ORIGINS': os.environ.get('ALLOWED_ORIGINS'),
}

allowed_image_modification_parameters = ['width', 'height', 'quality', 'format', 'blur', 'greyscale', 'flip', 'rotate', 'watermark', 'remove-bg']

# After request middleware

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', app_config['ALLOWED_ORIGINS'])
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET')

    return response



# Routes

@app.route('/docs')
def docs():
    return render_template('docs.html')


@app.route('/')
def home():
    # Fetch image URL from request
    image_url = request.args.get('image_url', 'https://cdn.om-mishra.com/logo.png')

    # Fetch the image from the URL
    try:
        image_request_response = requests.get(image_url, allow_redirects=True, timeout=5, headers={'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36'})

        print(image_request_response.status_code)

        if image_request_response.status_code != 200:
            return jsonify({'status': 'error', 'message': 'The requested image could not be fetched, from upstream origin.'}), 400
        
        image = BytesIO(image_request_response.content)

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
            except Exception as error:
                return jsonify({'status': 'error', 'message': 'Error applying modification: ' + str(error)}), 400

    # Get the modified image as a BytesIO object
    serve_image = image_editor.get_image_bytes(format="PNG")

    # Calculate the ETag for the image
    etag = image_editor.get_etag(format="PNG")

    # Serve the image
    return send_file(serve_image, mimetype='image/png', as_attachment=False, etag=etag, max_age=18000)


# Run the app

if __name__ == '__main__':
    app.run(debug=True)