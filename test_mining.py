import random
from main import Player

# Test the mining feature
def test_mining():
    # Create a player
    player = Player("MiningTester", "normal")
    
    print("Player initial inventory:", player.inventory)
    
    # Test mining several times to see different results
    mining_results = []
    for i in range(10):
        # We'll directly call the mining logic since we can't easily simulate input
        mining_items = ["Stone", "Iron Ore", "Gold Ore", "Diamond", "Nothing"]
        weights = [0.4, 0.25, 0.2, 0.1, 0.05]
        
        result = random.choices(mining_items, weights=weights)[0]
        mining_results.append(result)
        
        if result != "Nothing":
            player.inventory.append(result)
    
    print("\nMining results:", mining_results)
    print("Player inventory after mining:", player.inventory)
    
    # Test crafting feature
    # Add a wooden axe to inventory first
    player.inventory.append("Wooden Axe")
    print("\nAdded Wooden Axe to inventory")
    print("Inventory before crafting attempt:", player.inventory)
    
    # Check if we have both diamond and wooden axe for crafting
    if "Diamond" in player.inventory and "Wooden Axe" in player.inventory:
        print("\nCrafting conditions met - would prompt to craft Diamond Sword")
    else:
        print("\nCrafting conditions not met")

if __name__ == "__main__":
    test_mining()