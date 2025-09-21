# CLI-Based RPG Game

Welcome to the CLI-Based RPG Game! This is a simple text-based adventure game that runs in your terminal.

## Features

- Character creation with customizable names
- Battle system with enemies (Goblins, Orcs, Dragons)
- Health management system
- Inventory tracking
- Multiple actions: explore, rest, attack, run, quit
- **Multiple game modes for varied difficulty levels**

## How to Play

1. Run the game with `python main.py`
2. Select your game mode:
   - Normal: Balanced difficulty
   - Easy: More health, stronger attacks, weaker enemies, better healing
   - Hardcore: Less health, weaker attacks, stronger enemies, no resting
3. Enter your character's name when prompted
4. Choose actions from the menu:
   - `explore`: Encounter random enemies
   - `rest`: Recover health points (not available in hardcore mode)
   - `quit`: Exit the game
5. During battles, choose to `attack` or `run`

## AI Player Mode

You can also watch an AI play the game using `python small_llm_play_game.py`

## Requirements

- Python 3.x

## Game Modes

### Normal Mode
The default balanced experience with standard player stats and enemy difficulty.

### Easy Mode
- Player starts with 150 HP (instead of 100)
- Player has increased attack (15) and defense (8)
- Enemies are weaker versions
- Resting heals more HP (15-35 instead of 10-25)

### Hardcore Mode
- Player starts with only 75 HP
- Player has reduced attack (8) and defense (3)
- Enemies are stronger versions
- **Resting is disabled entirely**
- Perfect for players seeking a challenge
