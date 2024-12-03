import pygame
import sys
import json
import heapq
import random

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
GREEN=(0,255,0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
AGENT_COLORS = [(0, 128, 255), (0, 255, 128), (255, 0, 128), (128, 0, 255), (255, 128, 0)]

# Grid settings
GRID_SIZE = 20

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Game - Multiple Agents with Obstacles")

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
        if (
            agent.x < self.x + self.size
            and agent.x + agent.size > self.x
            and agent.y < self.y + self.size
            and agent.y + agent.size > self.y
        ):
            return True
        return False

class Map:
    def __init__(self, grid_size, screen_width, screen_height, map_file):
        self.grid_size = grid_size
        self.rows = screen_height // grid_size
        self.cols = screen_width // grid_size
        self.walls = self.load_map(map_file)
        self.fires = []  # Initialize fires as an empty list
        self.last_fire_time = pygame.time.get_ticks()  # Initialize the timer for fire creation
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
                adjacent_positions = [
                    (fire.x, fire.y - GRID_SIZE),
                    (fire.x, fire.y + GRID_SIZE),
                    (fire.x - GRID_SIZE, fire.y),
                    (fire.x + GRID_SIZE, fire.y),
                ]
                for pos in adjacent_positions:
                    new_x, new_y = pos
                    if 0 <= new_x < SCREEN_WIDTH and 0 <= new_y < SCREEN_HEIGHT:
                        if (new_x, new_y) not in self.walls and not any(f.x == new_x and f.y == new_y for f in self.fires):
                            new_fires.append(Fire(new_x, new_y, GRID_SIZE))
            self.fires.extend(new_fires)
            self.last_fire_time = current_time

    def draw_background(self, screen):
        screen.fill(WHITE)
        for x in range(0, SCREEN_WIDTH, self.grid_size):
            pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, self.grid_size):
            pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y), 1)

    def draw_walls(self, screen):
        for wall in self.walls:
            pygame.draw.rect(screen, RED, (wall[0], wall[1], self.grid_size, self.grid_size))

    def draw_fires(self, screen):
        for fire in self.fires:
            fire.draw(screen)

    def add_fire_at_position(self, x, y):
        if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
            self.fires.append(Fire(x, y, GRID_SIZE))

    def add_wall_at_position(self, x, y):
        if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
            if (x, y) not in self.walls and not any(f.x == x and f.y == y for f in self.fires):
                self.walls.append((x, y))

class Fire:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

    def draw(self, screen):
        pygame.draw.rect(screen, ORANGE, (self.x, self.y, self.size, self.size))

class Agent:
    def __init__(self, x, y, size, speed, color):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.color = color
        self.path = []
        self.health = 100  # Initialize agent health to 100 HP
        self.last_move_time = pygame.time.get_ticks()

    def move(self):
        current_time = pygame.time.get_ticks()
        if self.path and current_time - self.last_move_time >= 200:
            next_position = self.path.pop(0)
            self.x, self.y = next_position
            self.last_move_time = current_time

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))
        # Draw health bar above the agent
        health_bar_width = self.size
        health_bar_height = 5
        health_percentage = self.health / 100
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, health_bar_width * health_percentage, health_bar_height))

def astar(start, goal, walls, fires, avoid_fire=True):
    open_list = []
    closed_list = set()
    came_from = {}

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

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
                is_fire = any(f.x == neighbor_x and f.y == neighbor_y for f in fires)
                fire_penalty = 10 if is_fire else 0
                # If avoiding fire, treat fire cells as walls
                if avoid_fire and is_fire:
                    continue

                if neighbor_pos not in walls:
                    tentative_g_score = g_score[current] + 1 + fire_penalty
                    if neighbor_pos not in g_score or tentative_g_score < g_score[neighbor_pos]:
                        came_from[neighbor_pos] = current
                        g_score[neighbor_pos] = tentative_g_score
                        f_score[neighbor_pos] = tentative_g_score + heuristic(neighbor_pos, goal)
                        heapq.heappush(open_list, (f_score[neighbor_pos], neighbor_pos))

    return []  # Return an empty path if no route is found


def game_loop():
    map_file = "map.json"
    game_map = Map(GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, map_file)

    num_agents = random.randint(1, 10)
    agents = []
    for i in range(num_agents):
        while True:
            x = random.randint(0, game_map.cols - 1) * GRID_SIZE
            y = random.randint(0, game_map.rows - 1) * GRID_SIZE
            if (x, y) not in game_map.walls and not any(f.x == x and f.y == y for f in game_map.fires):
                agents.append(Agent(x, y, GRID_SIZE, 5, random.choice(AGENT_COLORS)))
                break

    while agents:
        game_map.spawn_new_fires()
        game_map.draw_background(screen)
        game_map.draw_walls(screen)
        game_map.draw_fires(screen)
        game_map.draw_exit_door(screen)

        for agent in agents[:]:
            if game_map.exit_door.check_collision(agent):
                agents.remove(agent)
                continue

            start = (agent.x, agent.y)
            goal = (game_map.exit_door.x, game_map.exit_door.y)

            # Prioritize path avoiding fire
            agent.path = astar(start, goal, game_map.walls, game_map.fires, avoid_fire=True)

            # If no path exists avoiding fire, allow traversal through fire
            if not agent.path:
                agent.path = astar(start, goal, game_map.walls, game_map.fires, avoid_fire=False)

            if agent.path:
                # Check if the next step is through fire and reduce health slower
                next_step = agent.path[0]
                if any(f.x == next_step[0] and f.y == next_step[1] for f in game_map.fires):
                    agent.health -= 5  # Slower HP reduction
                    if agent.health <= 0:
                        agents.remove(agent)
                        continue

            agent.move()
            agent.draw(screen)          


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                x = x // GRID_SIZE * GRID_SIZE
                y = y // GRID_SIZE * GRID_SIZE
                if event.button == 1:
                    game_map.add_wall_at_position(x, y)
                elif event.button == 3:
                    game_map.add_fire_at_position(x, y)

        pygame.display.flip()
        clock.tick(60)

game_loop()
