# CLI-Based RPG Game

Welcome to the CLI-Based RPG Game! This is a simple text-based adventure game that runs in your terminal.

## Features

- Character creation with customizable names
- Battle system with enemies (Goblins, Orcs, Dragons)
- Health management system
- Inventory tracking with items and equipment
- Leveling system with experience points
- Mining feature to find resources
- Shop system to purchase items
- Multiple actions: explore, rest, attack, run, quit, view stats, save game
- **Multiple game modes for varied difficulty levels**

## How to Play

1. Run the game with `python main.py`
2. Choose whether to load a saved game or create a new character
3. Select your game mode:
   - Normal: Balanced difficulty
   - Easy: More health, stronger attacks, weaker enemies, better healing
   - Hardcore: Less health, weaker attacks, stronger enemies, no resting
4. Enter your character's name when prompted
5. Choose actions from the menu:
   - `explore`: Encounter random enemies
   - `rest`: Recover health points (not available in hardcore mode)
   - `view stats`: Display your current character statistics
   - `shop`: Visit the shop to purchase items
   - `mine`: Mine for resources
   - `save game`: Save your current progress
   - `quit`: Exit the game
6. During battles, choose to `attack`, `run`, or `use item`

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

## Level System

- Gain experience points by defeating enemies
- Level up when you accumulate enough experience points
- Each level up increases your attack, defense, and maximum health
- Enemies scale in difficulty based on your level

## Mining System

- Find various resources including Stone, Iron Ore, Gold Ore, and Diamond
- Some items can be crafted together to create more powerful equipment
- Mining results are random with different probabilities for each resource

## Shop System

- Purchase items using your accumulated coins
- Available items include:
  - Health Potion: Restore health during battle
  - Strength Potion: Temporarily increase attack power
  - Swords (Iron, Steel, Diamond, Godly): Permanent attack boosts
  - Axes (Wooden, Iron): Permanent attack boosts
  - Shield: Permanent defense boost
