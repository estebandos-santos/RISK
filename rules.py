import pygame

from rules_text import rules_text # Dictionary

def draw_rules(window, font):
    """ Affiche les règles du jeu dans une fenêtre semi-transparente. """
    running = True
    clock = pygame.time.Clock()

    # Couleurs
    background_color = (0, 0, 0, 180)  # Fond semi-transparent
    text_color = (255, 255, 255)

    # Surface semi-transparente
    rules_surface = pygame.Surface((600, 500), pygame.SRCALPHA)
    rules_surface.fill(background_color)

    while running:
        window.blit(rules_surface, (100, 100))

        # Affichage du texte ligne par ligne
        y_offset = 120
        for line in rules_text:
            text_surface = font.render(line, True, text_color)
            window.blit(text_surface, (120, y_offset))
            y_offset += 30

        pygame.display.update()
        clock.tick(30)

        # Gestion des événements pour quitter l'affichage des règles
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False  # Fermer les règles

