# CLI-Based RPG Game

import random

class Player:
    def __init__(self, name):
        self.name = name
        self.health = 100
        self.attack = 10
        self.defense = 5
        self.inventory = []
    
    def rest(self):
        """Rest to regain health"""
        heal_amount = random.randint(10, 25)
        self.health = min(100, self.health + heal_amount)  # Cap health at 100
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

def create_enemy():
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

def main():
    print("Welcome to the CLI-Based RPG Game!")
    name = input("Enter your character's name: ")
    player = Player(name)
    
    print(f"\nHello, {player.name}! Your adventure begins now.")
    
    while player.health > 0:
        display_stats(player)
        
        action = input("\nWhat would you like to do? (explore/rest/quit): ").lower()
        
        if action == "explore":
            enemy = create_enemy()
            result = battle(player, enemy)
            
            if result is False:
                break
        
        elif action == "rest":
            heal_amount = player.rest()
            print(f"\nYou rest and regain {heal_amount} health. Your health is now {player.health}.")
        
        elif action == "quit":
            print("\nThanks for playing!")
            break
        
        else:
            print("\nInvalid action. Please choose 'explore', 'rest' or 'quit'.")
    
    if player.health <= 0:
        print("\nGame Over!")

if __name__ == "__main__":
    main()
