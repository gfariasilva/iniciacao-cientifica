import joblib
import numpy as np
import pandas as pd
import os
import json


def model_fn(model_dir):
    """Load the model and scaler"""
    model = joblib.load(os.path.join(model_dir, 'model.joblib'))
    scaler = joblib.load(os.path.join(model_dir, 'scaler.joblib'))
    return model, scaler


def input_fn(request_body, request_content_type):
    """Parse input data"""
    if request_content_type == 'application/json':
        data = json.loads(request_body)
        
        # Convert to DataFrame
        df = pd.DataFrame([data])
        
        # Select features in same order as training
        features = [
            'trip_duration', 'distance_traveled', 'num_of_passengers',
            'fare', 'tip', 'miscellaneous_fees', 'surge_applied',
            'speed', 'fare_per_mile', 'fare_per_minute'
        ]
        
        return df[features]
    else:
        raise ValueError("Unsupported content type: {}".format(request_content_type))


def predict_fn(input_data, model_scaler):
    """Make prediction"""
    model, scaler = model_scaler
    
    # Scale features
    scaled_data = scaler.transform(input_data)
    
    # Make prediction
    prediction = model.predict(scaled_data)
    return prediction


def output_fn(prediction, content_type):
    """Format output"""
    if content_type == 'application/json':
        return json.dumps({'predicted_total_fare': float(prediction[0])})
    else:
        raise ValueError("Unsupported content type: {}".format(content_type))