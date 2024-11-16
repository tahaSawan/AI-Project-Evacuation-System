import pygame
import sys
import json

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Map Editor - Create and Save Obstacles")

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

# Grid settings
GRID_SIZE = 20

# Clock to control frame rate
clock = pygame.time.Clock()

class MapEditor:
    def __init__(self, screen_width, screen_height, grid_size):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.grid_size = grid_size
        self.walls = set()

    def draw_grid(self, screen):
        screen.fill(WHITE)  # Fill screen with white
        for x in range(0, self.screen_width, self.grid_size):  # Vertical lines
            pygame.draw.line(screen, GRAY, (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, self.grid_size):  # Horizontal lines
            pygame.draw.line(screen, GRAY, (0, y), (self.screen_width, y), 1)

    def draw_walls(self, screen):
        for wall in self.walls:
            pygame.draw.rect(screen, RED, (wall[0], wall[1], self.grid_size, self.grid_size))

    def toggle_wall(self, mouse_pos):
        # Calculate grid cell coordinates
        x = (mouse_pos[0] // self.grid_size) * self.grid_size
        y = (mouse_pos[1] // self.grid_size) * self.grid_size

        # Add or remove the wall
        if (x, y) in self.walls:
            self.walls.remove((x, y))
        else:
            self.walls.add((x, y))

    def save_map(self, filename):
        # Save walls as a list of dictionaries
        wall_list = [{"x": x, "y": y} for x, y in self.walls]
        with open(filename, 'w') as f:
            json.dump(wall_list, f, indent=4)

# Initialize map editor
map_editor = MapEditor(SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            map_editor.toggle_wall(pygame.mouse.get_pos())

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:  # Press 'S' to save the map
                map_editor.save_map("map.json")
                print("Map saved as 'map.json'")

    # Draw everything
    map_editor.draw_grid(screen)  # Draw the grid
    map_editor.draw_walls(screen)  # Draw the walls
    pygame.display.flip()  # Update display

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
