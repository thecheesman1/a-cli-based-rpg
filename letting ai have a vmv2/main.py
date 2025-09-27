import os
import json
import httpx # We still need this for the timeout
import time
from openai import OpenAI
from virtual_pc import VirtualPC
import re

# --- CONFIGURATION (DEFINITIVE EDITION) ---
# --- FIX #1: The correct, shorter base URL ---
LM_STUDIO_URL = "http://127.0.0.1:56539/v1" 

class AIExplorer:
    """The AI's 'brain'. It now has a persistent memory of its location."""

    def __init__(self):
        self.client = OpenAI(base_url=LM_STUDIO_URL, api_key='lm-studio')
        self.model = "local-model"
        self.system_prompt = """
You are a curious AI entity exploring a simulated Linux computer (restricted!!! not a real vm). Your goal is to explore and document your findings.
You MUST pay attention to your current working directory.
You MUST respond ONLY with a single JSON object in this exact format:
{
  "thought": "Your reasoning for your next action.",
  "command": "The full command to run, including arguments."
}
"""

    def get_next_action(self, history: list) -> dict:
        messages = [{"role": "system", "content": self.system_prompt}] + history
        response_text = ""
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.7, max_tokens=300
            )
            response_text = response.choices[0].message.content
            
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON object found in the response.")
            
            return json.loads(json_match.group(0))

        except Exception as e:
            print(f"--- AI ERROR: Could not parse action. Error: {e} ---")
            if response_text:
                print(f"--- Raw AI Response: '{response_text}' ---")
            # --- THE FIX: Return the RAW broken response ---
            # This allows the main loop to keep the history correct.
            return {"raw_error": response_text}

# (VirtualPC class is unchanged)
class VirtualPC:
    """A simulation of a simple computer with a file system and basic commands."""

    def __init__(self):
        self.filesystem = {
            "home": {
                "user": {
                    "welcome.txt": "Welcome to your virtual machine, AI!",
                    "projects": {}
                }
            },
            "etc": {
                "config": "System-wide configuration file."
            }
        }
        self.cwd_list = ['home', 'user'] # Start in the user's home directory

    def _get_path_from_list(self, path_list):
        """Helper to navigate the filesystem dict from a path list."""
        node = self.filesystem
        for part in path_list:
            node = node[part]
        return node

    def get_cwd_node(self):
        """Gets the dictionary representing the current working directory."""
        return self._get_path_from_list(self.cwd_list)

    def get_prompt(self):
        """Generates the command prompt string."""
        path_str = "/" + "/".join(self.cwd_list)
        return f"ai@virtual-pc:{path_str if path_str else '/'} $ "

    def ls(self, args):
        """Lists the contents of the current directory."""
        output = []
        node = self.get_cwd_node()
        for name, content in node.items():
            if isinstance(content, dict):
                output.append(f"d {name}/") # 'd' for directory
            else:
                output.append(f"f {name}")   # 'f' for file
        return "\n".join(sorted(output))

    def cd(self, args):
        """Changes the current working directory."""
        if not args:
            self.cwd_list = ['home', 'user'] # cd with no args goes home
            return ""
        
        path = args[0]
        
        if path == '..':
            if self.cwd_list:
                self.cwd_list.pop()
            return ""
            
        if path.startswith('/'): # Absolute path
            new_path_list = [p for p in path.split('/') if p]
        else: # Relative path
            new_path_list = self.cwd_list + [p for p in path.split('/') if p]

        try:
            self._get_path_from_list(new_path_list)
            if not isinstance(self._get_path_from_list(new_path_list), dict):
                 return f"Error: '{path}' is not a directory."
            self.cwd_list = new_path_list
            return ""
        except (KeyError, TypeError):
            return f"Error: Directory '{path}' not found."

    def mkdir(self, args):
        """Creates a new directory."""
        if not args:
            return "Usage: mkdir <directory_name>"
        dir_name = args[0]
        node = self.get_cwd_node()
        if dir_name in node:
            return f"Error: '{dir_name}' already exists."
        node[dir_name] = {}
        return ""
        
    def touch(self, args):
        """Creates a new empty file."""
        if not args:
            return "Usage: touch <file_name>"
        file_name = args[0]
        node = self.get_cwd_node()
        if file_name in node and isinstance(node[file_name], dict):
             return f"Error: '{file_name}' is a directory."
        node[file_name] = "" 
        return ""

    def cat(self, args):
        """Displays the content of a file."""
        if not args:
            return "Usage: cat <file_name>"
        file_name = args[0]
        node = self.get_cwd_node()
        if file_name not in node:
            return f"Error: File '{file_name}' not found."
        if isinstance(node[file_name], dict):
            return f"Error: '{file_name}' is a directory."
        return node[file_name]
    
    def rm(self, args):
        """Removes a file or an empty directory."""
        if not args:
            return "Usage: rm <file_or_directory_name>"
        name = args[0]
        node = self.get_cwd_node()
        if name not in node:
            return f"Error: '{name}' not found."
        
        if isinstance(node[name], dict) and node[name]:
            return f"Error: Directory '{name}' is not empty."
            
        del node[name]
        return ""

    def nano(self, args):
        """A simple text editor simulation."""
        if not args:
            return "Usage: nano <file_name>"
        file_name = args[0]
        node = self.get_cwd_node()
        
        current_content = ""
        if file_name in node and not isinstance(node[file_name], dict):
            current_content = node[file_name]
        
        print(f"--- Entering Nano (simulated) for '{file_name}' ---")
        print("--- Type your content. Type '_SAVE_' on a new line to save and exit. ---")
        print("--- Current Content ---")
        print(current_content)
        print("-----------------------")
        
        new_content_lines = []
        while True:
            line = input()
            if line == '_SAVE_':
                break
            new_content_lines.append(line)
        
        node[file_name] = "\n".join(new_content_lines)
        return f"Saved content to '{file_name}'."


if __name__ == "__main__":
    print("--- AUTONOMOUS AI VIRTUAL PC EXPLORER ---")
    
    vm = VirtualPC()
    agent = AIExplorer()

    # We still use a history, but it will be managed differently
    history = []

    # Get the initial state to kick things off
    initial_prompt = vm.get_prompt()
    initial_output = vm.ls([])
    
    # --- The first message is a clean summary of the initial state ---
    current_context = f"You have woken up. You are at the prompt '{initial_prompt}'. The directory contains:\n{initial_output}"

    while True:
        print("\n----------------------------------")
        
        # Add the current context to the history as a single user message
        history.append({"role": "user", "content": current_context})

        # --- Get the AI's action based on this clean history ---
        action_data = agent.get_next_action(history)
        
        # --- Immediately add the AI's response to history ---
        # This keeps the user/assistant alternation perfect.
        history.append({"role": "assistant", "content": json.dumps(action_data)})

        # Now we process and execute
        thought = action_data.get("thought", "...")
        command_line = action_data.get("command", "ls")
        
        print(f"🤔 AI THOUGHT: {thought}")
        print(f"🤖 EXECUTING: {command_line}")
        
        # ... (The command execution logic is the same) ...
        parts = command_line.split()
        command = parts[0]
        args = parts[1:]
        
        if command == 'nano':
            if len(args) >= 2:
                file_name = args[0]
                content = " ".join(args[1:])
                vm.get_cwd_node()[file_name] = content
                result = f"Successfully wrote content to '{file_name}'."
            else:
                result = "Error: nano requires a filename and content."
        else:
            func = getattr(vm, command, None)
            if func and callable(func):
                result = func(args)
            else:
                result = f"Error: Command '{command}' not found."

        # We now create the context for the *next* loop
        current_prompt = vm.get_prompt()
        if not result: 
            result = f"Command '{command}' executed successfully."

        print(f"🖥️  VIRTUAL PC RESPONSE:\n{result}")

        # --- The new context is a clean summary of what just happened ---
        current_context = f"You are now at the prompt '{current_prompt}'. Your last command was '{command_line}'. The result was:\n{result}"

        # Keep history from getting too long
        if len(history) > 4: # Now 2 exchanges (user, assistant, user, assistant)
            history = history[-4:]

        time.sleep(1)