# Library imports

import os
import requests
from io import BytesIO
from hashlib import sha1
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template, send_file, redirect

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

@app.route('/favicon.ico')
def favicon():
    return redirect('https://cdn.om-mishra.com/favicon.ico', code=301)

@app.route('/')
def home():

    if app_config['SERVE_REQUESTS'] == 'false':
        return jsonify({'status': 'error', 'message': 'This service is currently disabled.'}), 503
    
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
                    case 'blur':
                        image_editor._blur(int(request.args.get('blur')))
                    case 'greyscale':
                        image_editor._greyscale()
                    case 'flip':
                        image_editor._flip()
                    case 'rotate':
                        image_editor._rotate(int(request.args.get('rotate')))
                    case 'remove-bg':
                        image_editor._remove_bg()
                    case 'watermark':
                        image_editor._watermark(request.args.get('watermark'))
                    case _:
                        pass

            except Exception as error:
                return jsonify({'status': 'error', 'message': 'Error applying modification: ' + str(error)}), 400

    # Get the modified image as a BytesIO object
    serve_image = image_editor.get_image_bytes()

    # Calculate the ETag for the image
    etag = image_editor.get_etag(format="PNG")

    if request.headers.get('If-None-Match') == etag:
        return '', 304

    # Serve the image
    return send_file(serve_image, mimetype='image/png', as_attachment=False, etag=etag, max_age=18000)


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