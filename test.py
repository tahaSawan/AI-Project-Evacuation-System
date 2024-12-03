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
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
AGENT_COLORS = [(0, 128, 255), (0, 255, 128), (255, 0, 128), (128, 0, 255), (255, 128, 0)]

# Grid settings
GRID_SIZE = 20

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Multi-Level Agent Game")

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


class EntryDoor:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.size, self.size))


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
        self.last_move_time = pygame.time.get_ticks()

    def move(self):
        current_time = pygame.time.get_ticks()
        if self.path and current_time - self.last_move_time >= 200:
            next_position = self.path.pop(0)
            self.x, self.y = next_position
            self.last_move_time = current_time

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))
        health_bar_width = self.size
        health_bar_height = 5
        health_percentage = self.health / 100
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, health_bar_width * health_percentage, health_bar_height))


class Map:
    def __init__(self, grid_size, screen_width, screen_height, has_entry=False):
        self.grid_size = grid_size
        self.rows = screen_height // grid_size
        self.cols = screen_width // grid_size
        self.walls = self.generate_random_walls()
        self.fires = []
        self.last_fire_time = pygame.time.get_ticks()
        self.exit_doors = [ExitDoor(random.randint(0, self.cols - 1) * grid_size,
                                    random.randint(0, self.rows - 1) * grid_size, grid_size) for _ in range(2)]
        self.entry_door = EntryDoor(0, 0, grid_size) if has_entry else None

    def generate_random_walls(self):
        num_walls = random.randint(50, 100)
        walls = []
        for _ in range(num_walls):
            x = random.randint(0, self.cols - 1) * self.grid_size
            y = random.randint(0, self.rows - 1) * self.grid_size
            walls.append((x, y))
        return walls

    def spawn_new_fires(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_fire_time >= 3000:
            for fire in self.fires[:]:
                adjacent_positions = [
                    (fire.x, fire.y - GRID_SIZE),
                    (fire.x, fire.y + GRID_SIZE),
                    (fire.x - GRID_SIZE, fire.y),
                    (fire.x + GRID_SIZE, fire.y),
                ]
                for pos in adjacent_positions:
                    new_x, new_y = pos
                    if (new_x, new_y) not in self.walls and not any(f.x == new_x and f.y == new_y for f in self.fires):
                        self.fires.append(Fire(new_x, new_y, GRID_SIZE))
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

    def draw_exit_doors(self, screen):
        for exit_door in self.exit_doors:
            exit_door.draw(screen)

    def draw_entry_door(self, screen):
        if self.entry_door:
            self.entry_door.draw(screen)


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
                if avoid_fire and is_fire:
                    continue

                if neighbor_pos not in walls:
                    tentative_g_score = g_score[current] + 1 + fire_penalty
                    if neighbor_pos not in g_score or tentative_g_score < g_score[neighbor_pos]:
                        came_from[neighbor_pos] = current
                        g_score[neighbor_pos] = tentative_g_score
                        f_score[neighbor_pos] = tentative_g_score + heuristic(neighbor_pos, goal)
                        heapq.heappush(open_list, (f_score[neighbor_pos], neighbor_pos))
    return None



def main():
    # Game Mode Selection
    print("Welcome to the Multi-Level Agent Game!")
    print("1. Single Level")
    print("2. Multi-Level")
    mode = input("Choose the game mode (1 or 2): ")

    # Validate input
    while mode not in ["1", "2"]:
        print("Invalid choice. Please enter 1 or 2.")
        mode = input("Choose the game mode (1 or 2): ")

    mode = int(mode)
    num_levels = 1 if mode == 1 else 3  # Number of levels in the game

    # Agent settings
    num_agents = 10
    agents = [
        Agent(
            random.randint(0, (SCREEN_WIDTH // GRID_SIZE) - 1) * GRID_SIZE,
            random.randint(0, (SCREEN_HEIGHT // GRID_SIZE) - 1) * GRID_SIZE,
            GRID_SIZE,
            speed=1,
            color=random.choice(AGENT_COLORS),
        )
        for _ in range(num_agents)
    ]

    # Game statistics
    total_agents = len(agents)
    saved_agents = 0
    lost_agents = 0

    for level in range(num_levels):
        print(f"Starting Level {level + 1}")
        has_entry = level > 0
        game_map = Map(GRID_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, has_entry=has_entry)

        # Set entry point for agents in subsequent levels
        if has_entry:
            for agent in agents:
                agent.x, agent.y = game_map.entry_door.x, game_map.entry_door.y

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Move agents
            for agent in agents[:]:
                if not agent.path:
                    closest_exit = min(
                        game_map.exit_doors,
                        key=lambda door: abs(agent.x - door.x) + abs(agent.y - door.y),
                    )
                    agent.path = astar(
                        (agent.x, agent.y),
                        (closest_exit.x, closest_exit.y),
                        game_map.walls,
                        game_map.fires,
                        avoid_fire=True,
                    )

                agent.move()

                # Collision with fire
                for fire in game_map.fires:
                    if (
                        agent.x < fire.x + fire.size
                        and agent.x + agent.size > fire.x
                        and agent.y < fire.y + fire.size
                        and agent.y + agent.size > fire.y
                    ):
                        agent.health -= 10
                        if agent.health <= 0:
                            lost_agents += 1
                            agents.remove(agent)
                            break

                # Collision with exit door
                for exit_door in game_map.exit_doors:
                    if exit_door.check_collision(agent):
                        saved_agents += 1
                        agents.remove(agent)
                        break

            # Check if all agents are processed
            if not agents:
                running = False

            # Update fires
            game_map.spawn_new_fires()

            # Draw the screen
            game_map.draw_background(screen)
            game_map.draw_walls(screen)
            game_map.draw_fires(screen)
            game_map.draw_exit_doors(screen)
            if has_entry:
                game_map.draw_entry_door(screen)

            for agent in agents:
                agent.draw(screen)

            pygame.display.flip()
            clock.tick(30)

        if level < num_levels - 1 and agents:
            print(f"Level {level + 1} completed. Moving to Level {level + 2}.")
        elif not agents:
            print(f"All agents are lost. Game Over!")
            break

    # Game Over Summary
    total_agents_saved = saved_agents
    total_agents_lost = total_agents - total_agents_saved
    survival_rate = (total_agents_saved / total_agents) * 100

    print("\n--- Game Over ---")
    print(f"Total Agents: {total_agents}")
    print(f"Saved Agents: {total_agents_saved}")
    print(f"Lost Agents: {total_agents_lost}")
    print(f"Survival Rate: {survival_rate:.2f}%")

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()