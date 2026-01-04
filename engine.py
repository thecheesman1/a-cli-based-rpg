import random
import json
import os
from typing import Optional
from models import Player, Enemy, ITEMS, RESOURCES, Colors
from ui import GameUI

class GameController:
    def __init__(self):
        self.player: Optional[Player] = None
        self.ui = GameUI()

    def create_enemy(self):
        lvl = self.player.level
        mode = self.player.game_mode
        
        if mode == "easy":
            enemies = [("Slime", 20, 5, 1), ("Bat", 15, 6, 0)]
        elif mode == "hardcore":
            enemies = [("Demon Lord", 200, 40, 20), ("Death Knight", 150, 35, 15)]
        else:
            enemies = [("Goblin", 40, 12, 5), ("Orc", 60, 18, 8), ("Skeleton", 50, 15, 6)]
            
        name, h, a, d = random.choice(enemies)
        return Enemy(name, h + (lvl*10), a + (lvl*3), d + lvl, lvl)

    def battle(self):
        enemy = self.create_enemy()
        self.ui.print_header(f"ENCOUNTER: {enemy.name}")
        
        while enemy.health > 0 and self.player.health > 0:
            print(f"\n{enemy.name} HP: {enemy.health} | {self.player.name} HP: {self.player.health}")
            action = input("Actions: [A]ttack, [R]un, [I]tem: ").lower()
            
            if action == 'a':
                is_crit = random.random() < 0.15
                base_dmg = self.player.attack - enemy.defense
                dmg = max(1, base_dmg + random.randint(-2, 5))
                if is_crit:
                    dmg *= 2
                    print(f"{Colors.WARNING}{Colors.BOLD}CRITICAL HIT!{Colors.ENDC}")
                
                enemy.health -= dmg
                print(f"{Colors.GREEN}You dealt {dmg} damage!{Colors.ENDC}")
                
                if enemy.health > 0:
                    e_dmg = max(1, enemy.attack - self.player.defense + random.randint(-2, 2))
                    self.player.health -= e_dmg
                    print(f"{Colors.FAIL}{enemy.name} strikes back for {e_dmg}!{Colors.ENDC}")
            elif action == 'r':
                if random.random() > 0.3:
                    print("You managed to escape!")
                    return True
                print("Escape failed!")
            elif action == 'i':
                self.use_item_menu()

        if self.player.health <= 0:
            print(f"{Colors.FAIL}YOU HAVE BEEN DEFEATED!{Colors.ENDC}")
            return False
        
        exp_gain = enemy.level * 50
        coin_gain = enemy.level * 20
        print(f"{Colors.GREEN}Victory! Gained {exp_gain} EXP and {coin_gain} coins.{Colors.ENDC}")
        if self.player.gain_experience(exp_gain):
            print(f"{Colors.WARNING}LEVEL UP! You feel stronger.{Colors.ENDC}")
        self.player.coins += coin_gain
        return True

    def use_item_menu(self):
        if not self.player.inventory:
            print("Your inventory is empty!")
            return
        
        for i, item in enumerate(self.player.inventory):
            print(f"{i+1}. {item}")
        
        try:
            choice = input("Select item # (or 'c' to cancel): ")
            if choice.lower() == 'c': return
            idx = int(choice) - 1
            item_name = self.player.inventory.pop(idx)
            item = ITEMS.get(item_name)
            
            if item.item_type == "heal":
                self.player.health = min(self.player.max_health, self.player.health + item.bonus)
            elif item.item_type == "attack_boost":
                self.player.attack += item.bonus
            elif item.item_type == "defense_boost":
                self.player.defense += item.bonus
            print(f"{Colors.CYAN}Used {item_name}!{Colors.ENDC}")
        except:
            print("Invalid selection.")

    def shop(self):
        self.ui.print_header("VILLAGE SHOP")
        shop_items = list(ITEMS.keys())[:10]
        for i, name in enumerate(shop_items):
            print(f"{i+1}. {name:15} | {ITEMS[name].price:>4} coins")
        print("S. Sell Resources")
        
        choice = input("Choice (0 to exit): ").upper()
        if choice == '0': return
        if choice == 'S': self.sell_resources(); return
        
        try:
            idx = int(choice) - 1
            item_name = shop_items[idx]
            item = ITEMS[item_name]
            if self.player.coins >= item.price:
                self.player.coins -= item.price
                self.player.inventory.append(item_name)
                print(f"Purchased {item_name}!")
            else:
                print("Insufficient coins!")
        except:
            print("Invalid input.")

    def sell_resources(self):
        resources = [r for r in self.player.inventory if r in RESOURCES]
        if not resources:
            print("No resources to sell!")
            return
        for i, r in enumerate(resources):
            print(f"{i+1}. {r:10} | {RESOURCES[r]:>3} coins")
        try:
            idx = int(input("Select resource: ")) - 1
            r_name = resources[idx]
            self.player.inventory.remove(r_name)
            self.player.coins += RESOURCES[r_name]
            print(f"Sold {r_name} for {RESOURCES[r_name]} coins.")
        except:
            print("Invalid input.")

    def save_game(self):
        data = {
            "name": self.player.name, "mode": self.player.game_mode,
            "lvl": self.player.level, "exp": self.player.experience,
            "coins": self.player.coins, "inv": self.player.inventory,
            "hp": self.player.health, "atk": self.player.attack, "def": self.player.defense
        }
        with open(f"{self.player.name}_save.json", 'w') as f:
            json.dump(data, f)
        print("Progress saved.")

    def load_game(self):
        name = input("Enter character name: ")
        if os.path.exists(f"{name}_save.json"):
            with open(f"{name}_save.json", 'r') as f:
                d = json.load(f)
            self.player = Player(d['name'], d['mode'])
            self.player.level, self.player.experience = d['lvl'], d['exp']
            self.player.coins, self.player.inventory = d['coins'], d['inv']
            self.player.health, self.player.attack, self.player.defense = d['hp'], d['atk'], d['def']
            return True
        return False