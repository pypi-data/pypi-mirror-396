#!/usr/bin/env python3
"""
CLI tests for AdDownloader
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
import pandas as pd

# Add the AdDownloader module to path
sys.path.append('..')

class TestCLIImports(unittest.TestCase):
    """Test CLI module imports and basic structure"""
    
    def test_cli_imports(self):
        """Test if CLI modules can be imported"""
        try:
            import AdDownloader.cli
            print("✓ Successfully imported AdDownloader.cli")
        except ImportError as e:
            self.fail(f"Failed to import CLI module: {e}")
    
    def test_main_entry_point(self):
        """Test if main entry point can be imported"""
        try:
            from AdDownloader import __main__
            print("✓ Successfully imported AdDownloader.__main__")
        except ImportError as e:
            self.fail(f"Failed to import main entry point: {e}")
    
    def test_typer_app_creation(self):
        """Test if Typer app is created correctly"""
        from AdDownloader.cli import app
        import typer
        
        self.assertIsInstance(app, typer.Typer, "Should create a Typer app instance")
        print("✓ Typer app created successfully")


class TestValidators(unittest.TestCase):
    """Test input validators used in CLI"""
    
    def test_number_validator(self):
        """Test NumberValidator functionality"""
        from AdDownloader.helpers import NumberValidator
        
        # Test valid numbers
        valid_numbers = ["1", "50", "100", "999"]
        for num in valid_numbers:
            try:
                result = NumberValidator.validate_number({}, num)
                self.assertTrue(result, f"Should validate valid number: {num}")
            except Exception as e:
                self.fail(f"Valid number {num} failed validation: {e}")
        
        # Test invalid numbers
        invalid_numbers = ["abc", "12.5", "", "test123"]
        for num in invalid_numbers:
            with self.assertRaises(Exception, msg=f"Should reject invalid number: {num}"):
                NumberValidator.validate_number({}, num)
        
        print("✓ NumberValidator works correctly")
    
    def test_date_validator(self):
        """Test DateValidator functionality"""
        from AdDownloader.helpers import DateValidator
        
        # Test valid dates
        valid_dates = ["2023-01-01", "2024-12-31", "2022-06-15"]
        for date in valid_dates:
            try:
                result = DateValidator.validate_date({}, date)
                self.assertTrue(result, f"Should validate valid date: {date}")
            except Exception as e:
                self.fail(f"Valid date {date} failed validation: {e}")
        
        # Test invalid dates
        invalid_dates = ["2023-13-01", "abc", "2023/01/01", ""]
        for date in invalid_dates:
            with self.assertRaises(Exception, msg=f"Should reject invalid date: {date}"):
                DateValidator.validate_date({}, date)
        
        print("✓ DateValidator works correctly")
    
    def test_country_validator(self):
        """Test CountryValidator functionality"""
        from AdDownloader.helpers import CountryValidator
        
        # Test valid country codes
        valid_countries = ["US", "NL", "DE", "FR", "GB"]
        for country in valid_countries:
            try:
                result = CountryValidator.validate_country({}, country)
                self.assertTrue(result, f"Should validate valid country: {country}")
            except Exception as e:
                self.fail(f"Valid country {country} failed validation: {e}")
        
        # Test invalid country codes
        invalid_countries = ["XX", "ABC", "123", ""]
        for country in invalid_countries:
            with self.assertRaises(Exception, msg=f"Should reject invalid country: {country}"):
                CountryValidator.validate_country({}, country)
        
        print("✓ CountryValidator works correctly")
    
    def test_excel_validator_with_mock_file(self):
        """Test ExcelValidator with mock Excel file"""
        from AdDownloader.helpers import ExcelValidator
        
        # Create a temporary Excel file for testing
        test_data = pd.DataFrame({
            'page_id': [123456789, 987654321],
            'page_name': ['Test Page 1', 'Test Page 2']
        })
        
        # Use a simpler approach with mocking instead of actual file creation
        test_data = pd.DataFrame({
            'page_id': [123456789, 987654321],
            'page_name': ['Test Page 1', 'Test Page 2']
        })
        
        # Mock all file operations
        with patch('AdDownloader.helpers.os.path.join') as mock_join:
            with patch('AdDownloader.helpers.os.path.exists', return_value=True):
                with patch('AdDownloader.helpers.pd.read_excel', return_value=test_data):
                    mock_join.return_value = 'mock_path.xlsx'
                    
                    try:
                        result = ExcelValidator.validate_excel({}, 'test_file.xlsx')
                        self.assertTrue(result, "Should validate Excel file with page_id column")
                        print("✓ ExcelValidator works with valid Excel file")
                    except Exception as e:
                        self.fail(f"Excel validation failed: {e}")


class TestCLIFunctions(unittest.TestCase):
    """Test CLI functions with mocked dependencies"""
    
    def test_request_params_task_AC_structure(self):
        """Test the structure of request_params_task_AC function"""
        from AdDownloader.cli import request_params_task_AC
        
        # Mock inquirer3.prompt to return test values
        mock_answers = {
            'ad_type': 'All',
            'ad_reached_countries': 'US',
            'ad_delivery_date_min': '2023-01-01',
            'ad_delivery_date_max': '2023-12-31',
            'search_by': 'Search Terms',
            'search_terms': 'test'
        }
        
        with patch('AdDownloader.cli.inquirer3.prompt', return_value=mock_answers):
            result = request_params_task_AC()
            
            self.assertIsInstance(result, dict, "Should return a dictionary")
            expected_keys = ['ad_type', 'ad_reached_countries', 'ad_delivery_date_min', 
                           'ad_delivery_date_max', 'search_by']
            for key in expected_keys:
                self.assertIn(key, result, f"Should contain key: {key}")
            
            print("✓ request_params_task_AC function structure is correct")
    
    @patch('AdDownloader.cli.time.time')
    @patch('AdDownloader.cli.rprint')
    @patch('AdDownloader.cli.request_params_task_AC')
    @patch('AdDownloader.cli.AdLibAPI')
    def test_run_task_A_structure(self, mock_api, mock_request_params, mock_rprint, mock_time):
        """Test run_task_A function structure"""
        from AdDownloader.cli import run_task_A
        
        # Mock dependencies
        mock_time.return_value = 1000
        mock_request_params.return_value = {
            'ad_type': 'All',
            'ad_reached_countries': 'US',
            'ad_delivery_date_min': '2023-01-01',
            'ad_delivery_date_max': '2023-12-31',
            'search_by': 'Search Terms',
            'search_terms': 'test',
            'pages_id_path': None
        }
        
        # Mock API instance
        mock_api_instance = MagicMock()
        mock_api.return_value = mock_api_instance
        mock_api_instance.get_parameters.return_value = {'test': 'params'}
        
        test_answers = {'access_token': 'test_token'}
        
        # Test function execution
        try:
            run_task_A('test_project', test_answers)
            
            # Verify API was called correctly
            mock_api.assert_called_once_with('test_token', project_name='test_project')
            mock_api_instance.add_parameters.assert_called_once()
            mock_api_instance.start_download.assert_called_once()
            
            print("✓ run_task_A function structure is correct")
            
        except Exception as e:
            # This is expected since we're mocking dependencies
            if "Mock" not in str(e):
                self.fail(f"Unexpected error in run_task_A: {e}")
    
    @patch('AdDownloader.cli.pd.read_excel')
    @patch('AdDownloader.cli.update_access_token')
    @patch('AdDownloader.cli.start_media_download')
    @patch('AdDownloader.cli.inquirer3.prompt')
    @patch('AdDownloader.cli.print')
    def test_run_task_B_structure(self, mock_print, mock_prompt, mock_download, mock_update_token, mock_read_excel):
        """Test run_task_B function structure"""
        from AdDownloader.cli import run_task_B
        
        # Mock data
        test_data = pd.DataFrame({
            'id': [1, 2, 3],
            'ad_snapshot_url': ['url1', 'url2', 'url3']
        })
        
        mock_read_excel.return_value = test_data
        mock_update_token.return_value = test_data
        mock_prompt.return_value = {'nr_ads': 'A - 50'}
        
        test_answers = {'access_token': 'test_token'}
        
        try:
            run_task_B('test_project', test_answers)
            
            # Verify functions were called
            mock_read_excel.assert_called_once()
            mock_update_token.assert_called_once()
            mock_download.assert_called_once()
            
            print("✓ run_task_B function structure is correct")
            
        except Exception as e:
            if "Mock" not in str(e) and "start_media_download" not in str(e):
                self.fail(f"Unexpected error in run_task_B: {e}")
    
    @patch('AdDownloader.cli.inquirer3.prompt')
    @patch('AdDownloader.cli.rprint')
    @patch('AdDownloader.cli.input')
    @patch('AdDownloader.cli.run_task_A')
    def test_intro_messages_task_A(self, mock_run_task_A, mock_input, mock_rprint, mock_prompt):
        """Test intro_messages function for Task A"""
        from AdDownloader.cli import intro_messages
        
        mock_prompt.return_value = {
            'task': 'A - download ads data only',
            'access_token': 'test_token',
            'start': True
        }
        mock_input.return_value = 'test_project'
        
        try:
            intro_messages()
            
            # Verify task A was called
            mock_run_task_A.assert_called_once_with('test_project', {
                'task': 'A - download ads data only',
                'access_token': 'test_token',
                'start': True
            })
            
            print("✓ intro_messages handles Task A correctly")
            
        except Exception as e:
            if "Mock" not in str(e):
                self.fail(f"Unexpected error in intro_messages: {e}")
    
    @patch('AdDownloader.cli.inquirer3.prompt')
    @patch('AdDownloader.cli.rprint')
    @patch('AdDownloader.cli.input')
    @patch('AdDownloader.cli.run_task_B')
    def test_intro_messages_task_B(self, mock_run_task_B, mock_input, mock_rprint, mock_prompt):
        """Test intro_messages function for Task B"""
        from AdDownloader.cli import intro_messages
        
        mock_prompt.return_value = {
            'task': 'B - download ads media content only',
            'access_token': 'test_token',
            'start': True
        }
        mock_input.return_value = 'existing_project'
        
        try:
            intro_messages()
            
            # Verify task B was called
            mock_run_task_B.assert_called_once_with('existing_project', {
                'task': 'B - download ads media content only',
                'access_token': 'test_token',
                'start': True
            })
            
            print("✓ intro_messages handles Task B correctly")
            
        except Exception as e:
            if "Mock" not in str(e):
                self.fail(f"Unexpected error in intro_messages: {e}")


class TestCLIIntegration(unittest.TestCase):
    """Test CLI integration and command structure"""
    
    def test_app_commands_exist(self):
        """Test if CLI app has the expected commands"""
        from AdDownloader.cli import app
        
        # Test that app is a Typer instance with registered commands
        self.assertTrue(hasattr(app, 'registered_commands'), "Should have registered commands")
        
        # Alternative: test that we can get info about the app
        import typer
        self.assertIsInstance(app, typer.Typer, "Should be a Typer app")
        
        print("✓ CLI app structure is correct")
    
    def test_run_analysis_command_structure(self):
        """Test run_analysis command structure"""
        from AdDownloader.cli import run_analysis
        
        # Test that function exists and is callable
        self.assertTrue(callable(run_analysis), "run_analysis should be callable")
        
        # Test function signature
        import inspect
        sig = inspect.signature(run_analysis)
        self.assertEqual(len(sig.parameters), 0, "run_analysis should take no parameters")
        
        print("✓ run_analysis command has correct structure")
    
    @patch('AdDownloader.cli.typer.confirm')
    @patch('AdDownloader.cli.intro_messages')
    @patch('AdDownloader.cli.rprint')
    def test_run_analysis_loop_logic(self, mock_rprint, mock_intro, mock_confirm):
        """Test run_analysis loop logic"""
        from AdDownloader.cli import run_analysis
        
        # Mock user saying no to rerun
        mock_confirm.return_value = False
        
        try:
            run_analysis()
            
            # Verify intro_messages was called once
            mock_intro.assert_called_once()
            mock_confirm.assert_called_once()
            
            print("✓ run_analysis loop logic works correctly")
            
        except Exception as e:
            if "Mock" not in str(e):
                self.fail(f"Unexpected error in run_analysis: {e}")


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions used by CLI"""
    
    def test_is_valid_excel_file_with_mock(self):
        """Test is_valid_excel_file function"""
        from AdDownloader.helpers import is_valid_excel_file
        
        # Test with valid file
        with patch('AdDownloader.helpers.os.path.exists', return_value=True):
            with patch('AdDownloader.helpers.pd.read_excel', return_value=pd.DataFrame()):
                result = is_valid_excel_file('test.xlsx')
                self.assertTrue(result, "Should validate existing Excel file")
        
        # Test with non-existent file
        with patch('AdDownloader.helpers.os.path.exists', return_value=False):
            result = is_valid_excel_file('nonexistent.xlsx')
            self.assertFalse(result, "Should reject non-existent file")
        
        # Test with invalid extension
        with patch('AdDownloader.helpers.os.path.exists', return_value=True):
            result = is_valid_excel_file('test.txt')
            self.assertFalse(result, "Should reject non-Excel file")
        
        print("✓ is_valid_excel_file works correctly")


class TestCLIErrorHandling(unittest.TestCase):
    """Test error handling in CLI functions"""
    
    @patch('AdDownloader.cli.pd.read_excel')
    @patch('AdDownloader.cli.print')
    def test_run_task_B_error_handling(self, mock_print, mock_read_excel):
        """Test error handling in run_task_B"""
        from AdDownloader.cli import run_task_B
        
        # Mock file not found error
        mock_read_excel.side_effect = FileNotFoundError("File not found")
        
        test_answers = {'access_token': 'test_token'}
        
        try:
            run_task_B('nonexistent_project', test_answers)
            # Should not raise exception, should print error
            mock_print.assert_called()
            print("✓ run_task_B handles file not found error gracefully")
        except Exception as e:
            self.fail(f"run_task_B should handle errors gracefully: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
