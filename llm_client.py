import os
import traceback
import logging
from dotenv import load_dotenv
import groq

load_dotenv()

# Setup logging for tracing errors
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("llm_client")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = groq.Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None
# Default to an available model on Groq
MODEL_NAME = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")


def call_llm(messages: list[dict], system_prompt: str = None) -> str:
    """
    Call Groq LLM API with formatted messages and detailed exception tracing.
    """
    if not client:
        err_msg = "GROQ_API_KEY environment variable is missing. Please check your .env file."
        logger.error(err_msg)
        raise ValueError(err_msg)

    formatted_messages = []
    
    if system_prompt:
        formatted_messages.append({"role": "system", "content": system_prompt})
        
    for msg in messages:
        formatted_messages.append({"role": msg["role"], "content": msg["content"]})

    try:
        logger.info(f"Calling Groq API with model: {MODEL_NAME}, message count: {len(formatted_messages)}")
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=formatted_messages,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except groq.NotFoundError as e:
        logger.error(f"Model '{MODEL_NAME}' not found or access denied on Groq: {e}\n{traceback.format_exc()}")
        # Fallback to another popular available model if the configured model is not found
        fallback_model = "qwen/qwen3.6-27b"
        logger.info(f"Attempting fallback to model: {fallback_model}")
        try:
            response = client.chat.completions.create(
                model=fallback_model,
                messages=formatted_messages,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as fallback_err:
            logger.error(f"Fallback model call failed: {fallback_err}\n{traceback.format_exc()}")
            raise fallback_err
    except Exception as e:
        logger.error(f"Groq API call failed: {e}\n{traceback.format_exc()}")
        raise e
