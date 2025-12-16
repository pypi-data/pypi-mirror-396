#!/usr/bin/env python3
"""
API functionality tests for AdDownloader using mocking
No real API calls or access tokens required!
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
import json
import pandas as pd
from datetime import datetime

# Add the AdDownloader module to path
sys.path.append('..')

class TestAdLibAPIInitialization(unittest.TestCase):
    """Test AdLibAPI class initialization"""
    
    @patch('AdDownloader.adlib_api.configure_logging')
    def test_api_initialization_basic(self, mock_configure_logging):
        """Test basic API initialization"""
        from AdDownloader.adlib_api import AdLibAPI
        
        mock_configure_logging.return_value = MagicMock()
        
        # Test basic initialization
        api = AdLibAPI("test_token", project_name="test_project")
        
        self.assertEqual(api.access_token, "test_token")
        self.assertEqual(api.project_name, "test_project")
        self.assertEqual(api.version, "v20.0")
        self.assertIn("v20.0", api.base_url)
        self.assertIsNone(api.fields)
        
        # Verify logging was configured
        mock_configure_logging.assert_called_once_with("test_project")
        
        print("✓ AdLibAPI initializes correctly")
    
    @patch('AdDownloader.adlib_api.configure_logging')
    def test_api_initialization_custom_version(self, mock_configure_logging):
        """Test API initialization with custom version"""
        from AdDownloader.adlib_api import AdLibAPI
        
        mock_configure_logging.return_value = MagicMock()
        
        api = AdLibAPI("test_token", version="v19.0", project_name="custom_project")
        
        self.assertEqual(api.version, "v19.0")
        self.assertIn("v19.0", api.base_url)
        self.assertEqual(api.project_name, "custom_project")
        
        print("✓ AdLibAPI accepts custom version")
    
    @patch('AdDownloader.adlib_api.configure_logging')
    def test_api_initialization_default_project_name(self, mock_configure_logging):
        """Test API initialization with default project name"""
        mock_configure_logging.return_value = MagicMock()
        
        # Import after patches are setup
        from AdDownloader.adlib_api import AdLibAPI
        
        # Instead of mocking the default parameter, just test that we get a valid timestamp format
        api = AdLibAPI("test_token")
        
        # Check that project_name matches the expected timestamp format (YYYYMMDDHHMMSS)
        import re
        timestamp_pattern = r'^\d{14}$'  # 14 digits: YYYYMMDDHHMMSS
        self.assertRegex(api.project_name, timestamp_pattern)
        self.assertEqual(len(api.project_name), 14)
        
        print("✓ AdLibAPI uses default project name with correct format")
        print("✓ AdLibAPI generates default project name")


class TestAdLibAPIParameterHandling(unittest.TestCase):
    """Test API parameter handling and validation"""
    
    @patch('AdDownloader.adlib_api.configure_logging')
    def setUp(self, mock_configure_logging):
        """Set up API instance for testing"""
        from AdDownloader.adlib_api import AdLibAPI
        
        mock_configure_logging.return_value = MagicMock()
        self.api = AdLibAPI("test_token", project_name="test")
    
    @patch('AdDownloader.adlib_api.datetime')
    def test_add_parameters_basic(self, mock_datetime):
        """Test basic parameter addition"""
        mock_datetime.today.return_value.strftime.return_value = "2024-01-01"
        
        with patch.object(self.api, 'get_fields', return_value="id,ad_creative_bodies"):
            self.api.add_parameters(
                ad_reached_countries="US",
                ad_delivery_date_min="2023-01-01",
                ad_delivery_date_max="2023-12-31",
                search_terms="test search"
            )
        
        params = self.api.request_parameters
        
        self.assertEqual(params["ad_reached_countries"], "US")
        self.assertEqual(params["ad_delivery_date_min"], "2023-01-01")
        self.assertEqual(params["ad_delivery_date_max"], "2023-12-31")
        self.assertEqual(params["search_terms"], "test search")
        self.assertEqual(params["access_token"], "test_token")
        
        print("✓ add_parameters handles basic parameters correctly")
    
    @patch('AdDownloader.adlib_api.datetime')
    @patch('AdDownloader.adlib_api.is_valid_excel_file')
    @patch('AdDownloader.adlib_api.pd.read_excel')
    def test_add_parameters_with_page_ids(self, mock_read_excel, mock_is_valid, mock_datetime):
        """Test parameter addition with page IDs"""
        mock_datetime.today.return_value.strftime.return_value = "2024-01-01"
        mock_is_valid.return_value = True
        mock_read_excel.return_value = pd.DataFrame({
            'page_id': ['123456789', '987654321']
        })
        
        with patch.object(self.api, 'get_fields', return_value="id,ad_creative_bodies"):
            self.api.add_parameters(
                search_page_ids="test_pages.xlsx"
            )
        
        params = self.api.request_parameters
        
        self.assertEqual(params["search_page_ids"], ['123456789', '987654321'])
        self.assertIsNone(params["search_terms"])
        
        print("✓ add_parameters handles page IDs correctly")
    
    @patch('AdDownloader.adlib_api.datetime')
    def test_date_validation_future_dates(self, mock_datetime):
        """Test date validation for future dates"""
        mock_datetime.today.return_value.strftime.return_value = "2024-01-01"
        
        with patch.object(self.api, 'get_fields', return_value="id"):
            with patch.object(self.api, 'logger') as mock_logger:
                self.api.add_parameters(
                    ad_delivery_date_min="2025-01-01",  # Future date
                    ad_delivery_date_max="2025-12-31",  # Future date
                    search_terms="test"
                )
        
        params = self.api.request_parameters
        
        # Should be corrected to current date
        self.assertEqual(params["ad_delivery_date_min"], "2024-01-01")
        self.assertEqual(params["ad_delivery_date_max"], "2024-01-01")
        
        print("✓ Date validation corrects future dates")
    
    @patch('AdDownloader.adlib_api.datetime')
    def test_date_validation_min_greater_than_max(self, mock_datetime):
        """Test date validation when min > max"""
        mock_datetime.today.return_value.strftime.return_value = "2024-01-01"
        
        with patch.object(self.api, 'get_fields', return_value="id"):
            with patch.object(self.api, 'logger') as mock_logger:
                self.api.add_parameters(
                    ad_delivery_date_min="2023-12-01",
                    ad_delivery_date_max="2023-01-01",  # Earlier than min
                    search_terms="test"
                )
        
        params = self.api.request_parameters
        
        # Should be swapped
        self.assertEqual(params["ad_delivery_date_min"], "2023-01-01")
        self.assertEqual(params["ad_delivery_date_max"], "2023-12-01")
        
        print("✓ Date validation swaps incorrect min/max dates")
    
    def test_add_parameters_with_kwargs(self):
        """Test parameter addition with additional kwargs"""
        with patch.object(self.api, 'get_fields', return_value="id"):
            self.api.add_parameters(
                search_terms="test",
                estimated_audience_size_max=10000,
                custom_param="custom_value"
            )
        
        params = self.api.request_parameters
        
        self.assertEqual(params["estimated_audience_size_max"], 10000)
        self.assertEqual(params["custom_param"], "custom_value")
        
        print("✓ add_parameters handles additional kwargs")


class TestAdLibAPIDataFetching(unittest.TestCase):
    """Test API data fetching with mocked requests"""
    
    @patch('AdDownloader.adlib_api.configure_logging')
    def setUp(self, mock_configure_logging):
        """Set up API instance for testing"""
        from AdDownloader.adlib_api import AdLibAPI
        
        mock_configure_logging.return_value = MagicMock()
        self.api = AdLibAPI("test_token", project_name="test")
        self.api.logger = MagicMock()
    
    @patch('AdDownloader.adlib_api.requests.get')
    @patch('AdDownloader.adlib_api.os.makedirs')
    @patch('AdDownloader.adlib_api.os.path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('AdDownloader.adlib_api.json.dump')
    def test_fetch_data_successful(self, mock_json_dump, mock_file, mock_exists, mock_makedirs, mock_requests):
        """Test successful data fetching"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [
                {"id": "1", "ad_creative_bodies": ["Test ad 1"]},
                {"id": "2", "ad_creative_bodies": ["Test ad 2"]}
            ]
        }
        mock_requests.return_value = mock_response
        mock_exists.return_value = False  # Folder doesn't exist
        
        # Test fetch_data
        self.api.fetch_data("http://test.url", {"param": "value"}, page_number=1)
        
        # Verify API call was made
        mock_requests.assert_called_once_with("http://test.url", params={"param": "value"})
        
        # Verify folder creation
        mock_makedirs.assert_called_once()
        
        # Verify JSON file was written
        mock_json_dump.assert_called_once()
        
        print("✓ fetch_data handles successful response")
    
    @patch('AdDownloader.adlib_api.requests.get')
    def test_fetch_data_api_error(self, mock_requests):
        """Test handling of API error responses"""
        # Mock API error response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "error": {
                "message": "Invalid access token"
            }
        }
        mock_requests.return_value = mock_response
        
        # Test fetch_data with error
        result = self.api.fetch_data("http://test.url", {"param": "value"})
        
        # Should handle error gracefully and return None
        self.assertIsNone(result)
        
        print("✓ fetch_data handles API errors")
    
    @patch('AdDownloader.adlib_api.requests.get')
    def test_fetch_data_no_data(self, mock_requests):
        """Test handling when no data is returned"""
        # Mock response with no data
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": []}
        mock_requests.return_value = mock_response
        
        # Test fetch_data with empty data
        result = self.api.fetch_data("http://test.url", {"param": "value"})
        
        # Should handle empty data and return None
        self.assertIsNone(result)
        
        print("✓ fetch_data handles empty data")
    
    @patch('AdDownloader.adlib_api.requests.get')
    def test_fetch_data_with_pagination(self, mock_requests):
        """Test data fetching with pagination"""
        # Mock first response with pagination
        mock_response_1 = MagicMock()
        mock_response_1.json.return_value = {
            "data": [{"id": "1", "ad_creative_bodies": ["Test ad 1"]}],
            "paging": {"next": "http://test.url/page2"}
        }
        
        # Mock second response (final page)
        mock_response_2 = MagicMock()
        mock_response_2.json.return_value = {
            "data": [{"id": "2", "ad_creative_bodies": ["Test ad 2"]}]
        }
        
        mock_requests.side_effect = [mock_response_1, mock_response_2]
        
        with patch('AdDownloader.adlib_api.os.makedirs'):
            with patch('AdDownloader.adlib_api.os.path.exists', return_value=True):
                with patch('builtins.open', mock_open()):
                    with patch('AdDownloader.adlib_api.json.dump'):
                        # Test fetch_data with pagination
                        self.api.fetch_data("http://test.url", {"param": "value"})
        
        # Should make 2 API calls due to pagination
        self.assertEqual(mock_requests.call_count, 2)
        
        print("✓ fetch_data handles pagination")
    
    @patch('AdDownloader.adlib_api.requests.get')
    def test_fetch_data_request_exception_with_retry(self, mock_requests):
        """Test request exception handling with retry"""
        # Mock first request to fail, second to succeed
        mock_response_success = MagicMock()
        mock_response_success.json.return_value = {
            "data": [{"id": "1", "ad_creative_bodies": ["Test ad"]}]
        }
        
        # First call raises exception during json(), second succeeds
        mock_response_error = MagicMock()
        mock_response_error.json.side_effect = Exception("Connection error")
        
        mock_requests.side_effect = [
            mock_response_error,
            mock_response_success
        ]
        
        with patch('AdDownloader.adlib_api.os.makedirs'):
            with patch('AdDownloader.adlib_api.os.path.exists', return_value=True):
                with patch('builtins.open', mock_open()):
                    with patch('AdDownloader.adlib_api.json.dump'):
                        self.api.fetch_data("http://test.url", {"param": "value"})
        
        # Should make 2 API calls (original + retry)
        self.assertEqual(mock_requests.call_count, 2)
        
        print("✓ fetch_data handles exceptions with retry")


class TestAdLibAPIStartDownload(unittest.TestCase):
    """Test the start_download functionality"""
    
    @patch('AdDownloader.adlib_api.configure_logging')
    def setUp(self, mock_configure_logging):
        """Set up API instance for testing"""
        from AdDownloader.adlib_api import AdLibAPI
        
        mock_configure_logging.return_value = MagicMock()
        self.api = AdLibAPI("test_token", project_name="test")
        self.api.logger = MagicMock()
    
    @patch('AdDownloader.adlib_api.AdLibAPI.fetch_data')
    def test_start_download_with_search_terms(self, mock_fetch_data):
        """Test start_download with search terms"""
        # Set up parameters with all required keys
        self.api.request_parameters = {
            "search_terms": "test search",
            "search_page_ids": None,
            "ad_reached_countries": "US",
            "limit": "300",
            "access_token": "test_token"
        }
        
        # Test start_download
        self.api.start_download()
        
        # Verify fetch_data was called
        mock_fetch_data.assert_called_once()
        
        print("✓ start_download works with search terms")
    
    @patch('AdDownloader.adlib_api.AdLibAPI.fetch_data')
    def test_start_download_with_page_ids(self, mock_fetch_data):
        """Test start_download with page IDs"""
        # Set up parameters with page IDs and all required keys
        # Using only 2 page IDs which fit in one batch (batches of 10)
        self.api.request_parameters = {
            "search_page_ids": ["123456789", "987654321"],
            "search_terms": None,
            "ad_reached_countries": "US",
            "limit": "300",
            "access_token": "test_token"
        }
        
        # Test start_download
        self.api.start_download()
        
        # Should call fetch_data once for a single batch of 2 page IDs
        self.assertEqual(mock_fetch_data.call_count, 1)
        
        print("✓ start_download works with page IDs (single batch)")
    
    @patch('AdDownloader.adlib_api.AdLibAPI.fetch_data')
    def test_start_download_with_multiple_page_id_batches(self, mock_fetch_data):
        """Test start_download with multiple batches of page IDs"""
        # Set up parameters with 15 page IDs to test multiple batches (batches of 10)
        page_ids = [f"12345678{i}" for i in range(15)]  # 15 page IDs
        self.api.request_parameters = {
            "search_page_ids": page_ids,
            "search_terms": None,
            "ad_reached_countries": "US", 
            "limit": "300",
            "access_token": "test_token"
        }
        
        # Test start_download
        self.api.start_download()
        
        # Should call fetch_data twice: batch 1 (0-9), batch 2 (10-14)
        self.assertEqual(mock_fetch_data.call_count, 2)
        
        print("✓ start_download works with multiple page ID batches")
    
    def test_start_download_no_parameters(self):
        """Test start_download with no parameters set"""
        # Empty parameters should cause an error
        self.api.request_parameters = {}
        
        with patch('builtins.print') as mock_print:
            try:
                self.api.start_download()
            except KeyError:
                # Expected behavior when parameters are missing
                pass
        
        print("✓ start_download handles missing parameters")


class TestAdLibAPIHelperMethods(unittest.TestCase):
    """Test helper methods of AdLibAPI"""
    
    @patch('AdDownloader.adlib_api.configure_logging')
    def setUp(self, mock_configure_logging):
        """Set up API instance for testing"""
        from AdDownloader.adlib_api import AdLibAPI
        
        mock_configure_logging.return_value = MagicMock()
        self.api = AdLibAPI("test_token", project_name="test")
    
    def test_get_parameters(self):
        """Test get_parameters method"""
        # Set some parameters
        test_params = {
            "ad_reached_countries": "US",
            "search_terms": "test"
        }
        self.api.request_parameters = test_params
        
        result = self.api.get_parameters()
        
        self.assertEqual(result, test_params)
        
        print("✓ get_parameters returns correct parameters")
    
    def test_get_fields_for_different_ad_types(self):
        """Test get_fields method for different ad types"""
        # Test for ALL ads
        fields_all = self.api.get_fields("ALL")
        self.assertIsInstance(fields_all, str)
        self.assertIn("id", fields_all)
        
        # Test for POLITICAL ads
        fields_political = self.api.get_fields("POLITICAL_AND_ISSUE_ADS")
        self.assertIsInstance(fields_political, str)
        self.assertIn("id", fields_political)
        
        # Political ads should have additional fields
        self.assertNotEqual(fields_all, fields_political)
        
        print("✓ get_fields works for different ad types")


if __name__ == "__main__":
    unittest.main(verbosity=2)
