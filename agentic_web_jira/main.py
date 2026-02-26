import sys
from jira_agent import JiraAgent
from scraper import ScraperAgent
from llm_processor import LLMProcessor
import getpass
import config

def main():
    print("=== Agentic Jira Story Creator ===")
    
    # 1. Jira Setup
    print("\n[Jira Configuration]")
    # Email is now loaded from config via JiraAgent
    
    jira_agent = JiraAgent()
    if not jira_agent.connect(jira_agent.email):
        print("Could not connect to Jira. Exiting.")
        return

    # 2. Content Source
    print("\n[Content Retrieval]")
    print("1. Scrape specific URL")
    print(f"2. Scrape Configured Confluence Page")
    print("3. Manual Input / Paste Meeting Notes")
    choice = input("Select option (1/2/3): ").strip()
    
    scraper = ScraperAgent()
    content = ""
    
    if choice == '1':
        target_url = input("Enter URL: ").strip()
        content = scraper.scrape_url(target_url, username=jira_agent.email, token=jira_agent.api_token)
    elif choice == '2':
        target_url = config.CONFLUENCE_PAGE_URL
        print(f"Using configured URL: {target_url}")
        content = scraper.scrape_url(target_url, username=jira_agent.email, token=jira_agent.api_token)
    elif choice == '3':
        print("\nEnter/Paste your meeting notes (type 'DONE' on a new line when finished):")
        lines = []
        while True:
            try:
                line = input()
                if line.strip().upper() == 'DONE':
                    break
                lines.append(line)
            except EOFError:
                break
        content = "\n".join(lines)
    else:
        print("Invalid choice.")
        return

    if not content:
        print("No content retrieved. Exiting.")
        return
        
    print(f"\nRetrieved {len(content)} characters of text.")
    
    # 3. LLM Processing
    print("\n[LLM Processing]")
    print(f"Current Configured Provider: {config.LLM_PROVIDER}")
    print("1. Use Configured Provider")
    print("2. Switch to OpenAI")
    print("3. Switch to Ollama")
    llm_choice = input("Select option (1/2/3): ").strip()
    
    provider = config.LLM_PROVIDER
    model = None
    
    if llm_choice == '2':
        provider = 'openai'
        model = input(f"Enter OpenAI model (default: {config.OPENAI_MODEL}): ").strip() or config.OPENAI_MODEL
    elif llm_choice == '3':
        provider = 'ollama'
        model = input(f"Enter Ollama model (default: {config.OLLAMA_MODEL}): ").strip() or config.OLLAMA_MODEL
    else:
        # Use default
        pass

    processor = LLMProcessor(provider=provider, model_name=model)
    
    stories = processor.generate_stories(content)
    
    if not stories:
        print("No stories generated.")
        return
        
    print(f"\nGenerated {len(stories)} stories.")
    
    # 4. Review and Create
    print("\n[Review & Create]")
    
    # Fetch and list projects
    print("Fetching available projects...")
    projects = jira_agent.get_projects()
    if projects:
        print("\nAvailable Projects:")
        for idx, (key, name) in enumerate(projects):
            print(f"{idx + 1}. {key} - {name}")
        
        p_choice = input("Enter Project Key (or number): ").strip()
        
        # Check if number
        if p_choice.isdigit() and 1 <= int(p_choice) <= len(projects):
            project_key = projects[int(p_choice) - 1][0]
        else:
            project_key = p_choice.upper()
    else:
        print("Could not fetch projects. Try entering key manually.")
        project_key = input("Enter Jira Project Key (e.g., KAN): ").strip()
    
    print(f"Using Project: {project_key}")
    
    # 5. Select Issue Type
    print("\nFetching issue types...")
    issue_types = jira_agent.get_issue_types(project_key)
    selected_issue_type = "Story"
    
    if issue_types:
        print("\nAvailable Issue Types:")
        for idx, t_name in enumerate(issue_types):
            print(f"{idx + 1}. {t_name}")
        
        # Default to 'Story' if present, otherwise first one
        default_idx = next((i for i, t in enumerate(issue_types) if t.lower() == 'story'), 0) + 1
        
        it_choice = input(f"Select Issue Type (number, default {default_idx}): ").strip()
        if not it_choice:
            selected_issue_type = issue_types[default_idx - 1]
        elif it_choice.isdigit() and 1 <= int(it_choice) <= len(issue_types):
            selected_issue_type = issue_types[int(it_choice) - 1]
        else:
            print("Invalid selection, using default/Story.")
            # Fallback
            if 'Story' in issue_types:
                 selected_issue_type = 'Story'
            else:
                 selected_issue_type = issue_types[0]
    else:
        print("Could not fetch issue types. Defaulting to 'Story'.")

    print(f"Using Issue Type: {selected_issue_type}")

    for i, story in enumerate(stories):
        print(f"\n--- Story {i+1} ---")
        print(f"Summary: {story.get('summary')}")
        print(f"Description: {story.get('description')}")
        print(f"Criteria: {story.get('acceptance_criteria')}")
        
        action = input(f"Create this story in Jira? (y/n/q to quit): ").strip().lower()
        if action == 'y':
            # Format description for Jira
            desc = story.get('description') + "\n\n*Acceptance Criteria:*\n" + "\n".join(f"- {ac}" for ac in story.get('acceptance_criteria', []))
            
            key = jira_agent.create_story(project_key, story.get('summary'), desc, issue_type=selected_issue_type)
            if key:
                print(f"Success: {key} created.")
        elif action == 'q':
            break

    print("\nDone.")

if __name__ == "__main__":
    main()
