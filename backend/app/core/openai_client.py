from openai import OpenAI
from app.core.config import settings

_client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)

def get_openai_client() -> OpenAI:
    return _client
