import math
import random
import pygame
from config import FRUIT_SPEED_MIN, FRUIT_SPEED_MAX, FRUIT_SPAWN_INTERVAL, RED, ORANGE, GREEN, YELLOW, PURPLE, WHITE

def line_circle_intersect(p1, p2, center, radius):
    # p1: (x1, y1), p2: (x2, y2), center: (cx, cy)
    x1, y1 = p1
    x2, y2 = p2
    cx, cy = center
    
    dx = x2 - x1
    dy = y2 - y1
    
    if dx == 0 and dy == 0:
        return math.hypot(cx - x1, cy - y1) <= radius
        
    t = ((cx - x1) * dx + (cy - y1) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))
    
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    
    dist = math.hypot(cx - closest_x, cy - closest_y)
    return dist <= radius

class Fruit:
    def __init__(self, screen_width, screen_height):
        self.pos = [random.randint(100, screen_width - 100), screen_height + 30]
        self.vel = [random.uniform(-3, 3), random.uniform(-FRUIT_SPEED_MAX, -FRUIT_SPEED_MIN)]
        self.gravity = 0.35
        self.fruit_type = random.choice(['apple', 'orange', 'watermelon', 'banana', 'pineapple'])
        
        color_map = {
            'apple': RED,
            'orange': ORANGE,
            'watermelon': GREEN,
            'banana': YELLOW,
            'pineapple': PURPLE
        }
        self.color = color_map[self.fruit_type]
        self.inner_color = tuple(min(255, c + 60) for c in self.color)
        
        self.radius = 35 if self.fruit_type in ['watermelon', 'pineapple'] else 28
        self.sliced = False
        self.rotation = 0.0
        self.rotation_speed = random.uniform(-4.0, 4.0)
        self.off_screen = False
        self.missed = False
        self.letter = self.fruit_type[0].upper()

    def update(self, screen_height):
        self.vel[1] += self.gravity
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.rotation += self.rotation_speed
        
        if self.pos[1] > screen_height + 60:
            self.off_screen = True
            if not self.sliced:
                self.missed = True

    def draw(self, surface):
        center = (int(self.pos[0]), int(self.pos[1]))
        pygame.draw.circle(surface, self.color, center, self.radius)
        pygame.draw.circle(surface, self.inner_color, center, max(1, self.radius - 8))
        
        # Shine effect
        shine_rect = pygame.Rect(center[0] - 8 - 5, center[1] - 8 - 5, 10, 10)
        pygame.draw.ellipse(surface, WHITE, shine_rect)

        # Letter overlay
        font = pygame.font.SysFont(None, int(self.radius * 1.5), bold=True)
        text_surf = font.render(self.letter, True, WHITE)
        rotated_surf = pygame.transform.rotate(text_surf, -self.rotation)
        text_rect = rotated_surf.get_rect(center=center)
        surface.blit(rotated_surf, text_rect)

    def check_slice(self, slice_points):
        if len(slice_points) < 2:
            return False
        for i in range(len(slice_points) - 1):
            if line_circle_intersect(slice_points[i], slice_points[i+1], self.pos, self.radius):
                if not self.sliced:
                    self.sliced = True
                    return True
        return False

class Bomb:
    def __init__(self, screen_width, screen_height):
        self.pos = [random.randint(100, screen_width - 100), screen_height + 30]
        self.vel = [random.uniform(-3, 3), random.uniform(-FRUIT_SPEED_MAX, -FRUIT_SPEED_MIN)]
        self.gravity = 0.35
        
        self.color = (30, 30, 30)
        self.inner_color = (80, 80, 80)
        self.radius = 28
        self.sliced = False
        self.rotation = 0.0
        self.rotation_speed = random.uniform(-4.0, 4.0)
        self.off_screen = False
        self.missed = False
        self.bomb_hit = False

    def update(self, screen_height):
        self.vel[1] += self.gravity
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.rotation += self.rotation_speed
        
        if self.pos[1] > screen_height + 60:
            self.off_screen = True

    def draw(self, surface):
        center = (int(self.pos[0]), int(self.pos[1]))
        pygame.draw.circle(surface, self.color, center, self.radius)
        pygame.draw.circle(surface, self.inner_color, center, max(1, self.radius - 8))
        
        # Fuse
        fuse_len = 15
        rad = math.radians(self.rotation)
        start_x = center[0] - (self.radius - 5) * math.sin(rad)
        start_y = center[1] - (self.radius - 5) * math.cos(rad)
        end_x = start_x + fuse_len * math.sin(rad)
        end_y = start_y - fuse_len * math.cos(rad)
        pygame.draw.line(surface, ORANGE, (start_x, start_y), (end_x, end_y), 3)

    def check_slice(self, slice_points):
        if len(slice_points) < 2:
            return False
        for i in range(len(slice_points) - 1):
            if line_circle_intersect(slice_points[i], slice_points[i+1], self.pos, self.radius):
                if not self.bomb_hit:
                    self.bomb_hit = True
                    self.sliced = True
                    return True
        return False

class FruitSpawner:
    def __init__(self):
        self.last_spawn_time = 0
        self.bomb_chance = 0.15
        self.current_interval = FRUIT_SPAWN_INTERVAL

    def spawn_if_ready(self, current_time, screen_width, screen_height):
        if current_time - self.last_spawn_time > self.current_interval:
            self.last_spawn_time = current_time
            self.current_interval = max(800, self.current_interval - 20)
            if random.random() < self.bomb_chance:
                return Bomb(screen_width, screen_height)
            else:
                return Fruit(screen_width, screen_height)
        return None
