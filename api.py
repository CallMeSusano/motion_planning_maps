from flask import Flask, request, jsonify
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import pickle
from pypmml import Model

# Load the model and scaler
model_linear = load_model('models/travel_time_model_linear.keras')
model_angular = load_model('models/travel_time_model_angular.keras')
with open('models/scaler_linear.pkl', 'rb') as f:
    scaler_linear = pickle.load(f)
with open('models/scaler_angular.pkl', 'rb') as f:
    scaler_angular = pickle.load(f)

linear_model = Model.load('models/Modelo_Distancia.pmml')
angular_model = Model.load('models/Modelo_Rotacao.pmml')


# Initialize Flask app
app = Flask(__name__)

# Prediction function
def predictLinearTime(distance, velocity):
    input_data = np.array([[distance, velocity]])
    input_data = scaler_linear.transform(input_data)
    predicted_time = model_linear.predict(input_data)
    return float(predicted_time[0][0])  # Convert to native Python float

def predictAngularTime(angle, velocity):
    input_data = np.array([[angle, velocity]])
    input_data = scaler_angular.transform(input_data)
    predicted_time = model_angular.predict(input_data)
    return float(predicted_time[0][0])  # Convert to native Python float

def get_linear_time(distance):
    input_data = {'distance': distance}
    result = linear_model.predict(input_data)
    predicted_time = result['predicted_time']
    print("time linear", predicted_time)
    return predicted_time

def get_rotation_time(angle):
    input_data = {'angle': angle}
    result = angular_model.predict(input_data)
    predicted_time = result['predicted_time']
    print("time angle", predicted_time)
    return predicted_time

# Define a route for prediction
@app.route('/predictAngleTf', methods=['POST'])
def predictAngleTf():
    data = request.get_json()
    angle = data['Angle']
    velocity = data['Velocity']
    predicted_time = predictAngularTime(angle, velocity)
    return jsonify({'predicted_time': predicted_time})


@app.route('/predictLinearTf', methods=['POST'])
def predictLinearTf():
    data = request.get_json()
    distance = data['Distance']
    velocity = data['Velocity']
    predicted_time = predictLinearTime(distance, velocity)
    return jsonify({'predicted_time': predicted_time})

# Define a route for prediction
@app.route('/predictAnglePmml', methods=['POST'])
def predictAnglePmml():
    data = request.get_json()
    angle = data['Angle']
    predicted_time = get_rotation_time(angle)
    return jsonify({'predicted_time': predicted_time})

@app.route('/predictLinearPmml', methods=['POST'])
def predictLinearPmml():
    data = request.get_json()
    distance = data['Distance']
    predicted_time = get_linear_time(distance)
    return jsonify({'predicted_time': predicted_time})

if __name__ == '__main__':
    app.run(debug=True)
