import pygame
import sys
import json
import heapq
import random
from concurrent.futures import ThreadPoolExecutor


pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
GREEN=(0,255,0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
AGENT_COLORS = [(0, 128, 255), (0, 255, 128), (255, 0, 128), (128, 0, 255), (255, 128, 0)]

NUM_AGENTS = 50
GRID_SIZE = 10

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Based Evacuation Simulation")

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
        self.fires = []
        self.exit_door = ExitDoor(screen_width - grid_size * 2, screen_height - grid_size * 2, grid_size)
        self.fire_positions = set()
        self.new_fires = []

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
        new_fires = []
        for fire in self.fires:
            for dx, dy in [(-GRID_SIZE, 0), (GRID_SIZE, 0), (0, -GRID_SIZE), (0, GRID_SIZE)]:
                new_x, new_y = fire.x + dx, fire.y + dy
                if (0 <= new_x < SCREEN_WIDTH and 0 <= new_y < SCREEN_HEIGHT and
                        (new_x, new_y) not in self.fire_positions and (new_x, new_y) not in self.walls):
                    new_fires.append((new_x, new_y))

        self.new_fires = []

        for x, y in new_fires:
            if (x, y) not in self.fire_positions and random.random() < 0.3:
                self.new_fires.append(Fire(x, y, GRID_SIZE))
                self.fires.append(Fire(x, y, GRID_SIZE))
                self.fire_positions.add((x, y))


    def draw_background(self, screen):
        screen.fill(WHITE)

    def draw_background_fence(self, screen):
        for x in range(0, SCREEN_WIDTH, self.grid_size):
            pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, self.grid_size):
            pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y), 1)


    def draw_walls(self, screen):
        for wall in self.walls:
            pygame.draw.rect(screen, RED, (wall[0], wall[1], self.grid_size, self.grid_size))

    def draw_fires(self, screen):
        if self.new_fires is []:
            return
        for fire in self.new_fires:
            pygame.draw.rect(screen, ORANGE, (fire.x, fire.y, self.grid_size, self.grid_size))


    def add_fire_at_position(self, x, y):
        if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT and (x, y) not in self.fire_positions:
            self.fires.append(Fire(x, y, GRID_SIZE))
            self.fire_positions.add((x, y))

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
        self.health = 100

    def move(self):
        if self.path:
            next_position = self.path.pop(0)
            self.x, self.y = next_position

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))
        # health_bar_width = self.size
        # health_bar_height = 5
        # health_percentage = self.health / 100
        # pygame.draw.rect(screen, RED, (self.x, self.y - 10, health_bar_width, health_bar_height))
        # pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, health_bar_width * health_percentage, health_bar_height))
    
    def remove_draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.size, self.size))

def astar(start, goal, walls, fires, avoid_fire=True):

    start_time = pygame.time.get_ticks()

    open_list = []
    closed_list = set()
    came_from = {}

    def heuristic(a, b):
        # return abs(a[0] - b[0]) + abs(a[1] - b[1])
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def nearest_fire_distance(position):
        if not fires:
            return 0
        # return min(abs(position[0] - fire.x) + abs(position[1] - fire.y) for fire in fires)
        # use euclidian distance
        # return 0
        return min(((position[0] - fire.x) ** 2 + (position[1] - fire.y) ** 2) ** 0.5 for fire in fires)
        
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal) - nearest_fire_distance(start)}

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
                if avoid_fire and is_fire:
                    continue

                if neighbor_pos not in walls:
                    tentative_g_score = g_score[current] + 1 + fire_penalty
                    if neighbor_pos not in g_score or tentative_g_score < g_score[neighbor_pos]:
                        came_from[neighbor_pos] = current
                        g_score[neighbor_pos] = tentative_g_score
                        f_score[neighbor_pos] = tentative_g_score + heuristic(neighbor_pos, goal) - nearest_fire_distance(neighbor_pos)
                        heapq.heappush(open_list, (f_score[neighbor_pos], neighbor_pos))
        
    return []

def calculate_astar(agent, game_map):
    start = (agent.x, agent.y)
    goal = (game_map.exit_door.x, game_map.exit_door.y)
    
    path = astar(start, goal, game_map.walls, game_map.fires, avoid_fire=True)
    if not path:
        path = astar(start, goal, game_map.walls, game_map.fires, avoid_fire=False)
    return agent, path

def game_loop():
    map_file = "map.json"
    game_map = Map(GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, map_file)

    num_agents = NUM_AGENTS
    agents = []
    for i in range(num_agents):
        while True:
            x = random.randint(0, game_map.cols - 1) * GRID_SIZE
            y = random.randint(0, game_map.rows - 1) * GRID_SIZE
            if (x, y) not in game_map.walls and (x, y) not in game_map.fire_positions:
                agents.append(Agent(x, y, GRID_SIZE, 5, random.choice(AGENT_COLORS)))
                break

    fire_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    walls_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    for wall in game_map.walls:
        pygame.draw.rect(walls_surface, RED, (wall[0], wall[1], GRID_SIZE, GRID_SIZE))

    frame_count = 0

    game_map.draw_background(screen)
    game_map.draw_exit_door(screen)

    while agents:
        frame_count += 1
        start_time = pygame.time.get_ticks()

        if frame_count % 2 == 0:
            game_map.spawn_new_fires()

        screen.blit(walls_surface, (0, 0))

        fire_surface.fill((0, 0, 0, 0))
        game_map.draw_fires(fire_surface)
        screen.blit(fire_surface, (0, 0))

        game_map.draw_background_fence(screen)


        with ThreadPoolExecutor() as executor:
            future_to_agent = {executor.submit(calculate_astar, agent, game_map): agent for agent in agents}

            for future in future_to_agent:
                agent, path = future.result()
                agent.path = path

        if pygame.time.get_ticks() - start_time < 100:
            pygame.time.wait(100)

        for agent in agents[:]:
            if game_map.exit_door.check_collision(agent):
                agents.remove(agent)
                continue
            if agent.path:
                next_step = agent.path[0]
                if (next_step[0], next_step[1]) in game_map.fire_positions:
                    agent.health -= 5
                    if agent.health <= 0:
                        agents.remove(agent)
                        continue

            agent.remove_draw(screen)
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
                    pygame.draw.rect(walls_surface, RED, (x, y, GRID_SIZE, GRID_SIZE))
                elif event.button == 3:
                    game_map.add_fire_at_position(x, y)

        pygame.display.flip()

game_loop()
