# CLI-Based RPG Game

import random
import json
import os
import time
import threading

class Player:
    def __init__(self, name, game_mode="normal", health=100, attack=10, defense=5, level=1, experience=0, coins=0):
        self.name = name
        self.game_mode = game_mode
        self.level = level
        self.experience = experience
        self.coins = coins
        
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
        self.auto_mining = False
        self.mining_thread = None
    
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
            "inventory": self.inventory,
            "level": self.level,
            "experience": self.experience,
            "coins": self.coins
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
            elif item == "Diamond Sword":
                self.attack += 25
                print(f"\nYou equipped a Diamond Sword! Attack increased by 25.")
            elif item == "Godly Sword":
                self.attack += 50
                print(f"\nYou equipped a Godly Sword! Attack increased by 50.")
            elif item == "Wooden Axe":
                self.attack += 8
                print(f"\nYou equipped a Wooden Axe! Attack increased by 8.")
            elif item == "Iron Axe":
                self.attack += 12
                print(f"\nYou equipped an Iron Axe! Attack increased by 12.")
            elif item == "Shield":
                self.defense += 5
                print(f"\nYou equipped a Shield! Defense increased by 5.")
        else:
            print(f"\nYou don't have a {item} in your inventory!")
    
    def mine(self):
        """Manual mining feature"""
        mining_results = ["Stone", "Iron Ore", "Gold Ore", "Diamond", "Nothing"]
        weights = [0.4, 0.25, 0.2, 0.1, 0.05]  # Probability weights
        
        result = random.choices(mining_results, weights=weights)[0]
        
        if result == "Nothing":
            print("\nYou didn't find anything while mining.")
        else:
            self.inventory.append(result)
            print(f"\nYou mined and found: {result}!")
            
            # Special case: if you find a diamond, you might be able to craft a diamond sword
            if result == "Diamond" and "Wooden Axe" in self.inventory:
                craft_choice = input("Would you like to craft a Diamond Sword? (y/n): ").lower()
                if craft_choice == "y":
                    # Remove the diamond and wooden axe
                    self.inventory.remove("Diamond")
                    self.inventory.remove("Wooden Axe")
                    self.inventory.append("Diamond Sword")
                    print("You crafted a Diamond Sword!")
    
    def auto_mine(self):
        """Auto mining feature that generates coins"""
        print("\nAuto mining started. You will gain 10 coins per minute.")
        print("Type 'stop mining' at any time to stop auto mining.")
        
        while self.auto_mining:
            time.sleep(60)  # Wait for 1 minute
            if self.auto_mining:  # Check again in case it was stopped during sleep
                self.coins += 10
                print(f"\n[Auto Mining] You've gained 10 coins! Total coins: {self.coins}")
    
    def start_auto_mining(self):
        """Start the auto mining thread"""
        if not self.auto_mining:
            self.auto_mining = True
            self.mining_thread = threading.Thread(target=self.auto_mine, daemon=True)
            self.mining_thread.start()
            print("\nAuto mining started successfully!")
        else:
            print("\nAuto mining is already running!")
    
    def stop_auto_mining(self):
        """Stop the auto mining thread"""
        if self.auto_mining:
            self.auto_mining = False
            print("\nAuto mining stopped.")
        else:
            print("\nAuto mining is not currently running!")
    
    def gain_experience(self, exp):
        """Gain experience and level up if enough experience is gained"""
        self.experience += exp
        exp_needed = self.level * 100  # Experience needed to level up
        
        if self.experience >= exp_needed:
            self.level_up()
    
    def level_up(self):
        """Level up the player, increasing stats"""
        self.level += 1
        self.experience = 0  # Reset experience after level up
        
        # Increase stats
        self.attack += 5
        self.defense += 3
        self.health += 20
        
        print(f"\nCongratulations! You've reached level {self.level}!")
        print("Your stats have increased!")


class Enemy:
    def __init__(self, name, health, attack, defense=0, level=1):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.level = level


def display_stats(player):
    print(f"\n{player.name}'s Stats:")
    print(f"Level: {player.level}")
    print(f"Experience: {player.experience}")
    print(f"Health: {player.health}")
    print(f"Attack: {player.attack}")
    print(f"Defense: {player.defense}")
    print(f"Coins: {player.coins}")
    print(f"Inventory: {', '.join(player.inventory) if player.inventory else 'Empty'}")
    print(f"Game Mode: {player.game_mode.capitalize()}")
    if player.auto_mining:
        print("Auto Mining: Active")
    else:
        print("Auto Mining: Inactive")


def create_enemy(game_mode="normal", player_level=1):
    # Adjust enemy difficulty based on game mode and player level
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
    
    # Select a random enemy
    enemy_data = random.choice(enemies)
    
    # Scale enemy stats based on player level
    scaled_health = enemy_data[1] + (player_level - 1) * 10
    scaled_attack = enemy_data[2] + (player_level - 1) * 3
    scaled_defense = enemy_data[3] + (player_level - 1) * 1
    
    return Enemy(enemy_data[0], scaled_health, scaled_attack, scaled_defense, player_level)


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
                
                # Gain experience based on enemy level
                exp_gained = enemy.level * 50
                player.gain_experience(exp_gained)
                print(f"You gained {exp_gained} experience points!")
                
                # Add a random item to inventory upon victory
                items = ["Health Potion", "Strength Potion", "Iron Sword", "Steel Sword", "Diamond Sword", "Godly Sword", "Wooden Axe", "Iron Axe", "Shield"]
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
        ("Diamond Sword", 500),
        ("Godly Sword", 1000),
        ("Wooden Axe", 30),
        ("Iron Axe", 150),
        ("Shield", 150)
    ]
    
    print(f"\nWelcome to the shop! You have {player.coins} coins.")
    print("Here's what's for sale:")
    
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
            
            # Check if player has enough coins
            if player.coins >= price:
                player.inventory.append(item)
                player.coins -= price
                print(f"\nYou bought a {item} for {price} coins!")
                print(f"Remaining coins: {player.coins}")
            else:
                print("\nYou don't have enough coins!")
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
            player_data["defense"],
            player_data.get("level", 1),  # Default to level 1 if not present
            player_data.get("experience", 0),  # Default to 0 experience if not present
            player_data.get("coins", 0)  # Default to 0 coins if not present
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
    
    print(f"\nWelcome, {player.name}! You are playing in {player.game_mode.capitalize()} mode.")
    
    # Main game loop
    while player.health > 0:
        print("\nWhat would you like to do?")
        print("1. Explore")
        print("2. Rest")
        print("3. View Stats")
        print("4. Shop")
        print("5. Mine")
        print("6. Start Auto Mining")
        print("7. Stop Auto Mining")
        print("8. Save Game")
        print("9. Quit")
        
        choice = input("> ").strip()
        
        if choice == "1":
            enemy = create_enemy(player.game_mode, player.level)
            result = battle(player, enemy)
            if result is False:  # Player was defeated
                break
        elif choice == "2":
            heal_amount = player.rest()
            if heal_amount > 0:
                print(f"\nYou rested and recovered {heal_amount} HP!")
        elif choice == "3":
            display_stats(player)
        elif choice == "4":
            shop(player)
        elif choice == "5":
            player.mine()
        elif choice == "6":
            player.start_auto_mining()
        elif choice == "7":
            player.stop_auto_mining()
        elif choice == "8":
            player.save()
        elif choice == "9":
            if player.auto_mining:
                player.stop_auto_mining()
            print("\nThanks for playing!")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 9.")
    
    if player.health <= 0:
        print("\nGame Over! Your character has died.")
        print("Thanks for playing!")

if __name__ == "__main__":
    main()