import random
from engine import GameController
from models import Player, RESOURCES, Colors
from ui import GameUI

def main():
    gc = GameController()
    ui = GameUI()
    
    ui.clear()
    print(f"{Colors.BOLD}{Colors.CYAN}--- ENHANCED RPG EXPERIENCE ---{Colors.ENDC}")
    
    if input("Continue previous adventure? (y/n): ").lower() == 'y':
        if not gc.load_game():
            print("No save found. Starting anew.")
            name = input("Character Name: ")
            mode = input("Mode (easy/normal/hardcore): ").lower()
            gc.player = Player(name, mode)
    else:
        name = input("Character Name: ")
        mode = input("Mode (easy/normal/hardcore): ").lower()
        gc.player = Player(name, mode)

    while gc.player.health > 0:
        ui.print_status(gc.player)
        print("\nWhat will you do?")
        print("1. Explore the Wilds")
        print("2. Visit the Shop")
        print("3. Go Mining")
        print("4. Save Progress")
        print("5. Quit Game")
        
        choice = input("> ")
        
        if choice == '1':
            if not gc.battle():
                print(f"{Colors.FAIL}Game Over, {gc.player.name}.{Colors.ENDC}")
                break
        elif choice == '2':
            gc.shop()
        elif choice == '3':
            ui.print_header("MINING")
            print("Digging for resources...")
            if random.random() < 0.7:
                res_list = list(RESOURCES.keys())
                # Weights for: Stone, Coal, Iron Ore, Gold Ore, Emerald, Diamond, Obsidian, Mithril
                weights = [40, 25, 15, 10, 5, 3, 1.5, 0.5]
                res = random.choices(res_list, weights=weights)[0]
                gc.player.inventory.append(res)
                print(f"{Colors.GREEN}Success! You found {res}.{Colors.ENDC}")
            else:
                print("You found nothing but dirt.")
        elif choice == '4':
            gc.save_game()
        elif choice == '5':
            print("Farewell, adventurer!")
            break

if __name__ == "__main__":
    main()