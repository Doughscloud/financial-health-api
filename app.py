import logging
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tips.db'
db = SQLAlchemy(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define model
class Tip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

# Routes
@app.route('/tips', methods=['GET'])
def get_tips():
    try:
        tips = Tip.query.all()
        logger.info('Fetched all tips')
        return jsonify({"tips": [tip.content for tip in tips]})
    except Exception as e:
        logger.error(f"Error fetching tips: {e}")
        return jsonify({"message": "Error fetching tips"}), 500

@app.route('/tips', methods=['POST'])
def add_tip():
    try:
        if not request.is_json:
            logger.warning("Request body is not JSON")
            abort(400, description="Request must be JSON")
        new_tip = request.json.get('tip')
        if not new_tip:
            logger.warning("No tip provided in POST request")
            return jsonify({"message": "Tip is required!"}), 400
        tip = Tip(content=new_tip)
        db.session.add(tip)
        db.session.commit()
        logger.info(f"Added new tip: {new_tip}")
        return jsonify({"message": "Tip added!"}), 201
    except Exception as e:
        logger.error(f"Error adding tip: {e}")
        return jsonify({"message": "Error adding tip"}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f"404 error occurred: {error}")
    return jsonify({"message": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error occurred: {error}")
    return jsonify({"message": "Internal server error"}), 500

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5001)

