# snake_oop.py
# Python 3.8+ | Turtle OOP Snake Game
# Controls: W/A/S/D or Arrow Keys

import time
import random
from turtle import Turtle, Screen

# ---------------------------- Config ---------------------------- #
WIDTH, HEIGHT = 600, 600
BG_COLOR = "black"
SNAKE_COLOR = "white"
FOOD_COLOR = "DeepSkyBlue2"
TEXT_COLOR = "white"
MOVE_DISTANCE = 20
START_POSITIONS = [(0, 0), (-20, 0), (-40, 0)]
UP, DOWN, LEFT, RIGHT = 90, 270, 180, 0
BORDER_LIMIT_X = (WIDTH // 2) - 10
BORDER_LIMIT_Y = (HEIGHT // 2) - 10
HIGHSCORE_FILE = "highscore.txt"

# ---------------------------- Snake ---------------------------- #
class Snake:
    """Snake composed of segments; handles movement & growth."""
    def __init__(self, color=SNAKE_COLOR):
        self.segments = []
        self._create_snake(color)
        self.head = self.segments[0]

    def _create_snake(self, color):
        for pos in START_POSITIONS:
            self._add_segment(pos, color)

    def _add_segment(self, position, color):
        seg = Turtle("square")
        seg.penup()
        seg.color(color)
        seg.goto(position)
        self.segments.append(seg)

    def extend(self):
        """Add a new segment to the snake at the tail."""
        self._add_segment(self.segments[-1].position(), self.segments[-1].pencolor())

    def move(self):
        """Move snake forward by moving tail segments first, then head."""
        for idx in range(len(self.segments) - 1, 0, -1):
            new_x = self.segments[idx - 1].xcor()
            new_y = self.segments[idx - 1].ycor()
            self.segments[idx].goto(new_x, new_y)
        self.head.forward(MOVE_DISTANCE)

    # Direction guards to avoid reversing into itself
    def up(self):
        if self.head.heading() != DOWN:
            self.head.setheading(UP)

    def down(self):
        if self.head.heading() != UP:
            self.head.setheading(DOWN)

    def left(self):
        if self.head.heading() != RIGHT:
            self.head.setheading(LEFT)

    def right(self):
        if self.head.heading() != LEFT:
            self.head.setheading(RIGHT)

    def reset(self):
        """Send old snake segments off-screen and re-init."""
        for seg in self.segments:
            seg.goto(1000, 1000)
        self.segments.clear()
        self._create_snake(SNAKE_COLOR)
        self.head = self.segments[0]

# ---------------------------- Food ---------------------------- #
class Food(Turtle):
    """Food is a turtle circle appearing at random positions."""
    def __init__(self, color=FOOD_COLOR):
        super().__init__("circle")
        self.penup()
        self.color(color)
        self.shapesize(stretch_wid=0.6, stretch_len=0.6)  # smaller dot
        self.speed("fastest")
        self.refresh()

    def refresh(self):
        """Place food at a new random grid-aligned location."""
        # Align to 20px grid for clean collision and movement
        x = random.randrange(-BORDER_LIMIT_X + 20, BORDER_LIMIT_X - 20, 20)
        y = random.randrange(-BORDER_LIMIT_Y + 20, BORDER_LIMIT_Y - 20, 20)
        self.goto(x, y)

# ---------------------------- Scoreboard ---------------------------- #
class Scoreboard(Turtle):
    """Displays score and high score; persists high score to file."""
    def __init__(self, color=TEXT_COLOR):
        super().__init__()
        self.score = 0
        self.high_score = self._load_high_score()
        self.color(color)
        self.hideturtle()
        self.penup()

        # --- top-right position (with small margins) ---
        self._margin_x = 16
        self._margin_y = 24
        self._top_right = ((WIDTH // 2) - self._margin_x, (HEIGHT // 2) - self._margin_y)
        self.goto(*self._top_right)

        self._draw()

    def _load_high_score(self):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                return int(f.read().strip())
        except Exception:
            return 0

    def _save_high_score(self):
        try:
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(self.high_score))
        except Exception:
            pass  # ignore file errors silently

    def _draw(self):
        # Right-align so growing text stays hugged to top-right
        self.clear()
        self.write(
            f"Score: {self.score}   High Score: {self.high_score}",
            align="right",
            font=("Courier", 18, "bold"),
        )

    def increase(self, points=1):
        self.score += points
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()
        self._draw()

    def reset(self):
        self.score = 0
        # ensure we’re still at top-right even after any prior writes
        self.goto(*self._top_right)
        self._draw()

    def game_over(self):
        # Temporarily write in the center, then restore to top-right
        old_pos = self.position()
        old_heading = self.heading()

        self.goto(0, 0)
        self.write("GAME OVER", align="center", font=("Courier", 24, "bold"))
        self.goto(0, -30)
        self.write("Press Space to Restart", align="center", font=("Courier", 14, "normal"))

        # restore scoreboard cursor to top-right (and original heading just in case)
        self.goto(*self._top_right)


# ---------------------------- Game ---------------------------- #
class Game:
    """Main game orchestrator: input, loop, collisions, and state."""
    def __init__(self):
        # Screen setup
        self.screen = Screen()
        self.screen.setup(width=WIDTH, height=HEIGHT)
        self.screen.bgcolor(BG_COLOR)
        self.screen.title("Snake (Turtle + OOP)")
        self.screen.tracer(0)  # manual screen updates

        # Entities
        self.snake = Snake()
        self.food = Food()
        self.scoreboard = Scoreboard()

        # Input bindings
        self.screen.listen()
        self.screen.onkey(self.snake.up, "Up")
        self.screen.onkey(self.snake.down, "Down")
        self.screen.onkey(self.snake.left, "Left")
        self.screen.onkey(self.snake.right, "Right")
        self.screen.onkey(self.snake.up, "w")
        self.screen.onkey(self.snake.down, "s")
        self.screen.onkey(self.snake.left, "a")
        self.screen.onkey(self.snake.right, "d")
        self.screen.onkey(self.restart, "space")

        # Game loop control
        self.running = True
        self.speed_delay = 0.1  # lower is faster

    # -------------------- Collision Helpers -------------------- #
    def _hit_wall(self):
        x, y = self.snake.head.xcor(), self.snake.head.ycor()
        return abs(x) > BORDER_LIMIT_X or abs(y) > BORDER_LIMIT_Y

    def _hit_food(self):
        return self.snake.head.distance(self.food) < 15

    def _hit_self(self):
        # skip head (index 0), check collision with any segment
        for seg in self.snake.segments[1:]:
            if self.snake.head.distance(seg) < 10:
                return True
        return False

    # -------------------- Game Flow -------------------- #
    def restart(self):
        """Restart game state after game over."""
        if not self.running:
            self.scoreboard.clear()
            self.scoreboard.reset()
            self.snake.reset()
            self.food.refresh()
            self.speed_delay = 0.1
            self.running = True
            self.loop()  # resume loop

    def loop(self):
        """Main game loop."""
        while self.running:
            self.screen.update()
            time.sleep(self.speed_delay)
            self.snake.move()

            # Food collision
            if self._hit_food():
                self.food.refresh()
                self.snake.extend()
                self.scoreboard.increase(1)
                # Slightly increase difficulty
                self.speed_delay = max(0.05, self.speed_delay - 0.002)

            # Wall or self collision
            if self._hit_wall() or self._hit_self():
                self.running = False
                self.scoreboard.game_over()

        # Keep window responsive to restart or close
        self.screen.update()

    def run(self):
        self.loop()
        self.screen.mainloop()

# ---------------------------- Entry ---------------------------- #
if __name__ == "__main__":
    Game().run()
