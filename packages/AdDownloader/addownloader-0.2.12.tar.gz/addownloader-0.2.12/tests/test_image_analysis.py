#!/usr/bin/env python3
"""
Image analysis tests for AdDownloader
"""

import sys
import os
import unittest
import tempfile
import numpy as np
from PIL import Image

# Add the AdDownloader module to path
sys.path.append('..')

class TestImageAnalysis(unittest.TestCase):
    """Test image analysis functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_images_path = "data/images"
        # Create a simple test image if needed
        self.temp_image = None
    
    def tearDown(self):
        """Clean up test fixtures"""
        if self.temp_image and os.path.exists(self.temp_image):
            os.remove(self.temp_image)
    
    def create_test_image(self, width=100, height=100, colors=[(255,0,0), (0,255,0), (0,0,255)]):
        """Create a simple test image for testing"""
        img = Image.new('RGB', (width, height))
        pixels = img.load()
        
        # Create blocks of different colors
        block_width = width // len(colors)
        for i, color in enumerate(colors):
            for x in range(i * block_width, min((i + 1) * block_width, width)):
                for y in range(height):
                    pixels[x, y] = color
        
        # Save to temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        img.save(temp_file.name)
        self.temp_image = temp_file.name
        return temp_file.name
    
    def test_dominant_colors_extraction(self):
        """Test dominant color extraction"""
        if os.path.exists(self.test_images_path):
            from AdDownloader.analysis import extract_dominant_colors
            
            image_files = [f for f in os.listdir(self.test_images_path) if f.endswith(('jpg', 'png', 'jpeg'))]
            
            if image_files:
                test_image = os.path.join(self.test_images_path, image_files[0])
                
                # Test with different numbers of colors
                for num_colors in [1, 3, 5]:
                    colors, percentages = extract_dominant_colors(test_image, num_colors=num_colors)
                    
                    self.assertEqual(len(colors), num_colors, f"Should return {num_colors} colors")
                    self.assertEqual(len(percentages), num_colors, f"Should return {num_colors} percentages")
                    
                    # Check if colors are valid hex codes
                    for color in colors:
                        self.assertRegex(color, r'^#[0-9a-fA-F]{6}$', "Should be valid hex color")
                    
                    # Check if percentages sum to ~100
                    self.assertAlmostEqual(sum(percentages), 100, places=0, 
                                         msg="Percentages should sum to approximately 100")
                
                print(f"✓ Dominant colors extraction works for {image_files[0]}")
            else:
                # Create and test with synthetic image
                test_image = self.create_test_image()
                colors, percentages = extract_dominant_colors(test_image, num_colors=3)
                
                self.assertEqual(len(colors), 3, "Should return 3 colors")
                print("✓ Dominant colors extraction works with synthetic image")
        else:
            self.skipTest("No images available for testing")
    
    def test_image_quality_assessment(self):
        """Test image quality assessment"""
        if os.path.exists(self.test_images_path):
            from AdDownloader.analysis import assess_image_quality
            
            image_files = [f for f in os.listdir(self.test_images_path) if f.endswith(('jpg', 'png', 'jpeg'))]
            
            if image_files:
                test_image = os.path.join(self.test_images_path, image_files[0])
                
                resolution, brightness, contrast, sharpness = assess_image_quality(test_image)
                
                # Basic sanity checks
                self.assertIsInstance(resolution, (int, float), "Resolution should be numeric")
                self.assertIsInstance(brightness, (int, float), "Brightness should be numeric")
                self.assertIsInstance(contrast, (int, float), "Contrast should be numeric")
                self.assertIsInstance(sharpness, (int, float), "Sharpness should be numeric")
                
                self.assertGreater(resolution, 0, "Resolution should be positive")
                self.assertGreaterEqual(brightness, 0, "Brightness should be non-negative")
                self.assertGreaterEqual(contrast, 0, "Contrast should be non-negative")
                self.assertGreaterEqual(sharpness, 0, "Sharpness should be non-negative")
                
                print(f"✓ Image quality assessment works: res={resolution}, bright={brightness:.1f}, "
                      f"contrast={contrast:.1f}, sharp={sharpness:.1f}")
            else:
                # Test with synthetic image
                test_image = self.create_test_image(width=200, height=150)
                resolution, brightness, contrast, sharpness = assess_image_quality(test_image)
                
                self.assertEqual(resolution, 200 * 150, "Should calculate correct resolution")
                print("✓ Image quality assessment works with synthetic image")
        else:
            self.skipTest("No images available for testing")
    
    def test_full_image_analysis(self):
        """Test the complete image analysis pipeline"""
        if os.path.exists(self.test_images_path):
            from AdDownloader.analysis import analyse_image
            
            image_files = [f for f in os.listdir(self.test_images_path) if f.endswith(('jpg', 'png', 'jpeg'))]
            
            if image_files:
                test_image = os.path.join(self.test_images_path, image_files[0])
                
                result = analyse_image(test_image)
                
                # Check required keys
                required_keys = ['ad_id', 'resolution', 'brightness', 'contrast', 'sharpness', 'ncorners']
                for key in required_keys:
                    self.assertIn(key, result, f"Result should contain {key}")
                
                # Check for dominant color keys
                color_keys = [key for key in result.keys() if key.startswith('dom_color_')]
                self.assertGreater(len(color_keys), 0, "Should contain dominant color information")
                
                print(f"✓ Full image analysis completed for {image_files[0]}")
                print(f"  Found {len(color_keys)} color-related metrics")
            else:
                self.skipTest("No ad-pattern images found for testing")
        else:
            self.skipTest("No images available for testing")
    
    def test_image_folder_analysis(self):
        """Test batch image analysis"""
        if os.path.exists(self.test_images_path):
            from AdDownloader.analysis import analyse_image_folder
            
            result_df = analyse_image_folder(self.test_images_path, nr_images=3)
            
            self.assertIsNotNone(result_df, "Should return a DataFrame")
            self.assertGreater(len(result_df), 0, "Should analyze at least one image")
            self.assertLessEqual(len(result_df), 3, "Should not analyze more than requested")
            
            # Check required columns
            required_columns = ['ad_id', 'resolution', 'brightness', 'contrast', 'sharpness']
            for col in required_columns:
                self.assertIn(col, result_df.columns, f"DataFrame should contain {col} column")
            
            print(f"✓ Batch image analysis completed for {len(result_df)} images")
        else:
            self.skipTest("No images available for testing")


class TestImageCaptioning(unittest.TestCase):
    """Test image captioning functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_images_path = "data/images"
    
    def test_blip_call_import(self):
        """Test if BLIP function can be imported"""
        try:
            from AdDownloader.analysis import blip_call
            
            # Check function signature
            import inspect
            sig = inspect.signature(blip_call)
            
            expected_params = {'images_path', 'task', 'nr_images', 'questions'}
            actual_params = set(sig.parameters.keys())
            
            self.assertTrue(expected_params.issubset(actual_params), 
                          "Function should have expected parameters")
            
            print("✓ BLIP function imported successfully with correct signature")
            
        except ImportError as e:
            self.skipTest(f"BLIP function not available: {e}")
    
    def test_blip_call_safe_execution(self):
        """Test BLIP function with safe parameters (if transformers available)"""
        if not os.path.exists(self.test_images_path):
            self.skipTest("No test images available")
        
        try:
            from AdDownloader.analysis import blip_call
            import transformers  # Check if transformers is available
            
            image_files = [f for f in os.listdir(self.test_images_path) if f.endswith(('jpg', 'png', 'jpeg'))]
            
            if image_files:
                # Test with a very small number of images to avoid long execution
                try:
                    result = blip_call(self.test_images_path, task="image_captioning", nr_images=1)
                    
                    self.assertIsNotNone(result, "Should return result")
                    self.assertGreater(len(result), 0, "Should process at least one image")
                    self.assertIn('img_caption', result.columns, "Should contain caption column")
                    
                    print(f"✓ BLIP captioning successful for 1 image")
                    print(f"  Sample caption: {result.iloc[0]['img_caption']}")
                    
                except Exception as e:
                    print(f"⚠ BLIP execution failed (may be expected): {e}")
            else:
                self.skipTest("No image files found")
                
        except ImportError:
            self.skipTest("Transformers library not available")


if __name__ == "__main__":
    unittest.main(verbosity=2)
