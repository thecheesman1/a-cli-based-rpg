import random
import json
import os
from typing import Optional, List
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
        
        self.ui.print_header("INVENTORY")
        unique_items = sorted(list(set(self.player.inventory)))
        item_list = []
        for i, item_name in enumerate(unique_items):
            count = self.player.inventory.count(item_name)
            item_list.append((i+1, item_name, count))
            self.ui.print_table_row([i+1, item_name, f"x{count}"], [4, 25, 5])
        
        try:
            choice = input("Select item # (or 'c' to cancel): ")
            if choice.lower() == 'c': return
            idx = int(choice) - 1
            item_name = unique_items[idx]
            
            item = ITEMS.get(item_name)
            if not item:
                if item_name in RESOURCES:
                    print("You can't use resources! Sell them at the shop.")
                else:
                    print("This item cannot be used.")
                return

            self.player.inventory.remove(item_name)
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
        shop_items = list(ITEMS.keys())
        self.ui.print_table_row(["#", "Item Name", "Price", "Effect"], [4, 25, 8, 15])
        print("-" * 55)
        for i, name in enumerate(shop_items):
            item = ITEMS[name]
            effect = f"+{item.bonus} {item.item_type.split('_')[0]}"
            self.ui.print_table_row([i+1, name, item.price, effect], [4, 25, 8, 15])
        
        print("\nS. Sell Resources")
        print("0. Exit")
        
        choice = input("Choice: ").upper()
        if choice == '0': return
        if choice == 'S': self.sell_resources(); return
        
        try:
            idx = int(choice) - 1
            item_name = shop_items[idx]
            item = ITEMS[item_name]
            
            qty_input = input(f"How many {item_name} do you want to buy? (default 1): ")
            qty = int(qty_input) if qty_input.strip() else 1
            if qty <= 0: return
            
            total_cost = item.price * qty
            if self.player.coins >= total_cost:
                self.player.coins -= total_cost
                for _ in range(qty):
                    self.player.inventory.append(item_name)
                print(f"{Colors.GREEN}Purchased {qty}x {item_name}!{Colors.ENDC}")
            else: 
                print(f"{Colors.FAIL}Insufficient coins!{Colors.ENDC}")
        except:
            print("Invalid input.")

    def sell_resources(self):
        player_resources = [r for r in self.player.inventory if r in RESOURCES]
        if not player_resources:
            print("No resources to sell!")
            return
            
        self.ui.print_header("SELL RESOURCES")
        counts = {r: self.player.inventory.count(r) for r in RESOURCES if self.player.inventory.count(r) > 0}
        active_resources = sorted(list(counts.keys()))
        
        self.ui.print_table_row(["#", "Resource", "Price", "Owned"], [4, 15, 8, 8])
        for i, r in enumerate(active_resources):
            self.ui.print_table_row([i+1, r, RESOURCES[r], counts[r]], [4, 15, 8, 8])
        
        print("\nA. Sell ALL resources")
        choice = input("Select resource # or 'A' (or 'c' to cancel): ").upper()
        if choice == 'C': return

        if choice == 'A':
            total_gain = 0
            # Efficiently clear resources
            new_inventory = []
            for item in self.player.inventory:
                if item in RESOURCES:
                    total_gain += RESOURCES[item]
                else:
                    new_inventory.append(item)
            self.player.inventory = new_inventory
            self.player.coins += total_gain
            print(f"{Colors.GREEN}Sold all resources for {total_gain} coins!{Colors.ENDC}")
            return

        try:
            idx = int(choice) - 1
            r_name = active_resources[idx]
            
            qty_input = input(f"How many {r_name} to sell? (max {counts[r_name]}): ")
            qty = int(qty_input) if qty_input.strip() else 1
            qty = min(qty, counts[r_name])
            
            if qty <= 0: return
            
            gain = RESOURCES[r_name] * qty
            for _ in range(qty):
                self.player.inventory.remove(r_name)
            self.player.coins += gain
            print(f"{Colors.GREEN}Sold {qty}x {r_name} for {gain} coins.{Colors.ENDC}")
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