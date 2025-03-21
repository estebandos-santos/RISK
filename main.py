import pygame
import random
from territories import territories  # Import territories from territories.py
from territories import continents     # Import continents from continents.py
from rules import draw_rules         # Import rules from rules.py


pygame.init()

# Window settings
WIDTH, HEIGHT = 800, 700
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RISK - My first game")

# Load the game map
game_map = pygame.image.load("img/maprisk.png")
color_map = pygame.image.load("img/mapcolor.png")
# Load Button png
end_phase_img = pygame.image.load("img/next.png")
# Load Button rules
rules_img = pygame.image.load("img/rules.png")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
GRAY = (150, 150, 150)

font = pygame.font.SysFont(None, 32)

# Default players
players = ["Player 1", "Player 2"]
num_players = 2
max_players = 6
player_colors = {
    "Player 1": (255, 0, 0),
    "Player 2": (0, 255, 0),
    "Player 3": (0, 0, 255),
    "Player 4": (255, 255, 0),
    "Player 5": (255, 0, 255),
    "Player 6": (0, 255, 255)
}

# UI Elements
input_boxes = []
player_inputs = ["Player 1", "Player 2", "Player 3", "Player 4", "Player 5", "Player 6"]

def draw_text(text, x, y, color=BLACK):
    text_surface = font.render(text, True, color)
    window.blit(text_surface, (x, y))

def draw_buttons():
    pygame.draw.rect(window, GREEN if num_players > 2 else GRAY, (250, 500, 100, 40))
    pygame.draw.rect(window, RED if num_players < max_players else GRAY, (450, 500, 100, 40))
    pygame.draw.rect(window, BLUE, (350, 560, 100, 40))
    draw_text("-", 290, 510, WHITE)
    draw_text("+", 490, 510, WHITE)
    draw_text("Start", 380, 570, WHITE)

def main_menu():
    global num_players
    running = True
    active_box = None
    
    while running:
        window.fill(WHITE)
        draw_text("Select Number of Players:", 300, 200)
        draw_text(f"{num_players}", 390, 240)
        draw_buttons()
        
        for i in range(num_players):
            pygame.draw.rect(window, BLACK if active_box == i else GRAY, (300, 270 + i * 40, 200, 30), 2)
            draw_text(player_inputs[i], 310, 275 + i * 40)
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 250 <= x <= 350 and 500 <= y <= 540 and num_players > 2:
                    num_players -= 1
                elif 450 <= x <= 550 and 500 <= y <= 540 and num_players < max_players:
                    num_players += 1
                elif 350 <= x <= 450 and 560 <= y <= 600:
                    return player_inputs[:num_players]
                for i in range(num_players):
                    if 300 <= x <= 500 and 270 + i * 40 <= y <= 300 + i * 40:
                        active_box = i
                        break
                else:
                    active_box = None
            elif event.type == pygame.KEYDOWN and active_box is not None:
                if event.key == pygame.K_RETURN:
                    active_box = None
                elif event.key == pygame.K_BACKSPACE:
                    player_inputs[active_box] = player_inputs[active_box][:-1]
                else:
                    player_inputs[active_box] += event.unicode

# Scale button pass
scale_factor = 0.2
new_width = int(end_phase_img.get_width() * scale_factor)
new_height = int(end_phase_img.get_height() * scale_factor)
end_phase_img = pygame.transform.scale(end_phase_img, (new_width, new_height))

# Position button pass
margin = 10
button_x = WIDTH - new_width - margin 
button_y = HEIGHT - new_height - margin
end_phase_rect = pygame.Rect(button_x, button_y, new_width, new_height)

# Scale button rules
rules_img = pygame.transform.scale(rules_img, (50, 50))
rules_rect = rules_img.get_rect(topleft=(10, 10))

# Start the game after selection
selected_players = main_menu()
if selected_players:
    players = selected_players
    num_players = len(players)
    
    # Update player colors
    new_player_colors = {}
    available_colors = list(player_colors.values())
    for i, player in enumerate(players):
        if i < len(available_colors):
            new_player_colors[player] = available_colors[i]
        else:
            new_player_colors[player] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    player_colors = new_player_colors
else:
    pygame.quit()
    exit()

# Determine the number of starting armies for each player
army_distribution = {2: 25, 3: 35, 4: 30, 5: 25, 6: 20} #40 but 2:10 phase test
num_players = len(players)
starting_armies = army_distribution.get(num_players, 20)

# Initialize player data
player_armies = {player: starting_armies for player in players}
player_territories = {player: [] for player in players}

# Shuffle and assign territories randomly to players
territory_list = list(territories.keys())
random.shuffle(territory_list)

for i, territory_color in enumerate(territory_list):
    player = players[i % num_players]
    player_territories[player].append(territory_color)
    territories[territory_color]["owner"] = player

# Ensure each territory has at least 1 army at the beginning
for player, terr_list in player_territories.items():
    for terr in terr_list:
        territories[terr]["armies"] = 1
        player_armies[player] -= 1

# Initialize game variables for phases
current_player_index = 0
current_player = players[current_player_index]
placement_phase = True      # This controls the placement phase
attack_phase = False        # This controls the attack phase
reinforcement_phase = False # This controls the reinforcement phase
move_phase = False          # This controls the movement phase
movement_done = False       # This controls the movement phase

selected_attacker = None    # For attack phase
selected_defender = None    # For attack phase
selected_source = None       # For movement phase (source territory)
selected_destination = None  # For movement phase (destination territory)

attack_dice = []            # Store the dice rolls for the attacker
defense_dice = []           # Store the dice rolls for the defender

game_over = False          # Flag to indicate the game is over
pygame.font.init()
font = pygame.font.SysFont(None, 24)
    
# Function next turn button
def next_turn():
    global current_player_index, current_player, reinforcement_phase, attack_phase, move_phase, movement_done, running
    # Initialize the phase for new turn
    move_phase = False
    attack_phase = False
    reinforcement_phase = True
    movement_done = False
    # Move to the next player
    current_player_index = (current_player_index + 1) % num_players
    current_player = players[current_player_index]
    player_armies[current_player] += calculate_reinforcements(current_player)
    print(f"Turn passed. {current_player} starts with {player_armies[current_player]} armies.")
    # Check for victory
    winner = check_victory()
    if winner is not None:
        print(f"VICTORY ! {winner} wins the game!")
        running = False
    else:
        print(f"Turn passed. {current_player} starts with {player_armies[current_player]} armies.")

# Function to verify if two territories are adjacent
def is_reachable(source, destination, territories):
    owner = source["owner"]
    # Breadth-first search to find a path from source to destination
    visited = set()
    queue = [source["name"]]
    while queue:
        current = queue.pop(0)
        if current == destination["name"]:
            return True
        visited.add(current)
        # Looking for name of the current territory
        for terr in territories.values():
            if terr["name"] == current:
                for neighbor in terr["adjacent"]:
                    # Check if the neighbor is owned by the same player and has not been visited
                    for t in territories.values():
                        if t["name"] == neighbor and t["owner"] == owner and neighbor not in visited:
                            queue.append(neighbor)
                break
    return False


# Function to victory check
def check_victory():
    owner_counts = {}
    for terr in territories.values():
        owner = terr.get("owner")
        if owner: 
            owner_counts[owner] = owner_counts.get(owner, 0) + 1
    
    # if a plyaer owns all territories, he wins
    total_territories = len(territories)
    for owner, count in owner_counts.items():
        if count == total_territories:
            return owner
    return None


# Function to draw dice results
def draw_dice_results():
    dice_start_x = 300
    dice_y = 550

    # Attacker dice (red)
    for i, value in enumerate(attack_dice):
        pygame.draw.circle(window, (255, 0, 0), (dice_start_x + i * 40, dice_y), 15)
        text_surface = font.render(str(value), True, (255, 255, 255))
        window.blit(text_surface, (dice_start_x + i * 40 + 10, dice_y + 5))

    # Defender dice (blue)
    for i, value in enumerate(defense_dice):
        pygame.draw.circle(window, (0, 0, 255), (dice_start_x + i * 40, dice_y + 40), 15)
        text_surface = font.render(str(value), True, (255, 255, 255))
        window.blit(text_surface, (dice_start_x + i * 40 + 10, dice_y + 45))


# Function to calculate reinforcements
def calculate_reinforcements(player):
    num_territories = sum(1 for terr in territories.values() if terr["owner"] == player)
    base_reinforcements = max(3, num_territories // 3)

    # Check for continent bonuses
    bonus = 0
    bonus_messages = []
    for continent, info in continents.items():
        if all(any(t["name"] == terr_name and t["owner"] == player for t in territories.values())
            for terr_name in info["territories"]):
            bonus += info["bonus"]
            bonus_messages.append(f"Controlled {continent} for a bonus of {info['bonus']} armies")
    total_reinforcements = base_reinforcements + bonus
    if bonus_messages:
        print(f"{player} receives {total_reinforcements} armies ({base_reinforcements} base + {bonus} bonus)") 
    else:
        print(f"{player} receives {total_reinforcements} armies ({base_reinforcements} base, no continent bonus)")
 
    return total_reinforcements

# Draw "End Turn" button
def draw_end_turn_button():
    button_rect = pygame.Rect(650, 600, 100, 40)
    pygame.draw.rect(window, BLUE, button_rect)
    draw_text("End Turn", 675, 610, WHITE)
    return button_rect

# Debug : Print assigned territories and armies
for player, terr_list in player_territories.items():
    print(f"{player} owns : {[territories[t]['name'] for t in terr_list]}")
    print(f"{player} starts with {player_armies[player]} armies left to place")

# Debug: Print assigned territories and armies (version 2)
for player, terr_list in player_territories.items():
    print(f"{player} owns : {[territories[t]['name'] for t in terr_list]}")
    print(f"{player} starts with {player_armies[player]} armies left to place")

# Game loop
running = True
while running:
    # --- Event Handling ---
    for event in pygame.event.get():
        if game_over and event.type != pygame.QUIT:
            continue

        elif event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Check if the "Rules" button is clicked
            if rules_rect.collidepoint(event.pos):
                draw_rules(window, font)

            # Check if the "End Phase" button is clicked
            elif end_phase_rect.collidepoint(mouse_x, mouse_y):
                print(f"{current_player} attempts to end his turn.")
                if placement_phase:
                    if player_armies[current_player] > 0:
                        print(f"{current_player} still has {player_armies[current_player]} armies to place.")
                    else:
                        current_player_index = (current_player_index + 1) % num_players
                        current_player = players[current_player_index]
                        print(f"Turn passed. It's now {current_player}'s turn.")
                        if all(army == 0 for army in player_armies.values()):
                            placement_phase = False
                            reinforcement_phase = True
                            print("No more placements. Starting reinforcement phase.")                        
                elif reinforcement_phase:
                    if player_armies[current_player] > 0:
                        print(f"{current_player} still has {player_armies[current_player]} armies to place.")
                    else:
                        reinforcement_phase = False
                        attack_phase = True
                        print(f"{current_player} is in attack phase.")
                elif attack_phase:
                    attack_phase = False
                    move_phase = True
                    print(f"{current_player} is in movement phase.")
                elif move_phase:
                    next_turn()

            # Handle click on a territory using the color map
            elif 0 <= mouse_x < color_map.get_width() and 0 <= mouse_y < color_map.get_height():
                clicked_color = tuple(color_map.get_at((mouse_x, mouse_y))[:3])
                if clicked_color and clicked_color in territories:
                    territory = territories[clicked_color]

                    # PHASE 0: INITIAL PLACEMENT PHASE
                    if placement_phase:
                        if territory["owner"] == current_player and player_armies[current_player] > 0:
                            territory["armies"] += 1
                            player_armies[current_player] -= 1
                            print(f"{current_player} placed an army on {territory['name']}")
                            
                            # Move to the next player
                            current_player_index = (current_player_index + 1) % num_players
                            current_player = players[current_player_index]
                            if all(army == 0 for army in player_armies.values()):
                                placement_phase = False
                                reinforcement_phase = True
                                print("No more placements. Starting reinforcement phase.")

                    # PHASE 1: REINFORCEMENT PHASE
                    elif reinforcement_phase:
                        if territory["owner"] == current_player and player_armies[current_player] > 0:
                            territory["armies"] += 1
                            player_armies[current_player] -= 1
                            print(f"{current_player} reinforces {territory['name']} with one army")

                    # PHASE 2: ATTACK PHASE
                    elif attack_phase:
                        print(f"Clicked on {territory['name']} owned by {territory['owner']}")
                        if territory["owner"] == current_player:
                            selected_attacker = territory
                            print(f"{current_player} selects {selected_attacker['name']} to attack from.")
                        elif selected_attacker and territory["owner"] != current_player:
                            selected_defender = territory
                            print(f"{current_player} wants to attack {selected_defender['name']} from {selected_attacker['name']}")
                            
                            # Validate attack adjacency (check if the territories are adjacent)
                            if selected_defender["name"] in selected_attacker["adjacent"]:
                                print(f"✅ Attack Validated: {selected_attacker['name']} -> {selected_defender['name']}")
                                if selected_attacker["armies"] > 1:
                                    attack_dice = sorted([random.randint(1, 6) for _ in range(min(3, selected_attacker["armies"] - 1))], reverse=True)
                                    defense_dice = sorted([random.randint(1, 6) for _ in range(min(2, selected_defender["armies"]))], reverse=True)
                                    print(f"{current_player} rolled {attack_dice}, {selected_defender['owner']} rolled {defense_dice}")
                                    for i in range(min(len(attack_dice), len(defense_dice))):
                                        if attack_dice[i] > defense_dice[i]:
                                            selected_defender["armies"] -= 1
                                        else:
                                            selected_attacker["armies"] -= 1
                                    
                                    if selected_defender["armies"] == 0:
                                        print(f"{current_player} conquered {selected_defender['name']} from {selected_defender['owner']}")
                                        selected_defender["owner"] = current_player
                                        selected_defender["armies"] = selected_attacker["armies"] - 1
                                        selected_attacker["armies"] = 1

                                        # Check for victory
                                        winner = check_victory()
                                        if winner is not None:
                                            print(f"VICTORY ! {winner} wins the game!")
                                            game_over = True
                                    
                                        # Reset selections after the attack
                                        selected_attacker = None
                                        selected_defender = None
                                else:
                                    print("Attack not possible! You need at least 2 armies to attack.")
                                    selected_defender = None

                   # PHASE 3: Movement (Fortification)
                    elif move_phase:
                        if not movement_done:
                            if territory["owner"] == current_player:
                                if selected_source is None:
                                    if territory["armies"] > 1:
                                        selected_source = territory
                                        print(f"{current_player} selects {territory['name']} as the source for movement.")
                                    else:
                                        print("Not enough armies in this territory to move.")
                                elif selected_source is not None and territory != selected_source:
                                    if is_reachable(selected_source, territory, territories):
                                        selected_destination = territory
                                        armies_to_move = selected_source["armies"] - 1
                                        selected_destination["armies"] += armies_to_move
                                        selected_source["armies"] = 1
                                        print(f"{current_player} moves {armies_to_move} armies from {selected_source['name']} to {selected_destination['name']}.")
                                        movement_done = True  # One movement per turn
                                    else:
                                        print(f"{territory['name']} is not reachable from {selected_source['name']}.")
                                    selected_source = None
                                    selected_destination = None
                        else:
                            print("Movement already done this turn.")

    # Rendering Phase 
    window.fill((60, 179, 113))
    window.blit(game_map, (0, 0))
    
    # Draw territories
    for color, data in territories.items():
        position = data["position"]
        owner = data["owner"]
        if owner:
            pygame.draw.circle(window, player_colors[owner], position, 7)
    
    # Display the number of armies on each territory
    for color, data in territories.items():
        position = data["position"]
        armies = data["armies"]
        text_surface = font.render(str(armies), True, WHITE)
        window.blit(text_surface, position)
    
    # Draw dice results
    draw_dice_results()
    
    # Draw the "End Phase" button (drawn last to ensure it's on top)
    window.blit(end_phase_img, end_phase_rect.topleft)
    
    # Draw the "Rules" button
    window.blit(rules_img, rules_rect.topleft)

    if game_over:
        victory_text = font.render(f"VICTORY ! {winner} wins the game!", True, RED)
        window.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, HEIGHT // 2))
    # Update display
    pygame.display.update()
