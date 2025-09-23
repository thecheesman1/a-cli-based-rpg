import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import Player

def test_auto_mine():
    # Create a player
    player = Player("TestPlayer", "normal")
    
    # Enable test mode
    player.test_mode = True
    
    # Start auto mining
    player.start_auto_mining()
    
    # Manually trigger mining rewards to test functionality
    # In test mode, the auto_mine function will stop after 3 intervals
    import time
    time.sleep(4)  # Wait for mining to complete
    
    # Check if coins were added
    print(f"Player coins after auto mining: {player.coins}")
    print(f"Mining intervals completed: {player.mining_intervals}")
    
    # Verify the auto mining worked
    if player.coins == 30 and player.mining_intervals == 3:
        print("Auto mining test PASSED")
        return True
    else:
        print("Auto mining test FAILED")
        return False

if __name__ == "__main__":
    test_auto_mine()