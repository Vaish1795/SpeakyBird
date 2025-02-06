import time

import pygame as pg


class Button:
    def __init__(self, settings, constants, image, x, y, text_input, enabled=True):
        self.settings = settings
        self.constants = constants
        self.image = image
        self.x = x
        self.y = y
        self.enabled = enabled

        self.text_input = text_input
        self.text = self.settings.menu_font.render(self.text_input, True, (255, 255, 255))
        if self.image is None:
            self.image = self.text

        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.text_rect = self.text.get_rect(center=(self.x, self.y))

    def draw(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def check_for_mouse_input(self, position):
        # This function checks if the given mouse position co-ordinates is within the button's rect
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    def change_color(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.settings.menu_font.render(self.text_input, True, self.settings.buttontext_hover_color)
        else:
            self.text = self.settings.menu_font.render(self.text_input, True, self.settings.buttontext_color)

    def update_image(self, image):
        self.image = image


def update_level_button_images(button, alpha_value, state):
    surface = pg.Surface((200, 50), pg.SRCALPHA)
    if state == 'enabled':
        surface.fill((0, 0, 0, alpha_value))
    else:
        surface.fill((115, 147, 179, alpha_value + 30))
    button.update_image(surface)


class TextInput:
    def __init__(self, font, initial_text='', max_length=None, cursor_color=(0, 45, 98)):
        self.font = font
        self.text = initial_text
        self.max_length = max_length
        self.cursor_color = cursor_color
        self.cursor_visible = True
        self.cursor_timer = time.time()

    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pg.K_RETURN:
                return self.text
            elif self.max_length is None or len(self.text) < self.max_length:
                self.text += event.unicode
        return None

    def update(self):
        if time.time() - self.cursor_timer >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = time.time()

    def draw(self, screen, rect):
        pg.draw.rect(screen, (200, 200, 200), rect, 0)
        pg.draw.rect(screen, (0, 0, 0), rect, 2)

        # Render the text surface
        text_surface = self.font.render(self.text, True, (0, 45, 98))

        # Calculate the x position to center the text
        text_x = rect.x + (rect.width - text_surface.get_width()) // 2
        text_y = rect.y + (rect.height - text_surface.get_height()) // 2

        # Ensure text does not go out of bounds on the left
        if text_x < rect.x + 5:
            text_x = rect.x + 5

        # Blit the text surface to the screen
        screen.blit(text_surface, (text_x, text_y))

        # Draw cursor if visible
        if self.cursor_visible:
            cursor_x = text_x + text_surface.get_width() + 2
            cursor_y = text_y
            cursor_height = text_surface.get_height()
            pg.draw.line(screen, self.cursor_color, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)
