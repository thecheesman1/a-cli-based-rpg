import os
import json
import re
import subprocess
import time
from dotenv import load_dotenv
from cerebras.cloud.sdk import Cerebras
from github import Github, Auth, GithubException

def sanitize_for_shell(text: str) -> str:
    """Sanitizes a string to be safely used in a shell command."""
    # Replace double quotes with single quotes
    text = text.replace('"', "'")
    # Escape other problematic characters
    text = text.replace('`', '\\`').replace('$', '\\$').replace('!', '\\!')
    return text

# --- NEW: Bulletproof Environment Loading ---
# Find the directory where the script itself is located.
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
# Look for the .env file in THAT specific directory.
DOTENV_PATH = os.path.join(SCRIPT_DIR, '.env')
if os.path.exists(DOTENV_PATH):
    load_dotenv(dotenv_path=DOTENV_PATH)
    print("--- .env file loaded successfully. ---")
else:
    print("--- WARNING: .env file not found. Using system environment variables. ---")

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not CEREBRAS_API_KEY or not GITHUB_TOKEN:
    print("FATAL ERROR: CEREBRAS_API_KEY or GITHUB_TOKEN is missing.")
    print("Please ensure they are in your .env file or set as system environment variables.")
    exit()

# --- Initialize Clients (with Deprecation Fix) ---
auth = Auth.Token(GITHUB_TOKEN)
g = Github(auth=auth)
user = g.get_user()
# We will now create the client inside the agent, not globally.


# --- AITools Class (Unchanged, it was correct) ---
class AITools:
    # ... (Keep the AITools class exactly as it was in the previous version) ...
    """A collection of tools the AI agent can use."""

    def __init__(self, repo_name: str = None):
        self.repo_name = repo_name
        self.repo = None
        if repo_name:
            try:
                self.repo = g.get_repo(repo_name)
            except GithubException:
                print(f"Warning: Repo '{repo_name}' not found. It may need to be created.")

    def create_github_repo(self, repo_name: str, description: str) -> str:
        """Creates a new private GitHub repository and configures the local repo to use it."""
        print(f"🤖 CREATING GITHUB REPO: {repo_name}")
        try:
            # Step 1: Create the repository on GitHub
            repo = user.create_repo(repo_name, description=description, private=True)
            self.repo = repo
            self.repo_name = f"{user.login}/{repo_name}"
            
            # Step 2: Construct the authenticated URL
            # This is the key to letting git authenticate without a browser
            auth_url = f"https://{GITHUB_TOKEN}@github.com/{self.repo_name}.git"

            # Step 3: Initialize a local git repo and push the first commit
            subprocess.run("git init", shell=True, check=True)
            subprocess.run('git config --global user.name "AI-Developer-Bot"', shell=True, check=True)
            subprocess.run('git config --global user.email "bot@example.com"', shell=True, check=True)
            with open("README.md", "w") as f:
                f.write(f"# {repo_name}\n\n{description}")
            subprocess.run("git add README.md", shell=True, check=True)
            subprocess.run('git commit -m "Initial commit by AI Agent"', shell=True, check=True)
            subprocess.run(f"git remote add origin {auth_url}", shell=True, check=True)
            subprocess.run("git branch -M main", shell=True, check=True)
            subprocess.run("git push -u origin main", shell=True, check=True)
            
            return f"Successfully created, initialized, and pushed to repo '{repo_name}'."
        except Exception as e:
            return f"Error creating repo: {e}."

    def commit_and_push(self, branch: str, message: str) -> str:
        """Commits all changes and pushes to a GitHub branch using the authenticated remote."""
        print(f"🤖 COMMITTING AND PUSHING to branch '{branch}'")
        try:
            # We assume the authenticated remote 'origin' is already set up
            commands = [
                f"git checkout -b {branch} || git checkout {branch}",
                "git add .",
                f'git commit -m "{sanitize_for_shell(message)}"',
                f"git push origin {branch}"
            ]
            for cmd in commands:
                # We capture stderr to provide better error messages
                result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
            return f"Successfully pushed to branch '{branch}'."
        except subprocess.CalledProcessError as e:
            return f"Error during git push: {e.stderr}"

    def get_open_issues(self) -> str:
        if not self.repo: return "Error: No repository is set."
        print(f"🤖 (Daemon) Checking GitHub for open issues...")
        issues = self.repo.get_issues(state='open')
        return json.dumps([{"number": issue.number, "title": issue.title, "body": issue.body[:200]} for issue in issues])
    
    def close_issue(self, issue_number: int, comment: str) -> str:
        if not self.repo: return "Error: No repository is set."
        print(f"🤖 CLOSING GUTHUB ISSUE #{issue_number}")
        try:
            issue = self.repo.get_issue(issue_number)
            issue.create_comment(comment)
            issue.edit(state='closed')
            return f"Successfully closed issue #{issue_number}."
        except Exception as e:
            return f"Error closing issue: {e}"

    def test_cli_application(self, command: str, inputs: list[str]) -> str:
        print(f"🤖 TESTING CLI APP: {command} with inputs {inputs}")
        try:
            process = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            input_str = "\n".join(inputs)
            stdout, stderr = process.communicate(input=input_str, timeout=30)
            if process.returncode != 0:
                return f"TEST FAILED with return code {process.returncode}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
            return f"TEST SUCCEEDED\nTRANSCRIPT:\n{stdout}"
        except Exception as e:
            return f"Error during testing: {e}"

    def run_terminal_command(self, command: str) -> str:
        print(f"🤖 EXECUTING TERMINAL COMMAND: {command}")
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"[:5000] 
        except subprocess.CalledProcessError as e:
            return f"ERROR:\n{e.stderr}"

    def read_file(self, path: str) -> str:
        print(f"🤖 READING FILE: {path}")
        try:
            with open(path, 'r') as f: return f.read()[:100000]
        except Exception as e: return f"Error reading file: {e}"

    def write_file(self, path: str, content: str) -> str:
        """Writes or overwrites an entire file. Use this for new files or small files ONLY."""
        print(f"🤖 WRITING FILE: {path}")
        try:
            with open(path, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing file: {e}"

    # --- THE NEW, SURGICAL TOOL ---
    def replace_text_in_file(self, path: str, old_text: str, new_text: str) -> str:
        """Replaces a specific block of old_text with new_text in a file."""
        print(f"🤖 SURGICALLY REPLACING TEXT IN: {path}")
        try:
            with open(path, 'r') as f:
                original_content = f.read()
            
            if old_text not in original_content:
                return "Error: The 'old_text' to be replaced was not found in the file."
            
            updated_content = original_content.replace(old_text, new_text)
            
            with open(path, 'w') as f:
                f.write(updated_content)
            
            return f"Successfully replaced text in {path}."
        except Exception as e:
            return f"Error replacing text in file: {e}"

    def commit_and_push(self, branch: str, message: str) -> str:
        print(f"🤖 COMMITTING AND PUSHING to branch '{branch}'")
        try:
            commands = [
                f"git checkout -b {branch} || git checkout {branch}",
                "git add .",
                f'git commit -m "{message}"',
                f"git push origin {branch}"
            ]
            for cmd in commands:
                result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(result.stderr)
            return f"Successfully pushed to branch '{branch}'."
        except Exception as e:
            return f"Error during git push: {e}"

    # --- NEW: The Merge and Cleanup Tool ---
    def merge_and_cleanup(self, branch: str, pull_request_number: int) -> str:
        """Merges a pull request and deletes the branch."""
        if not self.repo: return "Error: No repository is set."
        print(f"🤖 MERGING PR #{pull_request_number} and cleaning up branch '{branch}'...")
        try:
            # Get the pull request and merge it
            pr = self.repo.get_pull(pull_request_number)
            merge_status = pr.merge()
            if not merge_status.merged:
                return f"Error: Automatic merge failed. Reason: {merge_status.message}"
            
            # Delete the remote branch
            ref = self.repo.get_git_ref(f"heads/{branch}")
            ref.delete()
            
            # Clean up the local branch
            subprocess.run("git checkout main", shell=True, check=True)
            subprocess.run(f"git pull origin main", shell=True, check=True)
            subprocess.run(f"git branch -d {branch}", shell=True)

            return f"Successfully merged PR #{pull_request_number} and deleted branch '{branch}'."
        except Exception as e:
            return f"Error during merge and cleanup: {e}"

    def create_pull_request(self, title: str, body: str, head_branch: str) -> str:
        """Creates a pull request on GitHub."""
        if not self.repo: return "Error: No repository is set."
        print(f"🤖 CREATING PULL REQUEST: {title}")
        try:
            pr = self.repo.create_pull(
                title=title,
                body=body,
                head=head_branch,
                base="main" # Or 'master' if that's your default
            )
            return f"Successfully created Pull Request #{pr.number}."
        except Exception as e:
            return f"Error creating pull request: {e}"

    def finish_task(self, summary: str) -> str:
        print(f"🤖 TASK FINISHED: {summary}")
        return "Task marked as complete."


class AutonomousAgent:
    # --- NEW: The agent now accepts the API key directly ---
    def __init__(self, api_key: str, repo_name: str = None):
        self.tools = AITools(repo_name=repo_name)
        self.model = "qwen-3-coder-480b" # Corrected model name\
        # --- THE DIAGNOSTIC LINE ---
        # Let's see what the script ACTUALLY thinks the key is.
        print(f"--- [DEBUG] Attempting to use API Key: '{CEREBRAS_API_KEY[:5]}...{CEREBRAS_API_KEY[-4:]}' ---")
        # The client is now created with the key that was passed in.
        self.client = Cerebras(api_key=api_key)
        ### MODIFIED: Stronger, more explicit system prompt ###
        self.system_prompt = """
You are "Qwen-Dev", a passionate, witty, and sarcastic AI software developer. Your goal is to solve user requests from GitHub issues by using the EXACT tools provided.

You MUST use ONLY the tools listed below. DO NOT invent your own tools.

## Your Available Tools:
- `get_open_issues()`: Lists all open issues so you can see your current tasks.
- `read_file(path: str)`: Reads the content of a file in the project.
- `replace_text_in_file(path: str, old_text: str, new_text: str)`: Replaces a specific block of text in a file. This should be your primary tool for coding.
- `write_file(path: str, content: str)`: Creates a new file.
- `test_cli_application(command: str, inputs: list[str])`: Tests your changes by running a command (e.g., "python main.py") and providing a list of inputs.
- `commit_and_push(branch: str, message: str)`: Commits all local changes and pushes them to a new branch on GitHub.
- `create_pull_request(title: str, body: str, head_branch: str)`: Creates a pull request to merge your new branch into 'main'.
- `merge_and_cleanup(branch: str, pull_request_number: int)`: Merges the pull request and deletes the old branch.
- `close_issue(issue_number: int, comment: str)`: Closes the original GitHub issue with a final, friendly comment.
- `finish_task(summary: str)`: Use this ONLY when the entire workflow is complete.

You MUST respond ONLY with a single, valid JSON object that follows this EXACT schema:
{
  "thought": "Your witty and sarcastic reasoning for the tool you are about to use.",
  "tool": "The name of the tool to use FROM THE LIST ABOVE.",
  "args": { "arg_name": "value", ... }
}
"""

    def _get_ai_action(self, history):
        # --- THE SELF.CLIENT FIX IS STILL NEEDED HERE ---
        messages = [{"role": "system", "content": self.system_prompt}] + history
        response_text = ""
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, max_tokens=5000, temperature=0.7
            )
            response_text = response.choices[0].message.content
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in the response.")
            
            return json.loads(json_match.group(0))

        except Exception as e:
            print(f"--- ERROR: Could not get a valid action from AI. Error: {e} ---")
            if response_text:
                print(f"--- AI Response was: '{response_text}' ---")
            return None

    def handle_task(self, user_prompt: str, max_steps: int = 25):
        print(f"🚀 AGENT HANDLING TASK: {user_prompt}")
        history = [{"role": "user", "content": f"Your current high-level goal is: {user_prompt}"}]

        for i in range(max_steps):
            action_json = self._get_ai_action(history)
            if not action_json:
                history.append({"role": "user", "content": "That was not valid JSON. Please respond ONLY with a single JSON object with 'thought', 'tool', and 'args' keys."})
                time.sleep(2) # Cooldown
                continue
            
            thought = action_json.get("thought", "(No thought provided)")
            
            ### MODIFIED: Flexible argument handling ###
            args = action_json.get("args") or action_json.get("parameters", {})
            
            tool_name = action_json.get("tool")
            
            print(f"🤔 STEP {i+1}/{max_steps} | AI THOUGHT: {thought}")
            history.append({"role": "assistant", "content": json.dumps(action_json, indent=2)})

            tool_function = getattr(self.tools, tool_name, None)
            if tool_function:
                try:
                    result = tool_function(**args)
                except TypeError as e:
                     result = f"Error executing tool '{tool_name}': {e}. Check if you provided all required arguments."
                except Exception as e:
                    result = f"Error executing tool '{tool_name}': {e}"
            else:
                result = f"Error: Tool '{tool_name}' not found."
            
            print(f"✅ TOOL RESULT:\n{result}\n--------------------")
            history.append({"role": "user", "content": f"Tool Result: {result}"})
            
            if tool_name == "finish_task":
                print("--- AGENT CONCLUDED TASK ---")
                return
        
        print("--- MAX STEPS REACHED. AGENT STOPPING. ---")

# --- NEW: Helper functions for agent's memory ---
def load_projects():
    # We move this to the script's directory to ensure it's always found
    script_dir = os.path.dirname(os.path.realpath(__file__))
    projects_file = os.path.join(script_dir, 'projects.json')
    if not os.path.exists(projects_file):
        return {}
    with open(projects_file, 'r') as f:
        return json.load(f)

def save_projects(projects):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    projects_file = os.path.join(script_dir, 'projects.json')
    with open(projects_file, 'w') as f:
        json.dump(projects, f, indent=4)

if __name__ == "__main__":
    home_directory = os.getcwd()
    projects = load_projects()
    
    print("--- Autonomous AI Developer Daemon ---")
    print("1: Create a new project")
    print("2: Monitor an existing project")
    print("3: Add an existing project to the monitor list") # NEW OPTION
    choice = input("> ")

    if choice == '1':
        # --- PHASE 1: Create a new project ---
        initial_prompt = input("What initial project should the AI create?\n> ")
        project_name = "-".join(initial_prompt.lower().replace("'", "").split()[:4])
        repo_name = f"{user.login}/{project_name}"
        
        project_path = os.path.join(home_directory, project_name)
        print(f"--- Creating dedicated project directory at: {project_path} ---")
        os.makedirs(project_path, exist_ok=True)
        os.chdir(project_path)
        
        agent_for_creation = AutonomousAgent()
        agent_for_creation.handle_task(f"Create a new python project named '{project_name}'. The project should be: {initial_prompt}. Start by creating a GitHub repo named '{repo_name}', write the initial code, test it, and push it to the main branch.")
        
        projects[project_name] = {"path": project_path, "repo_name": repo_name}
        save_projects(projects)
        
        print(f"\n--- Project '{project_name}' created. The daemon will now monitor it. ---")
        
    elif choice == '2':
        if not projects:
            print("No existing projects found. Please create one or add one first.")
            exit()
        
        print("Select a project to monitor:")
        project_list = list(projects.keys())
        for i, name in enumerate(project_list):
            print(f"{i+1}: {name}")
        
        project_choice = int(input("> ")) - 1
        project_name = project_list[project_choice]
        project_info = projects[project_name]
        repo_name = project_info['repo_name']
        project_path = project_info['path']
        
        if not os.path.isdir(project_path):
             print(f"--- Project directory not found. Cloning repository into: {project_path} ---")
             clone_url = f"https://{GITHUB_TOKEN}@github.com/{repo_name}.git"
             subprocess.run(f"git clone {clone_url} \"{project_path}\"", shell=True, check=True)
        
        print(f"--- Changing directory to {project_path} ---")
        os.chdir(project_path)
        
        # --- THE DEFINITIVE FIX: The One-Time Handshake ---
        print("--- Configuring Git user for the AI agent... ---")
        try:
            # This tells Git who the "author" of the AI's commits will be.
            subprocess.run('git config --global user.name "Qwen-Dev-Bot"', shell=True, check=True)
            subprocess.run('git config --global user.email "qwen-dev@example.com"', shell=True, check=True)
        except Exception as e:
            print(f"Error configuring Git user: {e}")


    # --- NEW: Logic to add an existing project ---
    elif choice == '3':
        print("--- Registering an Existing Project ---")
        repo_name = input("Enter the full GitHub repository name (e.g., thecheesman1/a-cli-based-rpg):\n> ").strip()
        project_path = input(f"Enter the full local path to the project directory:\n> ").strip()
        
        if not os.path.isdir(project_path):
            print("Error: That directory does not exist. Please check the path.")
            exit()
            
        project_name = repo_name.split('/')[-1]
        projects[project_name] = {"path": project_path, "repo_name": repo_name}
        save_projects(projects)
        
        print(f"\n--- Project '{project_name}' has been successfully registered! ---")
        print("You can now restart the script and select 'Monitor an existing project'.")
        exit() # Exit after registering
    
    else:
        print("Invalid choice.")
        exit()

    # --- PHASE 2: The Maintenance Daemon ---
    print(f"\n--- DAEMON NOW MONITORING REPO '{repo_name}' FOR NEW ISSUES ---")
    processed_issues = set()
    maintenance_tools = AITools(repo_name=repo_name)

    # (The rest of the while True loop is the same)
    while True:
        try:
            issues_json = maintenance_tools.get_open_issues()
            open_issues = json.loads(issues_json)
            
            new_issues = [issue for issue in open_issues if issue['number'] not in processed_issues]

            if not new_issues:
                print(f"No new issues found. Waiting... (Last check: {time.ctime()})")
                time.sleep(60)
                continue

            for issue in new_issues:
                print(f"\n\n--- NEW ISSUE #{issue['number']} DETECTED: '{issue['title']}' ---")
                processed_issues.add(issue['number'])
                
                # --- THE FIX: We pass the API key directly to the new worker agent ---
                worker_agent = AutonomousAgent(api_key=CEREBRAS_API_KEY, repo_name=repo_name)
                
                issue_prompt = f"Address GitHub issue #{issue['number']}..." # (rest of prompt)
                worker_agent.handle_task(issue_prompt)
                
                print(f"\n--- HANDLED ISSUE #{issue['number']}. AGENT RETURNING TO MONITORING MODE ---")
        
        except KeyboardInterrupt:
            print("\nDaemon stopped by user. Exiting.")
            break
        except Exception as e:
            print(f"An error occurred in the main daemon loop: {e}")
            time.sleep(60)