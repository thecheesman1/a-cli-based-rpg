import os
from models import Colors, Player

class GameUI:
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def print_header(text: str):
        print(f"\n{Colors.HEADER}{'='*20} {text.upper()} {'='*20}{Colors.ENDC}")

    @staticmethod
    def print_status(player: Player):
        print(f"\n{Colors.CYAN}{Colors.BOLD}--- {player.name} ---{Colors.ENDC}")
        health_bar = GameUI.get_health_bar(player.health, player.max_health)
        print(f"{Colors.GREEN}HP:    [{health_bar}] {player.health}/{player.max_health}{Colors.ENDC}")
        print(f"{Colors.WARNING}Level: {player.level:<3} | EXP: {player.experience}/{player.level*100}{Colors.ENDC}")
        print(f"{Colors.BLUE}Coins: {player.coins}{Colors.ENDC}")
        print(f"{Colors.CYAN}ATK:   {player.attack:<3} | DEF: {player.defense}{Colors.ENDC}")

    @staticmethod
    def get_health_bar(current, max_val, length=20):
        percent = max(0, min(1, current / max_val))
        filled = int(length * percent)
        return "#" * filled + "-" * (length - filled)

    @staticmethod
    def print_table_row(cols: list, widths: list):
        row = "" 
        for col, width in zip(cols, widths):
            row += f"{str(col):<{width}} | "
        print(row[:-3])