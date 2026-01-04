import random
from typing import List, Optional

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