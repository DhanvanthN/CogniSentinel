import logging
import os
from typing import Dict, Text, Any, List, Optional

# Import Flair for sentiment analysis
try:
    import flair.nn
    from flair.data import Sentence
    FLAIR_AVAILABLE = True
except ImportError:
    FLAIR_AVAILABLE = False
    logging.warning("Flair is not installed. Emotion detection will use fallback method.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionDetector:
    """Class to detect emotions in text using Flair NLP with fallback mechanisms."""
    
    # Keywords for more specific emotion detection when Flair is not available
    # or to refine Flair's classification
    EMOTION_KEYWORDS = {
        'joy': ['happy', 'glad', 'joy', 'excited', 'pleased', 'delighted', 'content', 'cheerful', 'thrilled', 'wonderful'],
        'sadness': ['sad', 'unhappy', 'depressed', 'down', 'miserable', 'heartbroken', 'gloomy', 'disappointed', 'upset', 'grief'],
        'anger': ['angry', 'mad', 'furious', 'irritated', 'annoyed', 'frustrated', 'outraged', 'enraged', 'hostile', 'bitter'],
        'fear': ['afraid', 'scared', 'frightened', 'terrified', 'anxious', 'worried', 'nervous', 'panicked', 'stressed', 'uneasy'],
        'neutral': ['okay', 'fine', 'neutral', 'normal', 'average', 'so-so']
    }
    
    def __init__(self):
        """Initialize the emotion classifier model."""
        self.emotion_model = None
        if FLAIR_AVAILABLE:
            try:
                # Load the emotion classification model
                self.emotion_model = flair.nn.SequenceTagger.load('en-emotion')
                logger.info("Emotion detection model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading emotion model: {str(e)}")
                logger.warning("Using keyword-based fallback for emotion detection")
    
    def detect_emotion(self, text: Text) -> Dict[Text, Any]:
        """Detect emotions in the given text.
        
        Args:
            text: The text to analyze for emotions
            
        Returns:
            A dictionary containing the detected emotion and confidence score
        """
        if not text or text.strip() == "":
            return {"emotion": "neutral", "confidence": 0.0, "method": "default"}
        
        # First try with Flair if available
        if self.emotion_model is not None:
            try:
                # Create a Flair sentence object
                sentence = Sentence(text)
                
                # Predict emotions
                self.emotion_model.predict(sentence)
                
                # Get the predicted label
                if len(sentence.get_labels()) > 0:
                    emotion_label = sentence.get_labels()[0]
                    emotion = emotion_label.value
                    confidence = emotion_label.score
                    
                    return {
                        "emotion": emotion.lower(),
                        "confidence": confidence,
                        "method": "flair",
                        "all_emotions": [
                            {"emotion": label.value.lower(), "confidence": label.score}
                            for label in sentence.get_labels()
                        ]
                    }
            except Exception as e:
                logger.error(f"Error in Flair emotion detection: {e}")
                # Fall back to keyword method if Flair fails
        
        # Fallback to keyword-based detection
        emotion, confidence = self._detect_with_keywords(text)
        return {
            "emotion": emotion,
            "confidence": confidence,
            "method": "keywords"
        }
        
    def _detect_with_keywords(self, text: Text) -> tuple:
        """Detect emotion using keyword matching as a fallback method.
        
        Args:
            text: The text to analyze
            
        Returns:
            A tuple of (emotion, confidence)
        """
        text = text.lower()
        
        # Count matches for each emotion category
        emotion_scores = {emotion: 0 for emotion in self.EMOTION_KEYWORDS.keys()}
        
        # Check for keyword matches
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    emotion_scores[emotion] += 1
        
        # Find the emotion with the highest score
        max_score = 0
        detected_emotion = 'neutral'  # Default
        
        for emotion, score in emotion_scores.items():
            if score > max_score:
                max_score = score
                detected_emotion = emotion
        
        # Calculate a confidence score (normalized by the number of keywords found)
        total_matches = sum(emotion_scores.values())
        confidence = 0.5  # Default confidence
        
        if total_matches > 0:
            confidence = min(0.9, 0.5 + (max_score / total_matches) * 0.4)  # Scale between 0.5 and 0.9
        
        return detected_emotion, confidence
    
    def get_response_for_emotion(self, emotion: Text) -> Text:
        """Get an appropriate response based on the detected emotion.
        
        Args:
            emotion: The detected emotion
            
        Returns:
            A suitable response for the emotion
        """
        emotion_responses = {
            "joy": "I'm glad to hear you're feeling positive!",
            "happy": "It's wonderful that you're feeling happy!",
            "sadness": "I'm sorry to hear you're feeling down. Remember that it's okay to feel sad sometimes, and I'm here to support you.",
            "sad": "I understand you're feeling sad. Would you like to talk about what's bothering you?",
            "anger": "I can sense you're feeling frustrated. Taking deep breaths can sometimes help manage anger. Would you like to discuss what's bothering you?",
            "angry": "I notice you seem upset. It's okay to feel angry, but remember to be kind to yourself.",
            "fear": "It sounds like you might be feeling anxious or scared. That's a normal human emotion, and I'm here to help you through it.",
            "afraid": "I understand that feeling afraid can be overwhelming. Would it help to talk about what's causing this fear?",
            "disgust": "I sense you're feeling uncomfortable about something. Would you like to talk about what's bothering you?",
            "surprise": "That seems to have caught you off guard! Would you like to talk more about it?",
            "neutral": "I'm here to listen and support you. How can I help you today?"
        }
        
        return emotion_responses.get(emotion.lower(), "I'm here to listen and support you. How can I help you today?")

# Singleton instance for reuse
_emotion_detector = None

def get_emotion_detector() -> EmotionDetector:
    """Get or create a singleton instance of the EmotionDetector."""
    global _emotion_detector
    if _emotion_detector is None:
        _emotion_detector = EmotionDetector()
    return _emotion_detector

# Example usage
if __name__ == "__main__":
    detector = get_emotion_detector()
    
    # Test with different emotional texts
    test_texts = [
        "I'm feeling really happy today!",
        "I'm so sad and depressed right now.",
        "This makes me so angry and frustrated!",
        "I'm really anxious and worried about my exam.",
        "I'm doing okay, just a normal day."
    ]
    
    for text in test_texts:
        result = detector.detect_emotion(text)
        print(f"Text: '{text}'")
        print(f"Detected emotion: {result['emotion']} (confidence: {result['confidence']:.2f}, method: {result['method']})")
        print("---")