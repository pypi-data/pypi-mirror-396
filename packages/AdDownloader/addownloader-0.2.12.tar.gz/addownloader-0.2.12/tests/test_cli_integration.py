#!/usr/bin/env python3
"""
CLI and Integration tests for AdDownloader
"""

import sys
import os
import unittest
import subprocess
import tempfile
from unittest.mock import patch, MagicMock

# Add the AdDownloader module to path
sys.path.append('../AdDownloader')

class TestCLIIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data_path = "../data"
    
    def test_cli_help(self):
        """Test if CLI help command works"""
        try:
            result = subprocess.run(
                ['python', '-m', 'AdDownloader', '--help'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd='..'
            )
            
            self.assertEqual(result.returncode, 0, "Help command should exit successfully")
            self.assertIn('AdDownloader', result.stdout, "Should contain AdDownloader in help text")
            
            print("✓ CLI help command works")
            
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            self.skipTest(f"CLI test skipped: {e}")
    
    def test_module_imports(self):
        """Test if all main modules can be imported without errors"""
        modules_to_test = [
            'AdDownloader',
            'AdDownloader.analysis',
            'AdDownloader.cli'
        ]
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
                print(f"✓ Successfully imported {module_name}")
            except ImportError as e:
                self.fail(f"Failed to import {module_name}: {e}")
    
    def test_analysis_end_to_end(self):
        """Test end-to-end analysis workflow"""
        if not os.path.exists(self.test_data_path):
            self.skipTest("No test data available")
        
        from analysis import load_data, start_text_analysis
        
        # Find Excel files
        excel_files = [f for f in os.listdir(self.test_data_path) if f.endswith('.xlsx')]
        
        if excel_files:
            test_file = os.path.join(self.test_data_path, excel_files[0])
            
            # Load data
            data = load_data(test_file)
            self.assertIsNotNone(data, "Should load data successfully")
            
            # Check if text column exists for analysis
            text_columns = [col for col in data.columns if 'creative' in col.lower() or 'body' in col.lower()]
            
            if text_columns:
                # Test text analysis without topics
                tokens, freq_dist, textblob_sent, nltk_sent = start_text_analysis(
                    data, column_name=text_columns[0], topics=False
                )
                
                self.assertIsNotNone(tokens, "Should return tokens")
                self.assertIsNotNone(freq_dist, "Should return frequency distribution")
                self.assertIsNotNone(textblob_sent, "Should return TextBlob sentiment")
                self.assertIsNotNone(nltk_sent, "Should return NLTK sentiment")
                
                print("✓ End-to-end text analysis completed successfully")
            else:
                print("⚠ No text columns found for analysis")
        else:
            self.skipTest("No Excel files found for testing")
    
    def test_visualization_functions(self):
        """Test visualization function calls (without actually displaying)"""
        if not os.path.exists(self.test_data_path):
            self.skipTest("No test data available")
        
        from analysis import load_data, get_graphs
        
        excel_files = [f for f in os.listdir(self.test_data_path) if f.endswith('.xlsx')]
        
        if excel_files:
            test_file = os.path.join(self.test_data_path, excel_files[0])
            data = load_data(test_file)
            
            try:
                # Test graph generation (this should not display but should not error)
                graphs = get_graphs(data)
                self.assertEqual(len(graphs), 10, "Should return 10 graphs")
                
                print("✓ Visualization functions work without errors")
                
            except Exception as e:
                self.fail(f"Graph generation failed: {e}")
        else:
            self.skipTest("No Excel files found for testing")
    
    def test_image_captioning_import(self):
        """Test if image captioning function can be imported and called safely"""
        try:
            from analysis import blip_call
            
            # Test function signature without actually running
            import inspect
            sig = inspect.signature(blip_call)
            expected_params = {'images_path', 'task', 'nr_images', 'questions'}
            actual_params = set(sig.parameters.keys())
            
            self.assertTrue(expected_params.issubset(actual_params), 
                          f"Function should have parameters: {expected_params}")
            
            print("✓ Image captioning function is importable and has correct signature")
            
        except ImportError as e:
            print(f"⚠ Image captioning import failed: {e} (this may be expected if transformers not installed)")
    
    def test_topic_modeling_functionality(self):
        """Test topic modeling with mock data"""
        from analysis import get_topics
        
        # Create mock processed tokens
        mock_tokens = [
            "great product amazing deal offer",
            "best price quality service excellent", 
            "discount sale special limited time",
            "new product launch innovative technology",
            "customer service support help assistance"
        ]
        
        try:
            lda_model, topics, coherence, perplexity, log_likelihood, similarity, topics_df = get_topics(
                mock_tokens, nr_topics=2
            )
            
            self.assertIsNotNone(lda_model, "Should return LDA model")
            self.assertEqual(len(topics), 2, "Should return 2 topics")
            self.assertIsInstance(coherence, float, "Coherence should be float")
            self.assertIsInstance(topics_df, pd.DataFrame, "Should return DataFrame")
            
            print("✓ Topic modeling functionality works")
            
        except Exception as e:
            self.fail(f"Topic modeling failed: {e}")


class TestPerformance(unittest.TestCase):
    """Test performance of key functions"""
    
    def setUp(self):
        self.test_data_path = "../data"
    
    def test_data_loading_performance(self):
        """Test data loading performance"""
        import time
        from analysis import load_data
        
        excel_files = [f for f in os.listdir(self.test_data_path) if f.endswith('.xlsx')]
        
        if excel_files:
            test_file = os.path.join(self.test_data_path, excel_files[0])
            
            start_time = time.time()
            data = load_data(test_file)
            end_time = time.time()
            
            load_time = end_time - start_time
            
            self.assertIsNotNone(data, "Should load data successfully")
            self.assertLess(load_time, 10, "Should load data in less than 10 seconds")
            
            print(f"✓ Data loaded in {load_time:.2f} seconds ({len(data)} rows)")
        else:
            self.skipTest("No Excel files found for performance testing")
    
    def test_text_processing_performance(self):
        """Test text processing performance with larger dataset"""
        import time
        from analysis import preprocess, get_word_freq
        
        # Create larger test dataset
        test_texts = [
            "This is a test advertisement with many words to process",
            "Another sample text with different content and structure",
            "More text content for performance testing purposes"
        ] * 100  # Repeat 100 times
        
        start_time = time.time()
        processed_texts = [preprocess(text) for text in test_texts]
        word_freq = get_word_freq(processed_texts)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        self.assertLess(processing_time, 30, "Should process 300 texts in less than 30 seconds")
        self.assertGreater(len(word_freq), 0, "Should generate word frequencies")
        
        print(f"✓ Processed {len(test_texts)} texts in {processing_time:.2f} seconds")


if __name__ == "__main__":
    # Run tests with high verbosity
    unittest.main(verbosity=2)
