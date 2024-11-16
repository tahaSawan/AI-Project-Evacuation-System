import pygame
import sys
import json

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)

# Grid settings
GRID_SIZE = 20

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Game - Map Obstacles from JSON")

# Clock to control frame rate
clock = pygame.time.Clock()

# Map class
class Map:
    def __init__(self, grid_size, screen_width, screen_height, map_file):
        self.grid_size = grid_size
        self.rows = screen_height // grid_size
        self.cols = screen_width // grid_size
        self.walls = self.load_map(map_file)
        self.fires = []  # Initialize fires as an empty list
        self.last_fire_time = pygame.time.get_ticks()  # Initialize the timer for fire creation

    def load_map(self, map_file):
        try:
            with open(map_file, 'r') as file:
                data = json.load(file)
                return [(entry['x'], entry['y']) for entry in data]
        except FileNotFoundError:
            print(f"Error: {map_file} not found.")
            sys.exit()
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in {map_file}.")
            sys.exit()

    def spawn_new_fires(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fire_time >= 3000:  # Check if 3 seconds have passed
            new_fires = []
            for fire in self.fires:
                # Check adjacent cells (up, down, left, right)
                adjacent_positions = [
                    (fire.x, fire.y - GRID_SIZE),  # Up
                    (fire.x, fire.y + GRID_SIZE),  # Down
                    (fire.x - GRID_SIZE, fire.y),  # Left
                    (fire.x + GRID_SIZE, fire.y),  # Right
                ]
                for pos in adjacent_positions:
                    new_x, new_y = pos
                    # Ensure the new fire is within bounds
                    if 0 <= new_x < SCREEN_WIDTH and 0 <= new_y < SCREEN_HEIGHT:
                        # Check if the position is not already occupied by a wall or fire
                        if (new_x, new_y) not in self.walls and not any(f.x == new_x and f.y == new_y for f in self.fires):
                            new_fires.append(Fire(new_x, new_y, GRID_SIZE))
            
            self.fires.extend(new_fires)
            self.last_fire_time = current_time  # Reset the timer

    def draw_background(self, screen):
        screen.fill(WHITE)  # Fill screen with white
        for x in range(0, SCREEN_WIDTH, self.grid_size):  # Vertical lines
            pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, self.grid_size):  # Horizontal lines
            pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y), 1)

    def draw_walls(self, screen):
        for wall in self.walls:
            pygame.draw.rect(
                screen, RED, (wall[0], wall[1], self.grid_size, self.grid_size)
            )

    def draw_fires(self, screen):
        for fire in self.fires:
            fire.draw(screen)

    def add_fire_at_position(self, x, y):
        """Add a new fire at the given (x, y) position."""
        if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
            self.fires.append(Fire(x, y, GRID_SIZE))


    def add_wall_at_position(self, x, y):
        """Add a new wall at the given (x, y) position."""
        if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
            # Only add the wall if it's not already a wall or fire
            if (x, y) not in self.walls and not any(f.x == x and f.y == y for f in self.fires):
                self.walls.append((x, y))
                
# Fire class
class Fire:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

    def draw(self, screen):
        pygame.draw.rect(screen, ORANGE, (self.x, self.y, self.size, self.size))

    def check_collision(self, agent):
        # Check if the agent touches the fire
        if (
            agent.x < self.x + self.size
            and agent.x + agent.size > self.x
            and agent.y < self.y + self.size
            and agent.y + agent.size > self.y
        ):
            return True
        return False


# Agent class
class Agent:
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.score = 100  # Starting score

    def move(self, keys, walls, fires):
        new_x, new_y = self.x, self.y
        if keys[pygame.K_w]:  # Move up
            new_y -= self.speed
        if keys[pygame.K_s]:  # Move down
            new_y += self.speed
        if keys[pygame.K_a]:  # Move left
            new_x -= self.speed
        if keys[pygame.K_d]:  # Move right
            new_x += self.speed

        # Prevent going out of bounds
        new_x = max(0, min(SCREEN_WIDTH - self.size, new_x))
        new_y = max(0, min(SCREEN_HEIGHT - self.size, new_y))

        # Check collisions
        if not self.check_collision(new_x, new_y, walls):
            self.x, self.y = new_x, new_y

    def check_collision(self, new_x, new_y, walls):
        # Check wall collisions
        for wall in walls:
            if (
                new_x < wall[0] + GRID_SIZE
                and new_x + self.size > wall[0]
                and new_y < wall[1] + GRID_SIZE
                and new_y + self.size > wall[1]
            ):
                return True

        return False

    def update_score(self, amount):
        self.score += amount
        if self.score < 0:
            self.score = 0  # Prevent score from going below 0

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.size, self.size))


def main():
    # Initialize the map and agent
    game_map = Map(GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, 'map.json')
    agent = Agent(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 10, 3)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Right-click to create a fire
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // GRID_SIZE * GRID_SIZE
                grid_y = mouse_y // GRID_SIZE * GRID_SIZE
                if event.button == 3:
                    # Add a fire at the mouse position
                    game_map.add_fire_at_position(grid_x, grid_y)
                elif event.button == 1:
                    # Add a wall at the mouse position
                    game_map.add_wall_at_position(grid_x, grid_y)

        keys = pygame.key.get_pressed()
        agent.move(keys, game_map.walls, game_map.fires)

        # Check if the agent touches any fire
        for fire in game_map.fires:
            if fire.check_collision(agent):
                agent.update_score(-5)

        # Spawn new fires around existing ones
        game_map.spawn_new_fires()

        # Draw everything
        game_map.draw_background(screen)
        game_map.draw_walls(screen)
        game_map.draw_fires(screen)
        agent.draw(screen)

        # Display score
        font = pygame.font.SysFont("Arial", 24)
        score_text = font.render(f"Score: {agent.score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
