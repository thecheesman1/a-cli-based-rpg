import random
import json
import os
import time
import threading
from typing import Dict, List, Optional

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Item:
    def __init__(self, name: str, price: int, item_type: str, bonus: int):
        self.name = name
        self.price = price
        self.item_type = item_type
        self.bonus = bonus

ITEMS = {
    "Health Potion": Item("Health Potion", 20, "heal", 30),
    "Strength Potion": Item("Strength Potion", 50, "attack_boost", 5),
    "Iron Sword": Item("Iron Sword", 100, "attack_boost", 10),
    "Steel Sword": Item("Steel Sword", 200, "attack_boost", 15),
    "Diamond Sword": Item("Diamond Sword", 500, "attack_boost", 25),
    "Godly Sword": Item("Godly Sword", 1000, "attack_boost", 50),
    "Wooden Axe": Item("Wooden Axe", 30, "attack_boost", 8),
    "Iron Axe": Item("Iron Axe", 150, "attack_boost", 12),
    "Shield": Item("Shield", 150, "defense_boost", 5),
    "Magic Staff": Item("Magic Staff", 300, "attack_boost", 20),
    "Enchanted Bow": Item("Enchanted Bow", 250, "attack_boost", 18),
    "Leather Armor": Item("Leather Armor", 100, "defense_boost", 10),
    "Chainmail Armor": Item("Chainmail Armor", 200, "defense_boost", 20)
}

RESOURCES = {
    "Stone": 2,
    "Iron Ore": 5,
    "Gold Ore": 10,
    "Diamond": 50
}

class Player:
    def __init__(self, name: str, game_mode: str = "normal"):
        self.name = name
        self.game_mode = game_mode
        self.level = 1
        self.experience = 0
        self.coins = 0
        self.inventory: List[str] = []
        self.auto_mining = False
        
        if game_mode == "easy":
            self.max_health = 150
            self.attack = 15
            self.defense = 8
        elif game_mode == "hardcore":
            self.max_health = 75
            self.attack = 8
            self.defense = 3
        else:
            self.max_health = 100
            self.attack = 10
            self.defense = 5
            
        self.health = self.max_health

    def level_up(self):
        self.level += 1
        self.experience = 0
        self.attack += 5
        self.defense += 3
        self.max_health += 20
        self.health = self.max_health
        return True

    def gain_experience(self, exp: int):
        self.experience += exp
        if self.experience >= self.level * 100:
            return self.level_up()
        return False

class Enemy:
    def __init__(self, name: str, health: int, attack: int, defense: int, level: int):
        self.name = name
        self.health = health
        self.attack = attack
        self.defense = defense
        self.level = level

class GameUI:
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_header(text: str):
        print(f"\n{Colors.HEADER}{'='*10} {text} {'='*10}{Colors.ENDC}")

    @staticmethod
    def print_status(player: Player):
        print(f"\n{Colors.CYAN}{Colors.BOLD}{player.name}{Colors.ENDC} | "
              f"{Colors.GREEN}HP: {player.health}/{player.max_health}{Colors.ENDC} | "
              f"{Colors.WARNING}Level: {player.level}{Colors.ENDC} | "
              f"{Colors.BLUE}Coins: {player.coins}{Colors.ENDC}")

class GameController:
    def __init__(self):
        self.player: Optional[Player] = None
        self.ui = GameUI()

    def create_enemy(self):
        mode = self.player.game_mode
        lvl = self.player.level
        
        if mode == "easy":
            enemies = [("Slime", 20, 5, 1), ("Bat", 15, 6, 0), ("Weak Goblin", 30, 8, 2)]
        elif mode == "hardcore":
            enemies = [("Demon Lord", 200, 40, 20), ("Death Knight", 150, 35, 15), ("Void Stalker", 120, 45, 10)]
        else:
            enemies = [("Goblin", 40, 12, 5), ("Orc", 60, 18, 8), ("Skeleton", 50, 15, 6)]
            
        name, h, a, d = random.choice(enemies)
        return Enemy(name, h + (lvl*10), a + (lvl*3), d + lvl, lvl)

    def battle(self):
        enemy = self.create_enemy()
        self.ui.print_header(f"BATTLE: vs {enemy.name}")
        
        while enemy.health > 0 and self.player.health > 0:
            print(f"\nEnemy HP: {enemy.health} | Your HP: {self.player.health}")
            action = input("Actions: [A]ttack, [R]un, [I]tem: ").lower()
            
            if action == 'a':
                dmg = max(1, self.player.attack - enemy.defense + random.randint(-2, 5))
                enemy.health -= dmg
                print(f"{Colors.GREEN}You hit for {dmg}!{Colors.ENDC}")
                
                if enemy.health > 0:
                    e_dmg = max(1, enemy.attack - self.player.defense + random.randint(-2, 2))
                    self.player.health -= e_dmg
                    print(f"{Colors.FAIL}{enemy.name} hit you for {e_dmg}!{Colors.ENDC}")
            elif action == 'r':
                if random.random() > 0.3:
                    print("Escaped!")
                    return
                print("Failed to escape!")
            elif action == 'i':
                self.use_item_menu()

        if self.player.health <= 0:
            print(f"{Colors.FAIL}YOU DIED!{Colors.ENDC}")
            return False
        
        print(f"{Colors.GREEN}Victory! Gained {enemy.level * 50} EXP.{Colors.ENDC}")
        if self.player.gain_experience(enemy.level * 50):
            print(f"{Colors.WARNING}LEVEL UP!{Colors.ENDC}")
        self.player.coins += enemy.level * 20
        return True

    def use_item_menu(self):
        if not self.player.inventory:
            print("Inventory empty!")
            return
        for i, item in enumerate(self.player.inventory):
            print(f"{i+1}. {item}")
        try:
            idx = int(input("Select item #: ")) - 1
            item_name = self.player.inventory.pop(idx)
            item = ITEMS.get(item_name)
            if item.item_type == "heal":
                self.player.health = min(self.player.max_health, self.player.health + item.bonus)
            elif item.item_type == "attack_boost":
                self.player.attack += item.bonus
            elif item.item_type == "defense_boost":
                self.player.defense += item.bonus
            print(f"Used {item_name}!")
        except:
            print("Invalid selection.")

    def shop(self):
        self.ui.print_header("THE SHOP")
        print(f"Your Coins: {self.player.coins}")
        shop_items = list(ITEMS.keys())[:8]
        for i, name in enumerate(shop_items):
            print(f"{i+1}. {name} ({ITEMS[name].price} coins)")
        print("9. Sell Resources")
        
        try:
            choice = int(input("Choice (0 to exit): "))
            if choice == 0: return
            if choice == 9: self.sell_resources(); return
            
            item_name = shop_items[choice-1]
            item = ITEMS[item_name]
            if self.player.coins >= item.price:
                self.player.coins -= item.price
                self.player.inventory.append(item_name)
                print(f"Bought {item_name}!")
            else:
                print("Not enough coins!")
        except:
            print("Invalid input.")

    def sell_resources(self):
        resources = [r for r in self.player.inventory if r in RESOURCES]
        if not resources:
            print("No resources to sell!")
            return
        for i, r in enumerate(resources):
            print(f"{i+1}. {r} ({RESOURCES[r]} coins)")
        try:
            idx = int(input("Select to sell: ")) - 1
            r_name = resources[idx]
            self.player.inventory.remove(r_name)
            self.player.coins += RESOURCES[r_name]
            print(f"Sold {r_name}!")
        except:
            print("Invalid input.")

    def save_game(self):
        data = {
            "name": self.player.name,
            "mode": self.player.game_mode,
            "lvl": self.player.level,
            "exp": self.player.experience,
            "coins": self.player.coins,
            "inv": self.player.inventory,
            "hp": self.player.health,
            "atk": self.player.attack,
            "def": self.player.defense
        }
        with open(f"{self.player.name}_save.json", 'w') as f:
            json.dump(data, f)
        print("Game Saved!")

    def load_game(self):
        name = input("Enter name: ")
        if os.path.exists(f"{name}_save.json"):
            with open(f"{name}_save.json", 'r') as f:
                d = json.load(f)
            self.player = Player(d['name'], d['mode'])
            self.player.level = d['lvl']
            self.player.experience = d['exp']
            self.player.coins = d['coins']
            self.player.inventory = d['inv']
            self.player.health = d['hp']
            self.player.attack = d['atk']
            self.player.defense = d['def']
            return True
        return False

    def run(self):
        self.ui.clear()
        print(f"{Colors.BOLD}{Colors.BLUE}=== RPG REFACTORED ==={Colors.ENDC}")
        if input("Load game? (y/n): ").lower() == 'y':
            if not self.load_game():
                print("Load failed.")
                return
        else:
            name = input("Character Name: ")
            mode = input("Mode (easy/normal/hardcore): ").lower()
            self.player = Player(name, mode)

        while self.player.health > 0:
            self.ui.print_status(self.player)
            print("1. Explore  2. Shop  3. Mine  4. Save  5. Quit")
            choice = input("> ")
            
            if choice == '1':
                if not self.battle(): break
            elif choice == '2':
                self.shop()
            elif choice == '3':
                res = random.choices(list(RESOURCES.keys()) + ["Nothing"], weights=[0.4, 0.3, 0.2, 0.1, 0.5])[0]
                if res != "Nothing":
                    self.player.inventory.append(res)
                    print(f"Mined {res}!")
                else: print("Found nothing.")
            elif choice == '4':
                self.save_game()
            elif choice == '5':
                break
        
        print("Game Over.")

if __name__ == "__main__":
    GameController().run()