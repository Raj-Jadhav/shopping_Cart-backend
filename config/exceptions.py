
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    Uses functional programming to transform errors.
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        # Transform error response to consistent format
        error_data = {
            'success': False,
            'error': {
                'message': '',
                'details': {},
                'code': response.status_code
            }
        }
        
        # Extract error messages using functional approach
        if isinstance(response.data, dict):
            error_messages = list(map(
                lambda item: f"{item[0]}: {item[1][0]}" if isinstance(item[1], list) else f"{item[0]}: {item[1]}",
                filter(lambda item: item[0] != 'detail', response.data.items())
            ))
            
            if 'detail' in response.data:
                error_data['error']['message'] = str(response.data['detail'])
            elif error_messages:
                error_data['error']['message'] = '; '.join(error_messages)
            else:
                error_data['error']['message'] = 'An error occurred'
                
            error_data['error']['details'] = response.data
        else:
            error_data['error']['message'] = str(response.data)
        
        response.data = error_data
        
        # Log error for monitoring
        logger.error(
            f"API Error: {error_data['error']['message']} | "
            f"Path: {context.get('request').path if context.get('request') else 'Unknown'} | "
            f"User: {context.get('request').user if context.get('request') else 'Anonymous'}"
        )
    else:
        # Handle unexpected errors
        logger.critical(f"Unhandled exception: {str(exc)}", exc_info=True)
        response = Response(
            {
                'success': False,
                'error': {
                    'message': 'An unexpected error occurred. Please try again later.',
                    'details': {},
                    'code': status.HTTP_500_INTERNAL_SERVER_ERROR
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    return response