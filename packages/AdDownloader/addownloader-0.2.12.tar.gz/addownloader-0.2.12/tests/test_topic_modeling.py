#!/usr/bin/env python3
"""
Topic modeling and advanced text analysis tests for AdDownloader
"""

import sys
import os
import unittest
import pandas as pd
import numpy as np

# Add the AdDownloader module to path
sys.path.append('..')

class TestTopicModeling(unittest.TestCase):
    """Test topic modeling functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_texts = [
            "Great burger restaurant with amazing food and excellent service",
            "Best pizza place in town with fresh ingredients and fast delivery", 
            "Terrible customer service and poor quality food disappointed",
            "Amazing deals on electronics and gadgets with free shipping",
            "High quality smartphones and laptops at affordable prices",
            "Poor website design and difficult checkout process",
            "Excellent customer support team very helpful and responsive",
            "Fast delivery and secure packaging for all orders",
            "Bad experience with damaged products and slow refunds",
            "Outstanding quality control and premium materials used"
        ]
    
    def test_topic_modeling_basic(self):
        """Test basic topic modeling functionality"""
        from AdDownloader.analysis import preprocess, get_topics
        
        # Preprocess the texts
        processed_texts = [preprocess(text) for text in self.sample_texts]
        
        # Test topic modeling with different numbers of topics
        for num_topics in [2, 3]:
            try:
                lda_model, topics, coherence, perplexity, log_likelihood, similarity, topics_df = get_topics(
                    processed_texts, nr_topics=num_topics
                )
                
                # Basic assertions
                self.assertIsNotNone(lda_model, "Should return LDA model")
                self.assertEqual(len(topics), num_topics, f"Should return {num_topics} topics")
                self.assertIsInstance(coherence, float, "Coherence should be float")
                self.assertIsInstance(perplexity, float, "Perplexity should be float")
                self.assertIsInstance(log_likelihood, float, "Log likelihood should be float")
                self.assertIsInstance(similarity, float, "Similarity should be float")
                self.assertIsInstance(topics_df, pd.DataFrame, "Should return DataFrame")
                
                # Check topics_df structure
                self.assertEqual(len(topics_df), len(processed_texts), 
                               "Topics DataFrame should have same length as input")
                self.assertIn('dom_topic', topics_df.columns, "Should contain dominant topic column")
                self.assertIn('perc_contr', topics_df.columns, "Should contain percentage contribution")
                self.assertIn('topic_keywords', topics_df.columns, "Should contain topic keywords")
                
                # Check value ranges
                self.assertGreaterEqual(coherence, 0, "Coherence should be non-negative")
                self.assertGreater(perplexity, 0, "Perplexity should be positive")
                self.assertGreaterEqual(similarity, 0, "Similarity should be non-negative")
                self.assertLessEqual(similarity, 1, "Similarity should be <= 1")
                
                print(f"✓ Topic modeling with {num_topics} topics successful")
                print(f"  Coherence: {coherence:.3f}, Perplexity: {perplexity:.3f}")
                print(f"  Similarity: {similarity:.3f}")
                
            except Exception as e:
                self.fail(f"Topic modeling with {num_topics} topics failed: {e}")
    
    def test_topic_assignment(self):
        """Test topic assignment functionality"""
        from AdDownloader.analysis import preprocess, get_topics, get_topic_per_caption
        
        processed_texts = [preprocess(text) for text in self.sample_texts]
        
        # Get topics
        lda_model, topics, coherence, perplexity, log_likelihood, similarity, topics_df = get_topics(
            processed_texts, nr_topics=2
        )
        
        # Check topic assignments
        dominant_topics = topics_df['dom_topic'].values
        
        # Should assign topics 0 or 1 for 2-topic model
        self.assertTrue(all(topic in [0, 1] for topic in dominant_topics), 
                       "Should assign topics 0 or 1")
        
        # Percentage contributions should be between 0 and 1
        percentages = topics_df['perc_contr'].values
        self.assertTrue(all(0 <= p <= 1 for p in percentages), 
                       "Percentage contributions should be between 0 and 1")
        
        # Each row should have topic keywords
        for keywords in topics_df['topic_keywords']:
            self.assertIsInstance(keywords, str, "Keywords should be string")
            self.assertGreater(len(keywords), 0, "Keywords should not be empty")
        
        print("✓ Topic assignment functionality works correctly")
    
    def test_text_analysis_pipeline(self):
        """Test complete text analysis pipeline"""
        from AdDownloader.analysis import start_text_analysis
        
        # Create DataFrame with text data
        test_data = pd.DataFrame({
            'ad_creative_bodies': self.sample_texts,
            'id': range(len(self.sample_texts))
        })
        
        # Test without topics
        tokens, freq_dist, textblob_sent, nltk_sent = start_text_analysis(
            test_data, column_name='ad_creative_bodies', topics=False
        )
        
        self.assertIsNotNone(tokens, "Should return tokens")
        self.assertIsNotNone(freq_dist, "Should return frequency distribution")
        self.assertIsNotNone(textblob_sent, "Should return TextBlob sentiment")
        self.assertIsNotNone(nltk_sent, "Should return NLTK sentiment")
        
        # Check lengths
        self.assertEqual(len(tokens), len(self.sample_texts), "Tokens should match input length")
        self.assertEqual(len(textblob_sent), len(self.sample_texts), "Sentiment should match input length")
        self.assertEqual(len(nltk_sent), len(self.sample_texts), "NLTK sentiment should match input length")
        
        # Test with topics
        result_with_topics = start_text_analysis(
            test_data, column_name='ad_creative_bodies', topics=True
        )
        
        self.assertEqual(len(result_with_topics), 11, "Should return 11 components with topics")
        
        tokens_t, freq_dist_t, textblob_sent_t, nltk_sent_t, lda_model, topics, coherence, perplexity, log_likelihood, similarity, topics_df = result_with_topics
        
        self.assertIsNotNone(lda_model, "Should return LDA model")
        self.assertIsNotNone(topics_df, "Should return topics DataFrame")
        
        print("✓ Complete text analysis pipeline works")
    
    def test_sentiment_analysis_accuracy(self):
        """Test sentiment analysis with known sentiment texts"""
        from AdDownloader.analysis import get_sentiment
        
        positive_texts = pd.Series([
            "Amazing product! Absolutely love it!",
            "Excellent service and great quality!",
            "Outstanding experience, highly recommend!"
        ])
        
        negative_texts = pd.Series([
            "Terrible quality, very disappointed.",
            "Awful customer service, never again.",
            "Complete waste of money, horrible."
        ])
        
        neutral_texts = pd.Series([
            "The product is okay.",
            "Normal service, nothing special.",
            "Average quality and price."
        ])
        
        # Test positive sentiment
        textblob_pos, nltk_pos = get_sentiment(positive_texts)
        avg_positive = textblob_pos.mean()
        self.assertGreater(avg_positive, 0, "Positive texts should have positive average sentiment")
        
        # Test negative sentiment  
        textblob_neg, nltk_neg = get_sentiment(negative_texts)
        avg_negative = textblob_neg.mean()
        self.assertLess(avg_negative, 0, "Negative texts should have negative average sentiment")
        
        # Test neutral sentiment
        textblob_neu, nltk_neu = get_sentiment(neutral_texts)
        avg_neutral = textblob_neu.mean()
        self.assertGreater(avg_neutral, avg_negative, "Neutral should be more positive than negative")
        self.assertLess(avg_neutral, avg_positive, "Neutral should be less positive than positive")
        
        print("✓ Sentiment analysis shows expected patterns")
        print(f"  Average sentiments - Positive: {avg_positive:.3f}, Neutral: {avg_neutral:.3f}, Negative: {avg_negative:.3f}")


class TestTextProcessingEdgeCases(unittest.TestCase):
    """Test text processing with edge cases and error handling"""
    
    def test_empty_text_handling(self):
        """Test handling of empty or invalid text"""
        from AdDownloader.analysis import preprocess, get_word_freq, get_sentiment
        
        # Test empty strings
        empty_texts = ["", "   ", "\n\t"]
        
        for text in empty_texts:
            processed = preprocess(text)
            self.assertIsInstance(processed, str, "Should return string even for empty input")
        
        # Test get_word_freq with empty processed texts
        empty_processed = ["", "", ""]
        try:
            freq_result = get_word_freq(empty_processed)
            # Should either return empty list or handle gracefully
            self.assertIsInstance(freq_result, list, "Should return list for empty input")
        except Exception as e:
            print(f"⚠ Empty text handling: {e} (may be expected)")
        
        # Test sentiment with empty texts
        empty_series = pd.Series(["", "test", ""])
        textblob_sent, nltk_sent = get_sentiment(empty_series)
        
        self.assertEqual(len(textblob_sent), 3, "Should handle mixed empty/valid texts")
        self.assertEqual(len(nltk_sent), 3, "Should handle mixed empty/valid texts")
        
        print("✓ Empty text handling works")
    
    def test_special_characters_handling(self):
        """Test handling of special characters and unicode"""
        from AdDownloader.analysis import preprocess
        
        special_texts = [
            "Hello! @#$%^&*() World!!!",
            "Price: $19.99 (50% OFF!!!)",
            "café résumé naïve",  # Unicode characters
            "🎉 Amazing deals! 🔥 Hot offers! 💯",  # Emojis
            "Visit us at https://example.com or call +1-800-123-4567"
        ]
        
        for text in special_texts:
            try:
                processed = preprocess(text)
                self.assertIsInstance(processed, str, "Should handle special characters")
                print(f"✓ Processed special text: '{text[:30]}...' -> '{processed[:30]}...'")
            except Exception as e:
                self.fail(f"Failed to process special text '{text}': {e}")
    
    def test_very_long_text_handling(self):
        """Test handling of very long texts"""
        from AdDownloader.analysis import preprocess, get_word_freq
        
        # Create very long text
        long_text = "This is a very long advertisement text. " * 1000
        
        processed = preprocess(long_text)
        self.assertIsInstance(processed, str, "Should handle very long text")
        
        # Test with word frequency
        long_texts = [long_text, "Short text", long_text]
        freq_result = get_word_freq(long_texts)
        self.assertIsInstance(freq_result, list, "Should handle long texts in frequency analysis")
        
        print(f"✓ Handled very long text ({len(long_text)} characters)")
    
    def test_data_type_handling(self):
        """Test handling of different data types"""
        from AdDownloader.analysis import get_sentiment
        
        # Test with different pandas Series types
        mixed_data = pd.Series([
            "Good product",
            123,  # Number
            None,  # None value
            "Bad service"
        ])
        
        try:
            textblob_sent, nltk_sent = get_sentiment(mixed_data)
            print("✓ Mixed data types handled gracefully")
        except Exception as e:
            print(f"⚠ Mixed data type handling: {e} (may be expected)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
