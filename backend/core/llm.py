import os
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq


def get_llm(temperature: float = 0.2):
    """
    Returns a LangChain LLM.
    Set USE_GROQ=true in .env to use the free Groq API (llama3-70b).
    Otherwise falls back to OpenAI gpt-4o-mini.
    """
    use_groq = os.getenv("USE_GROQ", "false").lower() == "true"

    if use_groq:
        return ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.3-70b-versatile",
            temperature=temperature,
        )

    return ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
        temperature=temperature,
    )
