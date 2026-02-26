# Configuration
import os
from dotenv import load_dotenv

load_dotenv()

# Jira Configuration
JIRA_URL = os.getenv("JIRA_URL", "https://ravikanthmasanal.atlassian.net")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN", "")
JIRA_EMAIL = os.getenv("JIRA_EMAIL", "ravikanth.masanal@gmail.com")

# Confluence Configuration
CONFLUENCE_PAGE_URL = os.getenv("CONFLUENCE_PAGE_URL", "https://ravikanthmasanal.atlassian.net/wiki/spaces/~7120208d0b443ee4af464889146a4138af33f3/pages/393218/2026-02-06+Meeting+notes")

# LLM Configuration
LLM_PROVIDER = "ollama"

# Ollama Settings
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "ai/llama3.2")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:12434/engines/v1")
