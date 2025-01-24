from flask import Flask, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import random, string
from urllib.parse import urlparse

app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Database model
class URLMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_id = db.Column(db.String(6), unique=True, nullable=False)
    long_url = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    click_count = db.Column(db.Integer, default=0)

# Function to generate a random short ID
def generate_short_id(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

# Function to check if url is valid or not
def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    data = request.json
    long_url = data.get('long_url')

    # Validate input
    if not long_url:
        return jsonify({'error': 'Long URL is required'}), 400
    if not is_valid_url(long_url):
        return jsonify({'error': 'Invalid URL format'}), 400
    if len(long_url) > 500:
        return jsonify({'error': 'URL is too long (maximum 500 characters)'}), 400

    # Check if URL already exists in the database
    existing_url = URLMapping.query.filter_by(long_url=long_url).first()
    if existing_url:
        short_url = url_for('redirect_to_url', short_id=existing_url.short_id, _external=True)
        return jsonify({'short_url': short_url}), 200

    # Generate a unique short ID
    short_id = generate_short_id()
    while URLMapping.query.filter_by(short_id=short_id).first():
        short_id = generate_short_id()

    # Save the mapping to the database
    new_url = URLMapping(short_id=short_id, long_url=long_url)
    db.session.add(new_url)
    db.session.commit()

    # Return the short URL
    short_url = url_for('redirect_to_url', short_id=short_id, _external=True)
    return jsonify({'short_url': short_url}), 201

@app.route('/<short_id>')
def redirect_to_url(short_id):
    url_mapping = URLMapping.query.filter_by(short_id=short_id).first()
    if url_mapping:
        # Increment click count
        url_mapping.click_count += 1
        db.session.commit()
        return redirect(url_mapping.long_url)

    return jsonify({'error': 'URL not found'}), 404

@app.route('/api/analytics/<short_id>', methods=['GET'])
def get_analytics(short_id):
    url_mapping = URLMapping.query.filter_by(short_id=short_id).first()
    if url_mapping:
        return jsonify({
            'short_id': url_mapping.short_id,
            'long_url': url_mapping.long_url,
            'click_count': url_mapping.click_count,
            'created_at': url_mapping.created_at
        }), 200

    return jsonify({'error': 'Short ID not found'}), 404

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/url-shortener')
def home():
    return """
    <h1>Welcome to the URL Shortener</h1>
    <p>Use the <code>/api/shorten</code> endpoint to shorten your URLs.</p>
    """

if __name__ == '__main__':
    app.run()
