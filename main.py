from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/fetch', methods=['GET'])
def fetch_url():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'URL parameter is missing'}), 400
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return jsonify({'content': response.text})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)


