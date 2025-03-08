import os
import requests
from typing import Optional, Dict

EDEN_AI_API_KEY = os.getenv("EDEN_AI_API_KEY")
EDEN_AI_ENDPOINT = "https://api.edenai.run/v2/text/generation"

def generate_sql_query(
    natural_language_query: str,
    schema: Optional[Dict] = None
) -> str:
    """
    Generate SQL query from natural language using Eden AI API
    """
    if not EDEN_AI_API_KEY:
        raise ValueError("EDEN AI API key not found in environment variables")

    # Prepare the prompt with schema context if available
    prompt = natural_language_query
    if schema:
        schema_context = "\nDatabase Schema:\n" + str(schema)
        prompt = prompt + schema_context

    headers = {
        "Authorization": f"Bearer {EDEN_AI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "providers": "google",  # Using Google's model through Eden AI
        "text": f"Convert this to SQL query: {prompt}",
        "temperature": 0.1,
        "max_tokens": 300
    }

    try:
        response = requests.post(
            EDEN_AI_ENDPOINT,
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        
        result = response.json()
        sql_query = result['google']['generated_text']
        
        # Basic cleanup of the generated SQL
        sql_query = sql_query.strip()
        if sql_query.startswith('```sql'):
            sql_query = sql_query[6:-3]  # Remove markdown code blocks if present
            
        return sql_query.strip()
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")
    except KeyError as e:
        raise Exception(f"Unexpected API response format: {str(e)}")
