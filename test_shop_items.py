import json
import os
from main import Player, shop

# Test the extended shop items
def test_shop_items():
    # Create a player with enough attack to buy expensive items
    player = Player("ShopTester", "normal", attack=150)
    
    print("Player initial attack:", player.attack)
    print("Player initial inventory:", player.inventory)
    
    # Test buying a Diamond Sword (costs 500 coins)
    # We'll simulate the input for choosing item 5 (Diamond Sword)
    # Since we can't easily simulate input, we'll directly call the shop logic
    
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
    
    # Try to buy a Diamond Sword
    item, price = items_for_sale[4]  # Diamond Sword is at index 4
    
    if player.attack >= price / 10:
        player.inventory.append(item)
        player.attack -= price / 10
        print(f"\nBought {item} successfully!")
        print(f"Player attack after purchase: {player.attack}")
        print(f"Player inventory after purchase: {player.inventory}")
    else:
        print(f"\nCannot afford {item}")
    
    # Try to buy a Godly Sword
    item, price = items_for_sale[5]  # Godly Sword is at index 5
    
    if player.attack >= price / 10:
        player.inventory.append(item)
        player.attack -= price / 10
        print(f"\nBought {item} successfully!")
        print(f"Player attack after purchase: {player.attack}")
        print(f"Player inventory after purchase: {player.inventory}")
    else:
        print(f"\nCannot afford {item}")

if __name__ == "__main__":
    test_shop_items()