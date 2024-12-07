import pygame
import sys
import json

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Map Editor - Create and Save Obstacles")

WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)

GRID_SIZE = 10

clock = pygame.time.Clock()

class MapEditor:
    def __init__(self, screen_width, screen_height, grid_size):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.grid_size = grid_size
        self.walls = set()
        self.dragging = False

    def draw_grid(self, screen):
        screen.fill(WHITE)
        for x in range(0, self.screen_width, self.grid_size):
            pygame.draw.line(screen, GRAY, (x, 0), (x, self.screen_height), 1)
        for y in range(0, self.screen_height, self.grid_size):
            pygame.draw.line(screen, GRAY, (0, y), (self.screen_width, y), 1)

    def draw_walls(self, screen):
        for wall in self.walls:
            pygame.draw.rect(screen, RED, (wall[0], wall[1], self.grid_size, self.grid_size))

    def toggle_wall(self, mouse_pos, add=True):
        x = (mouse_pos[0] // self.grid_size) * self.grid_size
        y = (mouse_pos[1] // self.grid_size) * self.grid_size

        if add:
            self.walls.add((x, y))
        else:
            if (x, y) in self.walls:
                self.walls.remove((x, y))

    def save_map(self, filename):
        wall_list = [{"x": x, "y": y} for x, y in self.walls]
        with open(filename, 'w') as f:
            json.dump(wall_list, f, indent=4)

map_editor = MapEditor(SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click to remove walls
                map_editor.dragging = True
                map_editor.toggle_wall(pygame.mouse.get_pos(), add=False)

            elif event.button == 3:  # Right click to add walls
                map_editor.dragging = True
                map_editor.toggle_wall(pygame.mouse.get_pos(), add=True)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button in [1, 3]:  # Release either button to stop dragging
                map_editor.dragging = False

        if event.type == pygame.MOUSEMOTION:
            if map_editor.dragging:
                if pygame.mouse.get_pressed()[0]:  # Left button pressed
                    map_editor.toggle_wall(pygame.mouse.get_pos(), add=False)
                elif pygame.mouse.get_pressed()[2]:  # Right button pressed
                    map_editor.toggle_wall(pygame.mouse.get_pos(), add=True)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:
                map_editor.save_map("map.json")
                print("Map saved as 'map.json'")

    map_editor.draw_grid(screen) 
    map_editor.draw_walls(screen)
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
sys.exit()
