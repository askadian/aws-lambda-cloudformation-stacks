"""
Simple Hello World Lambda Function
This function demonstrates a basic AWS Lambda handler in Python
"""
import json
import logging
from datetime import datetime, timezone

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda function handler
    
    Args:
        event: The event dict that contains the parameters sent when the function is invoked
        context: An object provided by AWS Lambda with runtime information
    
    Returns:
        dict: Response containing statusCode and body
    """
    
    # Log the incoming event
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Get current timestamp
    current_time = datetime.now(timezone.utc).isoformat()
    
    # Extract information from the event (if provided)
    name = event.get('name', 'World')
    
    # Create response message
    message = f"Hello, {name}!"
    
    # Log the response
    logger.info(f"Returning message: {message}")
    
    # Return the response
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'message': message,
            'timestamp': current_time,
            'function_name': context.function_name if context else 'local',
            'request_id': context.request_id if context else 'N/A'
        })
    }
    
    return response


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        'name': 'GitHub User'
    }
    
    # Mock context for local testing
    class MockContext:
        function_name = "HelloWorldLambda"
        request_id = "local-test-request-id"
    
    # Run the handler
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
