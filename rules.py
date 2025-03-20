import pygame
from rules_text import rules_text  # Import the rules text list

def draw_rules(window, font):
    running = True
    clock = pygame.time.Clock()

    # Colors and settings
    background_color = (0, 0, 0, 180) 
    text_color = (255, 255, 255)
    close_color = (200, 0, 0)       
    close_hover = (255, 50, 50)     

    # Define the close button 
    close_rect = pygame.Rect(670, 110, 20, 20)

    # Scroll settings
    scroll_y = 0                   
    line_height = 30               
    max_width = 540                
    text_height = len(rules_text) * line_height  
    max_scroll = max(0, text_height - 450)        

    # Create a surface for the rules window
    rules_surface = pygame.Surface((600, 500), pygame.SRCALPHA)

    while running:
        # Clear the rules surface and blit it
        rules_surface.fill(background_color)
        window.blit(rules_surface, (100, 100))

        # Draw the close button
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if close_rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(window, close_hover, close_rect)
        else:
            pygame.draw.rect(window, close_color, close_rect)
        # Draw the "X" symbol in the close button
        cross_font = pygame.font.SysFont(None, 26)
        close_text = cross_font.render("X", True, (255, 255, 255))
        window.blit(close_text, (close_rect.x + 3, close_rect.y))

        # Draw a rectangle to clip the text inside the rules box
        text_rect = pygame.Rect(120, 120, max_width, 450)
        pygame.draw.rect(window, background_color, text_rect)

        # Display the wrapped text with scrolling
        y_offset = 120 - scroll_y  # Apply scrolling offset
        for line in rules_text:
            # Only render if the line is (partially) visible
            if 120 <= y_offset <= 550:
                words = line.split()
                wrapped_lines = []
                current_line = ""
                for word in words:
                    test_line = current_line + word + " "
                    test_surface = font.render(test_line, True, text_color)
                    if test_surface.get_width() < max_width:
                        current_line = test_line
                    else:
                        wrapped_lines.append(current_line)
                        current_line = word + " "
                wrapped_lines.append(current_line)  

                # Render each wrapped line
                for wrapped_line in wrapped_lines:
                    text_surface = font.render(wrapped_line, True, text_color)
                    window.blit(text_surface, (130, y_offset))
                    y_offset += line_height  
            y_offset += line_height  

        # Draw the scrollbar on the right side if needed
        if max_scroll > 0:
            scrollbar_height = max(50, int(450 * (450 / (max_scroll + 450))))
            scrollbar_pos = int(120 + (scroll_y / max_scroll) * (450 - scrollbar_height))
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle click on the close button (left click)
                if event.button == 1:
                    if close_rect.collidepoint(event.pos):
                        running = False
                # Handle scroll wheel
                elif event.button == 4:  # Scroll Up
                    scroll_y = max(0, scroll_y - line_height)
                elif event.button == 5:  # Scroll Down
                    scroll_y = min(max_scroll, scroll_y + line_height)
