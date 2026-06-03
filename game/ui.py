import pygame

class Button:
    def __init__(self, x, y, width, height, text, color=(70, 70, 120), hover_color=(100, 100, 170)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color

    def draw(self, surface, is_hovered=False):
        fill_color = self.hover_color if is_hovered else self.color
        pygame.draw.rect(surface, fill_color, self.rect, border_radius=12)
        
        border_color = tuple(min(255, c + 30) for c in fill_color)
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=12)
        
        font = pygame.font.Font(None, 36)
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_hovered_by(self, pos):
        if not pos:
            return False
        return self.rect.collidepoint(*pos)

    def check_gesture_click(self, cursor_pos, is_pinching):
        return self.is_hovered_by(cursor_pos) and is_pinching

class ScoreDisplay:
    def draw(self, surface, score):
        pill_rect = pygame.Rect(10, 10, 140, 70)
        pill_surf = pygame.Surface((pill_rect.width, pill_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(pill_surf, (0, 0, 0, 128), pill_surf.get_rect(), border_radius=15)
        surface.blit(pill_surf, pill_rect.topleft)
        
        small_font = pygame.font.Font(None, 24)
        large_font = pygame.font.SysFont(None, 48, bold=True)
        
        lbl_surf = small_font.render("SCORE", True, (200, 200, 200))
        score_surf = large_font.render(str(score), True, (255, 255, 255))
        
        surface.blit(lbl_surf, (25, 18))
        surface.blit(score_surf, (25, 38))

class LivesDisplay:
    def draw(self, surface, lives, max_lives):
        screen_w = surface.get_width()
        start_x = screen_w - 40 * max_lives - 10
        y = 35
        
        for i in range(max_lives):
            cx, cy = start_x + i * 40, y
            if i < lives:
                # Full heart (bright red circle with a small white shine)
                pygame.draw.circle(surface, (255, 30, 30), (cx, cy), 15)
                pygame.draw.circle(surface, (255, 255, 255), (cx - 5, cy - 5), 4)
            else:
                # Empty heart (dark outlined circle)
                pygame.draw.circle(surface, (50, 0, 0), (cx, cy), 15, width=2)
                pygame.draw.circle(surface, (0, 0, 0), (cx, cy), 13)

class GameUI:
    def __init__(self, screen_width, screen_height):
        self.w = screen_width
        self.h = screen_height
        cx = screen_width // 2
        
        self.start_btn = Button(cx - 100, screen_height // 2, 200, 50, "Start Game")
        self.quit_btn = Button(cx - 100, screen_height // 2 + 70, 200, 50, "Quit")
        
        self.restart_btn = Button(cx - 100, screen_height // 2 + 50, 200, 50, "Restart")
        self.quit_btn_go = Button(cx - 100, screen_height // 2 + 120, 200, 50, "Quit")
        
        self.score_display = ScoreDisplay()
        self.lives_display = LivesDisplay()

    def draw_hud(self, surface, score, lives):
        self.score_display.draw(surface, score)
        self.lives_display.draw(surface, lives, 3)

    def draw_main_menu(self, surface, cursor_pos, is_pinching):
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        title_font = pygame.font.SysFont(None, 80, bold=True)
        shadow_surf = title_font.render("GESTURE SLASH", True, (0, 0, 0))
        title_surf = title_font.render("GESTURE SLASH", True, (255, 200, 50))
        title_rect = title_surf.get_rect(center=(self.w // 2, self.h // 3))
        
        surface.blit(shadow_surf, (title_rect.x + 4, title_rect.y + 4))
        surface.blit(title_surf, title_rect)
        
        inst_font = pygame.font.Font(None, 32)
        inst_surf = inst_font.render("Pinch to select  |  Swipe to slice", True, (200, 200, 200))
        surface.blit(inst_surf, inst_surf.get_rect(center=(self.w // 2, self.h // 3 + 60)))
        
        self.start_btn.draw(surface, self.start_btn.is_hovered_by(cursor_pos))
        self.quit_btn.draw(surface, self.quit_btn.is_hovered_by(cursor_pos))
        
        if self.start_btn.check_gesture_click(cursor_pos, is_pinching):
            return "start"
        if self.quit_btn.check_gesture_click(cursor_pos, is_pinching):
            return "quit"
        return None

    def draw_game_over(self, surface, score, cursor_pos, is_pinching):
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((50, 0, 0, 180))
        surface.blit(overlay, (0, 0))
        
        title_font = pygame.font.SysFont(None, 80, bold=True)
        shadow_surf = title_font.render("GAME OVER", True, (0, 0, 0))
        title_surf = title_font.render("GAME OVER", True, (255, 50, 50))
        title_rect = title_surf.get_rect(center=(self.w // 2, self.h // 3 - 30))
        
        surface.blit(shadow_surf, (title_rect.x + 4, title_rect.y + 4))
        surface.blit(title_surf, title_rect)
        
        score_font = pygame.font.Font(None, 48)
        score_surf = score_font.render(f"Final Score: {score}", True, (255, 255, 255))
        surface.blit(score_surf, score_surf.get_rect(center=(self.w // 2, self.h // 3 + 40)))
        
        self.restart_btn.draw(surface, self.restart_btn.is_hovered_by(cursor_pos))
        self.quit_btn_go.draw(surface, self.quit_btn_go.is_hovered_by(cursor_pos))
        
        if self.restart_btn.check_gesture_click(cursor_pos, is_pinching):
            return "restart"
        if self.quit_btn_go.check_gesture_click(cursor_pos, is_pinching):
            return "quit"
        return None

    def draw_cursor(self, surface, cursor_pos, is_slicing):
        if not cursor_pos:
            return
            
        color = (255, 100, 100) if is_slicing else (255, 255, 255)
        radius = 12 if is_slicing else 8
        width = 4 if is_slicing else 2
        
        pygame.draw.circle(surface, color, cursor_pos, radius, width)
        pygame.draw.line(surface, color, (cursor_pos[0] - radius - 5, cursor_pos[1]), (cursor_pos[0] + radius + 5, cursor_pos[1]), 2)
        pygame.draw.line(surface, color, (cursor_pos[0], cursor_pos[1] - radius - 5), (cursor_pos[0], cursor_pos[1] + radius + 5), 2)
