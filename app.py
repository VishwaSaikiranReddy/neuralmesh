# neuralmesh/app.py
# This is the brain of NeuralMesh — the AI server

from flask import Flask, request, jsonify,request
from flask_cors import CORS
import numpy as np
import base64
import json
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)  # Allows the app to talk to the dashboard

# This stores all patient cases in memory (for demo)
# In real deployment, this would be a database
cases = []
risk_scores = []


def analyze_image_simple(image_data):
    """
    DEMO VERSION: Simulates AI analysis
    Real version uses TFLite model on device
    Returns: risk level and recommendation
    """

    # Simulate based on image size
    img_size = len(image_data)

    # Simulated risk score
    risk = random.uniform(0, 1)

    if risk < 0.3:
        return {
            'risk_level': 'LOW',
            'risk_score': round(risk * 100, 1),
            'recommendation': 'Patient appears healthy. Schedule routine check in 3 months.',
            'color': 'green'
        }

    elif risk < 0.7:
        return {
            'risk_level': 'MEDIUM',
            'risk_score': round(risk * 100, 1),
            'recommendation': 'Some indicators present. Refer to PHC within 2 weeks.',
            'color': 'orange'
        }

    else:
        return {
            'risk_level': 'HIGH',
            'risk_score': round(risk * 100, 1),
            'recommendation': 'URGENT: High risk indicators. Refer to PHC within 48 hours.',
            'color': 'red'
        }


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'NeuralMesh is running!',
        'version': '1.0'
    })


@app.route('/analyze', methods=['POST'])
def analyze():
    """Receives image and returns AI diagnosis"""

    data = request.json

    # Get patient info
    patient_id = data.get('patient_id', 'ANON_' + str(len(cases)))
    village = data.get('village', 'Unknown')
    condition_type = data.get('condition_type', 'general')
    image_data = data.get('image', '')

    # Run AI analysis
    result = analyze_image_simple(image_data)

    # Save case
    case = {
        'case_id': len(cases) + 1,
        'village': village,
        'condition_type': condition_type,
        'risk_level': result['risk_level'],
        'risk_score': result['risk_score'],
        'timestamp': datetime.now().isoformat()
    }

    cases.append(case)
    risk_scores.append(result['risk_score'])

    return jsonify({
        'success': True,
        'result': result,
        'case_id': case['case_id'],
        'message': 'Analysis complete'
    })


@app.route('/dashboard', methods=['GET'])
def dashboard():
    """Returns village health statistics for PHC dashboard"""

    if not cases:
        return jsonify({'message': 'No cases yet', 'cases': []})

    avg_risk = sum(risk_scores) / len(risk_scores)
    high_risk = sum(1 for r in risk_scores if r > 70)

    return jsonify({
        'total_cases': len(cases),
        'average_risk': round(avg_risk, 1),
        'high_risk_count': high_risk,
        'recent_cases': cases[-10:],
        'alert': 'OUTBREAK RISK' if avg_risk > 65 else 'NORMAL'
    })


if __name__ == '__main__':
    print('NeuralMesh starting on http://localhost:5000')
    app.run(debug=True, host='0.0.0.0', port=5000)