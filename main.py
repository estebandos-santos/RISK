import pygame
import random
from territories import territories # Import territories from territories.py


pygame.init()


# Window settings
window = pygame.display.set_mode((800, 700)) #800,534 size of the map
pygame.display.set_caption("RISK - My first game")

# Load the game map
game_map = pygame.image.load("img/maprisk.png")
# Hide the hidden color map
color_map = pygame.image.load("img/mapcolor.png")

# Variable to store the last click position
#last_click_pos = None

#Definie players
players = ["Player 1", "Player 2"] #"Player 3", "Player 4", "Player 5", "Player 6"]
player_colors = {
    "Player 1": (255, 0, 0), # Red
    "Player 2": (0, 255, 0), # Green
    "Player 3": (0, 0, 255), # Blue
    "Player 4": (255, 255, 0), # Yellow
    "Player 5": (255, 0, 255), # Purple
    "Player 6": (0, 255, 255) # Cyan
}

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
current_player = players[0]
selected_attacker = None # Store the selected attacking territory
selected_defender = None # Store the selected defending territory
placement_phase = True # This controls the placement phase
attack_dice = [] # Store the dice rolls for the attacker
defense_dice = [] # Store the dice rolls for the defender
pygame.font.init()
font = pygame.font.SysFont(None, 24)
    

# Funcion to draw dice results
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


# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Detect mouse click
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            clicked_color = tuple(color_map.get_at((mouse_x, mouse_y))[:3])

            
            # PHASE 1 : PLACEMENT PHASE
            if placement_phase:
                if clicked_color in territories and territories[clicked_color]["owner"] == current_player:
                    if player_armies[current_player] > 0:
                        territories[clicked_color]["armies"] += 1
                        player_armies[current_player] -= 1
                        print(f"{current_player} placed an army on {territories[clicked_color]['name']}")

                        # Switch to the next player
                        current_player = players[(players.index(current_player) + 1) % num_players]
                        print(f"Now it's {current_player}'s turn to place an army")
                    if all(army == 0 for army in player_armies.values()):
                        placement_phase = False
                        print("Placement phase is over. Let's start attacking!")

            # PHASE 2 : ATTACK PHASE
            else:

                # If clicked on a valid territory
                if clicked_color in territories:
                    selected_territory = territories[clicked_color]
                    print(f"Clicked on {selected_territory['name']} owned by {selected_territory['owner']}")

                    # Selectin ATTACKER
                    if selected_territory["owner"] == current_player:
                        selected_attacker = selected_territory
                        selected_defender = None
                        print(f"{current_player} selected {selected_attacker['name']} to attack")

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

    pygame.display.update()

# Quit pygame properly
pygame.quit()

