# all dependencies should already be available in the micropython version on the board, no pip install required
import math
import random
import gc9a01
import utime
import vga1_bold_16x32 as font
from machine import Pin, SPI


### Game Settings ###
initial_length = 2
refresh_rate = 70  # milliseconds
pixel_size = 10  # must be even
###               ###


class Dir:
    left = (-1, 0)
    up = (0, -1)
    right = (1, 0)
    down = (0, 1)


class Food:

    def __init__(self, border_radius):
        self.x: int = border_radius - 1
        self.y: int = 0
        self.border_radius = border_radius

    def move(self, snake: 'Snake'):
        # random point in a circle
        # https://stackoverflow.com/questions/5837572/generate-a-random-point-within-a-circle-uniformly

        r = (self.border_radius - 1) * math.sqrt(random.randint(0, 1000) / 1000.0)
        theta = (random.randint(0, 1000) / 1000.0) * 2 * math.pi
        x = round(r * math.cos(theta))
        y = round(r * math.sin(theta))
        if [x, y] in snake.pos_hist:
            self.move(snake)
        else:
            self.x, self.y = x, y


class Snake:

    def __init__(self, border_radius):
        self.x = 0
        self.y = 0
        self.prev_x = 0
        self.prev_y = 0
        self.border_radius = border_radius
        self.pos_hist = []
        self.length = initial_length
        self.dir = None
        self.reset()

    def step(self):
        self._take_step()
        self.pos_hist = self.pos_hist[:self.length]
        self.pos_hist = [[self.x, self.y]] + self.pos_hist

    @property
    def is_overlapping(self):
        return [self.x, self.y] in self.pos_hist[1:]

    def reset(self):
        self.x = 0
        self.y = 0
        self.prev_x = 0
        self.prev_y = 0
        self.dir = Dir.left
        self.pos_hist = [[i, 0] for i in range(self.length)]

    def _take_step(self):
        next_x = self.x + self.dir[0]
        next_y = self.y + self.dir[1]

        if math.sqrt(next_x ** 2 + next_y ** 2) > self.border_radius:
            if self.dir in [Dir.left, Dir.right]:
                next_x = -1 * self.x
            else:
                next_y = -1 * self.y

        self.x = next_x
        self.y = next_y


class TFTDisplay:
    screen_radius = 120
    center_x = screen_radius
    center_y = screen_radius

    def __init__(self):
        # ======== Setup display ===========
        self.char_width = 16
        self.char_height = 32
        self.char_height = 32
        spi = SPI(1, baudrate=40000000, sck=Pin(10), mosi=Pin(11))
        self.tft = gc9a01.GC9A01(
            spi,
            240,
            240,
            reset=Pin(12, Pin.OUT),
            cs=Pin(9, Pin.OUT),
            dc=Pin(8, Pin.OUT),
            backlight=Pin(13, Pin.OUT),
            rotation=0)

        self.tft.init()
        self.tft.rotation(0)
        self.reset()

        # ------joystck pin declaration-----
        self.joyRight = Pin(17, Pin.IN)
        self.joyDown = Pin(18, Pin.IN)
        self.joySel = Pin(19, Pin.IN)
        self.joyLeft = Pin(20, Pin.IN)
        self.joyUp = Pin(21, Pin.IN)

    def reset(self):
        self.tft.fill(gc9a01.BLACK)
        utime.sleep(0.5)

    def get_key_state(self):
        if self.joyRight.value() == 0:
            return Dir.right

        elif self.joyDown.value() == 0:
            return Dir.down

        elif self.joyLeft.value() == 0:
            return Dir.left

        elif self.joyUp.value() == 0:
            return Dir.up

        elif self.joySel.value() == 0:
            return 'select'

    def draw_snake(self, snake: Snake):
        if self.trans_scale(snake.pos_hist[-1][0]) < self.screen_radius * 2 \
                and \
                self.trans_scale(snake.pos_hist[-1][1]) < self.screen_radius * 2:
            x = self.trans_scale(snake.pos_hist[-1][0])
            y = self.trans_scale(snake.pos_hist[-1][1])
            self.tft.fill_rect(x, y, self.scale(1), self.scale(1), gc9a01.BLACK)
        x = self.trans_scale(snake.x)
        y = self.trans_scale(snake.y)

        if self.trans_scale(snake.x) < self.screen_radius * 2 \
                and \
                self.trans_scale(snake.y) < self.screen_radius * 2:
            self.tft.fill_rect(x, y, self.scale(1), self.scale(1), gc9a01.BLUE)

    def draw_food(self, food: Food):
        x = self.trans_scale(food.x)
        y = self.trans_scale(food.y)
        self.tft.fill_rect(x, y, self.scale(1), self.scale(1), gc9a01.YELLOW)

    def get_text_x(self, text):
        return round(self.screen_radius - ((self.char_width * len(text)) / 2))

    def get_text_y(self, line_num):
        top_padding = 30
        line_padding = 8
        return round(top_padding + (line_num * (self.char_height + line_padding)))

    def draw_centered_text(self, text, color, line_num):
        self.tft.text(font, text, self.get_text_x(text), self.get_text_y(line_num), color)

    def show_gameover(self, score):
        fname = 'highscore.txt'
        with open(fname, 'a+') as f:
            highscore = f.read()
            if not highscore:
                highscore = 0
            else:
                highscore = int(highscore)
            print('Score: ', score, 'Highscore: ', highscore)
        if score > highscore:
            with open(fname, 'w+') as f:
                f.write(str(score))
        self.draw_centered_text("GAME OVER", gc9a01.RED, 0)
        self.draw_centered_text("High Score:", gc9a01.WHITE, 3)
        self.draw_centered_text(str(highscore), gc9a01.WHITE, 4)
        self.draw_centered_text("Score:", gc9a01.WHITE, 1)
        self.draw_centered_text(str(score), gc9a01.WHITE, 2)

    def trans_scale(self, value):
        """ Translate and scale abs coordinate to screensize """
        return int(value * pixel_size) + self.screen_radius

    def scale(self, value: int):
        """ Scale dimension to screensize """
        return int(value * pixel_size)


class Runner:

    def __init__(self):
        self.score = 0
        self.display = TFTDisplay()
        self.snake = Snake(border_radius=int(self.display.screen_radius / pixel_size))
        self.food = Food(border_radius=int(self.display.screen_radius / pixel_size))
        self.last_step = utime.ticks_ms()

    def reset_game(self):
        self.score = 0
        self.display.reset()
        self.snake = Snake(border_radius=int(self.display.screen_radius / pixel_size))
        self.food = Food(border_radius=int(self.display.screen_radius / pixel_size))
        self.last_step = utime.ticks_ms()
        self.food.move(self.snake)

    def game_over(self):
        self.display.show_gameover(self.score)
        while True:
            if self.display.get_key_state() == 'select':
                break
        self.reset_game()
        self._game_loop()

    def run(self):
        self.reset_game()
        self._game_loop()

    def _game_loop(self):
        while True:
            if utime.ticks_diff(utime.ticks_ms(), self.last_step) >= refresh_rate:
                self.last_step = utime.ticks_ms()
                self.snake.step()
                if self.snake.x == self.food.x and self.snake.y == self.food.y:
                    self.score += 1
                    self.snake.length += 1
                    self.food.move(self.snake)
                self.display.draw_snake(self.snake)
                self.display.draw_food(self.food)
                if self.snake.is_overlapping:
                    self.game_over()
                key_state = self.display.get_key_state()
                if key_state:
                    if key_state != 'select':
                        if (self.snake.dir in [Dir.left, Dir.right] and key_state not in [Dir.left, Dir.right]) \
                                or (self.snake.dir in [Dir.up, Dir.down] and key_state not in [Dir.up, Dir.down]):
                            self.snake.dir = key_state


def reset_highscore():
    """ Can only be called manually while plugged into computer to reset `highscore.txt` value to 0 """
    with open('highscore.txt', 'w+') as f:
        f.write(str(0))


if __name__ == '__main__':
    runner = Runner()
    runner.run()
