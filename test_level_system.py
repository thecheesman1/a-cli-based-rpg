import json
import os
from main import Player, Enemy, battle, create_enemy

# Test the level system
def test_level_system():
    # Create a player
    player = Player("LevelTester", "normal")
    
    # Display initial stats
    print("Initial player stats:")
    print(f"Level: {player.level}")
    print(f"Experience: {player.experience}")
    print(f"Attack: {player.attack}")
    print(f"Defense: {player.defense}")
    print(f"Health: {player.health}")
    
    # Gain some experience
    player.gain_experience(50)
    print(f"\nAfter gaining 50 exp: Level {player.level}, Exp {player.experience}")
    
    # Gain enough experience to level up
    player.gain_experience(50)
    print(f"\nAfter gaining another 50 exp: Level {player.level}, Exp {player.experience}")
    
    # Check if player leveled up
    if player.level > 1:
        print("\nLevel up successful!")
        print(f"New stats - Attack: {player.attack}, Defense: {player.defense}, Health: {player.health}")
    else:
        print("\nLevel up failed.")
    
    # Test enemy scaling
    enemy = create_enemy("normal", player.level)
    print(f"\nEnemy stats at player level {player.level}: {enemy.name} - HP: {enemy.health}, Attack: {enemy.attack}, Defense: {enemy.defense}")

if __name__ == "__main__":
    test_level_system()