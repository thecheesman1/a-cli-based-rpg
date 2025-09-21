# CLI-Based RPG Game

import random

class Player:
    def __init__(self, name, game_mode="normal"):
        self.name = name
        self.game_mode = game_mode
        
        # Set stats based on game mode
        if game_mode == "easy":
            self.health = 150
            self.attack = 15
            self.defense = 8
        elif game_mode == "hardcore":
            self.health = 75
            self.attack = 8
            self.defense = 3
        else:  # normal mode
            self.health = 100
            self.attack = 10
            self.defense = 5
            
        self.inventory = []
    
    def rest(self):
        """Rest to regain health"""
        if self.game_mode == "easy":
            heal_amount = random.randint(15, 35)
        elif self.game_mode == "hardcore":
            print("\nResting is disabled in hardcore mode!")
            return 0
        else:  # normal mode
            heal_amount = random.randint(10, 25)
        
        self.health = min(100 if self.game_mode == "normal" else 150 if self.game_mode == "easy" else 75, self.health + heal_amount)  # Cap health based on mode
        return heal_amount

class Enemy:
    def __init__(self, name, health, attack, defense=0):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense

def display_stats(player):
    print(f"\n{player.name}'s Stats:")
    print(f"Health: {player.health}")
    print(f"Attack: {player.attack}")
    print(f"Defense: {player.defense}")
    print(f"Inventory: {', '.join(player.inventory) if player.inventory else 'Empty'}")
    print(f"Game Mode: {player.game_mode.capitalize()}")

def create_enemy(game_mode="normal"):
    # Adjust enemy difficulty based on game mode
    if game_mode == "easy":
        enemies = [
            ("Weak Goblin", 20, 6, 1),
            ("Young Orc", 35, 8, 3),
            ("Baby Dragon", 70, 15, 7)
        ]
    elif game_mode == "hardcore":
        enemies = [
            ("Goblin Champion", 40, 12, 4),
            ("Orc Warrior", 70, 18, 8),
            ("Ancient Dragon", 150, 30, 15)
        ]
    else:  # normal mode
        enemies = [
            ("Goblin", 30, 8, 2),
            ("Orc", 50, 12, 5),
            ("Dragon", 100, 20, 10)
        ]
    
    enemy_data = random.choice(enemies)
    return Enemy(enemy_data[0], enemy_data[1], enemy_data[2], enemy_data[3])

def battle(player, enemy):
    print(f"\nA wild {enemy.name} appears!")
    
    while player.health > 0 and enemy.health > 0:
        print(f"\n{player.name}: {player.health} HP")
        print(f"{enemy.name}: {enemy.health} HP")
        
        action = input("\nWhat will you do? (attack/run): ").lower()
        
        if action == "attack":
            damage = max(0, player.attack - enemy.defense + random.randint(-5, 5))
            enemy.health -= damage
            print(f"\nYou hit the {enemy.name} for {damage} damage!")
            
            if enemy.health <= 0:
                print(f"\nYou defeated the {enemy.name}!")
                return True
            
            enemy_damage = max(0, enemy.attack - player.defense + random.randint(-3, 3))
            player.health -= enemy_damage
            print(f"The {enemy.name} hits you for {enemy_damage} damage!")
            
            if player.health <= 0:
                print("\nYou have been defeated!")
                return False
        
        elif action == "run":
            print("\nYou run away safely.")
            return None
        
        else:
            print("\nInvalid action. Please choose 'attack' or 'run'.")

def select_game_mode():
    """Allow player to select game mode"""
    print("\nSelect Game Mode:")
    print("1. Normal (balanced difficulty)")
    print("2. Easy (more health, stronger attacks, weaker enemies, better healing)")
    print("3. Hardcore (less health, weaker attacks, stronger enemies, no resting)")
    
    while True:
        choice = input("\nEnter your choice (1/2/3): ").strip()
        
        if choice == "1":
            return "normal"
        elif choice == "2":
            return "easy"
        elif choice == "3":
            return "hardcore"
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

def main():
    print("Welcome to the CLI-Based RPG Game!")
    
    # Select game mode
    game_mode = select_game_mode()
    
    name = input("Enter your character's name: ")
    player = Player(name, game_mode)
    
    print(f"\nHello, {player.name}! Your {game_mode} mode adventure begins now.")
    
    while player.health > 0:
        display_stats(player)
        
        # Adjust available actions based on game mode
        if game_mode == "hardcore":
            action = input("\nWhat would you like to do? (explore/quit): ").lower()
        else:
            action = input("\nWhat would you like to do? (explore/rest/quit): ").lower()
        
        if action == "explore":
            enemy = create_enemy(game_mode)
            result = battle(player, enemy)
            
            if result is False:
                break
        
        elif action == "rest" and game_mode != "hardcore":
            heal_amount = player.rest()
            if game_mode != "hardcore":  # Only show rest message if resting is allowed
                print(f"\nYou rest and regain {heal_amount} health. Your health is now {player.health}.")
        
        elif action == "quit":
            print("\nThanks for playing!")
            break
        
        else:
            if game_mode == "hardcore" and action == "rest":
                print("\nResting is disabled in hardcore mode!")
            else:
                print("\nInvalid action. Please choose a valid option.")
    
    if player.health <= 0:
        print("\nGame Over!")

if __name__ == "__main__":
    main()
