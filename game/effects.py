import pygame
import random
import math
from collections import deque

class SliceTrail:
    def __init__(self):
        self.points = deque(maxlen=18)

    def update(self, cursor_pos, is_slicing):
        if is_slicing and cursor_pos:
            self.points.append([cursor_pos[0], cursor_pos[1], 18])
            
        # Age all points
        for p in self.points:
            p[2] -= 1
            
        # Remove dead points
        while self.points and self.points[0][2] <= 0:
            self.points.popleft()

    def draw(self, surface):
        if len(self.points) < 2:
            return
            
        trail_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        points_list = list(self.points)
        
        for i in range(len(points_list) - 1):
            p1 = points_list[i]
            p2 = points_list[i+1]
            
            avg_age = (p1[2] + p2[2]) / 2.0
            alpha = int((avg_age / 18.0) * 255)
            width = max(1, int((avg_age / 18.0) * 5))
            color = (180, 240, 255, alpha)
            
            pygame.draw.line(trail_surface, color, (p1[0], p1[1]), (p2[0], p2[1]), width)
            pygame.draw.circle(trail_surface, color, (int(p1[0]), int(p1[1])), width // 2)
            
        surface.blit(trail_surface, (0, 0))

class ParticleExplosion:
    def __init__(self, x, y, color):
        self.particles = []
        for _ in range(16):
            life = random.randint(20, 35)
            self.particles.append({
                'pos': [x, y],
                'vel': [random.uniform(-5, 5), random.uniform(-5, 5)],
                'life': life,
                'max_life': life,
                'size': random.randint(3, 7),
                'color': color
            })

    def update(self):
        for p in self.particles:
            p['vel'][1] += 0.2  # Gravity
            p['pos'][0] += p['vel'][0]
            p['pos'][1] += p['vel'][1]
            p['life'] -= 1
            
        self.particles = [p for p in self.particles if p['life'] > 0]
        return len(self.particles) > 0

    def draw(self, surface):
        for p in self.particles:
            alpha = int(255 * (p['life'] / p['max_life']))
            color_with_alpha = (*p['color'][:3], alpha)
            
            size = p['size'] * 2
            particle_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color_with_alpha, (p['size'], p['size']), p['size'])
            surface.blit(particle_surf, (int(p['pos'][0] - p['size']), int(p['pos'][1] - p['size'])))

class SlicedHalf:
    def __init__(self, x, y, color, radius, direction):
        self.pos = [x, y]
        self.vel = [direction * 3, -4]
        self.color = color
        self.radius = radius
        self.direction = direction
        self.life = 40
        self.gravity = 0.35

    def update(self):
        self.vel[1] += self.gravity
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.life -= 1
        return self.life > 0

    def draw(self, surface):
        alpha = int(255 * (max(0, self.life) / 40.0))
        width = int(self.radius * 2 + 4)
        height = int(self.radius * 2 + 4)
        local_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        points = []
        num_points = 10
        start_angle = math.pi / 2 if self.direction == 1 else -math.pi / 2
        end_angle = start_angle + math.pi
        
        center_x, center_y = self.radius + 2, self.radius + 2
        
        for i in range(num_points + 1):
            angle = start_angle + (end_angle - start_angle) * (i / num_points)
            px = center_x + self.radius * math.cos(angle)
            py = center_y + self.radius * math.sin(angle)
            points.append((px, py))
            
        color_with_alpha = (*self.color[:3], alpha)
        if len(points) >= 3:
            pygame.draw.polygon(local_surf, color_with_alpha, points)
            
        surface.blit(local_surf, (int(self.pos[0] - center_x), int(self.pos[1] - center_y)))

class EffectsManager:
    def __init__(self):
        self.explosions = []
        self.halves = []
        self.slice_trail = SliceTrail()

    def add_slice_effect(self, x, y, color, radius):
        self.explosions.append(ParticleExplosion(x, y, color))
        self.halves.append(SlicedHalf(x, y, color, radius, -1))
        self.halves.append(SlicedHalf(x, y, color, radius, 1))

    def update_slice_trail(self, cursor_pos, is_slicing):
        self.slice_trail.update(cursor_pos, is_slicing)

    def update_all(self):
        self.explosions = [e for e in self.explosions if e.update()]
        self.halves = [h for h in self.halves if h.update()]

    def draw_all(self, surface):
        for h in self.halves:
            h.draw(surface)
        for e in self.explosions:
            e.draw(surface)
        self.slice_trail.draw(surface)
