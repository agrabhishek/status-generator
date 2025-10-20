"""
LLM Provider Integrations
==========================
Groq, OpenAI, xAI, Gemini support with rate limit handling.

Generated: 2025-10-19 18:28:32
"""

import streamlit as st
import requests
from typing import Tuple


@st.cache_data(ttl=3600)
def fetch_groq_models(api_key: str) -> list:
    """
    Fetch available Groq models dynamically.
    
    REQUIREMENT: Multi-LLM Integration - Dynamic model discovery
    Cached for 1 hour to avoid repeated API calls.
    """
    try:
        response = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        response.raise_for_status()
        models_data = response.json()
        model_ids = [model['id'] for model in models_data.get('data', [])]
        return sorted(model_ids)
    except Exception as e:
        st.error(f"Failed to fetch Groq models: {e}")
        return []


def call_groq_llm(prompt: str, model: str, api_key: str) -> Tuple[str, bool]:
    """
    Call Groq API with rate limit detection.
    
    REQUIREMENT: Handle 429 rate limits
    
    Returns:
        (response_text, is_rate_limited)
    """
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 400,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if response.status_code == 429:
            return "", True
        
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'], False
        
    except requests.exceptions.Timeout:
        return "⚠️ Request timeout. Try a different model.", False
    except Exception as e:
        return f"❌ Error: {str(e)}", False


def get_llm_summary(llm_provider: str, api_key: str, prompt: str, groq_model: str = None) -> str:
    """
    Get AI summary from selected provider.
    
    REQUIREMENT: Multi-LLM Integration
    Supports: Groq, OpenAI, xAI, Gemini
    """
    try:
        if llm_provider == "Groq (Free Tier)":
            if not groq_model:
                return "❌ No Groq model selected"
            
            summary, rate_limited = call_groq_llm(prompt, groq_model, api_key)
            
            if rate_limited:
                return f"⚠️ Rate limit hit for {groq_model}. Please select another model and regenerate."
            
            return summary
        
        elif llm_provider == "OpenAI":
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            return response.choices[0].message.content
        
        elif llm_provider == "xAI":
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "grok-beta",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 300
                }
            )
            return response.json()['choices'][0]['message']['content']
        
        elif llm_provider == "Gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return response.text
        
        return ""
    except Exception as e:
        return f"AI summary error: {str(e)}"
