import shlex
import json

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

    # --- SIMULATED LINUX COMMANDS ---

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
            # Check if the target is actually a directory
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
        node[file_name] = "" # Create empty file
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
        
        if isinstance(node[name], dict) and node[name]: # Non-empty directory
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

def run_human_mode():
    """The main loop for a human to interact with the Virtual PC."""
    vm = VirtualPC()
    print("Virtual PC started. Type 'exit' to quit.")
    while True:
        prompt = vm.get_prompt()
        try:
            command_line = input(prompt)
        except EOFError: # Handle Ctrl+D
            break

        if command_line.lower() == 'exit':
            break
            
        parts = shlex.split(command_line)
        if not parts:
            continue
            
        command = parts[0]
        args = parts[1:]
        
        func = getattr(vm, command, None)
        if func and callable(func):
            output = func(args)
            if output:
                print(output)
        else:
            print(f"Error: Command '{command}' not found.")

if __name__ == "__main__":
    run_human_mode()