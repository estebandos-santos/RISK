import pygame

from rules_text import rules_text # Dictionary

def draw_rules(window, font):
    running = True
    clock = pygame.time.Clock()

    # Colors
    background_color = (0, 0, 0, 180)  # Fond semi-transparent
    text_color = (255, 255, 255)

    # Scroll Settings
    scroll_y = 0
    line_height = 30
    max_width = 540
    text_height = len(rules_text) * line_height
    max_scroll = max(0, text_height - 450)

     # Surface
    rules_surface = pygame.Surface((600, 500), pygame.SRCALPHA)
    

    while running:
        rules_surface.fill(background_color)
        window.blit(rules_surface, (100, 100))

        # Clip the text to stay in Wondow
        text_rect = pygame.Rect(120, 120, max_width, 450)
        pygame.draw.rect(window, background_color, text_rect)

        # Display text 
        y_offset = 120 - scroll_y
        for line in rules_text:
            if 100 < y_offset < 550:
                words = line.split()
                wrapped_lines = []
                current_line = ""
                
            
                for word in words :
                    test_line = current_line + word + " "
                    test_surface = font.render(test_line, True, text_color)

                    if test_surface.get_width() < max_width:
                        current_line = test_line
                    else:
                        wrapped_lines.append(current_line)
                        current_line = word + " "

                wrapped_lines.append(current_line)
                    

                # Display each wrapped line
                for wrapped_line in wrapped_lines:
                    text_surface = font.render(wrapped_line, True, text_color)
                    window.blit(text_surface, (130, y_offset))
                    y_offset += line_height
                                    

            y_offset += line_height

        # Display scrollbar
        if max_scroll > 0:
            scrollbar_height = max(50, int(450 * (450 / (max_scroll + 450))))
            scrollbar_pos = int (100 + (scroll_y / max_scroll) * (450 - scrollbar_height))
            pygame.draw.rect(window, (200, 200, 200), (680, scrollbar_pos, 10, scrollbar_height))

        pygame.display.update()
        clock.tick(30)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False  # Close the rules window

            # NEW: Fix scrolling
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll Up
                    scroll_y = max(0, scroll_y - line_height)
                elif event.button == 5:  # Scroll Down
                    scroll_y = min(max_scroll, scroll_y + line_height)