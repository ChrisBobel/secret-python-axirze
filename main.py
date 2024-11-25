# app.py

from flask import Flask, render_template, request, jsonify
import os
import openai
from dotenv import load_dotenv

app = Flask(__name__)

# Umgebungsvariablen laden
load_dotenv()
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
ELEVENLABS_AGENT_ID = os.getenv('ELEVENLABS_AGENT_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

openai.api_key = OPENAI_API_KEY

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_config')
def get_config():
    # Achtung: In einer Produktionsumgebung sollten Sie den API-Schlüssel nicht an den Client senden.
    return jsonify({
        'agent_id': ELEVENLABS_AGENT_ID,
        'api_key': ELEVENLABS_API_KEY
    })

# Endpoint für den benutzerdefinierten LLM-Server
@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    data = request.get_json()

    # Extrahieren der benutzerdefinierten Anweisungen
    custom_instructions = ""
    if 'elevenlabs_extra_body' in data and 'custom_instructions' in data['elevenlabs_extra_body']:
        custom_instructions = data['elevenlabs_extra_body']['custom_instructions']

    # Modifizieren der Nachrichten
    messages = data['messages']
    if custom_instructions:
        messages.insert(0, {
            'role': 'system',
            'content': custom_instructions
        })

    # Aufruf der OpenAI API
    response = openai.ChatCompletion.create(
        model=data.get('model', 'gpt-3.5-turbo'),
        messages=messages,
        temperature=data.get('temperature', 0.7),
        max_tokens=data.get('max_tokens', 150),
        stream=False,
        user=data.get('user')
    )

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
