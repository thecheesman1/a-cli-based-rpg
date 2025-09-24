from main import Player

def test_use_item():
    # Create a player
    player = Player("TestPlayer", "normal")
    
    # Add items to inventory
    player.inventory = ["Health Potion", "Strength Potion", "Iron Sword", "Shield"]
    
    # Test using a health potion (capped at 100 HP in normal mode)
    initial_health = player.health
    player.use_item("Health Potion")
    expected_health = min(100, initial_health + 30)
    assert player.health == expected_health, f"Expected {expected_health}, got {player.health}"
    
    # Test using a strength potion
    initial_attack = player.attack
    player.use_item("Strength Potion")
    assert player.attack == initial_attack + 5, f"Expected {initial_attack + 5}, got {player.attack}"
    
    # Test using an iron sword
    initial_attack = player.attack
    player.use_item("Iron Sword")
    assert player.attack == initial_attack + 10, f"Expected {initial_attack + 10}, got {player.attack}"
    
    # Test using a shield
    initial_defense = player.defense
    player.use_item("Shield")
    assert player.defense == initial_defense + 5, f"Expected {initial_defense + 5}, got {player.defense}"
    
    # Test using an item not in inventory
    initial_health = player.health
    player.use_item("Nonexistent Item")  # Should not be in inventory
    assert player.health == initial_health, f"Expected {initial_health}, got {player.health}"
    
    print("All tests passed!")

if __name__ == "__main__":
    test_use_item()