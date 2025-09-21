import subprocess
import time
from openai import OpenAI

# --- CONFIGURATION ---
MODEL_NAME = "gemma:2b"  # The Ollama model you want to use
GAME_COMMAND = "python main.py" # The command to start the RPG game
AI_SPEED = 0.5 # Seconds to wait between AI actions, for watchability

class AIPlayer:
    """The AI's 'brain'. It now has a short-term memory."""

    def __init__(self, model_name):
        # Point the OpenAI client to your LM Studio server
        self.client = OpenAI(
            base_url='http://192.168.1.117:1234/v1',
            api_key='lm-studio', # can be anything
        )
        # We don't need to specify the model name here, as it's determined
        # by the model you've loaded in LM Studio.
        self.model = "local-model" # A placeholder name
        
        # The system prompt is now more direct, as the history will provide context
        self.system_prompt = """
You are a strategic AI playing a text-based RPG. Your goal is to survive as long as possible.
Analyze the recent history and the current game state to make the most logical move.
First, explain your reasoning in a 'Thought' line.
Then, on a new line, state the single command to execute.

Your response MUST be in this exact two-line format:
Thought: [Your reasoning here]
[command]

The command MUST be one of the following: 'explore', 'rest', 'attack', 'run', 'quit'
"""

    def get_action(self, history: list) -> dict: # Takes a list of messages
        """Gets a thought and action from the LLM based on conversation history."""
        try:
            # The history is now the main context
            messages = [{"role": "system", "content": self.system_prompt}] + history
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=100 # More tokens to allow for a thought
            )
            raw_response = response.choices[0].message.content.strip()
            
            # Parse the AI's two-line response
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

    while game.is_running():
        # 1. Read the state of the game
        game_state = game.read_output()
        if not game_state: # If there's no output, the game has probably ended
            break
        
        # 2. Add the game's output to the history
        conversation_history.append({"role": "user", "content": game_state})

        # 3. Keep the history to a manageable size (e.g., last 5 exchanges)
        # An exchange is 2 messages (user + assistant), so we keep 10 messages total.
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]

        # 4. Get the AI's next move based on the history
        ai_decision = ai_player.get_action(conversation_history)
        thought = ai_decision['thought']
        action = ai_decision['action']
        
        # 5. Display both the thought and the action
        print(f"\n🤔 AI THOUGHT: {thought}")
        print(f">>> AI chooses: {action}\n")

        # 6. Add the AI's full response to the history for self-reflection
        ai_full_response = f"Thought: {thought}\n{action}"
        conversation_history.append({"role": "assistant", "content": ai_full_response})
        
        # 7. Send the chosen action to the game
        game.send_input(action)

        # 8. Wait a moment so we can watch
        time.sleep(AI_SPEED)

    print("\n--- GAME OVER ---")
    # Capture any final error messages
    stdout, stderr = game.process.communicate()
    if stdout: print("Final STDOUT:\n", stdout)
    if stderr: print("Final STDERR:\n", stderr)