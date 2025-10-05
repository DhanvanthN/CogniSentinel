import requests
import json
import logging
import random
import datetime
from typing import Any, Text, Dict, List, Optional
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from .emotion_detector import get_emotion_detector

logger = logging.getLogger(__name__)

# Get the emotion detector instance
emotion_detector = get_emotion_detector()

# External API for mental health support
MENTAL_HEALTH_API_URL = "https://api.openai.com/v1/chat/completions"

# Therapy techniques and coping strategies
THERAPY_TECHNIQUES = {
    "sadness": [
        "Practice self-compassion by treating yourself with the same kindness you'd offer to a friend.",
        "Try journaling about your feelings to help process them.",
        "Engage in light physical activity like walking, which can help improve your mood.",
        "Connect with a supportive friend or family member.",
        "Remember that emotions are temporary and will pass with time."
    ],
    "anger": [
        "Take deep breaths, counting to 10 before responding.",
        "Try the 5-4-3-2-1 grounding technique to calm your nervous system.",
        "Consider the situation from the other person's perspective.",
        "Express your feelings using 'I' statements rather than accusations.",
        "Step away from the situation temporarily if possible to cool down."
    ],
    "fear": [
        "Practice mindful breathing to center yourself in the present moment.",
        "Challenge catastrophic thinking by examining the evidence for your fears.",
        "Break overwhelming tasks into smaller, manageable steps.",
        "Visualize yourself successfully handling the situation you fear.",
        "Remember past situations where you successfully overcame your fears."
    ],
    "joy": [
        "Savor this positive moment by being fully present in it.",
        "Express gratitude for the good things in your life.",
        "Share your happiness with others to strengthen connections.",
        "Reflect on what contributed to this positive feeling.",
        "Use this positive energy to tackle something challenging."
    ],
    "neutral": [
        "Practice mindfulness to become more aware of your thoughts and feelings.",
        "Set small, achievable goals to create a sense of accomplishment.",
        "Explore activities that have brought you joy in the past.",
        "Consider starting a gratitude practice to notice positive aspects of your life.",
        "Take care of your physical needs like sleep, nutrition, and exercise."
    ]
}

# Empathetic responses for different emotions
EMPATHETIC_RESPONSES = {
    "sadness": [
        "I hear that you're feeling down right now. That's completely valid, and I'm here to listen.",
        "It sounds like you're going through a difficult time. Remember that it's okay to feel sad sometimes.",
        "I'm sorry you're feeling this way. Would it help to talk more about what's troubling you?",
        "When we feel sad, it can be overwhelming. Let's take it one step at a time together.",
        "I understand that sadness can feel heavy. You don't have to carry that weight alone."
    ],
    "anger": [
        "I can sense your frustration. It's completely natural to feel angry sometimes.",
        "Your feelings are valid. Would it help to explore what's behind this anger?",
        "It sounds like this situation has really upset you, and that's understandable.",
        "Anger often comes from feeling unheard or disrespected. I'm here to listen to you.",
        "I appreciate you sharing these strong feelings with me. Let's work through this together."
    ],
    "fear": [
        "It's okay to feel anxious or scared. These feelings are trying to protect you.",
        "I hear that you're worried. Would it help to talk about what's causing this fear?",
        "Feeling anxious can be really uncomfortable. You're brave for acknowledging these feelings.",
        "When we're afraid, our minds often focus on the worst possibilities. Let's explore this together.",
        "Your concerns are valid. Let's take a moment to breathe and think about this situation."
    ],
    "joy": [
        "It's wonderful to hear you're feeling positive! Your happiness is important.",
        "I'm so glad things are going well for you. Would you like to share more about what's bringing you joy?",
        "That sounds really positive! It's great that you're experiencing these good feelings.",
        "I'm happy to hear that! Celebrating these positive moments is important.",
        "Your positive energy is contagious. Thank you for sharing this happy moment."
    ],
    "neutral": [
        "I'm here to support you, whatever you might be feeling right now.",
        "How are you feeling about everything that's going on?",
        "I'm listening and here to help in any way I can.",
        "Would you like to explore any particular thoughts or feelings today?",
        "Sometimes taking a moment to check in with ourselves can be helpful. How are you really doing?"
    ]
}

class ActionGetMotivationalQuote(Action):

    def name(self) -> Text:
        return "action_get_motivational_quote"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get the latest user message
        latest_message = tracker.latest_message.get("text", "")
        
        # Detect emotion in the user's message
        emotion_data = emotion_detector.detect_emotion(latest_message)
        emotion = emotion_data.get("emotion", "neutral")
        confidence = emotion_data.get("confidence", 0.0)
        method = emotion_data.get("method", "default")
        
        # Log the emotion detection results
        logger.info(f"Detected emotion: {emotion} (confidence: {confidence}, method: {method})")
        
        # Fallback quotes in case the API call fails
        fallback_quotes = [
            {"quote": "The only way out is through.", "author": "Robert Frost"},
            {"quote": "You are stronger than you think.", "author": "Unknown"},
            {"quote": "Every moment is a fresh beginning.", "author": "T.S. Eliot"},
            {"quote": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
            {"quote": "This too shall pass.", "author": "Persian Proverb"}
        ]
        
        # Try to call the FastAPI endpoint
        try:
            response = requests.get("http://localhost:8000/quote", timeout=3)
            if response.status_code == 200:
                data = response.json()
                quote = data.get("quote")
                author = data.get("author")
            else:
                # Use fallback if API returns error
                fallback = random.choice(fallback_quotes)
                quote = fallback["quote"]
                author = fallback["author"]
                logger.warning(f"API returned status code {response.status_code}, using fallback quote")
        except Exception as e:
            # Use fallback if API call fails
            fallback = random.choice(fallback_quotes)
            quote = fallback["quote"]
            author = fallback["author"]
            logger.error(f"Error fetching quote: {str(e)}")

        # Add emotion-specific prefix based on detected emotion
        if emotion in ["sadness", "sad"]:
            prefix = "I understand you might be feeling down. Here's something that might help: "
        elif emotion in ["anger", "angry"]:
            prefix = "I can sense you're frustrated. Take a deep breath and consider this: "
        elif emotion in ["fear", "afraid"]:
            prefix = "It's okay to feel anxious sometimes. Remember: "
        elif emotion in ["joy", "happy"]:
            prefix = "I'm glad you're feeling positive! Here's more inspiration: "
        else:
            prefix = "Here's a thought for you: "
            
        dispatcher.utter_message(text=f"{prefix}\n\"{quote}\"\n- {author}")

        # Store the detected emotion as a slot
        return [SlotSet("detected_emotion", emotion)]

class ActionProcessMessage(Action):
    def name(self) -> Text:
        return "action_process_message"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the latest user message
        latest_message = tracker.latest_message.get("text", "")
        
        # Get NLU data including intent confidence
        intent = tracker.latest_message.get("intent", {})
        intent_name = intent.get("name", "")
        confidence = intent.get("confidence", 0.0)
        
        # Detect emotion in the user's message
        emotion_data = emotion_detector.detect_emotion(latest_message)
        emotion = emotion_data.get("emotion", "neutral")
        emotion_confidence = emotion_data.get("confidence", 0.0)
        detection_method = emotion_data.get("method", "default")
        
        # Log the detection results
        logger.info(f"Message: '{latest_message}'")
        logger.info(f"Intent: {intent_name} (confidence: {confidence})")
        logger.info(f"Emotion: {emotion} (confidence: {emotion_confidence}, method: {detection_method})")
        
        # Get an emotion-specific response
        emotion_response = emotion_detector.get_response_for_emotion(emotion)
        
        # Check if confidence is below threshold (30%)
        if confidence < 0.3:
            # Use fallback API for low confidence responses
            return self._call_fallback_api(dispatcher, tracker, latest_message, emotion)
        else:
            # For high confidence intents, just store the emotion
            # The bot will use the regular dialogue flow
            return [SlotSet("detected_emotion", emotion)]
    
    def _call_fallback_api(self, dispatcher, tracker, message, emotion):
        # Add emotion context to the API request
        emotion_context = f"The user seems to be feeling {emotion}. "
        
        # First try to use a predefined empathetic response
        if random.random() < 0.7 and emotion in EMPATHETIC_RESPONSES:  # 70% chance to use predefined response
            response = random.choice(EMPATHETIC_RESPONSES[emotion])
            
            # Add a coping strategy or technique if appropriate
            if emotion in ["sadness", "anger", "fear"] and random.random() < 0.5:  # 50% chance to add technique
                technique = random.choice(THERAPY_TECHNIQUES[emotion])
                response += f"\n\nHere's a technique that might help: {technique}"
                
            dispatcher.utter_message(text=response)
            return [SlotSet("detected_emotion", emotion)]
        
        # Otherwise, try the external API
        try:
            # Call external API for a more comprehensive response
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer YOUR_API_KEY"  # Replace with actual API key in production
            }
            
            # Create a more detailed system prompt
            system_prompt = (
                f"You are an empathetic mental health assistant. {emotion_context}"
                f"Provide a supportive response that acknowledges the user's feelings "
                f"and offers gentle guidance. Keep your response concise (2-3 sentences) "
                f"and focus on emotional support rather than clinical advice."
            )
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "max_tokens": 150,
                "temperature": 0.7
            }
            
            response = requests.post(MENTAL_HEALTH_API_URL, headers=headers, json=payload, timeout=5)
            data = response.json()
            
            if response.status_code == 200 and "choices" in data:
                ai_response = data["choices"][0]["message"]["content"]
                dispatcher.utter_message(text=ai_response)
            else:
                # Fallback to emotion-based response if API fails
                fallback_response = random.choice(EMPATHETIC_RESPONSES[emotion])
                dispatcher.utter_message(text=fallback_response)
                logger.warning(f"API returned error: {data.get('error', 'Unknown error')}, using fallback response")
                
        except Exception as e:
            logger.error(f"Error in fallback API call: {str(e)}")
            # Use emotion-based response as fallback
            fallback_response = random.choice(EMPATHETIC_RESPONSES[emotion])
            dispatcher.utter_message(text=fallback_response)
        
        return [SlotSet("detected_emotion", emotion)]


class ActionFallbackAPI(Action):
    def name(self) -> Text:
        return "action_fallback_api"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        latest_message = tracker.latest_message.get("text", "")
        
        # Detect emotion in the user's message
        emotion_data = emotion_detector.detect_emotion(latest_message)
        emotion = emotion_data.get("emotion", "neutral")
        
        # First try to use a predefined empathetic response
        if random.random() < 0.7 and emotion in EMPATHETIC_RESPONSES:  # 70% chance to use predefined response
            response = random.choice(EMPATHETIC_RESPONSES[emotion])
            dispatcher.utter_message(text=response)
            return [SlotSet("detected_emotion", emotion)]
        
        # Otherwise, try the external API
        try:
            # Call external API for a more comprehensive response
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer YOUR_API_KEY"  # Replace with actual API key in production
            }
            
            # Create a more detailed system prompt
            system_prompt = (
                "You are an empathetic mental health assistant. "
                "Provide a supportive response that acknowledges the user's feelings "
                "and offers gentle guidance. Keep your response concise (2-3 sentences) "
                "and focus on emotional support rather than clinical advice."
            )
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": latest_message}
                ],
                "max_tokens": 150,
                "temperature": 0.7
            }
            
            response = requests.post(MENTAL_HEALTH_API_URL, headers=headers, json=payload, timeout=5)
            data = response.json()
            
            if response.status_code == 200 and "choices" in data:
                ai_response = data["choices"][0]["message"]["content"]
                dispatcher.utter_message(text=ai_response)
            else:
                # Fallback to generic response if API fails
                dispatcher.utter_message(text="I'm not sure how to respond to that. Could you rephrase or ask something else?")
                logger.warning(f"API returned error: {data.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Error in fallback API call: {str(e)}")
            dispatcher.utter_message(text="I'm having trouble processing your request right now. Let's try something else.")
            
        return [SlotSet("detected_emotion", emotion)]


class ActionCheckServerStatus(Action):
    """Action to check if the Rasa server is running and update the connection status."""
    
    def name(self) -> Text:
        return "action_check_server_status"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Try to connect to the Rasa server
        try:
            # Simple check to see if the server is responding
            response = requests.get("http://localhost:5005/status", timeout=2)
            
            if response.status_code == 200:
                # Server is running
                connection_status = "connected"
                logger.info("Rasa server connection: CONNECTED")
            else:
                # Server returned an error
                connection_status = "disconnected"
                logger.warning(f"Rasa server returned status code: {response.status_code}")
        except Exception as e:
            # Server is not responding
            connection_status = "disconnected"
            logger.error(f"Rasa server connection error: {str(e)}")
        
        # Set the connection status slot
        return [SlotSet("server_connection_status", connection_status)]


class ActionSuggestCopingStrategy(Action):
    """Action to suggest a coping strategy based on the detected emotion."""
    
    def name(self) -> Text:
        return "action_suggest_coping_strategy"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the current emotion from the slot
        current_emotion = tracker.get_slot("detected_emotion") or "neutral"
        
        # Map similar emotions to our categories
        emotion_mapping = {
            "sad": "sadness",
            "angry": "anger",
            "anxious": "fear",
            "afraid": "fear",
            "happy": "joy",
            "excited": "joy"
        }
        
        # Map the emotion to our categories
        mapped_emotion = emotion_mapping.get(current_emotion, current_emotion)
        
        # Default to neutral if we don't have strategies for this emotion
        if mapped_emotion not in THERAPY_TECHNIQUES:
            mapped_emotion = "neutral"
        
        # Get a random coping strategy for this emotion
        strategy = random.choice(THERAPY_TECHNIQUES[mapped_emotion])
        
        # Create an appropriate introduction based on the emotion
        if mapped_emotion == "sadness":
            intro = "When you're feeling down, it can help to:"
        elif mapped_emotion == "anger":
            intro = "To manage feelings of frustration or anger, you might try:"
        elif mapped_emotion == "fear":
            intro = "When anxiety or fear arises, this technique can be helpful:"
        elif mapped_emotion == "joy":
            intro = "To build on these positive feelings, consider:"
        else:
            intro = "Here's a helpful technique you might want to try:"
        
        # Send the coping strategy
        dispatcher.utter_message(text=f"{intro}\n\n{strategy}")
        
        return []