import subprocess
import time
import json
import re
from openai import OpenAI

# --- CONFIGURATION ---
MODEL_NAME = "gemma:2b"  # The Ollama model you want to use
GAME_COMMAND = "python main.py" # The command to start the RPG game
AI_SPEED = 2 # Seconds to wait between AI actions, for watchability


class AIPlayer:
    """The AI's 'brain'. It now has a short-term memory."""

    def __init__(self, model_name):
        # Point the OpenAI client to your LM Studio server
        self.client = OpenAI(
            base_url='http://127.0.0.1:56539/v1',
            api_key='lm-studio', # can be anything
        )
        # We don't need to specify the model name here, as it's determined
        # by the model you've loaded in LM Studio.
        self.model = "local-model" # A placeholder name
        
        # The system prompt is now more direct, as the history will provide context
        self.system_prompt = """
You are a strategic AI playing a text-based RPG. Your goal is to level up your character and survive.

# HOW TO PLAY
The game will present you with a numbered list of options. You must analyze the game state and choose the best option by responding with the corresponding number.

# YOUR RESPONSE FORMAT
You must respond ONLY with a single, perfectly valid JSON object in this exact format:
{
  "thought": "Your step-by-step reasoning for choosing the next action, including why you are choosing a specific number.",
  "command": "The single number corresponding to your choice from the menu."
}

# MAIN MENU COMMANDS
- "1": Explore (Risk fighting an enemy to gain experience and items)
- "2": Rest (Heal your character, but cannot be used in Hardcore mode)
- "3": View Stats (Check your current health, attack, inventory, etc. A very safe and useful move.)
- "4": Shop (Buy and sell items. You need coins.)
- "5": Mine (Gather resources which can be sold at the shop.)
- "6": Start Auto Mining (Begin generating coins over time.)
- "7": Stop Auto Mining (Stop generating coins.)
- "8": Save Game (Saves your progress.)
- "9": Quit (Ends the game.)

When a battle starts, the menu will change. You will need to choose between the WORDS 'attack', 'run', or 'use item'. DO NOT respond with a number during battle. Your JSON command must be one of these three words.
- 'attack': Fight the enemy.
- 'run': Escape the battle.
- 'use item': Use an item from your inventory.

Analyze the situation, decide on the best choice, and then output your JSON.
"""

    def get_action(self, history: list) -> dict:
        """
        The final, most robust parser. It gets the AI's response, tries to parse it
        as JSON, falls back to plain text if needed, and then intelligently corrects
        the final action based on the game's current context (menu vs. battle).
        """
        raw_response = "" # Initialize to handle errors gracefully
        try:
            # Step 1: Get the raw response from the AI
            messages = [{"role": "system", "content": self.system_prompt}] + history
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=250
            )
            raw_response = response.choices[0].message.content.strip()
            
            thought = "No thought provided."
            action = "3" # Default action (View Stats)

            # Step 2: Try to parse the response
            try:
                # First, attempt to parse the response as a JSON object
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                if json_match:
                    action_data = json.loads(json_match.group(0))
                    thought = action_data.get("thought", "I forgot to think.")
                    action = str(action_data.get("command", "3")) # Ensure action is a string
                else:
                    raise ValueError("No JSON object found in response.") # Force fallback to plain text

            except (json.JSONDecodeError, ValueError):
                # If JSON parsing fails, fall back to the plain text "Thought: \n command" format
                lines = raw_response.split('\n')
                thought_lines = [line.split(':', 1)[1].strip() for line in lines if line.lower().startswith('thought:')]
                if thought_lines:
                    thought = " ".join(thought_lines)
                
                # Find the last non-empty, non-thought line to be the action
                for line in reversed(lines):
                    cleaned_line = line.strip(".,'\"` ")
                    if cleaned_line and not cleaned_line.lower().startswith('thought:'):
                        action = cleaned_line
                        break

            # --- Step 3: The "Intelligent Corrector" ---
            # Get the last line of the game state to determine the context
            last_game_line = history[-1]['content'].strip().split('\n')[-1]

            is_battle_prompt = "attack/run/use item" in last_game_line.lower()
            is_menu_prompt = last_game_line.strip().endswith('>')
            is_name_prompt = "enter your character's name:" in last_game_line.lower()

            # If the AI is at a name prompt, it should be able to use a name, not a number
            if is_name_prompt:
                # The action is likely correct (e.g., "Phoenix"), so we don't change it.
                pass
            # If it's a battle prompt, the action MUST be a word
            elif is_battle_prompt and action.isdigit():
                thought += " (Correction: The game wants a word like 'attack', not a number. Defaulting to 'attack'.)"
                action = "attack"
            
            # If it's a menu prompt, the action MUST be a number
            elif is_menu_prompt and not action.isdigit():
                thought += f" (Correction: The game wants a number, not the word '{action}'. Trying to interpret.)"
                # Try to guess the intended number from the word
                action_lower = action.lower()
                if "explore" in action_lower: action = "1"
                elif "rest" in action_lower: action = "2"
                elif "stats" in action_lower: action = "3"
                elif "shop" in action_lower: action = "4"
                elif "mine" in action_lower: action = "5"
                elif "start" in action_lower: action = "6"
                elif "stop" in action_lower: action = "7"
                elif "save" in action_lower: action = "8"
                elif "quit" in action_lower: action = "9"
                else: action = "3" # Default to 'View Stats' if completely confused

            return {"thought": thought, "action": action}

        except Exception as e:
            print(f"--- AI ERROR: An unexpected error occurred: {e} ---")
            # Include the raw response in the thought for debugging
            thought = f"I encountered a system error. Raw response was: '{raw_response}'"
            return {"thought": thought, "action": "9"} # Quit on major error
        
class GameRunner:
    """Manages the game subprocess and communication."""

    def __init__(self, command):
        self.process = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1 # Line-buffered
        )

    def read_output(self) -> str:
        """Reads all output from the game one character at a time until it waits for input."""
        output_chars = []
        current_line = ""
        while self.is_running():
            # Read one character at a time
            char = self.process.stdout.read(1)
            if not char:
                # End of stream, process has likely closed
                break
            
            # Print the character to your console so you can watch the game live
            print(char, end='', flush=True)
            
            # Store the character for the AI
            output_chars.append(char)
            
            # Build up the current line to check for our prompt markers
            if char == '\n':
                current_line = ""
            else:
                current_line += char

            # If the current line ends with a prompt, we know the game is waiting for us.
            if current_line.strip().endswith(('):', 'name:', '>')):
                break
                
        return "".join(output_chars)

    def send_input(self, action: str):
        """Sends a command to the game."""
        self.process.stdin.write(action + '\n')
        self.process.stdin.flush()

    def is_running(self) -> bool:
        """Checks if the game process is still active."""
        return self.process.poll() is None

if __name__ == "__main__":
    print("--- AI GAMER AGENT (MEMORY EDITION) INITIALIZING ---")
    print(f"--- Model: {MODEL_NAME} ---")
    print("--- Make sure your LM Studio server is running! ---")
    
    ai_player = AIPlayer(MODEL_NAME)
    game = GameRunner(GAME_COMMAND)
    
    # Initialize a conversation history
    conversation_history = []
    
    print("\n--- GAME STARTING ---\n")
    time.sleep(2)

    conversation_history = []
    
    print("\n--- GAME STARTING ---\n")
    time.sleep(2)

    while game.is_running():
        # 1. Read the state of the game
        game_state = game.read_output()
        if not game_state:
            break
        
        # --- ROBUST HISTORY MANAGEMENT ---
        # If the last message was also from the user (game), it means the AI's last
        # turn failed or was invalid. We'll merge this new state with the last one.
        if conversation_history and conversation_history[-1]["role"] == "user":
            conversation_history[-1]["content"] += "\n" + game_state
        else:
            conversation_history.append({"role": "user", "content": game_state})

        # 2. Get the AI's next move
        # We now pass a *copy* of the history, so the AI can't mess with our main list
        ai_decision = ai_player.get_action(list(conversation_history))
        thought = ai_decision['thought']
        action = ai_decision['action']
        
        print(f"\n🤔 AI THOUGHT: {thought}")
        print(f">>> AI chooses: {action}\n")

        # 3. Add the AI's successful action to the history
        # Now we know for sure the sequence is user -> assistant
        ai_response_content = json.dumps({"thought": thought, "command": action})
        conversation_history.append({"role": "assistant", "content": ai_response_content})
        
        # 4. Prune the history to keep it a manageable size
        # We'll keep the last 5 full exchanges (10 messages)
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        # 5. Send the chosen action to the game
        game.send_input(action)
        time.sleep(AI_SPEED)

    print("\n--- GAME OVER ---")
    # Capture any final error messages
    stdout, stderr = game.process.communicate()
    if stdout: print("Final STDOUT:\n", stdout)
    if stderr: print("Final STDERR:\n", stderr)