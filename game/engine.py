import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, MAX_LIVES, STATE_MENU, STATE_PLAYING, STATE_GAME_OVER, DARK_BG
from game.fruit import FruitSpawner, Bomb, Fruit
from game.effects import EffectsManager
from game.ui import GameUI

class GameEngine:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("GestureSlash")
        self.clock = pygame.time.Clock()
        
        self.fruits = []
        self.spawner = FruitSpawner()
        self.effects = EffectsManager()
        self.ui = GameUI(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        self.score = 0
        self.lives = MAX_LIVES
        self.state = STATE_MENU
        
        self.slice_points = []
        self.running = True

    def reset_game(self):
        self.score = 0
        self.lives = MAX_LIVES
        self.fruits = []
        self.slice_points = []
        self.spawner = FruitSpawner()
        self.effects = EffectsManager()
        
    def run(self, gesture_provider):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.running = False
            
            gesture = gesture_provider()
            current_time = pygame.time.get_ticks()
            
            self.update(gesture, current_time)
            self.draw(gesture)
            
            self.clock.tick(FPS)
            
        pygame.quit()

    def update(self, gesture, current_time):
        if self.state == STATE_MENU:
            if gesture.cursor_pos and gesture.is_pinching:
                # We use the UI to check clicks implicitly by passing cursor_pos during draw,
                # but to structurally separate logic properly we check directly here too.
                # Actually, the prompt says "ui.draw_main_menu() ... actually just handle button logic here"
                # Since draw_main_menu handles input and return value, I'll process the return inside draw for menu
                # or just process a phantom click check. Let's process the return inside draw and let it set states.
                # Better: simulate a direct check here without drawing.
                if self.ui.start_btn.check_gesture_click(gesture.cursor_pos, gesture.is_pinching):
                    self.state = STATE_PLAYING
                    self.reset_game()
                elif self.ui.quit_btn.check_gesture_click(gesture.cursor_pos, gesture.is_pinching):
                    self.running = False

        elif self.state == STATE_PLAYING:
            if gesture.is_slicing and gesture.cursor_pos:
                self.slice_points.append(gesture.cursor_pos)
                if len(self.slice_points) > 8:
                    self.slice_points.pop(0)
            else:
                self.slice_points.clear()

            new_fruit = self.spawner.spawn_if_ready(current_time, SCREEN_WIDTH, SCREEN_HEIGHT)
            if new_fruit:
                self.fruits.append(new_fruit)

            for fruit in self.fruits[:]:
                fruit.update(SCREEN_HEIGHT)
                if fruit.sliced or fruit.off_screen:
                    if fruit.missed and not fruit.sliced:
                        self.lives -= 1
                    if fruit in self.fruits:
                        self.fruits.remove(fruit)
                    continue
                
                if len(self.slice_points) >= 2:
                    if fruit.check_slice(self.slice_points):
                        if isinstance(fruit, Bomb):
                            self.lives = 0
                        else:
                            self.score += 10
                            self.effects.add_slice_effect(int(fruit.pos[0]), int(fruit.pos[1]), fruit.color, fruit.radius)
                        if fruit in self.fruits:
                            self.fruits.remove(fruit)

            self.effects.update_all()
            self.effects.update_slice_trail(gesture.cursor_pos, gesture.is_slicing)

            if self.lives <= 0:
                self.state = STATE_GAME_OVER

        elif self.state == STATE_GAME_OVER:
            if gesture.cursor_pos and gesture.is_pinching:
                if self.ui.restart_btn.check_gesture_click(gesture.cursor_pos, gesture.is_pinching):
                    self.reset_game()
                    self.state = STATE_PLAYING
                elif self.ui.quit_btn_go.check_gesture_click(gesture.cursor_pos, gesture.is_pinching):
                    self.running = False

    def draw(self, gesture):
        self.screen.fill(DARK_BG)
        
        if self.state == STATE_PLAYING:
            for fruit in self.fruits:
                fruit.draw(self.screen)
            self.effects.draw_all(self.screen)
            self.ui.draw_hud(self.screen, self.score, self.lives)
            self.ui.draw_cursor(self.screen, gesture.cursor_pos, gesture.is_slicing)
            
        elif self.state == STATE_MENU:
            action = self.ui.draw_main_menu(self.screen, gesture.cursor_pos, gesture.is_pinching)
            # The prompt requested handling ui logic in update, but ui.draw_main_menu returns the action.
            # State is also handled in update via implicit check. I'll leave the return value here as purely aesthetic logic handling.
            
        elif self.state == STATE_GAME_OVER:
            action = self.ui.draw_game_over(self.screen, self.score, gesture.cursor_pos, gesture.is_pinching)
            
        pygame.display.flip()
