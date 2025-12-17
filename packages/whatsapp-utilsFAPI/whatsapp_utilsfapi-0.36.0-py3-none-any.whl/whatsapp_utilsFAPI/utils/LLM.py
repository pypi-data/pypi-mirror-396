
import logging

import re

from langchain_openai import AzureChatOpenAI

from langchain_core.prompts import ChatPromptTemplate

import requests

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    pass


def clear_text(text: str) -> str:
    """
    Clean and normalize text by removing special characters and extra spaces.
    
    Args:
        text: Input text to clean
        
    Returns:
        Cleaned text string
    """
    if not isinstance(text, str):
        return ""

    # Remove newline, tab, and carriage return
    text = text.replace("\n", " ").replace("\r", " ").replace("\t", " ")

    # Remove punctuation and special characters (keep Arabic, English letters, digits)
    text = re.sub(rf"[^A-Za-z0-9\u0600-\u06FF ]+", " ", text)

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    # Trim leading/trailing spaces
    return text.strip()


def llm_gpt4(question: str, sys_conf: dict) -> str:
    """
    Generate AI response using Azure OpenAI GPT-4.
    
    Args:
        question: User's question
        sys_conf: System configuration dictionary
        
    Returns:
        AI response text
        
    Raises:
        LLMError: If LLM processing fails
    """
    logger.info("Starting LLM processing")
    
    try:
        llm = AzureChatOpenAI(
            api_key=sys_conf["AZURE_OPENAI_KEY"],
            azure_endpoint=sys_conf["AZURE_OPENAI_ENDPOINT"],
            openai_api_version=sys_conf["OPENAI_API_VERSION"],
            azure_deployment=sys_conf["AZURE_OPENAI_DEPLOYMENT"],
            temperature=0
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a personal assistant.
             Respond in Egyptian Arabic.
             Summarize the answer to be 50 words maximum.
             Do not use punctuation or new lines - answer in one line."""),
            ("user", "{input}")
        ])
        
        chain = prompt | llm
        response = chain.invoke({"input": question})
        
        logger.info("LLM response received: %s", response)
        
        result = clear_text(response.content.strip())
        logger.info("Processed LLM response: %s", result)
        
        return result
        
    except Exception as e:
        logger.error("LLM processing failed: %s", str(e))
        raise LLMError(f"Failed to generate AI response: {str(e)}") from e


def llm_globy(question: str, sys_conf: dict):
    logger.info("####  llm_globy")
    payload= {
        "message": question,
        "agent_id": "",
        "thread_id":""
        }

    headers = {
            "Content-Type": "application/json"
        }

    response_ =  requests.post(sys_conf['Globy_caht_api'], json=payload, headers=headers,timeout=120)
    response_=response_.json()
    return response_
