import pygame
import subprocess
import json

pygame.init()

# === Variables ===
# Ball
Ball_color = (0, 0, 126)
Ball_x_pos, Ball_y_pos = 0, 0
Ball_x_vel, Ball_y_vel = 2, 2
Ball_radius = 10

# Bat
Bat_color = (0, 0, 0)
Bat_x_pos, Bat_y_pos = 400, 575
Bat_width, Bat_height = 150, 25
Bat_stroke = 10
bat_speed = 25

# Brick
brick_rows = 5
brick_cols = 8
brick_width = 80
brick_height = 30
brick_gap = 10
start_x = 50
start_y = 50

# Screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("LLM Pong Game")
clock = pygame.time.Clock()

# === LLM Controller ===
def get_llm_direction(ball_x, ball_y, bat_x, bat_width):
    prompt = f'''
You are controlling a paddle in a brick breaker game.
The ball is at x={ball_x}, y={ball_y}.
The paddle is at x={bat_x}, width={bat_width}.
Decide to move the paddle "LEFT", "RIGHT", or "NONE" to keep the ball above it.

Respond ONLY in this JSON format:
{{"response": "LEFT"}}
'''

    result = subprocess.run(
        ["ollama", "run", "gemma3:1b", prompt],
        capture_output=True,
        text=True
    )

    json_start = result.stdout.find("{")
    if json_start == -1:
        raise ValueError("No JSON found in response.")

    json_str = result.stdout[json_start:].strip("`\n ")
    data = json.loads(json_str)

    return data["response"]

# === Classes ===
class Brick:
    def __init__(self, color, x, y, wdh, hgt, border):
        self.color = color
        self.x = x
        self.y = y
        self.wdh = wdh
        self.hgt = hgt
        self.border = border

    def collision_brick(self, Ball):
        if (Ball.y - Ball.radius <= self.y + self.hgt) and (Ball.y + Ball.radius >= self.y) and \
           (Ball.x + Ball.radius >= self.x) and (Ball.x <= self.x + self.wdh):
            overlapLeft = abs((Ball.x + Ball.radius) - self.x)
            overlapRight = abs((Ball.x - Ball.radius) - (self.x + self.wdh))
            overlapTop = abs((Ball.y - Ball.radius) - self.y)
            overlapBottom = abs((Ball.y + Ball.radius) - (self.y + self.hgt))
            min_overlap = min(overlapBottom, overlapTop, overlapRight, overlapLeft)

            if min_overlap == overlapLeft:
                Ball.x = self.x - Ball.radius
                Ball.x_vel *= -1
            elif min_overlap == overlapRight:
                Ball.x = self.x + self.wdh + Ball.radius
                Ball.x_vel *= -1
            elif min_overlap == overlapTop:
                Ball.y = self.y - Ball.radius
                Ball.y_vel *= -1
            elif min_overlap == overlapBottom:
                Ball.y = self.y + self.hgt + Ball.radius
                Ball.y_vel *= -1
            return True
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.wdh, self.hgt), self.border)

class Ball:
    def __init__(self, color, x, y, x_vel, y_vel, radius):
        self.color = color
        self.x = x
        self.y = y
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.radius = radius

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)

    def bounce(self):
        Over_font = pygame.font.Font(None, 100)
        if self.x > WIDTH or self.x < 0:
            self.x_vel *= -1
        if self.y < 0:
            self.y_vel *= -1
        if self.y > HEIGHT:
            screen.fill((126, 0, 0))
            score_text2 = Over_font.render(f"GAME OVER", True, (0, 0, 0))
            screen.blit(score_text2, (200, 300))
            pygame.display.update()
            pygame.time.delay(2000)
            self.x, self.y = 0, 0
            return True
        return False

class Bat:
    def __init__(self, color, x_bat, y_bat, wdt, hgt, speed, border):
        self.color = color
        self.x_bat = x_bat
        self.y_bat = y_bat
        self.wdt = wdt
        self.hgt = hgt
        self.speed = speed
        self.border = border

    def move(self, direction=None):
        if direction == "RIGHT":
            self.x_bat += self.speed
        elif direction == "LEFT":
            self.x_bat -= self.speed

        self.x_bat = max(0, min(WIDTH - self.wdt, self.x_bat))

    def collision(self, Ball):
        if (Ball.y + Ball.radius >= HEIGHT - self.hgt) and (Ball.y + Ball.radius <= HEIGHT):
            if self.x_bat <= Ball.x <= self.x_bat + self.wdt:
                Ball.y_vel *= -1
                return True
        return False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x_bat, self.y_bat, self.wdt, self.hgt), self.border)

class GameManager:
    def __init__(self):
        self.score = 0

    def updateScore(self, collision, coll_brick, bounced_out):
        if collision:
            self.score += 1
        elif coll_brick:
            self.score += 5
        elif bounced_out:
            self.score = 0

# === Game Objects ===
ball = Ball(Ball_color, Ball_x_pos, Ball_y_pos, Ball_x_vel, Ball_y_vel, Ball_radius)
bat = Bat(Bat_color, Bat_x_pos, Bat_y_pos, Bat_width, Bat_height, bat_speed, Bat_stroke)
brick = Brick((0, 0, 0), 300, 300, 100, 50, 5)
manager = GameManager()

# === Game Loop ===
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 126, 0))

    # === LLM Decision ===
    try:
        direction = get_llm_direction(ball.x, ball.y, bat.x_bat, bat.wdt)
    except Exception as e:
        print("LLM error:", e)
        direction = None

    bat.move(direction)
    ball.move()

    bounced_out = ball.bounce()
    collision = bat.collision(ball)
    brick_collision = brick.collision_brick(ball)

    brick.draw(screen)
    ball.draw(screen)
    bat.draw(screen)

    manager.updateScore(collision, brick_collision, bounced_out)
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {manager.score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.update()
    clock.tick(30)

pygame.quit()
