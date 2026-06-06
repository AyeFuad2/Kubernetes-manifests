"""
Unit tests for Joke Generator Flask application
"""

import unittest
from unittest.mock import patch, MagicMock
import json
from app import app, format_joke_response, validate_category, validate_type


class JokeGeneratorTestCase(unittest.TestCase):
    """Test cases for Joke Generator API"""
    
    def setUp(self):
        """Set up test client and fixtures"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Sample joke responses
        self.sample_single_joke = {
            "type": "single",
            "joke": "Why did the programmer quit his job? Because he didn't get arrays.",
            "category": "Programming",
            "error": False
        }
        
        self.sample_twopart_joke = {
            "type": "twopart",
            "setup": "Why do Java developers wear glasses?",
            "delivery": "Because they don't C#",
            "category": "Programming",
            "error": False
        }
    
    # Health and Basic Endpoint Tests
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "healthy")
        self.assertIn("service", data)
    
    def test_not_found_endpoint(self):
        """Test 404 error handling"""
        response = self.client.get("/nonexistent")
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)
    
    # Category and Type Endpoint Tests
    
    def test_get_categories(self):
        """Test get categories endpoint"""
        response = self.client.get("/api/joke/categories")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("categories", data)
        self.assertIsInstance(data["categories"], list)
        self.assertTrue(len(data["categories"]) > 0)
    
    def test_get_types(self):
        """Test get types endpoint"""
        response = self.client.get("/api/joke/types")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("types", data)
        self.assertIsInstance(data["types"], list)
        self.assertEqual(data["types"], ["single", "twopart"])
    
    # Validation Tests
    
    def test_validate_category_valid(self):
        """Test category validation with valid category"""
        self.assertTrue(validate_category("General"))
        self.assertTrue(validate_category("Programming"))
        self.assertTrue(validate_category("Knock-Knock"))
    
    def test_validate_category_invalid(self):
        """Test category validation with invalid category"""
        self.assertFalse(validate_category("Invalid"))
        self.assertFalse(validate_category("Sports"))
    
    def test_validate_type_valid(self):
        """Test type validation with valid types"""
        self.assertTrue(validate_type("single"))
        self.assertTrue(validate_type("twopart"))
    
    def test_validate_type_invalid(self):
        """Test type validation with invalid types"""
        self.assertFalse(validate_type("invalid"))
        self.assertFalse(validate_type("three-part"))
    
    # Format Response Tests
    
    def test_format_single_joke(self):
        """Test formatting a single joke response"""
        formatted = format_joke_response(self.sample_single_joke)
        self.assertEqual(formatted["type"], "single")
        self.assertEqual(formatted["joke"], self.sample_single_joke["joke"])
        self.assertIn("fetched_at", formatted)
    
    def test_format_twopart_joke(self):
        """Test formatting a two-part joke response"""
        formatted = format_joke_response(self.sample_twopart_joke)
        self.assertEqual(formatted["type"], "twopart")
        self.assertEqual(formatted["setup"], self.sample_twopart_joke["setup"])
        self.assertEqual(formatted["delivery"], self.sample_twopart_joke["delivery"])
        self.assertIn("joke", formatted)
        self.assertIn("fetched_at", formatted)
    
    # API Endpoint Tests with Mocking
    
    @patch('app.fetch_joke_from_api')
    def test_get_random_joke_success(self, mock_fetch):
        """Test get random joke endpoint with successful response"""
        mock_fetch.return_value = self.sample_single_joke
        
        response = self.client.get("/api/joke")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["type"], "single")
        self.assertIn("joke", data)
    
    @patch('app.fetch_joke_from_api')
    def test_get_random_joke_with_category(self, mock_fetch):
        """Test get random joke endpoint with category filter"""
        mock_fetch.return_value = self.sample_single_joke
        
        response = self.client.get("/api/joke?category=Programming")
        self.assertEqual(response.status_code, 200)
        mock_fetch.assert_called_once_with("Programming", "any")
    
    @patch('app.fetch_joke_from_api')
    def test_get_random_joke_with_type(self, mock_fetch):
        """Test get random joke endpoint with type filter"""
        mock_fetch.return_value = self.sample_twopart_joke
        
        response = self.client.get("/api/joke?type=twopart")
        self.assertEqual(response.status_code, 200)
        mock_fetch.assert_called_once_with("Any", "twopart")
    
    @patch('app.fetch_joke_from_api')
    def test_get_random_joke_with_category_and_type(self, mock_fetch):
        """Test get random joke endpoint with both filters"""
        mock_fetch.return_value = self.sample_twopart_joke
        
        response = self.client.get("/api/joke?category=Programming&type=twopart")
        self.assertEqual(response.status_code, 200)
        mock_fetch.assert_called_once_with("Programming", "twopart")
    
    def test_get_random_joke_invalid_category(self):
        """Test get random joke endpoint with invalid category"""
        response = self.client.get("/api/joke?category=InvalidCategory")
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("Invalid category", data["error"])
    
    def test_get_random_joke_invalid_type(self):
        """Test get random joke endpoint with invalid type"""
        response = self.client.get("/api/joke?type=invalid")
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("Invalid type", data["error"])
    
    @patch('app.fetch_joke_from_api')
    def test_get_completely_random_joke(self, mock_fetch):
        """Test completely random joke endpoint"""
        mock_fetch.return_value = self.sample_single_joke
        
        response = self.client.get("/api/joke/random")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("joke", data)
        mock_fetch.assert_called_once_with("Any", "any")
    
    @patch('app.fetch_joke_from_api')
    def test_joke_api_error_handling(self, mock_fetch):
        """Test error handling when JokeAPI fails"""
        from app import JokeAPIError
        mock_fetch.side_effect = JokeAPIError("API Error: Service unavailable")
        
        response = self.client.get("/api/joke")
        self.assertEqual(response.status_code, 503)
        data = json.loads(response.data)
        self.assertIn("error", data)


class ResponseFormatTestCase(unittest.TestCase):
    """Test cases for response formatting"""
    
    def test_response_includes_timestamp(self):
        """Test that responses include timestamp"""
        joke_data = {
            "type": "single",
            "joke": "Test joke",
            "category": "General",
            "error": False
        }
        formatted = format_joke_response(joke_data)
        self.assertIn("fetched_at", formatted)
    
    def test_response_includes_category(self):
        """Test that responses include category"""
        joke_data = {
            "type": "single",
            "joke": "Test joke",
            "category": "Programming",
            "error": False
        }
        formatted = format_joke_response(joke_data)
        self.assertEqual(formatted["category"], "Programming")
    
    def test_response_includes_type(self):
        """Test that responses include type"""
        joke_data = {
            "type": "single",
            "joke": "Test joke",
            "category": "General",
            "error": False
        }
        formatted = format_joke_response(joke_data)
        self.assertEqual(formatted["type"], "single")


if __name__ == "__main__":
    unittest.main()
