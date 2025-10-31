#!/usr/bin/env python3
"""
Unit tests for the Rantoo Epoch Converter API
"""
import pytest
import json
from datetime import datetime, timezone
from app import app, human_to_epoch, epoch_to_human


class TestDateTimeFunctions:
    """Test the core datetime conversion functions"""
    
    def test_epoch_to_human(self):
        """Test epoch to human datetime conversion"""
        # Test known epoch timestamp
        epoch = 1757509860
        result = epoch_to_human(epoch)
        assert result == "Wed 2025-09-10 13:11:00 UTC"
        
        # Test Christmas 2023
        epoch = 1703520600
        result = epoch_to_human(epoch)
        assert result == "Mon 2023-12-25 16:10:00 UTC"
        
        # Test current time format
        current_epoch = int(datetime.now(timezone.utc).timestamp())
        result = epoch_to_human(current_epoch)
        # Should start with day abbreviation and have proper format
        assert result.startswith(('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'))
        assert ' ' in result  # Should have space between day and date
        assert ':' in result  # Should have colons in time
    
    def test_human_to_epoch_formats(self):
        """Test human to epoch conversion with various formats"""
        # Test YYYY-MM-DD-HHMMSS format
        result = human_to_epoch('2025-09-10-131100')
        assert result == 1757509860
        
        # Test YYYYMMDDHHMMSS format
        result = human_to_epoch('20250910131100')
        assert result == 1757509860
        
        # Test YYYYMMDDHHMM format (no seconds)
        result = human_to_epoch('202509101311')
        assert result == 1757509860  # Should default seconds to 00
        
        # Test legacy MM/DD/YYYY HH:MM format
        result = human_to_epoch('12/25/2023 16:10')
        assert result == 1703520600
    
    def test_human_to_epoch_invalid_formats(self):
        """Test human to epoch conversion with invalid formats"""
        with pytest.raises(ValueError):
            human_to_epoch('invalid-date')
        
        with pytest.raises(ValueError):
            human_to_epoch('2025-13-45-250000')  # Invalid month/day/time
        
        with pytest.raises(ValueError):
            human_to_epoch('not-a-date-at-all')
    
    def test_epoch_to_human_with_timezone(self):
        """Test epoch to human conversion with timezone"""
        # Test known epoch timestamp
        epoch = 1757509860
        
        # Test with Los Angeles timezone
        result = epoch_to_human(epoch, 'America/Los_Angeles')
        assert result.endswith('PST') or result.endswith('PDT')
        
        # Test with New York timezone
        result = epoch_to_human(epoch, 'America/New_York')
        assert result.endswith('EST') or result.endswith('EDT')
        
        # Test with Tokyo timezone
        result = epoch_to_human(epoch, 'Asia/Tokyo')
        assert result.endswith('JST') or 'GMT+9' in result
    
    def test_human_to_epoch_with_timezone(self):
        """Test human to epoch conversion with timezone"""
        # The same datetime in different timezones should produce different epoch values
        # 2025-09-10 13:11:00 in Los Angeles should be different from UTC
        
        # Convert same time in different timezones to verify they produce different epochs
        dt_str = '2025-09-10-131100'
        
        # Convert as UTC (default behavior)
        epoch_utc = human_to_epoch(dt_str)
        
        # Convert as Pacific Time
        epoch_pst = human_to_epoch(dt_str, 'America/Los_Angeles')
        
        # These should be different (LA is behind UTC)
        assert epoch_pst != epoch_utc
        
        # The epoch values should be approximately 8 hours apart (or 7 if DST)
        # PST is UTC-8, PDT is UTC-7
        time_diff = abs(epoch_utc - epoch_pst)
        assert 7 * 3600 <= time_diff <= 8 * 3600  # 7-8 hours in seconds


class TestAPIEndpoints:
    """Test the Flask API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_api_v1_epoch_to_datetime(self, client):
        """Test /api/v1/epoch/{epoch_time} endpoint"""
        response = client.get('/api/v1/epoch/1757509860')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['epoch'] == 1757509860
        assert data['datetime'] == "Wed 2025-09-10 13:11:00 UTC"
        assert data['input'] == "1757509860"
    
    def test_api_v1_datetime_to_epoch_formats(self, client):
        """Test /api/v1/datetime/{datetime_str} endpoint with various formats"""
        # Test YYYY-MM-DD-HHMMSS format
        response = client.get('/api/v1/datetime/2025-09-10-131100')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['epoch'] == 1757509860
        assert data['datetime'] == "2025-09-10-131100"
        
        # Test YYYYMMDDHHMMSS format
        response = client.get('/api/v1/datetime/20250910131100')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['epoch'] == 1757509860
        
        # Test YYYYMMDDHHMM format (no seconds)
        response = client.get('/api/v1/datetime/202509101311')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['epoch'] == 1757509860
    
    def test_api_v1_invalid_datetime(self, client):
        """Test /api/v1/datetime/{datetime_str} endpoint with invalid input"""
        response = client.get('/api/v1/datetime/invalid-date')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert 'message' in data
        assert 'Invalid datetime format' in data['message']
    
    def test_curl_v1_epoch_to_datetime(self, client):
        """Test /curl/v1/epoch/{epoch_time} endpoint"""
        response = client.get('/curl/v1/epoch/1757509860')
        assert response.status_code == 200
        
        text = response.data.decode('utf-8')
        assert 'Epoch:     1757509860' in text
        assert 'Datetime:  Wed 2025-09-10 13:11:00 UTC' in text
        assert 'Input:     1757509860' in text
    
    def test_curl_v1_datetime_to_epoch_formats(self, client):
        """Test /curl/v1/datetime/{datetime_str} endpoint with various formats"""
        # Test YYYY-MM-DD-HHMMSS format
        response = client.get('/curl/v1/datetime/2025-09-10-131100')
        assert response.status_code == 200
        
        text = response.data.decode('utf-8')
        assert 'Epoch:     1757509860' in text
        assert 'Datetime:  2025-09-10-131100' in text
        
        # Test YYYYMMDDHHMMSS format
        response = client.get('/curl/v1/datetime/20250910131100')
        assert response.status_code == 200
        
        text = response.data.decode('utf-8')
        assert 'Epoch:     1757509860' in text
    
    def test_curl_v1_invalid_datetime(self, client):
        """Test /curl/v1/datetime/{datetime_str} endpoint with invalid input"""
        response = client.get('/curl/v1/datetime/invalid-date')
        assert response.status_code == 400
        
        text = response.data.decode('utf-8')
        assert 'Error: Invalid datetime format' in text
    
    def test_health_endpoint(self, client):
        """Test /health endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns HTML"""
        response = client.get('/')
        assert response.status_code == 200
        assert 'text/html' in response.content_type


class TestSwaggerDocumentation:
    """Test Swagger documentation endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create a test client for the Flask app"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_api_swagger_json(self, client):
        """Test /api/swagger.json endpoint"""
        response = client.get('/api/swagger.json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'swagger' in data
        assert 'info' in data
        assert data['info']['title'] == 'TimePuff Epoch Converter API'
    
    def test_api_docs_endpoint(self, client):
        """Test /api/docs/ endpoint"""
        response = client.get('/api/docs/')
        assert response.status_code == 200
        assert 'text/html' in response.content_type


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
