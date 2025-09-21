# CLI-Based RPG Game

import random
import json
import os

class Player:
    def __init__(self, name, game_mode="normal", health=100, attack=10, defense=5):
        self.name = name
        self.game_mode = game_mode
        
        # Set stats based on game mode
        if game_mode == "easy":
            self.health = health if health is not None else 150
            self.attack = attack if attack is not None else 15
            self.defense = defense if defense is not None else 8
        elif game_mode == "hardcore":
            self.health = health if health is not None else 75
            self.attack = attack if attack is not None else 8
            self.defense = defense if defense is not None else 3
        else:  # normal mode
            self.health = health if health is not None else 100
            self.attack = attack if attack is not None else 10
            self.defense = defense if defense is not None else 5
            
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
    
    def save(self):
        """Save player data to a JSON file"""
        player_data = {
            "name": self.name,
            "game_mode": self.game_mode,
            "health": self.health,
            "attack": self.attack,
            "defense": self.defense,
            "inventory": self.inventory
        }
        
        filename = f"{self.name}_save.json"
        with open(filename, 'w') as f:
            json.dump(player_data, f)
        
        print(f"\nGame saved to {filename}!")
    
    def use_item(self, item):
        """Use an item from the inventory"""
        if item in self.inventory:
            self.inventory.remove(item)
            if item == "Health Potion":
                heal_amount = 30
                self.health = min(100 if self.game_mode == "normal" else 150 if self.game_mode == "easy" else 75, self.health + heal_amount)
                print(f"\nYou used a Health Potion and restored {heal_amount} HP!")
            elif item == "Strength Potion":
                self.attack += 5
                print(f"\nYou used a Strength Potion! Attack increased by 5.")
            elif item == "Iron Sword":
                self.attack += 10
                print(f"\nYou equipped an Iron Sword! Attack increased by 10.")
            elif item == "Steel Sword":
                self.attack += 15
                print(f"\nYou equipped a Steel Sword! Attack increased by 15.")
            elif item == "Shield":
                self.defense += 5
                print(f"\nYou equipped a Shield! Defense increased by 5.")
        else:
            print(f"\nYou don't have a {item} in your inventory!")

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
        
        action = input("\nWhat will you do? (attack/run/use item): ").lower()
        
        if action == "attack":
            damage = max(0, player.attack - enemy.defense + random.randint(-5, 5))
            enemy.health -= damage
            print(f"\nYou hit the {enemy.name} for {damage} damage!")
            
            if enemy.health <= 0:
                print(f"\nYou defeated the {enemy.name}!")
                # Add a random item to inventory upon victory
                items = ["Health Potion", "Strength Potion", "Iron Sword", "Steel Sword", "Shield"]
                if random.random() > 0.5:  # 50% chance to get an item
                    item = random.choice(items)
                    player.inventory.append(item)
                    print(f"You found a {item}!")
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
        
        elif action == "use item":
            if not player.inventory:
                print("\nYour inventory is empty!")
            else:
                print("\nInventory:")
                for i, item in enumerate(player.inventory):
                    print(f"{i+1}. {item}")
                
                try:
                    choice = int(input("\nWhich item would you like to use? (Enter number): "))
                    if 1 <= choice <= len(player.inventory):
                        item_to_use = player.inventory[choice-1]
                        player.use_item(item_to_use)
                    else:
                        print("\nInvalid choice!")
                except ValueError:
                    print("\nInvalid input!")
        
        else:
            print("\nInvalid action. Please choose 'attack', 'run', or 'use item'.")


def shop(player):
    """Visit the shop to buy items"""
    items_for_sale = [
        ("Health Potion", 20),
        ("Strength Potion", 50),
        ("Iron Sword", 100),
        ("Steel Sword", 200),
        ("Shield", 150)
    ]
    
    print("\nWelcome to the shop! Here's what's for sale:")
    
    # Display items and their prices
    for i, (item, price) in enumerate(items_for_sale):
        print(f"{i+1}. {item} - {price} coins")
    
    # Get player's choice
    try:
        choice = int(input("\nWhat would you like to buy? (Enter number, 0 to exit): "))
        
        if choice == 0:
            return
        
        if 1 <= choice <= len(items_for_sale):
            item, price = items_for_sale[choice-1]
            
            # Check if player has enough coins (we'll use a simple coin system)
            # For now, we'll just check if they can afford it based on their attack power
            # This is a simplified system - in a real game, you'd have a separate currency
            if player.attack >= price / 10:  # Simplified affordability check
                player.inventory.append(item)
                player.attack -= price / 10  # Deduct cost
                print(f"\nYou bought a {item}!")
            else:
                print("\nYou can't afford that item!")
        else:
            print("\nInvalid choice!")
    
    except ValueError:
        print("\nInvalid input!")


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


def load_game():
    """Load a saved game"""
    name = input("\nEnter your character's name to load: ").strip()
    filename = f"{name}_save.json"
    
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            player_data = json.load(f)
        
        player = Player(
            player_data["name"],
            player_data["game_mode"],
            player_data["health"],
            player_data["attack"],
            player_data["defense"]
        )
        player.inventory = player_data["inventory"]
        
        print(f"\nGame loaded successfully for {name}!")
        return player
    else:
        print(f"\nNo saved game found for {name}!")
        return None


def main():
    print("Welcome to the CLI-Based RPG Game!")
    
    # Ask if player wants to load a game
    load_choice = input("\nDo you want to load a saved game? (y/n): ").lower().strip()
    
    if load_choice == "y":
        player = load_game()
        if player is None:
            # If loading failed, create a new character
            game_mode = select_game_mode()
            name = input("\nEnter your character's name: ").strip()
            player = Player(name, game_mode)
    else:
        # Create a new character
        game_mode = select_game_mode()
        name = input("\nEnter your character's name: ").strip()
        player = Player(name, game_mode)
    
    print(f"\nWelcome, {player.name}! Your adventure begins...")
    
    while player.health > 0:
        display_stats(player)
        
        action = input("\nWhat would you like to do? (explore/rest/shop/save/quit): ").lower().strip()
        
        if action == "explore":
            enemy = create_enemy(player.game_mode)
            result = battle(player, enemy)
            
            if result is False:  # Player was defeated
                print("\nGame Over!")
                break
        
        elif action == "rest":
            heal_amount = player.rest()
            if heal_amount > 0:
                print(f"\nYou rested and recovered {heal_amount} HP.")
        
        elif action == "shop":
            shop(player)
        
        elif action == "save":
            player.save()
        
        elif action == "quit":
            print("\nThanks for playing!")
            break
        
        else:
            print("\nInvalid action. Please choose from the available options.")
    
    if player.health <= 0:
        print("\nYou have died. Game Over!")


if __name__ == "__main__":
    main()
