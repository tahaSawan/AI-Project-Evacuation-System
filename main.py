import pygame
import sys
import json
import heapq

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

class ExitDoor:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.size, self.size))

    def check_collision(self, agent):
        # Check if the agent touches the exit door
        if (
            agent.x < self.x + self.size
            and agent.x + agent.size > self.x
            and agent.y < self.y + self.size
            and agent.y + agent.size > self.y
        ):
            return True
        return False

# Map class
class Map:
    def __init__(self, grid_size, screen_width, screen_height, map_file):
        self.grid_size = grid_size
        self.rows = screen_height // grid_size
        self.cols = screen_width // grid_size
        self.walls = self.load_map(map_file)
        self.fires = []  # Initialize fires as an empty list
        self.last_fire_time = pygame.time.get_ticks()  # Initialize the timer for fire creation
        # Add an exit door at a predefined position
        self.exit_door = ExitDoor(screen_width - grid_size * 2, screen_height - grid_size * 2, grid_size)

    def draw_exit_door(self, screen):
        self.exit_door.draw(screen)

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
# Agent class
class Agent:
    def __init__(self, x, y, size, speed):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.score = 100  # Starting score
        self.path = []  # The path to follow
        self.last_move_time = pygame.time.get_ticks()  # Timer for movement speed

    def move(self):
        current_time = pygame.time.get_ticks()
        if self.path and current_time - self.last_move_time >= 200:  # Delay between movements (in milliseconds)
            next_position = self.path.pop(0)
            self.x, self.y = next_position
            self.last_move_time = current_time  # Reset the timer

    def update_score(self, amount):
        self.score += amount
        if self.score < 0:
            self.score = 0  # Prevent score from going below 0

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.size, self.size))



# A* algorithm to find the shortest path
def astar(start, goal, walls, fires):
    open_list = []
    closed_list = set()
    came_from = {}

    # Heuristic function (Manhattan distance)
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Node costs
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    heapq.heappush(open_list, (f_score[start], start))

    while open_list:
        current_f, current = heapq.heappop(open_list)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        closed_list.add(current)

        for neighbor in [(0, -GRID_SIZE), (0, GRID_SIZE), (-GRID_SIZE, 0), (GRID_SIZE, 0)]:
            neighbor_x = current[0] + neighbor[0]
            neighbor_y = current[1] + neighbor[1]
            neighbor_pos = (neighbor_x, neighbor_y)

            if 0 <= neighbor_x < SCREEN_WIDTH and 0 <= neighbor_y < SCREEN_HEIGHT and neighbor_pos not in closed_list:
                if neighbor_pos not in walls and not any(f.x == neighbor_x and f.y == neighbor_y for f in fires):
                    tentative_g_score = g_score[current] + 1
                    if neighbor_pos not in g_score or tentative_g_score < g_score[neighbor_pos]:
                        came_from[neighbor_pos] = current
                        g_score[neighbor_pos] = tentative_g_score
                        f_score[neighbor_pos] = tentative_g_score + heuristic(neighbor_pos, goal)
                        heapq.heappush(open_list, (f_score[neighbor_pos], neighbor_pos))

    return []  # Return an empty path if no path is found


# Main game loop
def game_loop():
    map_file = "map.json"  # Replace with your map file path
    game_map = Map(GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, map_file)
    agent = Agent(0, 0, GRID_SIZE, 5)  # Agent starting position

    while True:
        game_map.spawn_new_fires()
        game_map.draw_background(screen)
        game_map.draw_walls(screen)
        game_map.draw_fires(screen)
        game_map.draw_exit_door(screen)

        if game_map.exit_door.check_collision(agent):
            print("Agent reached the exit!")
            break  # End the game

        # A* pathfinding to find the exit
        start = (agent.x, agent.y)
        goal = (game_map.exit_door.x, game_map.exit_door.y)
        agent.path = astar(start, goal, game_map.walls, game_map.fires)

        agent.move()

        agent.draw(screen)

        # Handle mouse events for adding fires and walls
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = (mouse_x // GRID_SIZE) * GRID_SIZE
                grid_y = (mouse_y // GRID_SIZE) * GRID_SIZE
                if pygame.mouse.get_pressed()[0]:  # Left mouse button
                    game_map.add_fire_at_position(grid_x, grid_y)
                elif pygame.mouse.get_pressed()[2]:  # Right mouse button
                    game_map.add_wall_at_position(grid_x, grid_y)

        pygame.display.update()

        clock.tick(30)  # Slow down the movement of the agent

# Start the game loop
game_loop()
