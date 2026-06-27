"""
             FLAPPY BIRD — Python Project            
                Made with Pygame + OOP :                 
"""

import pygame
import random
import sys

# ── Initialize Pygame ─────
pygame.init()

# ═══════
#  CONSTANTS
# ═══════
SCREEN_W     = 480
SCREEN_H     = 640
FPS          = 60
GRAVITY      = 0.5
FLAP_POWER   = -9
PIPE_SPEED   = 3
PIPE_GAP     = 160
PIPE_SPACING = 220   # horizontal distance between pipes
GROUND_H     = 80

# Colors
SKY_TOP    = (113, 197, 233)
SKY_BOT    = (186, 232, 245)
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GREEN_DARK = (56,  142, 60)
GREEN_MID  = (76,  175, 80)
GREEN_LIT  = (129, 199, 132)
YELLOW     = (255, 214, 0)
YELLOW_LIT = (255, 241, 118)
YELLOW_DRK = (249, 168, 37)
RED        = (229, 57,  53)
BROWN      = (141, 110, 99)
BROWN_LIT  = (188, 152, 137)
GRASS_TOP  = (102, 187, 106)
GRASS_BOT  = (56,  142, 60)
ORANGE     = (255, 152, 0)
GREY_DARK  = (33,  33,  33)


# ══════════════
#  CLASS 1 — Bird
# ════════════
class Bird:
    """
    Represents the player-controlled bird.
    Encapsulation: all physics state is private/protected.
    """

    RADIUS = 18

    def __init__(self):
        self.__x   = 110                    # Private: x position (fixed)
        self.__y   = SCREEN_H // 2 - 60     # Private: y position
        self.__vy  = 0                      # Private: vertical velocity
        self.__angle = 0                    # Private: rotation angle
        self.__flap_frame = 0              # Private: wing animation timer
        self.__alive = True                # Private: alive flag

    # ── Getters (Encapsulation) ─────────
    @property
    def x(self):       return self.__x
    @property
    def y(self):       return self.__y
    @property
    def angle(self):   return self.__angle
    @property
    def alive(self):   return self.__alive
    @property
    def radius(self):  return self.RADIUS

    def flap(self):
        """Give the bird an upward boost."""
        self.__vy = FLAP_POWER
        self.__flap_frame = 10

    def update(self):
        """Apply gravity and update position each frame."""
        self.__vy += GRAVITY
        self.__vy  = min(self.__vy, 14)     # terminal velocity cap
        self.__y  += self.__vy

        # Rotation: nose-up on flap, nose-down on fall
        self.__angle = max(-30, min(self.__vy * 4, 80))

        if self.__flap_frame > 0:
            self.__flap_frame -= 1

        # Hit ground or ceiling
        if self.__y + self.RADIUS >= SCREEN_H - GROUND_H:
            self.__y     = SCREEN_H - GROUND_H - self.RADIUS
            self.__alive = False
        if self.__y - self.RADIUS <= 0:
            self.__y  = self.RADIUS
            self.__vy = 0

    def draw(self, surface: pygame.Surface):
        """Draw the bird with body, wing, eye and beak."""
        x, y = int(self.__x), int(self.__y)

        # Wing flap offset
        wing_dy = -6 if self.__flap_frame > 5 else 4

        # ── Wing ─────
        wing_surf = pygame.Surface((28, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(wing_surf, YELLOW_DRK, (0, 0, 28, 14))
        rotated_wing = pygame.transform.rotate(wing_surf, -self.__angle)
        rw = rotated_wing.get_rect(center=(x - 6, y + wing_dy))
        surface.blit(rotated_wing, rw)

        # ── Body ─────────────
        body_surf = pygame.Surface((self.RADIUS * 2 + 4, self.RADIUS * 2), pygame.SRCALPHA)
        pygame.draw.ellipse(body_surf, YELLOW,     (0, 0, self.RADIUS * 2 + 4, self.RADIUS * 2))
        pygame.draw.ellipse(body_surf, YELLOW_LIT, (4, 3, self.RADIUS * 2 - 4, self.RADIUS - 3))
        rotated_body = pygame.transform.rotate(body_surf, -self.__angle)
        rb = rotated_body.get_rect(center=(x, y))
        surface.blit(rotated_body, rb)

        # ── Eye ─────────────────
        eye_offset_x = int(8  * pygame.math.Vector2(1, 0).rotate(-self.__angle).x -
                           4  * pygame.math.Vector2(0, 1).rotate(-self.__angle).x)
        eye_offset_y = int(8  * pygame.math.Vector2(1, 0).rotate(-self.__angle).y -
                           8  * pygame.math.Vector2(0, 1).rotate(-self.__angle).y)
        ex, ey = x + eye_offset_x, y + eye_offset_y
        pygame.draw.circle(surface, WHITE,      (ex, ey),      6)
        pygame.draw.circle(surface, GREY_DARK,  (ex + 1, ey),  3)
        pygame.draw.circle(surface, WHITE,      (ex + 2, ey - 1), 1)

        # ── Beak ────────────
        bk_offset_x = int(16 * pygame.math.Vector2(1, 0).rotate(-self.__angle).x)
        bk_offset_y = int(16 * pygame.math.Vector2(1, 0).rotate(-self.__angle).y)
        bx, by_ = x + bk_offset_x, y + bk_offset_y
        pts = [
            (bx,      by_ - 3),
            (bx + 10, by_),
            (bx,      by_ + 4),
        ]
        pygame.draw.polygon(surface, ORANGE, pts)

    def get_rect(self) -> pygame.Rect:
        """Return collision rect (slightly smaller than visual)."""
        return pygame.Rect(
            self.__x - self.RADIUS + 5,
            self.__y - self.RADIUS + 5,
            self.RADIUS * 2 - 10,
            self.RADIUS * 2 - 10,
        )

    def kill(self):
        self.__alive = False


# 
#  CLASS 2 — Pipe (pair of top + bottom pipe)
# 
class Pipe:
    """
    A single pipe obstacle (top + bottom pair).
    Encapsulation: position and gap are private.
    """

    WIDTH = 58

    def __init__(self, x: int):
        self.__x        = x
        self.__gap_y    = random.randint(140, SCREEN_H - GROUND_H - 140)
        self.__passed   = False         # Private: scored flag
        self.__active   = True          # Private: still on screen

    # ── Getters 
    @property
    def x(self):       return self.__x
    @property
    def passed(self):  return self.__passed
    @property
    def active(self):  return self.__active
    @property
    def gap_y(self):   return self.__gap_y

    def update(self):
        """Move pipe leftward each frame."""
        self.__x -= PIPE_SPEED
        if self.__x + self.WIDTH < 0:
            self.__active = False

    def mark_passed(self):
        self.__passed = True

    def draw(self, surface: pygame.Surface):
        """Draw both top and bottom pipe with cap."""
        x    = int(self.__x)
        top  = self.__gap_y - PIPE_GAP // 2     # bottom edge of top pipe
        bot  = self.__gap_y + PIPE_GAP // 2     # top edge of bottom pipe
        cap  = 18                               # cap height
        cap_extra = 6                           # cap wider than pipe

        # ── TOP pipe body ──────────────────────────────
        pygame.draw.rect(surface, GREEN_DARK, (x, 0, self.WIDTH, top - cap))
        pygame.draw.rect(surface, GREEN_MID,  (x, 0, 10, top - cap))         # highlight
        # top pipe cap
        pygame.draw.rect(surface, GREEN_DARK,
                         (x - cap_extra, top - cap,
                          self.WIDTH + cap_extra * 2, cap),
                         border_radius=4)
        pygame.draw.rect(surface, GREEN_LIT,
                         (x - cap_extra + 2, top - cap + 2,
                          14, cap - 4))

        # ── BOTTOM pipe body ───────────────────────────
        pygame.draw.rect(surface, GREEN_DARK, (x, bot + cap, self.WIDTH, SCREEN_H - bot - cap))
        pygame.draw.rect(surface, GREEN_MID,  (x, bot + cap, 10, SCREEN_H - bot - cap))
        # bottom pipe cap
        pygame.draw.rect(surface, GREEN_DARK,
                         (x - cap_extra, bot,
                          self.WIDTH + cap_extra * 2, cap),
                         border_radius=4)
        pygame.draw.rect(surface, GREEN_LIT,
                         (x - cap_extra + 2, bot + 2,
                          14, cap - 4))

    def get_rects(self):
        """Return (top_rect, bottom_rect) for collision."""
        top = self.__gap_y - PIPE_GAP // 2
        bot = self.__gap_y + PIPE_GAP // 2
        cap_extra = 6
        top_rect = pygame.Rect(self.__x - cap_extra, 0,
                               self.WIDTH + cap_extra * 2, top)
        bot_rect = pygame.Rect(self.__x - cap_extra, bot,
                               self.WIDTH + cap_extra * 2,
                               SCREEN_H - bot)
        return top_rect, bot_rect


# 
#  CLASS 3 — Cloud (decoration)
# 
class Cloud:
    """Simple drifting background cloud."""

    def __init__(self, x=None):
        self.__x     = x if x else random.randint(0, SCREEN_W)
        self.__y     = random.randint(40, 200)
        self.__speed = random.uniform(0.3, 0.7)
        self.__size  = random.randint(22, 40)

    def update(self):
        self.__x -= self.__speed
        if self.__x + self.__size * 2.5 < 0:
            self.__x = SCREEN_W + self.__size
            self.__y = random.randint(40, 200)

    def draw(self, surface: pygame.Surface):
        x, y, r = int(self.__x), int(self.__y), self.__size
        cloud_color = (255, 255, 255, 200)
        for cx, cy, cr in [(x, y, r), (x+r, y-r//3, int(r*0.75)),
                            (x+int(r*1.6), y, int(r*0.65))]:
            pygame.draw.circle(surface, (240, 248, 255), (cx, cy), cr)
        pygame.draw.circle(surface, (255, 255, 255), (x, y), r)


# 
#  CLASS 4 — ScoreBoard (Encapsulation)
# 
class ScoreBoard:
    """
    Tracks current score and best score.
    Encapsulation: scores are private with public getters.
    """

    def __init__(self):
        self.__score = 0
        self.__best  = 0

    @property
    def score(self): return self.__score
    @property
    def best(self):  return self.__best

    def increment(self):
        self.__score += 1
        if self.__score > self.__best:
            self.__best = self.__score

    def reset(self):
        self.__score = 0

    def draw(self, surface: pygame.Surface, font_big, font_med):
        """Draw score at top center of screen."""
        # Shadow
        shadow = font_big.render(str(self.__score), True, (0, 0, 0, 120))
        sr = shadow.get_rect(center=(SCREEN_W // 2 + 2, 62))
        surface.blit(shadow, sr)
        # Main
        txt = font_big.render(str(self.__score), True, WHITE)
        tr  = txt.get_rect(center=(SCREEN_W // 2, 60))
        surface.blit(txt, tr)


#
#  CLASS 5 — Game (main controller)
#
class Game:
    """
    Main game controller.
    Encapsulation: all game state is private.
    Manages game loop, states, rendering.
    """

    STATE_IDLE    = "idle"
    STATE_PLAYING = "playing"
    STATE_OVER    = "over"

    def __init__(self):
        self.__screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(" Flappy Bird — Python Project")
        self.__clock   = pygame.time.Clock()
        self.__state   = self.STATE_IDLE

        # Fonts
        self.__font_big  = pygame.font.SysFont("Arial", 52, bold=True)
        self.__font_med  = pygame.font.SysFont("Arial", 28, bold=True)
        self.__font_sm   = pygame.font.SysFont("Arial", 20)

        # Permanent objects
        self.__clouds    = [Cloud(random.randint(0, SCREEN_W)) for _ in range(5)]
        self.__scoreboard = ScoreBoard()

        # Game objects (reset each round)
        self.__bird  = None
        self.__pipes = []
        self.__pipe_timer = 0
        self.__ground_x   = 0     # scrolling ground offset

        # Sky gradient surface (pre-render once)
        self.__sky = self.__make_sky()

    # ── Private helpers ─
    def __make_sky(self) -> pygame.Surface:
        sky = pygame.Surface((SCREEN_W, SCREEN_H))
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
            g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
            b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
            pygame.draw.line(sky, (r, g, b), (0, y), (SCREEN_W, y))
        return sky

    def __reset(self):
        self.__bird        = Bird()
        self.__pipes       = []
        self.__pipe_timer  = 0
        self.__scoreboard.reset()

    def __draw_ground(self):
        gx = int(self.__ground_x)
        gy = SCREEN_H - GROUND_H

        # Brown dirt
        pygame.draw.rect(self.__screen, BROWN,
                         (0, gy, SCREEN_W, GROUND_H))
        pygame.draw.rect(self.__screen, BROWN_LIT,
                         (0, gy, SCREEN_W, 6))

        # Green grass strip
        pygame.draw.rect(self.__screen, GRASS_TOP,
                         (0, gy - 4, SCREEN_W, 12))

        # Grass blades (scrolling)
        blade_w, blade_sp = 10, 22
        for i in range(-1, SCREEN_W // blade_sp + 2):
            bx = (i * blade_sp + gx % blade_sp)
            pygame.draw.rect(self.__screen, GRASS_BOT,
                             (bx, gy - 4, blade_w // 2, 8))

        # Dirt stripes
        pygame.draw.rect(self.__screen, BROWN_LIT,
                         (0, gy + 20, SCREEN_W, 4))

    def __draw_idle_screen(self):
        # Title box
        box = pygame.Surface((320, 70), pygame.SRCALPHA)
        box.fill((0, 0, 0, 120))
        self.__screen.blit(box, (SCREEN_W // 2 - 160, SCREEN_H // 2 - 120))
        title = self.__font_big.render("Flappy Bird", True, YELLOW)
        tr = title.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 85))
        self.__screen.blit(title, tr)

        # Instruction
        inst = self.__font_med.render("Press SPACE or Click to Start", True, WHITE)
        ir = inst.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 20))
        self.__screen.blit(inst, ir)

        # Controls hint
        h1 = self.__font_sm.render("SPACE / Click  =  Flap", True, (220, 220, 220))
        h2 = self.__font_sm.render("ESC  =  Quit", True, (220, 220, 220))
        self.__screen.blit(h1, h1.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 20)))
        self.__screen.blit(h2, h2.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 48)))

    def __draw_over_screen(self):
        # Dark overlay
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.__screen.blit(overlay, (0, 0))

        # Panel
        panel = pygame.Surface((320, 200), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 160))
        self.__screen.blit(panel, (SCREEN_W // 2 - 160, SCREEN_H // 2 - 120))

        over  = self.__font_big.render("Game Over!", True, RED)
        self.__screen.blit(over, over.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 90)))

        sc = self.__font_med.render(f"Score : {self.__scoreboard.score}", True, WHITE)
        bs = self.__font_med.render(f"Best  : {self.__scoreboard.best}",  True, YELLOW)
        rt = self.__font_sm.render("Press SPACE or Click to Restart", True, (200, 200, 200))

        self.__screen.blit(sc, sc.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 30)))
        self.__screen.blit(bs, bs.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 10)))
        self.__screen.blit(rt, rt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 60)))

    def __handle_flap(self):
        if self.__state == self.STATE_IDLE:
            self.__reset()
            self.__state = self.STATE_PLAYING
        elif self.__state == self.STATE_PLAYING:
            self.__bird.flap()
        elif self.__state == self.STATE_OVER:
            self.__reset()
            self.__state = self.STATE_PLAYING

    # ── Public: main game loop ───
    def run(self):
        while True:
            # ── Events ─
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        self.__handle_flap()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.__handle_flap()

            # ── Update 
            if self.__state == self.STATE_PLAYING:
                self.__bird.update()

                # Spawn pipes
                self.__pipe_timer += 1
                if self.__pipe_timer >= PIPE_SPACING // PIPE_SPEED:
                    self.__pipes.append(Pipe(SCREEN_W + 20))
                    self.__pipe_timer = 0

                # Update pipes
                for pipe in self.__pipes:
                    pipe.update()
                    # Score when pipe passes bird
                    if not pipe.passed and pipe.x + Pipe.WIDTH < self.__bird.x:
                        pipe.mark_passed()
                        self.__scoreboard.increment()

                # Remove off-screen pipes
                self.__pipes = [p for p in self.__pipes if p.active]

                # Collision check
                bird_rect = self.__bird.get_rect()
                for pipe in self.__pipes:
                    top_r, bot_r = pipe.get_rects()
                    if bird_rect.colliderect(top_r) or bird_rect.colliderect(bot_r):
                        self.__bird.kill()

                if not self.__bird.alive:
                    self.__state = self.STATE_OVER

                # Scroll ground
                self.__ground_x -= PIPE_SPEED
                if self.__ground_x <= -22:
                    self.__ground_x = 0

            # Update clouds always
            for cloud in self.__clouds:
                cloud.update()

            # ── Draw 
            self.__screen.blit(self.__sky, (0, 0))

            for cloud in self.__clouds:
                cloud.draw(self.__screen)

            for pipe in self.__pipes:
                pipe.draw(self.__screen)

            self.__draw_ground()

            if self.__bird:
                self.__bird.draw(self.__screen)

            if self.__state == self.STATE_PLAYING:
                self.__scoreboard.draw(self.__screen, self.__font_big, self.__font_med)

            if self.__state == self.STATE_IDLE:
                # Draw a demo bird on idle screen
                if not self.__bird:
                    self.__bird = Bird()
                self.__bird.draw(self.__screen)
                self.__draw_idle_screen()

            if self.__state == self.STATE_OVER:
                self.__draw_over_screen()

            pygame.display.flip()
            self.__clock.tick(FPS)


# 
#  ENTRY POINT
# 
if __name__ == "__main__":
    game = Game()
    game.run()
