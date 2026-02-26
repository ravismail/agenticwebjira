# User Guide: Jira Story Creation Agent

Welcome to the Jira Story Creation Agent! This tool helps you transform meeting notes and documentation into well-structured Jira User Stories automatically using AI.

## Table of Contents
1. [Setup and Installation](#setup-and-installation)
2. [Configuration](#configuration)
3. [Running the Application](#running-the-application)
4. [Using the Content Options](#using-the-content-options)
5. [Understanding the Scripts](#understanding-the-scripts)

---

## Setup and Installation



### Prerequisites
- **Python 3.8+**: Ensure you have Python installed.
- **Ollama (Optional)**: If you want to run LLMs locally (e.g., Llama 3). [Download Ollama here](https://ollama.com/).
- **OpenAI API Key (Optional)**: If you prefer using OpenAI's models.

### Installation
1. Navigate to the project directory.
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

---

## Configuration

Before running the agent, you must configure your credentials in `config.py`.

Open `config.py` and set the following:
- `JIRA_URL`: Your Jira instance URL (e.g., `https://your-domain.atlassian.net`).
- `JIRA_EMAIL`: The email address associated with your Jira account.
- `JIRA_API_TOKEN`: Your Atlassian API token. [Generate one here](https://id.atlassian.com/manage-profile/security/api-tokens).
- `CONFLUENCE_PAGE_URL`: (Optional) The default Confluence page you want to scrape.
- `LLM_PROVIDER`: Choose `ollama` or `openai`.
- `OPENAI_API_KEY`: Required if using `openai`.

---

## Running the Application

To start the agent, run the following command in your terminal:

```bash
python main.py
```

Follow the interactive prompts to:
1. Select a content source.
2. Choose your LLM model.
3. Review generated stories.
4. Select a Jira project and issue type.
5. Create the stories in Jira.

---

## Using the Content Options

The agent provides three ways to retrieve meeting notes:

1. **Scrape specific URL**: Enter a direct link to a website or public document.
2. **Scrape Configured Confluence Page**: Uses the URL provided in `config.py` to fetch internal documentation directly.
3. **Manual Input / Paste Meeting Notes**: **(Recommended for privacy)** Paste your notes directly into the terminal or type them in. Type `DONE` on a new line when you are finished.

---

## Understanding the Scripts

The project is organized into several key scripts, each with a specific responsibility:

### `main.py`
- **What it does**: This is the **Entry Point**. It manages the user interface (CLI) and orchestrates the flow of data between the scraper, the AI, and Jira.
- **When to use**: Always run this script to use the tool.

### `config.py`
- **What it does**: Stores all your **Settings and Credentials**.
- **When to use**: Edit this file once during setup or whenever you need to change your Jira/AI settings.

### `scraper.py`
- **What it does**: Handles the **Content Retrieval**. It knows how to search Google and extract clean text from websites and Confluence pages.
- **Note**: You don't run this directly; `main.py` uses it behind the scenes.

### `llm_processor.py`
- **What it does**: The **Brain** of the agent. it uses LangChain to send your notes to an LLM (OpenAI or Ollama) and ensures the output is a valid list of Jira stories with titles, descriptions, and criteria.

### `jira_agent.py`
- **What it does**: The **Jira Interface**. It handles the actual API calls to Jira to fetch projects, issue types, and create the tickets.

### `requirements.txt`
- **What it does**: Lists all the **Dependencies** (libraries like `langchain`, `atlassian-python-api`, etc.) needed for the project to work.

---

## Troubleshooting
- **Connection Error**: Double-check your `JIRA_API_TOKEN` and `JIRA_EMAIL`.
- **Model Not Found**: Ensure Ollama is running and you have "pulled" the model (e.g., `ollama pull llama3`).
- **Scraping Blocked**: Some sites block scraping. If a URL fails, try using the **Manual Input** (Option 3) to paste the text directly.



As a developer, I need to implement robust backend email validation for the updateProfile API endpoint so that data integrity is maintained.

curl http://localhost:12434/engines/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
  "model": "ai/llama3.2",
  "messages": [
   { "role":"user",
     "content":"Why is the sky blue?" }
  ]
}'