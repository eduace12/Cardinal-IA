#!/usr/bin/env python3
"""
Cardinal-IA Universal
Integra ABACUS + Todas as IAs (Gemini, Claude, GPT-4, DeepSeek, Ollama, etc.)
"""
import os
import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ===== CONFIGURAÇÃO DAS IAS =====
IA_CONFIGS = {
    "gemini": {
        "url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
        "key": os.getenv("GEMINI_API_KEY"),
        "headers": {"Content-Type": "application/json"}
    },
    "claude": {
        "url": "https://api.anthropic.com/v1/messages",
        "key": os.getenv("ANTHROPIC_API_KEY"),
        "headers": {"Content-Type": "application/json", "anthropic-version": "2023-06-01"}
    },
    "gpt4": {
        "url": "https://api.openai.com/v1/chat/completions",
        "key": os.getenv("OPENAI_API_KEY"),
        "headers": {"Content-Type": "application/json"}
    },
    "ollama": {
        "url": "http://localhost:11434/api/generate",
        "key": None,
        "headers": {"Content-Type": "application/json"}
    }
}

# ===== FUNÇÃO UNIVERSAL =====
def ask_ia(provider: str, prompt: str) -> str:
    config = IA_CONFIGS.get(provider)
    if not config:
        return "IA não configurada"

    try:
        if provider == "ollama":
            payload = {"model": "codellama", "prompt": prompt, "stream": False}
            response = requests.post(config["url"], json=payload)
            return response.json().get("response", "Sem resposta")
        
        elif provider == "gemini":
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            response = requests.post(f"{config['url']}?key={config['key']}", json=payload)
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        
        elif provider == "claude":
            payload = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post(config["url"], json=payload, headers=config["headers"])
            return response.json()["content"][0]["text"]
        
        elif provider == "gpt4":
            payload = {
                "model": "gpt-4",
                "messages": [{"role": "user", "content": prompt}]
            }
            response = requests.post(config["url"], json=payload, headers=config["headers"])
            return response.json()["choices"][0]["message"]["content"]
    
    except Exception as e:
        return f"Erro {provider}: {e}"

# ===== ROTAS FLASK =====
@app.route('/')
def home():
    return jsonify({
        "message": "Cardinal-IA Universal",
        "ias": list(IA_CONFIGS.keys()),
        "endpoint": "/ask?provider=gemini&prompt=sua_pergunta"
    })

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    provider = data.get("provider", "ollama")
    prompt = data.get("prompt", "")
    response = ask_ia(provider, prompt)
    return jsonify({"provider": provider, "response": response})

if __name__ == '__main__':
    print("🚀 Cardinal-IA Universal rodando!")
    app.run(host='0.0.0.0', port=5000)
