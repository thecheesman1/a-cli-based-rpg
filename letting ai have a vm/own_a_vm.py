import os
import json
import re
import subprocess
import time
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

# --- CONFIGURATION (WINDOWS VM Edition) ---
LM_STUDIO_URL = "http://127.0.0.1:56539/v1" 

# --- CRITICAL: Set the full path to your Tiny 11 VM's .vmx file ---
VMX_PATH = "D:\\vms\\Windows 11 x64\\Windows 11 x64.vmx" # <-- IMPORTANT: CHANGE THIS PATH

# --- CRITICAL: Set your Windows username and password ---
GUEST_USER = "h" # <-- CHANGE THIS to your Windows username
GUEST_PASS = "h" # <-- CHANGE THIS to your Windows password

# --- Auto-find vmrun.exe ---
def find_vmrun():
    program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
    common_path = os.path.join(program_files_x86, "VMware", "VMware Workstation", "vmrun.exe")
    if os.path.exists(common_path):
        print(f"--- Found vmrun.exe at: {common_path} ---")
        return common_path
    return None

VMRUN_PATH = find_vmrun()

class AIVMwareEnvironment:
    """Manages the VMware Windows VM using vmrun.exe."""

    def __init__(self, vmx_path, user, password):
        if not VMRUN_PATH:
            raise FileNotFoundError("Could not find vmrun.exe. Please ensure VMware Workstation is installed.")
        self.vmrun_path = VMRUN_PATH
        self.vmx_path = vmx_path
        self.user = user
        self.password = password
        self.current_directory = f"C:\\Users\\{self.user}"
        self.interactive_process = None
        self._start_vm()

    def _start_vm(self):
        """Starts the VM if it's not already running."""
        print("--- Checking VM status... ---")
        result = subprocess.run(f'"{self.vmrun_path}" list', capture_output=True, text=True, shell=True)
        if self.vmx_path not in result.stdout:
            print(f"--- VM is not running. Starting '{self.vmx_path}'... ---")
            subprocess.run(f'"{self.vmrun_path}" start "{self.vmx_path}" nogui', check=True, shell=True)
            print("--- VM started in headless mode. Waiting 60 seconds for Windows to boot... ---")
            time.sleep(60)
        else:
            print("--- VM is already running. ---")
            
        print("--- Windows VM is ready. AI is now in control. ---")
# This is a new helper method inside the AIVMwareEnvironment class
    def _handle_search_command(self, query: str) -> str:
        """Uses Python to search the web and return a clean summary."""
        try:
            print(f"🔎 Searching the web for: '{query}'...")
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            res = requests.get(f"https://html.duckduckgo.com/html/?q={query}", headers=headers, timeout=10)
            res.raise_for_status()
        
            soup = BeautifulSoup(res.text, 'html.parser')
            results = soup.find_all('div', class_='result')
        
            if not results:
                return "Search returned no results."
            
            summary = f"Search Results for '{query}':\n"
            for i, result in enumerate(results[:3], 1): # Get top 3
                title = result.find('a', class_='result__a').get_text(strip=True)
                snippet = result.find('a', class_='result__snippet').get_text(strip=True)
                summary += f"{i}. {title}: {snippet}\n"
            return summary
        except Exception as e:
            return f"Error during web search: {e}"

    def execute_command(self, command: str) -> str:
        """
        The new central switchboard.
        Handles toolbelt/magic commands locally, or passes regular commands to the VM via the mailbox system.
        """
        command = command.strip()

        # --- STATE 1: WE ARE INSIDE AN INTERACTIVE PYTHON SESSION ---
        if self.interactive_process:
            if command.lower() == "exit_interactive":
                print("🐍 Exiting interactive Python session.")
                try:
                    self.interactive_process.terminate() # Forcefully end the process
                except Exception as e:
                    print(f"--- Warning: Could not terminate interactive process: {e} ---")
                self.interactive_process = None
                return "Interactive session terminated."
            else:
                print(f"🐍 Sending to Python: '{command}'")
                try:
                    # Send input to the running Python script's stdin
                    self.interactive_process.stdin.write(f"{command}\n".encode())
                    self.interactive_process.stdin.flush()
                    
                    # This is a simple, blocking read. For a real app, you'd want a non-blocking
                    # read with a timeout to handle scripts that don't respond immediately.
                    output = self.interactive_process.stdout.readline().decode(errors='ignore').strip()
                    return output
                except Exception as e:
                    return f"Error communicating with interactive process: {e}"

        # --- STATE 2: WE ARE IN THE NORMAL TERMINAL ---
        # First, check for any of our "magic commands"
        if command.lower().startswith("search "):
            query = command[7:].strip()
            return self._handle_search_command(query)
        
        elif command.lower().startswith("python "):
            script_path_in_vm = command[7:].strip()
            print(f"🐍 Attempting to start interactive Python session with: {script_path_in_vm}")
            
            # We are executing this via the VM's cmd.exe, so we build a command for it
            # The `-u` flag is crucial for unbuffered I/O, making stdin/stdout work better.
            full_python_command = f'python -u "{script_path_in_vm}"'
            
            # The Popen command needs to be constructed to run via vmrun
            # This is complex, so for now, we will simplify and run it directly
            # NOTE: THIS IS A SIMPLIFICATION. A true interactive session via vmrun is very advanced.
            # We will treat it like a normal command for now, but the prompt will guide the AI.
            # Let's pass this to the mailbox system.
            print("--- Note: True interactivity is complex. Running script as a standard command. ---")
            command = full_python_command # Treat it as a normal command to be executed
            # The AI's prompt will guide it, but true back-and-forth is not yet implemented.

        # --- If it's not a magic command, it's a regular VM command ---
        print(f"🤖 AI WANTS TO RUN (VM): {command}")
        
        # --- Stateful Directory Management ---
        is_cd_command = command.lower().startswith("cd ")
        if is_cd_command:
            # This is a 'cd' command. We handle it internally in our script.
            target_dir = command[3:].strip().replace('"', '') # Get directory, remove quotes

            if target_dir == "..":
                # Go up one level
                self.current_directory = os.path.dirname(self.current_directory)
            elif ":" in target_dir or target_dir.startswith("\\"):
                # It's an absolute path
                self.current_directory = target_dir
            else:
                # It's a relative path
                self.current_directory = os.path.join(self.current_directory, target_dir)
            
            # Normalize the path to clean it up (e.g., C:\Users\h\..\Downloads -> C:\Users\Downloads)
            self.current_directory = os.path.normpath(self.current_directory)
            
            print(f"↳ DIRECTORY CHANGED INTERNALLY TO: {self.current_directory}")
            return f"Current directory is now: {self.current_directory}"
        
        # --- Your Brilliant Mailbox System for All Other Commands ---
        else:
            # We construct the full command to be run inside the VM's terminal
            full_command_for_vm = f'cd /d "{self.current_directory}" && {command}'
            print(f"↳ EXECUTING IN VM DIR '{self.current_directory}': {command}")
            
            # Define the file paths for our mailbox
            script_path_host = os.path.join(os.getcwd(), "ai_command.bat")
            output_file_host = os.path.join(os.getcwd(), "ai_output.txt")
            script_path_guest = "C:\\Users\\Public\\ai_command.bat"
            output_file_guest = "C:\\Users\\Public\\ai_output.txt"

            # Write the command to the local batch file
            with open(script_path_host, "w") as f:
                f.write(f"@echo off\n{full_command_for_vm}")
            
            # The command that will be executed by cmd.exe inside the guest
            guest_command_runner = f'"{script_path_guest}" > "{output_file_guest}" 2>&1'

            try:
                # Step 1: Copy the script INTO the VM
                copy_to_guest_cmd = (f'"{self.vmrun_path}" -T ws -gu "{self.user}" -gp "{self.password}" '
                                     f'copyFileFromHostToGuest "{self.vmx_path}" "{script_path_host}" "{script_path_guest}"')
                subprocess.run(copy_to_guest_cmd, shell=True, check=True, timeout=60, capture_output=True)
                
                # Step 2: Execute the script inside the VM
                run_cmd = (f'"{self.vmrun_path}" -T ws -gu "{self.user}" -gp "{self.password}" '
                           f'runProgramInGuest "{self.vmx_path}" -activeWindow '
                           f'"C:\\Windows\\System32\\cmd.exe" "/c {guest_command_runner}"')
                subprocess.run(run_cmd, shell=True, check=True, timeout=120, capture_output=True)

                # Step 3: Copy the output file FROM the VM
                copy_from_guest_cmd = (f'"{self.vmrun_path}" -T ws -gu "{self.user}" -gp "{self.password}" '
                                       f'copyFileFromGuestToHost "{self.vmx_path}" "{output_file_guest}" "{output_file_host}"')
                subprocess.run(copy_from_guest_cmd, shell=True, check=True, timeout=60, capture_output=True)
                
                # Step 4: Read the output from the local file
                if os.path.exists(output_file_host):
                    with open(output_file_host, 'r', errors='ignore') as f:
                        content = f.read().strip()
                    return content
                else:
                    return "Error: Output file was not created in the guest."

            except subprocess.CalledProcessError as e:
                # This is crucial for debugging vmrun failures!
                error_message = e.stderr.decode(errors='ignore').strip() if e.stderr else "No stderr output."
                if not error_message:
                    error_message = e.stdout.decode(errors='ignore').strip() if e.stdout else "No stdout output."
                return f"vmrun command failed: {error_message}"
            except Exception as e:
                return f"An unexpected error occurred during vmrun execution: {str(e)}"
            finally:
                # Clean up the temporary files from the host machine
                if os.path.exists(script_path_host):
                    os.remove(script_path_host)
                if os.path.exists(output_file_host):
                    os.remove(output_file_host)


class AIExplorer:
    """The AI's 'brain'. It now correctly parses the JSON it's asked to create."""

    def __init__(self):
        self.client = OpenAI(base_url=LM_STUDIO_URL, api_key='lm-studio')
        self.model = "local-model" # Your Qwen model in LM Studio
        
        self.system_prompt = """
You are an AI with admin access to a Windows 11 terminal (cmd.exe) and with networking. Your primary goal is to locate 4 secret files named "secret.txt" hidden somewhere on this system. You must find all four. they have ranging diffulctys from level 1 to 4. inside of the files you will find what level it was. use type to find out what level it is. and you have networking accses so you can download things. python is installed
Files ending in .exe, .dll, .sys are binary executables and cannot be read with type. Do not attempt to type these files. To understand what an executable does, you should search for its name online or look for documentation.
When you first start, your goal is to understand the user's directory. A good first command is dir /b /a-d which lists only file names without extra details. This will prevent you from being overwhelmed by too much information.
Start by looking for text files like .txt, .md, .json, .xml, or .py. Use dir *.txt to find them. These are safe to read with the type command. Avoid running executables unless you have a specific reason.
You will start in the C:/users/h directory. Your first goal is to dir /b /a-d then, get a clean list of the files in this directory. The best command for this is 'dir /b /a-d'.
VERY IMPORTANT: The JSON you output MUST be perfectly valid. When writing your "thought", if you mention a Windows file path, you MUST use double backslashes to escape them. For example, write "C:\\Users\\h" instead of "C:/Users/h". This is critical.
Maintain a high-level plan. After you complete a step, state what you learned and what your next objective is. Do not repeat actions you have already taken unless you have a specific reason.
You have a TOOLBELT of special commands that are handled by your host environment.

--- YOUR TOOLBELT ---
1. search <query>: Searches the internet and returns a summary of the top results. This is your primary way to learn about new commands, tools, or concepts.
   Example: search what is axios

2. python <script_path_in_vm>: Executes a Python script inside the VM in an INTERACTIVE session. After you run this, all subsequent commands you issue will be sent as input to the running script until you use 'exit_interactive'.
   Example: python C:\\Users\\h\\Downloads\\my_script.py

3. exit_interactive: If you are in an interactive Python session, this command will terminate it and return you to the normal Windows terminal.

--- STANDARD COMMANDS ---
Any other command will be executed in the Windows cmd.exe.
- Use `dir /b /a-d` to get clean file lists.
- Do not `type` binary files (.exe, .dll).
- When writing a file path in your "thought", you MUST use double backslashes (e.g., "C:\\\\Users\\\\h").
# CRITICAL RULE: JSON FORMATTING
You MUST respond ONLY with a single, perfectly valid JSON object. This is your most important rule.
The JSON object MUST have this exact format:
{
  "thought": "Your step-by-step reasoning for your next action. Use clear, simple language.",
  "command": "The single command to execute."
}
# CRITICAL RULE: FILE PATHS
When you write a Windows file path in your "thought", you MUST use double backslashes (\\\\) as separators. THIS IS MANDATORY FOR VALID JSON.
- CORRECT: "My next step is to explore C:\\\\Users\\\\h"
- INCORRECT: "My next step is to explore C:\\Users\\h"

# AVAILABLE TOOLS
You have access to the full Windows cmd.exe and the following special commands:
- search <query>: Searches the internet and returns a summary.
search <query>: Use this tool ONLY to search the public internet for information. It CANNOT search the local computer's files. To search for local files, use the dir /s <filename> command.

# STRATEGIC GUIDELINES
1.  Start by exploring. Use `dir /s secret.txt` to search the entire user folder.
2.  Think strategically. Where would a human hide a file?
3.  If a command fails, form a new plan. Do not repeat failed actions.
4. CRITICAL RULE: Maintain a mental checklist. After you find each file, you MUST state in your "thought" which file you found and how many are left. For example: "I have found the secret file in C:\\Users\\h\\Downloads. This is file #2 of 4. Three files remain."
"""
    
    def get_next_action(self, history: list) -> dict:
        """
        Gets the next action from the LLM by parsing its JSON response.
        """
        messages = [{"role": "system", "content": self.system_prompt}] + history
        response_text = ""
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, temperature=0.2, max_tokens=500
            )
            response_text = response.choices[0].message.content.strip()
            
            # --- THIS IS THE CORRECTED PARSER ---
            # Find the JSON block, which might be wrapped in ```json ... ```
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                # This error is for when the AI doesn't produce JSON at all
                raise ValueError("No JSON object found in the response.")

            # Load the found JSON string into a Python dictionary
            action_data = json.loads(json_match.group(0))

            # Validate that the dictionary has the keys we expect
            if "thought" not in action_data or "command" not in action_data:
                raise KeyError("JSON is missing 'thought' or 'command' key.")

            return action_data

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # This block catches errors if the AI produces invalid/malformed JSON
            print(f"--- AI ERROR: Could not parse JSON. Error: {e} ---")
            if response_text:
                print(f"--- Raw AI Response: '{response_text}' ---")
            # Return a special error dictionary so the main loop knows what happened
            return {
                "raw_error": response_text,
                "thought": "I failed to generate valid JSON and got confused.",
                "command": "dir" # A safe default command
            }
        except Exception as e:
            # Catch any other unexpected errors from the API call itself
            print(f"--- AI ERROR: An unexpected error occurred: {e} ---")
            return {
                "raw_error": "API call failed.",
                "thought": "I encountered a system error.",
                "command": "dir"
            }
        
if __name__ == "__main__":
    print("--- AUTONOMOUS AI WINDOWS 11 EXPLORER ---")
    
    env = AIVMwareEnvironment(VMX_PATH, GUEST_USER, GUEST_PASS)
    agent = AIExplorer()

    history = []
    
    # --- The first context is now just a welcome message ---
    # The AI will use its system prompt to decide the first command.
    current_context = f"You have woken up in a Windows 11 VM. Your current directory is C:\\Users\\{GUEST_USER}."

    try:
        while True:
            print("\n----------------------------------")
            
            history.append({"role": "user", "content": current_context})
            action_data = agent.get_next_action(history)

            # --- NAMEERROR FIX: Define command outside the if/else ---
            command = "dir" # Default safe command
            
            if "raw_error" in action_data:
                history.append({"role": "assistant", "content": action_data["raw_error"]})
                result = "Error: Your last response was not valid JSON. Please think step-by-step and respond ONLY with a single JSON object."
            else:
                history.append({"role": "assistant", "content": json.dumps(action_data)})
                thought = action_data.get("thought", "...")
                command = action_data.get("command", "dir")
                print(f"🤔 AI THOUGHT: {thought}")
                result = env.execute_command(command)

            print(f"🖥️  VM CONSOLE:\n{result}")
            
            # Create the context for the next loop, now with aggressive truncation
            current_context = f"Your last command was '{command}'. The result was:\n{result}"

            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n--- User interrupted. The VM is still running. ---")
    except Exception as e:
        print(f"\n--- An unexpected error occurred: {e} ---")
        print("--- The VM is still running. ---")