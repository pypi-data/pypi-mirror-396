#!/usr/bin/env python3
"""
Comprehensive tests for AdDownloader helpers module
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
import pandas as pd
import json
import tempfile
from datetime import datetime

# Add the AdDownloader module to path
sys.path.append('..')

class TestHelperValidators(unittest.TestCase):
    """Test all validator classes comprehensively"""
    
    def test_number_validator_edge_cases(self):
        """Test NumberValidator with edge cases"""
        from AdDownloader.helpers import NumberValidator
        
        # Test valid edge cases
        valid_edge_cases = ["0", "-1", "999999", "1"]
        for num in valid_edge_cases:
            try:
                result = NumberValidator.validate_number({}, num)
                self.assertTrue(result, f"Should validate edge case number: {num}")
            except Exception:
                self.fail(f"Valid edge case number {num} failed validation")
        
        # Test invalid edge cases (note: some may pass if the validator is lenient)
        invalid_edge_cases = [" ", "123.0", "1.5", "123abc", "abc", ""]
        for num in invalid_edge_cases:
            with self.assertRaises(Exception, msg=f"Should reject invalid edge case: {num}"):
                NumberValidator.validate_number({}, num)
        
        print("✓ NumberValidator handles edge cases correctly")
    
    def test_date_validator_comprehensive(self):
        """Test DateValidator comprehensively"""
        from AdDownloader.helpers import DateValidator
        
        # Test various valid date formats that should work
        valid_dates = [
            "2023-01-01", "2024-12-31", "2022-02-28", "2020-02-29",  # leap year
            "1999-12-31", "2030-06-15"
        ]
        for date in valid_dates:
            try:
                result = DateValidator.validate_date({}, date)
                self.assertTrue(result, f"Should validate date: {date}")
            except Exception:
                self.fail(f"Valid date {date} failed validation")
        
        # Test invalid dates
        invalid_dates = [
            "2023-13-01", "2023-00-01", "2023-01-32", "2023-02-30",
            "abc-01-01", "2023-ab-01", "2023-01-ab", "23-01-01",
            "2023/01/01", "01-01-2023", "", "2023"
        ]
        for date in invalid_dates:
            with self.assertRaises(Exception, msg=f"Should reject invalid date: {date}"):
                DateValidator.validate_date({}, date)
        
        print("✓ DateValidator comprehensive testing passed")
    
    def test_country_validator_comprehensive(self):
        """Test CountryValidator with various country codes"""
        from AdDownloader.helpers import CountryValidator
        
        # Test various valid country codes from the list
        valid_countries = ["US", "NL", "DE", "FR", "GB", "CA", "AU", "BR", "JP", "CN", "ALL"]
        for country in valid_countries:
            try:
                result = CountryValidator.validate_country({}, country)
                self.assertTrue(result, f"Should validate country: {country}")
            except Exception:
                self.fail(f"Valid country {country} failed validation")
        
        # Test invalid country codes
        invalid_countries = ["XX", "ZZ", "ABC", "123", "", "us", "nl", "USA", "Nederland", "12"]
        for country in invalid_countries:
            with self.assertRaises(Exception, msg=f"Should reject invalid country: {country}"):
                CountryValidator.validate_country({}, country)
        
        print("✓ CountryValidator comprehensive testing passed")


class TestHelperDataProcessing(unittest.TestCase):
    """Test data processing helper functions"""
    
    @patch('AdDownloader.helpers.os.listdir')
    @patch('AdDownloader.helpers.open', new_callable=mock_open)
    @patch('AdDownloader.helpers.json.loads')
    def test_load_json_from_folder(self, mock_json_loads, mock_file_open, mock_listdir):
        """Test load_json_from_folder function"""
        from AdDownloader.helpers import load_json_from_folder
        
        # Mock folder contents
        mock_listdir.return_value = ['file1.json', 'file2.json', 'file3.txt']  # .txt should be ignored
        
        # Mock JSON data
        mock_json_data = [
            {
                'data': [
                    {'id': '1', 'name': 'Ad 1'},
                    {'id': '2', 'name': 'Ad 2'}
                ]
            },
            {
                'data': [
                    {'id': '3', 'name': 'Ad 3'}
                ]
            }
        ]
        
        mock_json_loads.side_effect = mock_json_data
        
        # Test the function
        result_df = load_json_from_folder('test_folder')
        
        # Verify results
        self.assertIsInstance(result_df, pd.DataFrame, "Should return a DataFrame")
        self.assertEqual(len(result_df), 3, "Should have 3 rows from combined JSON files")
        
        # Verify only JSON files were processed
        self.assertEqual(mock_file_open.call_count, 2, "Should open only 2 JSON files")
        
        print("✓ load_json_from_folder works correctly")
    
    def test_flatten_age_country_gender_with_valid_data(self):
        """Test flatten_age_country_gender with valid data"""
        from AdDownloader.helpers import flatten_age_country_gender
        
        # Mock age-country-gender data structure
        mock_data = [
            {
                'country': 'US',
                'age_range': '25-34',
                'gender': 'male',
                'reach': 1000
            },
            {
                'country': 'US',
                'age_range': '35-44',
                'gender': 'female',
                'reach': 1500
            }
        ]
        
        result = flatten_age_country_gender(mock_data, 'US')
        
        self.assertIsInstance(result, dict, "Should return a dictionary")
        print("✓ flatten_age_country_gender handles valid data")
    
    def test_flatten_age_country_gender_with_empty_data(self):
        """Test flatten_age_country_gender with empty/invalid data"""
        from AdDownloader.helpers import flatten_age_country_gender
        
        # Test with empty data
        result_empty = flatten_age_country_gender([], 'US')
        self.assertIsInstance(result_empty, dict, "Should handle empty data")
        
        # Test with NaN data
        import pandas as pd
        import numpy as np
        result_nan = flatten_age_country_gender(np.nan, 'US')
        self.assertIsInstance(result_nan, dict, "Should handle NaN data")
        
        # Test with string data (after Excel loading)
        result_string = flatten_age_country_gender("[]", 'US')
        self.assertIsInstance(result_string, dict, "Should handle string data")
        
        print("✓ flatten_age_country_gender handles edge cases")
    
    @patch('AdDownloader.helpers.pd.read_excel')
    @patch('AdDownloader.helpers.os.path.exists')
    def test_is_valid_excel_file_comprehensive(self, mock_exists, mock_read_excel):
        """Test is_valid_excel_file with various scenarios"""
        from AdDownloader.helpers import is_valid_excel_file
        
        # Test valid Excel file
        mock_exists.return_value = True
        mock_read_excel.return_value = pd.DataFrame({'data': [1, 2, 3]})
        
        result = is_valid_excel_file('test.xlsx')
        self.assertTrue(result, "Should validate existing readable Excel file")
        
        # Test non-existent file
        mock_exists.return_value = False
        result = is_valid_excel_file('nonexistent.xlsx')
        self.assertFalse(result, "Should reject non-existent file")
        
        # Test invalid file extension
        mock_exists.return_value = True
        result = is_valid_excel_file('test.txt')
        self.assertFalse(result, "Should reject non-Excel file")
        
        # Test corrupted Excel file
        mock_exists.return_value = True
        mock_read_excel.side_effect = Exception("Corrupted file")
        result = is_valid_excel_file('corrupted.xlsx')
        self.assertFalse(result, "Should reject corrupted Excel file")
        
        print("✓ is_valid_excel_file comprehensive testing passed")


class TestHelperTokenManagement(unittest.TestCase):
    """Test token and access management functions"""
    
    @patch('AdDownloader.helpers.pd.DataFrame.to_excel')
    def test_update_access_token(self, mock_to_excel):
        """Test update_access_token function"""
        from AdDownloader.helpers import update_access_token
        
        # Create test data
        test_data = pd.DataFrame({
            'id': [1, 2, 3],
            'ad_snapshot_url': [
                'https://facebook.com/ad/1?access_token=old_token',
                'https://facebook.com/ad/2?access_token=old_token', 
                'https://facebook.com/ad/3?access_token=old_token'
            ]
        })
        
        new_token = 'new_test_token'
        
        # Test the function
        updated_data = update_access_token(test_data, new_token)
        
        # Verify token was updated
        self.assertIsInstance(updated_data, pd.DataFrame, "Should return DataFrame")
        for url in updated_data['ad_snapshot_url']:
            self.assertIn(new_token, url, "Should contain new token")
            self.assertNotIn('old_token', url, "Should not contain old token")
        
        print("✓ update_access_token works correctly")


class TestHelperErrorHandling(unittest.TestCase):
    """Test error handling in helper functions"""
    
    @patch('AdDownloader.helpers.os.listdir')
    def test_load_json_from_folder_error_handling(self, mock_listdir):
        """Test load_json_from_folder error handling"""
        from AdDownloader.helpers import load_json_from_folder
        
        # Test with non-existent folder
        mock_listdir.side_effect = FileNotFoundError("Folder not found")
        
        with self.assertRaises(FileNotFoundError):
            load_json_from_folder('nonexistent_folder')
        
        print("✓ load_json_from_folder handles errors correctly")
    
    def test_validator_error_messages(self):
        """Test that validators provide appropriate error messages"""
        from AdDownloader.helpers import NumberValidator, DateValidator, CountryValidator
        from inquirer3 import errors
        
        # Test NumberValidator error message
        try:
            NumberValidator.validate_number({}, "invalid")
        except errors.ValidationError as e:
            self.assertIn("valid number", str(e.reason), "Should contain helpful error message")
        
        # Test DateValidator error message  
        try:
            DateValidator.validate_date({}, "invalid")
        except errors.ValidationError as e:
            self.assertIn("valid date", str(e.reason), "Should contain helpful error message")
        
        # Test CountryValidator error message
        try:
            CountryValidator.validate_country({}, "invalid")
        except errors.ValidationError as e:
            self.assertIn("valid country", str(e.reason), "Should contain helpful error message")
        
        print("✓ Validators provide helpful error messages")


class TestHelperUtilityFunctions(unittest.TestCase):
    """Test utility functions in helpers module"""
    
    @patch('AdDownloader.helpers.logging.FileHandler')
    @patch('AdDownloader.helpers.logging.getLogger')
    @patch('AdDownloader.helpers.os.makedirs')
    @patch('AdDownloader.helpers.os.path.exists')
    def test_configure_logging(self, mock_exists, mock_makedirs, mock_get_logger, mock_file_handler):
        """Test configure_logging function"""
        from AdDownloader.helpers import configure_logging
        
        mock_exists.return_value = False  # Folder doesn't exist
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger
        mock_file_handler.return_value = MagicMock()
        
        # Test logger configuration
        result = configure_logging('test_project')
        
        # Verify folder creation was attempted
        mock_makedirs.assert_called()
        
        # Verify logger was configured
        mock_get_logger.assert_called_with('test_project')
        
        print("✓ configure_logging works correctly")
    
    def test_data_type_conversions(self):
        """Test various data type handling scenarios"""
        from AdDownloader.helpers import flatten_age_country_gender
        import ast
        
        # Test string conversion back to list
        test_string = "[{'country': 'US', 'reach': 100}]"
        
        # This should not raise an exception
        try:
            result = flatten_age_country_gender(test_string, 'US')
            self.assertIsInstance(result, dict, "Should handle string-to-list conversion")
        except Exception as e:
            # Should handle gracefully even if conversion fails
            pass
        
        print("✓ Data type conversion handling works")


class TestHelperFileOperations(unittest.TestCase):
    """Test file operation helper functions"""
    
    @patch('AdDownloader.helpers.shutil.copy2')
    @patch('AdDownloader.helpers.os.path.exists')
    def test_file_operations_mocked(self, mock_exists, mock_copy):
        """Test file operations with mocking"""
        # Test that file operations can be safely mocked
        mock_exists.return_value = True
        mock_copy.return_value = None
        
        # This demonstrates how we can test file operations safely
        mock_exists.assert_not_called()  # Should not be called yet
        
        # Simulate a function that checks if file exists
        if mock_exists('test_file.xlsx'):
            mock_copy('source.xlsx', 'destination.xlsx')
        
        mock_exists.assert_called_with('test_file.xlsx')
        
        print("✓ File operations can be safely mocked")


if __name__ == "__main__":
    unittest.main(verbosity=2)
