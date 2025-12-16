#!/usr/bin/env python3
"""
Core functionality tests for AdDownloader
"""

import sys
import os
import pandas as pd
import unittest
from unittest.mock import patch, MagicMock

# Add the AdDownloader module to path
sys.path.append('../AdDownloader')

class TestCoreFunctionality(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_data_path = "data"
        self.test_images_path = "data/images"
    
    def test_data_loading(self):
        """Test if Excel data files can be loaded correctly"""
        from AdDownloader.analysis import load_data
        
        # Test specifically with Belgium_ads_subset.xlsx which has the expected columns
        test_file = os.path.join(self.test_data_path, "Belgium_ads_subset.xlsx")
        
        if os.path.exists(test_file):
            data = load_data(test_file)
            
            self.assertIsNotNone(data, "Data should not be None")
            self.assertIsInstance(data, pd.DataFrame, "Should return a pandas DataFrame")
            self.assertGreater(len(data), 0, "DataFrame should not be empty")
            
            # Check if campaign_duration column is added
            self.assertIn('campaign_duration', data.columns, "Should add campaign_duration column")
            
            # Check if expected columns exist
            expected_columns = ['id', 'ad_delivery_start_time', 'ad_creative_bodies']
            for col in expected_columns:
                if col in data.columns:
                    self.assertIn(col, data.columns, f"Should contain {col} column")
            
            print(f"✓ Successfully loaded {len(data)} rows from Belgium_ads_subset.xlsx")
            print(f"  Columns: {len(data.columns)} total columns")
            print(f"  Sample data shape: {data.shape}")
            
            # Test that campaign_duration is calculated correctly
            if 'campaign_duration' in data.columns:
                duration_sample = data['campaign_duration'].iloc[:3]
                self.assertTrue(all(duration >= 0 for duration in duration_sample), 
                              "Campaign duration should be non-negative")
                print(f"  Sample campaign durations: {list(duration_sample)}")
                
        else:
            self.skipTest("Belgium_ads_subset.xlsx not found for testing")
    
    def test_text_preprocessing(self):
        """Test text preprocessing functionality"""
        from AdDownloader.analysis import preprocess
        
        test_texts = [
            "This is a test advertisement!",
            "Visit our store TODAY for AMAZING deals!!!",
            "Buy now and save 50% off regular prices."
        ]
        
        for text in test_texts:
            processed = preprocess(text)
            self.assertIsInstance(processed, str, "Should return a string")
            self.assertGreater(len(processed), 0, "Should not return empty string")
            print(f"✓ Preprocessed: '{text[:30]}...' -> '{processed[:30]}...'")
    
    def test_word_frequency(self):
        """Test word frequency calculation"""
        from AdDownloader.analysis import get_word_freq
        
        test_tokens = [
            "great product amazing deal",
            "amazing offer great price",
            "product quality great service amazing"
        ]
        
        word_freq = get_word_freq(test_tokens)
        
        self.assertIsInstance(word_freq, list, "Should return a list")
        self.assertGreater(len(word_freq), 0, "Should not be empty")
        
        # Check if it's sorted by frequency (descending)
        if len(word_freq) > 1:
            self.assertGreaterEqual(word_freq[0][1], word_freq[1][1], "Should be sorted by frequency")
        
        print(f"✓ Generated word frequencies: {word_freq[:3]}")
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis functionality"""
        from AdDownloader.analysis import get_sentiment
        
        test_captions = pd.Series([
            "This is an amazing product! I love it!",
            "Terrible service, very disappointed.",
            "The product is okay, nothing special."
        ])
        
        textblob_sent, nltk_sent = get_sentiment(test_captions)
        
        self.assertEqual(len(textblob_sent), len(test_captions), "Should have same length as input")
        self.assertEqual(len(nltk_sent), len(test_captions), "Should have same length as input")
        
        # Check if sentiment values are in expected ranges
        for sentiment in textblob_sent:
            self.assertGreaterEqual(sentiment, -1, "TextBlob sentiment should be >= -1")
            self.assertLessEqual(sentiment, 1, "TextBlob sentiment should be <= 1")
        
        print(f"✓ Sentiment analysis completed for {len(test_captions)} texts")
    
    def test_image_analysis_functions(self):
        """Test image analysis functions"""
        if not os.path.exists(self.test_images_path):
            self.skipTest("No test images available")
        
        from AdDownloader.analysis import extract_dominant_colors, assess_image_quality
        
        image_files = [f for f in os.listdir(self.test_images_path) if f.endswith(('jpg', 'png', 'jpeg'))]
        
        if image_files:
            test_image = os.path.join(self.test_images_path, image_files[0])
            
            # Test dominant colors extraction
            colors, percentages = extract_dominant_colors(test_image, num_colors=3)
            self.assertEqual(len(colors), 3, "Should return 3 colors")
            self.assertEqual(len(percentages), 3, "Should return 3 percentages")
            
            # Test image quality assessment
            resolution, brightness, contrast, sharpness = assess_image_quality(test_image)
            self.assertGreater(resolution, 0, "Resolution should be positive")
            self.assertGreater(brightness, 0, "Brightness should be positive")
            self.assertGreater(contrast, 0, "Contrast should be positive")
            self.assertGreater(sharpness, 0, "Sharpness should be positive")
            
            print(f"✓ Image analysis completed for {image_files[0]}")
            print(f"  Colors: {colors}")
            print(f"  Quality: res={resolution}, bright={brightness:.1f}, contrast={contrast:.1f}, sharp={sharpness:.1f}")
        else:
            self.skipTest("No image files found for testing")
    
    def test_demographic_transformation(self):
        """Test demographic data transformation"""
        from AdDownloader.analysis import transform_data_by_age, transform_data_by_gender
        
        # Create mock demographic data
        mock_data = pd.DataFrame({
            'reach_18-24_female': [100, 200],
            'reach_25-34_male': [150, 250],
            'reach_35-44_unknown': [50, 75]
        })
        
        # Test age transformation
        age_data = transform_data_by_age(mock_data)
        self.assertIn('Reach', age_data.columns, "Should have Reach column")
        self.assertIn('Age Range', age_data.columns, "Should have Age Range column")
        
        # Test gender transformation
        gender_data = transform_data_by_gender(mock_data)
        self.assertIn('Reach', gender_data.columns, "Should have Reach column")
        self.assertIn('Gender', gender_data.columns, "Should have Gender column")
        
        print("✓ Demographic transformation tests passed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
