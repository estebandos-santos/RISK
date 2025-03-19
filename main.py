import pygame
import random
from territories import territories  # Import territories from territories.py

pygame.init()

# Window settings
WIDTH, HEIGHT = 800, 700
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RISK - My first game")

# Load the game map
game_map = pygame.image.load("img/maprisk.png")
color_map = pygame.image.load("img/mapcolor.png")

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
army_distribution = {2: 40, 3: 35, 4: 30, 5: 25, 6: 20}
num_players = len(players)
starting_armies =army_distribution.get(num_players, 20)

# Initialize player data
player_armies = {player: starting_armies for player in players}
player_territories = {player: [] for player in players}

# Shuffle and assign territories randomly to players
territoy_list = list(territories.keys())
random.shuffle(territoy_list)


for i, territory_color in enumerate(territoy_list):
    player = players[i % num_players]
    player_territories[player].append(territory_color)
    territories[territory_color]["owner"] = player

# Ensure each territory has at least 1 army at the beginning
for player, terr_list in player_territories.items():
    for terr in terr_list:
        territories[terr]["armies"] = 1
        player_armies[player] -= 1

# Initialize game variables
current_player_index = 0
current_player = players[current_player_index]
placement_phase = True # This controls the placement phase
attack_phase = False # This controls the attack phase
reinforcement_phase = False # This controls the reinforcement phase
move_phase = False # This controls the move phase
selected_attacker = None # Store the selected attacking territory
selected_defender = None # Store the selected defending territory
attack_dice = [] # Store the dice rolls for the attacker
defense_dice = [] # Store the dice rolls for the defender

pygame.font.init()
font = pygame.font.SysFont(None, 24)
    

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


# Debug : Print assigned territories and armies
for player, terr_list in player_territories.items():
    print(f"{player} owns : {[territories[t]["name"] for t in terr_list]}")
    print(f"{player} starts with {player_armies[player]} armies left to place")

## Function to calculate reinforcements
def calculate_reinforcements(player):
    num_territories = len(player_territories[player])
    reinforcements = max(3, num_territories // 3)
    return reinforcements

# Draw "End Turn" button
def draw_end_turn_button():
    button_rect = pygame.Rect(650, 600, 100, 40)
    pygame.draw.rect(window, BLUE, button_rect)
    draw_text("End Turn", 675, 610, WHITE)
    return button_rect

# Function to draw text
def draw_text(text, x, y, color=BLACK):
    text_surface = font.render(text, True, color)
    window.blit(text_surface, (x, y))

# Debug: Print assigned territories and armies
for player, terr_list in player_territories.items():
    print(f"{player} ownd : {[territories[t]['name'] for t in terr_list]}")
    print(f"{player} starts with {player_armies[player]} armies left to place")

# Game loop
running = True
while running:
    window.fill((60, 179, 113))
    window.blit(game_map, (0, 0))

    # Draw territories
    for color, data in territories.items():
        position = data["position"]
        owner = data["owner"]

        if owner:
            pygame.draw.circle(window, player_colors[owner], position, 7)
    
    # Number of armies on territories
    for color, data in territories.items():
        position = data["position"]
        armies = data["armies"]
        text_surface = font.render(str(armies), True, (255, 255, 255))
        window.blit(text_surface, position)

    
    pygame.display.update()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Detect mouse click
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            if 0 <= mouse_x < color_map.get_width() and 0 <= mouse_y < color_map.get_height():
                clicked_color = tuple(color_map.get_at((mouse_x, mouse_y))[:3])
            else:
                clicked_color = None
            
            if clicked_color and clicked_color in territories:
                 selected_territory = territories[clicked_color]

            # Bouton "End Turn"
            if 0 <= mouse_x <= 750 and 600 <= mouse_y <= 640:
                if placement_phase:
                    print("You need to place all yours armies")
                elif reinforcement_phase:
                    reinforcement_phase = False
                    attack_phase = True
                    print(f"{current_player} is on attack phase.")
                elif attack_phase:
                    attack_phase = False
                    move_phase = True
                    print(f"{current_player} is on movement phase.")
                elif move_phase:
                    move_phase = False
                    reinforcement_phase = True
                    current_player_index = (current_player_index + 1) % num_players
                    current_player = players[current_player_index]
                    player_armies[current_player] += calculate_reinforcements(current_player)
                    print(f"{current_player} start his turn with {player_armies[current_player]} more armies.")


            
            # PHASE 0 : INITIAL PLACEMENT PHASE
            elif placement_phase and clicked_color in territories:
                if territories[clicked_color]["owner"] == current_player and player_armies[current_player] > 0:
                    territories[clicked_color]["armies"] += 1
                    player_armies[current_player] -= 1
                    print(f"{current_player} put an army on {territories[clicked_color]['name']}")

                        # Switch to the next player
                    current_player_index = (current_player_index + 1) % num_players
                    current_player = players[current_player_index]

                    if all(army == 0 for army in player_armies.values()):
                        placement_phase = False
                        reinforcement_phase = True
                        print("No more placement. Start of reinforcement phase.")

            # PHASE 1 : REINFORCEMENT PHASE
            elif reinforcement_phase and clicked_color in territories:
                if territories[clicked_color]["owner"] == current_player and player_armies[current_player] > 0:
                    territories[clicked_color]["armies"] += 1
                    player_armies[current_player] -= 1
                    print(f"{current_player} reinforce {territories[clicked_color]['name']} with one army")
            
            # PHASE 2 : ATTACK PHASE
            elif attack_phase and clicked_color in territories:
                selected_territory = territories[clicked_color]
                print(f"Clicked on {selected_territory['name']} owned by {selected_territory['owner']}")

                if selected_territory["owner"] == current_player:
                    selected_attacker = selected_territory
                    print(f"{current_player} select {selected_attacker['name']} to attack.")

                elif selected_attacker and selected_territory["owner"] != current_player:
                    selected_defender = selected_territory
                    print(f"{current_player} want to attack {selected_defender['name']} to {selected_attacker['name']}.")

                # Selecting DEFENDER
                elif selected_attacker and selected_territory["owner"] != current_player:
                    selected_defender = selected_territory
                    print(f"{current_player} wants to attack {selected_defender['name']} from {selected_attacker['name']}") 

                    # Validate attack adjency
                    if selected_defender["name"] in selected_attacker["adjacent"]:
                        print(f"✅ Attack Validated: {selected_attacker['name']} → {selected_defender['name']}")

                        # Dice roll
                        if selected_attacker["armies"] > 1:
                            attack_dice = sorted([random.randint(1, 6) for _ in range(min(3, selected_attacker["armies"] - 1))], reverse=True)
                            defense_dice = sorted([random.randint(1, 6) for _ in range(min(2, selected_defender["armies"]))], reverse=True)

                            print(f"{current_player} rolled {attack_dice}, {selected_defender['owner']} rolled {defense_dice}")

                            # Compare dice rolls
                            for i in range(min(len(attack_dice), len(defense_dice))):
                                if attack_dice[i] > defense_dice[i]:
                                    selected_defender["armies"] -= 1
                                else:
                                    selected_attacker["armies"] -= 1

                            # If defense has no more armies, the attacker wins
                            if selected_defender["armies"] == 0:
                                print(f"{current_player} conquered {selected_defender['name']} from {selected_defender['owner']}")
                                selected_defender["owner"] = current_player
                                selected_defender["armies"] = selected_attacker["armies"] - 1
                                selected_attacker["armies"] = 1

                            # Reset the selected territories
                            selected_attacker = None
                            selected_defender = None

                        else:
                            print("Attack not possible! You need at least 2 armies to attack")
                            selected_defender = None   

           

    # Fill Background
    window.fill((60, 179, 113))
    window.blit(game_map, (0, 0))

    # Draw a colored circle on each territory to represent the owner
    for color, data in territories.items():
        position = data["position"]
        owner = data["owner"]

        if owner:
            pygame.draw.circle(window, player_colors[owner], position, 7)

    # Display the number of armies on each territory
    for color, data in territories.items():
        position = data["position"]
        armies = data["armies"]

        # Render the army count
        text_surface = font.render(str(armies), True, (255,255, 255))
        window.blit(text_surface, position)

    # Draw the dice results
    draw_dice_results()

    # Draw End Turn button
    end_turn_butto_rect = draw_end_turn_button()

    # Update Screen
    pygame.display.update()

# Quit pygame properly
pygame.quit()


