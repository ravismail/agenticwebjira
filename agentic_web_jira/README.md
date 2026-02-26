# Agentic Jira Story Creator

A CLI-based agentic AI solution that scrapes meeting minutes (from Google Search or Confluence pages) and converts them into Jira stories using a local LLM and LangChain.

## Goal Description
Create a CLI-based agentic AI solution that scrapes meeting minutes (from Google Search or Confluence pages) and converts them into Jira stories using a local LLM and LangChain.

## Prerequisites
- **Ollama** running locally (default model: `llama3`).
- **Jira Account**: You need your email address and the API Token.
- **Python Environment**: Dependencies installed.

## Features & Architecture

### File Responsibilities

- **`main.py`**
  - **Role**: Application Entry Point & Orchestrator.
  - **Responsibilities**:
    - Initializes the application and handles the interactive CLI (Command Line Interface).
    - Prompts the user for input (e.g., selecting the content source, project key).
    - Coordinates data flow: Scraper -> LLM Processor -> Jira Agent.
    - Displays previews of generated stories and asks for user confirmation before creation.

- **`config.py`**
  - **Role**: Configuration Management.
  - **Responsibilities**:
    - Stores sensitive credentials (API Tokens, Email) and environment variables.
    - Defines constant URLs for Jira and Confluence to avoid hardcoding them in logic files.
    - Sets default LLM model parameters.
  
- **`scraper.py`**
  - **Role**: Data Retrieval.
  - **Responsibilities**:
    - Fetches content from the web.
    - **`search_google`**: Performs Google searches to find relevant meeting notes.
    - **`scrape_url`**: Downloads and parses text from a given URL.
    - **Confluence Integration**: specifically collects content from Confluence. Uses the Jira/Confluence API (with `username` and `token`) to retrieve page storage format directly, bypassing login screens and rendering issues common with standard web scraping.

- **`llm_processor.py`**
  - **Role**: AI Logic & Text Processing.
  - **Responsibilities**:
    - Interfaces with the local Ollama instance using `langchain_ollama`.
    - Defines the Prompt Template that instructs the AI how to format stories (Summary, Description, Acceptance Criteria).
    - **`generate_stories`**: Sends content to the LLM and robustly parses the output into structured JSON, handling potential formatting errors from the model.

- **`jira_agent.py`**
  - **Role**: Jira API Adapter.
  - **Responsibilities**:
    - Manages the connection to the Atlassian Jira Cloud instance.
    - **`connect`**: Authenticates using the email and API token.
    - **`get_projects`**: Fetches a list of accessible projects to validate user selection.
    - **`create_story`**: Pushes the finalized story data to Jira to create a new Issue.

- **`requirements.txt`**
  - List of all Python external libraries required to run the project.

## How to Run

1. **Install Dependencies**:
   Open your terminal in the project directory:
   ```bash
   cd c:/Users/ravis/Documents/Antigarvity/Agentic_jira
   pip install -r requirements.txt
   ```

2. **Configuration**:
   Edit `config.py` to set your Jira credentials and preferences:
   - `JIRA_URL`
   - `JIRA_API_TOKEN`
   - `JIRA_EMAIL`
   - `CONFLUENCE_PAGE_URL`
   - `LLM_PROVIDER` ('ollama' or 'openai')
   - `OLLAMA_MODEL`
   - `OPENAI_API_KEY`
   - `OPENAI_MODEL`

3. **Run the Application**:
   ```bash
   python main.py
   ```

4. **Follow the Prompts**:
    - **Content Source**: 
      - 1. Scrape specific URL
      - 2. Scrape Configured Confluence Page
      - 3. Manual Input / Paste Meeting Notes
    - **LLM**: Confirm the model name (default `llama3`).
    - **Review**: The tool will print generated stories.
    - **Create**: You will be prompted to select a project and verify stories before creation.

## Documentation
For detailed instructions and an overview of what each script does, please refer to the **[USER_GUIDE.md](USER_GUIDE.md)**.

## Verification
- The application implements:
    - LangChain + Ollama for story generation.
    - Web scraping (Google & Confluence API).
    - Jira integration for creating stories.
    - Interactive CLI.


