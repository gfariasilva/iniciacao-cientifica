import json
import boto3
import base64
import os

# Initialize SageMaker runtime client
sagemaker_runtime = boto3.client('sagemaker-runtime')

ENDPOINT_NAME = os.environ['ENDPOINT_NAME']

def lambda_handler(event, context):
    output = []
    
    for record in event['records']:
        try:
            # Decode the Firehose record
            payload = base64.b64decode(record['data'])
            data = json.loads(payload)
            
            # Validate required fields
            required_fields = [
                'trip_duration', 'distance_traveled', 'num_of_passengers',
                'fare', 'tip', 'miscellaneous_fees', 'surge_applied'
            ]
            
            # Check if all required fields are present
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                result = {
                    'recordId': record['recordId'],
                    'result': 'ProcessingFailed',
                    'data': record['data']  # Return original data
                }
                output.append(result)
                continue

            processed_data = process_features(data)
            
            # Call SageMaker endpoint
            response = sagemaker_runtime.invoke_endpoint(
                EndpointName=ENDPOINT_NAME,
                ContentType='application/json',
                Body=json.dumps(processed_data)
            )
            
            # Parse prediction result
            prediction_result = json.loads(response['Body'].read().decode())
            
            # Add prediction to the original data
            enriched_data = {**processed_data, **prediction_result}
            
            # Encode the enriched data back to base64
            encoded_data = base64.b64encode(json.dumps(enriched_data).encode('utf-8')).decode('utf-8')
            
            result = {
                'recordId': record['recordId'],
                'result': 'Ok',
                'data': encoded_data
            }
            
        except Exception as e:
            # If processing fails, return the original record
            result = {
                'recordId': record['recordId'],
                'result': 'ProcessingFailed',
                'data': record['data']  # Return original data
            }
        
        output.append(result)
    
    return {'records': output}

def process_features(data):
    processed_data = data.copy()
    
    # Calculate speed (mph) - handle division by zero
    if data['trip_duration'] > 0:
        processed_data['speed'] = data['distance_traveled'] / (data['trip_duration'] / 3600)
    else:
        processed_data['speed'] = 0
    
    # Calculate fare per mile - handle division by zero
    if data['distance_traveled'] > 0:
        processed_data['fare_per_mile'] = data['fare'] / data['distance_traveled']
    else:
        processed_data['fare_per_mile'] = data['fare']  # Use just the fare if distance is 0
    
    # Calculate fare per minute - handle division by zero
    if data['trip_duration'] > 0:
        processed_data['fare_per_minute'] = data['fare'] / (data['trip_duration'] / 60)
    else:
        processed_data['fare_per_minute'] = data['fare']  # Use just the fare if duration is 0
    
    return processed_data