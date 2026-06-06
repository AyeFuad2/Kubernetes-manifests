"""
Flask Joke Generator Application
Integrates with JokeAPI to fetch random jokes with filtering options
"""

from flask import Flask, jsonify, request
import requests
import logging
from datetime import datetime
from functools import lru_cache

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JokeAPI configuration
JOKE_API_URL = "https://v2.jokeapi.dev/joke"
JOKE_API_TIMEOUT = 5

# Supported joke categories
JOKE_CATEGORIES = ["General", "Programming", "Knock-Knock"]
JOKE_TYPES = ["single", "twopart"]


class JokeAPIError(Exception):
    """Custom exception for JokeAPI errors"""
    pass


@lru_cache(maxsize=128)
def get_supported_categories():
    """Get list of supported joke categories"""
    return JOKE_CATEGORIES


def validate_category(category):
    """Validate if category is supported"""
    if category not in get_supported_categories():
        return False
    return True


def validate_type(joke_type):
    """Validate if joke type is supported"""
    if joke_type not in JOKE_TYPES:
        return False
    return True


def fetch_joke_from_api(category="Any", joke_type="any"):
    """
    Fetch a joke from JokeAPI
    
    Args:
        category (str): Joke category (General, Programming, Knock-Knock, or Any)
        joke_type (str): Joke type (single, twopart, or any)
    
    Returns:
        dict: Joke data from API
    
    Raises:
        JokeAPIError: If API request fails
    """
    try:
        # Build API endpoint
        if category.lower() == "any":
            endpoint = f"{JOKE_API_URL}/Any"
        else:
            endpoint = f"{JOKE_API_URL}/{category}"
        
        # Build query parameters
        params = {
            "type": joke_type if joke_type.lower() != "any" else "any",
            "format": "json"
        }
        
        logger.info(f"Fetching joke from {endpoint} with params {params}")
        
        response = requests.get(
            endpoint,
            params=params,
            timeout=JOKE_API_TIMEOUT
        )
        response.raise_for_status()
        
        joke_data = response.json()
        
        if joke_data.get("error"):
            raise JokeAPIError(f"API Error: {joke_data.get('message', 'Unknown error')}")
        
        logger.info("Successfully fetched joke from API")
        return joke_data
        
    except requests.exceptions.Timeout:
        logger.error("Request to JokeAPI timed out")
        raise JokeAPIError("Request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to JokeAPI")
        raise JokeAPIError("Failed to connect to joke service. Please try again.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        raise JokeAPIError(f"Failed to fetch joke: {str(e)}")


def format_joke_response(joke_data):
    """
    Format joke data into a consistent response format
    
    Args:
        joke_data (dict): Raw joke data from API
    
    Returns:
        dict: Formatted joke response
    """
    formatted = {
        "joke": None,
        "type": joke_data.get("type"),
        "category": joke_data.get("category"),
        "fetched_at": datetime.utcnow().isoformat()
    }
    
    if joke_data.get("type") == "single":
        formatted["joke"] = joke_data.get("joke")
    elif joke_data.get("type") == "twopart":
        formatted["setup"] = joke_data.get("setup")
        formatted["delivery"] = joke_data.get("delivery")
        formatted["joke"] = f"{joke_data.get('setup')} {joke_data.get('delivery')}"
    
    return formatted


@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Joke Generator API",
        "version": "1.0.0"
    }), 200


@app.route("/api/joke", methods=["GET"])
def get_random_joke():
    """
    Get a random joke
    
    Query Parameters:
        - category: Joke category (General, Programming, Knock-Knock, or Any)
        - type: Joke type (single, twopart, or any)
    
    Returns:
        JSON: Random joke with metadata
    """
    try:
        category = request.args.get("category", "Any").strip()
        joke_type = request.args.get("type", "any").strip()
        
        # Validate inputs
        if category.lower() != "any" and not validate_category(category):
            return jsonify({
                "error": f"Invalid category: {category}",
                "supported_categories": get_supported_categories()
            }), 400
        
        if joke_type.lower() != "any" and not validate_type(joke_type):
            return jsonify({
                "error": f"Invalid type: {joke_type}",
                "supported_types": JOKE_TYPES
            }), 400
        
        # Fetch joke from API
        joke_data = fetch_joke_from_api(category, joke_type)
        formatted_joke = format_joke_response(joke_data)
        
        return jsonify(formatted_joke), 200
        
    except JokeAPIError as e:
        logger.error(f"Joke API Error: {str(e)}")
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.route("/api/joke/categories", methods=["GET"])
def get_categories():
    """Get list of supported joke categories"""
    return jsonify({
        "categories": get_supported_categories()
    }), 200


@app.route("/api/joke/types", methods=["GET"])
def get_types():
    """Get list of supported joke types"""
    return jsonify({
        "types": JOKE_TYPES
    }), 200


@app.route("/api/joke/random", methods=["GET"])
def get_completely_random_joke():
    """Get a completely random joke (any category, any type)"""
    try:
        joke_data = fetch_joke_from_api("Any", "any")
        formatted_joke = format_joke_response(joke_data)
        return jsonify(formatted_joke), 200
    except JokeAPIError as e:
        logger.error(f"Joke API Error: {str(e)}")
        return jsonify({"error": str(e)}), 503
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": {
            "GET /": "Health check",
            "GET /api/joke": "Get a random joke",
            "GET /api/joke/random": "Get a completely random joke",
            "GET /api/joke/categories": "Get supported categories",
            "GET /api/joke/types": "Get supported types"
        }
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
