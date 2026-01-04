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
    "Greater Health Potion": Item("Greater Health Potion", 60, "heal", 80),
    "Strength Potion": Item("Strength Potion", 100, "attack_boost", 5),
    "Iron Sword": Item("Iron Sword", 150, "attack_boost", 12),
    "Steel Sword": Item("Steel Sword", 400, "attack_boost", 25),
    "Diamond Sword": Item("Diamond Sword", 1000, "attack_boost", 60),
    "Godly Sword": Item("Godly Sword", 5000, "attack_boost", 150),
    "Wooden Axe": Item("Wooden Axe", 50, "attack_boost", 8),
    "Iron Axe": Item("Iron Axe", 200, "attack_boost", 15),
    "Shield": Item("Shield", 100, "defense_boost", 5),
    "Magic Staff": Item("Magic Staff", 500, "attack_boost", 35),
    "Enchanted Bow": Item("Enchanted Bow", 450, "attack_boost", 30),
    "Leather Armor": Item("Leather Armor", 150, "defense_boost", 8),
    "Chainmail Armor": Item("Chainmail Armor", 500, "defense_boost", 20),
    "Steel Armor": Item("Steel Armor", 1200, "defense_boost", 45),
    "Diamond Armor": Item("Diamond Armor", 3000, "defense_boost", 80),
    "Godly Armor": Item("Godly Armor", 8000, "defense_boost", 200)
}

RESOURCES = {
    "Stone": 2,
    "Coal": 5,
    "Iron Ore": 12,
    "Gold Ore": 30,
    "Emerald": 75,
    "Diamond": 150,
    "Obsidian": 300,
    "Mithril": 750
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
        self.max_health += 25
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