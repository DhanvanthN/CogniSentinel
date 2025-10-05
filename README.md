# Cognisentinel: A Personalised Mental Health Chatbot

A simple AI chatbot that provides mental health support through conversations.

## What it does
- Talks to users about their feelings
- Understands emotions like sadness, anxiety, and anger
- Provides supportive responses and exercises
- Available 24/7 through a website
- Keeps all conversations private

## How it works
1. User types a message on the website
2. Chatbot understands what they're feeling
3. Chatbot responds with helpful support
4. Conversation continues naturally

## Technology
- **Rasa** - Handles conversations
- **Flair** - Detects emotions in text
- **HTML/CSS** - Simple website interface
- **Python** - Main programming language

## Complete Setup Guide

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/cognisentinel.git
cd cognisentinel
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install core requirements
pip install rasa==3.6.15
pip install flair==0.13.1
pip install spacy==3.7.2

# Download spaCy model
python -m spacy download en_core_web_md

# Install web dependencies
pip install flask==2.3.3
pip install requests==2.31.0
```

### Step 4: Project Structure Setup
```
cognisentinel/
├── data/
│   ├── nlu.yml
│   ├── rules.yml
│   ├── stories.yml
│   └── domain.yml
├── actions/
│   └── actions.py
├── models/
├── templates/
│   └── index.html/modern_interface.thml/new_interface.html
├── config.yml
├── credentials.yml
├── endpoints.yml
└── app.py
```

### Step 5: Train the Model
```bash
# Train the Rasa model
rasa train

# This will create a model in the /models directory
# Training may take 5-10 minutes
```

### Step 6: Run the System
```bash
# Terminal 1 - Start Rasa server
rasa run --cors "*" --enable-api

# Terminal 2 - Start custom action server
rasa run actions

# Terminal 3 - Start web interface
python app.py
```

### Step 7: Access the Chatbot
Open your browser and go to:
```
http://localhost:5000
```

## Configuration Files

### config.yml(example)
```yaml
language: en
pipeline:
  - name: WhitespaceTokenizer
  - name: RegexFeaturizer
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 4
  - name: DIETClassifier
    epochs: 100
    constrain_similarities: true
  - name: EntitySynonymMapper
  - name: ResponseSelector
    epochs: 100
  - name: FallbackClassifier
    threshold: 0.3
    ambiguity_threshold: 0.1
```

### domain.yml(example)
```yaml
intents:
  - greet
  - goodbye
  - express_sadness
  - express_anxiety
  - request_help
  - request_exercise

responses:
  utter_greet:
  - text: "Hello! I'm here to listen. How are you feeling today?"
```

## Testing
```bash
# Test the model
rasa test

# Interactive testing
rasa shell

# Test specific stories
rasa test stories
```

## Deployment

### For Development
```bash
# Run all services in one command
python run_all.py
```

### For Production
```bash
# Using docker
docker build -t cognisentinel .
docker run -p 5000:5000 cognisentinel
```

## Troubleshooting

### Common Issues
1. **Port already in use**: Change port in `app.py`
2. **Model not found**: Run `rasa train` again
3. **Import errors**: Reactivate virtual environment

### Getting Help
- Check Rasa documentation: https://rasa.com/docs
- Flair NLP issues: https://github.com/flairNLP/flair
- Create an issue on GitHub

The chatbot is designed to be a supportive friend, not a replacement for professional therapy.
