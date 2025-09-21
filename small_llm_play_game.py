import subprocess
import time
from openai import OpenAI

# --- CONFIGURATION ---
MODEL_NAME = "gemma:2b"
GAME_COMMAND = "python main.py"
AI_SPEED = 0.5

class AIPlayer:
    """The AI's 'brain'. It now thinks before it acts."""

    def __init__(self, model_name):
        self.client = OpenAI(
            base_url='http://192.168.1.117:1234/v1', # Your LM Studio IP
            api_key='lm-studio',
        )
        self.model = "local-model" # Placeholder for LM Studio
        
        # --- NEW: A more advanced system prompt that demands a thought process ---
        self.system_prompt = """
You are an AI playing a text-based RPG. Your goal is to survive.
You must first explain your reasoning for your next move in a 'Thought' line.
Then, on a new line, you must state the single command to execute.

Analyze the game state and your health.
- If your health is low, your thought should be about resting to recover.
- If you are in an unwinnable fight, your thought should be about running away.
- If you are confident, your thought should be about attacking or exploring.

Your response MUST be in this exact two-line format:
Thought: [Your reasoning here]
[command]

The command on the second line MUST be one of the following: 'explore', 'rest', 'attack', 'run', 'quit'
"""

    def get_action(self, game_output: str) -> dict:
        """Gets a thought and action from the LLM."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": game_output}
                ],
                temperature=0.7,
                max_tokens=100 # More tokens to allow for a thought
            )
            raw_response = response.choices[0].message.content.strip()
            
            # --- NEW: Parse the AI's two-line response ---
            thought = "No thought provided."
            action = "explore" # Default action
            
            lines = raw_response.split('\n')
            for line in lines:
                if line.lower().startswith('thought:'):
                    thought = line.split(':', 1)[1].strip()
                else:
                    # Assume the last non-thought line is the command
                    cleaned_line = line.strip(".,'\"` ")
                    if cleaned_line: # Make sure it's not an empty line
                        action = cleaned_line

            return {"thought": thought, "action": action}

        except Exception as e:
            print(f"--- AI ERROR: Could not parse thought/action. Error: {e} ---")
            return {"thought": "I seem to be confused.", "action": "rest"}


class GameRunner:
    # (This class is unchanged, it works perfectly)
    def __init__(self, command):
        self.process = subprocess.Popen(
            command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, bufsize=1
        )

    def read_output(self) -> str:
        output_chars = []
        current_line = ""
        while self.is_running():
            char = self.process.stdout.read(1)
            if not char: break
            print(char, end='', flush=True)
            output_chars.append(char)
            if char == '\n':
                current_line = ""
            else:
                current_line += char
            if current_line.strip().endswith(('):', 'name:', '>')):
                break
        return "".join(output_chars)

    def send_input(self, action: str):
        self.process.stdin.write(action + '\n')
        self.process.stdin.flush()

    def is_running(self) -> bool:
        return self.process.poll() is None


if __name__ == "__main__":
    print("--- AI GAMER AGENT (THINKING EDITION) INITIALIZING ---")
    
    ai_player = AIPlayer(MODEL_NAME)
    game = GameRunner(GAME_COMMAND)
    
    print("\n--- GAME STARTING ---\n")
    time.sleep(2)

    while game.is_running():
        game_state = game.read_output()
        if not game_state: break

        # --- MODIFIED: Get the AI's decision (both thought and action) ---
        ai_decision = ai_player.get_action(game_state)
        thought = ai_decision['thought']
        action = ai_decision['action']
        
        # --- MODIFIED: Display both the thought and the action ---
        print(f"\n🤔 AI THOUGHT: {thought}")
        print(f">>> AI chooses: {action}\n")

        game.send_input(action)
        time.sleep(AI_SPEED)

    print("\n--- GAME OVER ---")
    stdout, stderr = game.process.communicate()
    if stdout: print("Final STDOUT:\n", stdout)
    if stderr: print("Final STDERR:\n", stderr)