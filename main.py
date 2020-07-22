import pygame
import random
import os


WIDTH = 512
HEIGHT = 256
FPS = 15

CELL_WIDTH = 16
ROWS = HEIGHT//CELL_WIDTH
COLS = WIDTH//CELL_WIDTH

LEVELS = 4
MAX_SCORE_PER_LVL = [90, 150, 210, 1000000]
DOUBLE_SPEED_TIME = 80

# initialize pygame and create window
pygame.init()
pygame.mixer.quit()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")


# fonts
FONT_LARGE = pygame.font.SysFont('comic-sans', 50)
FONT_MEDIUM = pygame.font.SysFont('comic-sans', 30)
FONT_SMALL = pygame.font.SysFont('comic-sans', 25)

# GRID CONSTANTS
EMPTY = 0
SNAKE = 1
WALL = 2
RABBIT = 3
BONUS_INFINITE_RABBITS = 4
BONUS_DOUBLE_SPEED = 5

# define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Sprites
snake_body_horiz = pygame.image.load(os.path.join('images', 'HORIZ.png'))
snake_body_vert = pygame.image.load(os.path.join('images', 'VERT.png'))
rabbit = pygame.image.load(os.path.join('images', 'rabbit.png'))
grass = pygame.image.load(os.path.join('images', 'grass.png'))
border = pygame.image.load(os.path.join('images', 'border-grey.png'))
star = pygame.image.load(os.path.join('images', 'star.png'))
snake_head = []
snake_tail = []
snake_corners = []

for i in range(1, 5):
    snake_head.append(pygame.image.load(os.path.join('images', f'H{i}.png')))
    snake_tail.append(pygame.image.load(os.path.join('images', f'T{i}.png')))
    snake_corners.append(pygame.image.load(os.path.join('images', f'C{i}.png')))


# Sound
eat_sound = pygame.mixer.Sound(os.path.join('sound', 'eat_sound.ogg'))
die_sound = pygame.mixer.Sound(os.path.join('sound', 'die_sound.ogg'))

class Snake:
    def __init__(self):
        self.head = [ROWS//2, COLS//2]
        self.body = []
        self.body.append([self.head[0], self.head[1] - 1])
        self.dir = 1
        self.body_dir = [1]

    def dir_up(self):
        if self.dir != 2:
            self.dir = 0

    def dir_down(self):
        if self.dir != 0:
            self.dir = 2

    def dir_left(self):
        if self.dir != 1:
            self.dir = 3

    def dir_right(self):
        if self.dir != 3:
            self.dir = 1


    def update(self):
        # update head position
        self.body.append(self.head)
        self.body_dir.append(self.dir)
        self.head = self.head.copy()

        # move head accorning to direction
        if self.dir == 0:
            self.head[0] -= 1
        elif self.dir == 1:
            self.head[1] += 1
        elif self.dir == 2:
            self.head[0] += 1
        else:
            self.head[1] -= 1

        # handle head position out of bounds
        if self.head[0] < 0:
            self.head[0] = ROWS - 1
        if self.head[0] >= ROWS:
            self.head[0] = 0
        if self.head[1] < 0:
            self.head[1] = COLS - 1
        if self.head[1] >= COLS:
            self.head[1] =0


    def reset(self):
        self.head = [ROWS//2, COLS//2]
        self.body = []
        self.body.append([self.head[0], self.head[1] - 1])
        self.body_dir = [1]
        self.dir = 1
        self.speed_col = 1
        self.speed_row = 0


    def draw(self, win):
        # draw head and tail
        head_x = self.head[1] * CELL_WIDTH
        head_y = self.head[0] * CELL_WIDTH

        tail_x = snake.body[0][1] * CELL_WIDTH
        tail_y = snake.body[0][0] * CELL_WIDTH
        tail_dir = snake.body_dir[0]

        win.blit(snake_head[self.dir], (head_x, head_y))
        win.blit(snake_tail[tail_dir], (tail_x, tail_y))

        # draw body
        for i, (row, col) in enumerate(self.body[1:]):
            x = col * CELL_WIDTH
            y = row * CELL_WIDTH

            dir = self.body_dir[i]
            next_dir = self.dir if (i + 1 >= len(self.body)) else self.body_dir[i+1]

            # select appropriate sprite for current body part
            if dir == next_dir:
                if  dir == 0 or dir == 2:
                    sprite = snake_body_vert
                else:
                    sprite = snake_body_horiz
            elif dir == 0 and next_dir == 1 or dir == 3 and next_dir == 2:
                sprite = snake_corners[3]
            elif dir == 3 and next_dir == 0 or dir == 2 and next_dir == 1:
                sprite = snake_corners[2]
            elif dir == 1 and next_dir == 0 or dir == 2 and next_dir == 3:
                sprite = snake_corners[1]
            else:
                sprite = snake_corners[0]

            # draw body part
            win.blit(sprite, (x, y))


class Grid():
    def __init__(self, lvl=0):
        self.grid = [[EMPTY for j in range(COLS)] for i in range(ROWS)]
        self.lvl = lvl
        self.set_random_rabbit()


    def set_rabbit(self, pos):
        row, col = pos
        self.grid[row][col] = RABBIT


    def set_random_rabbit(self):
        pos = self.random_empty_pos()
        self.set_rabbit(pos)


    def cell(self, pos):
        row, col = pos
        return self.grid[row][col]


    def set_cell(self, pos, content):
        row, col = pos
        self.grid[row][col] = content


    def advance_level(self):
        self.lvl += 1
        self.clear_rabbits()

        # for each level draw add additional wall cells
        if self.lvl == 1:
            for row in range(ROWS):
                if row != ROWS//2:
                    self.grid[row][0] = self.grid[row][COLS - 1] = WALL

            for col in range(COLS):
                self.grid[0][col] = self.grid[ROWS - 1][col] = WALL
        elif self.lvl == 2:
            row1, col1 = ROWS//4, COLS//4
            row2 = ROWS - row1
            col2 = COLS - col1

            for col in range(col1, col2):
                self.grid[row1][col] = WALL
                self.grid[row2][col] = WALL
        elif self.lvl == 3:
            row1, col1 = ROWS//4, COLS//4
            row2 = ROWS - row1
            row3 = (row1 + row2)//2
            col2 = COLS - col1

            print(col1, col2)
            for row in range(row1, row2 + 1):
                if row != row3:
                    self.grid[row][col1] = WALL
                    self.grid[row][col2] = WALL
                    print(row)


        self.set_random_rabbit()


    def clear_rabbits(self):
        for row in range(ROWS):
            for col in range(COLS):
                if self.grid[row][col] == RABBIT:
                    self.grid[row][col] = EMPTY


    def random_empty_pos(self):
        positions = []

        for row in range(ROWS):
            for col in range(COLS):
                if self.grid[row][col] == EMPTY:
                    positions.append([row, col])

        return random.choice(positions)


    def next_empty_pos(self, pos):
        row, col = pos
        for i in range(row, ROWS):
            if row != i:
                col = 0

            for j in range(col, COLS):
                if self.grid[i][j] == EMPTY:
                    return (i, j)

        return False


    def draw(self, screen):
        # draw grass on all cells
        for row in range(ROWS):
            for col in range(COLS):
                x = col * CELL_WIDTH
                y = row * CELL_WIDTH
                screen.blit(grass, (x, y))


        for row in range(ROWS):
            for col in range(COLS):
                if self.grid[row][col] == WALL:
                    x = col * CELL_WIDTH
                    y = row * CELL_WIDTH
                    screen.blit(border, (x, y))
                elif self.grid[row][col] == RABBIT:
                    x = col * CELL_WIDTH
                    y = row * CELL_WIDTH
                    screen.blit(rabbit, (x, y))
                elif self.grid[row][col] == BONUS_DOUBLE_SPEED or self.grid[row][col] == BONUS_INFINITE_RABBITS:
                    x = col * CELL_WIDTH - 8
                    y = row * CELL_WIDTH - 8
                    screen.blit(star, (x, y))


def end_game(win, score):
    pygame.time.wait(700)
    run = True

    while run:
        # draw grass
        for row in range(ROWS):
            for col in range(COLS):
                x = col * CELL_WIDTH
                y = row * CELL_WIDTH
                screen.blit(grass, (x, y))

        # display score
        best = best_score(score)
        text_message = FONT_LARGE.render(f'Score: {score}    Best: {best}', 1, WHITE)
        text_play_again = FONT_SMALL.render('Press any key to continue...', 1, WHITE)
        win.blit(text_message, ((WIDTH - text_message.get_width())//2, (HEIGHT - 3*text_message.get_height())//2))
        win.blit(text_play_again, ((WIDTH - text_play_again.get_width())//2, HEIGHT//2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                return False

    return True


def best_score(score):
    file = open('scores.txt', 'r+')

    file_content = file.readlines()
    best = 0

    if file_content:
        best = int(file_content[0])

    # sees if the current score is greater than the previous best
    if best < score:
        file.truncate(0)
        file.seek(0)
        file.write(str(score))
        best = score

    file.close()
    return best


def draw(screen, snake, grid, score):
    screen.fill(WHITE)
    grid.draw(screen)
    snake.draw(screen)

    # show score
    text = FONT_MEDIUM.render(f'Score: {score}', False, WHITE)
    screen.blit(text, (WIDTH - text.get_width() - 25, 20))
    pygame.display.flip()



clock = pygame.time.Clock()


snake = Snake()
grid = Grid()
score = 0
infinite_rabbits = False
double_speed_timer = 0
score_lvl = [0] * LEVELS # current score for each level

# Game loop
running = True
while running:
    # keep loop running at the right speed
    if double_speed_timer > 0:
        double_speed_timer -= 1
        clock.tick(int(2 * FPS))
    else:
        clock.tick(FPS)

    # Process input (events)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                snake.dir_down()
            elif event.key == pygame.K_UP:
                snake.dir_up()
            elif event.key == pygame.K_RIGHT:
                snake.dir_right()
            elif event.key == pygame.K_LEFT:
                snake.dir_left()

    # Snake head on RABBIT
    if grid.cell(snake.head) == RABBIT:
        eat_sound.play()
        score += 10 if not infinite_rabbits else 1
        grid.set_cell(snake.head, EMPTY)

        if not infinite_rabbits:
            grid.set_random_rabbit()
    else:
        snake.body.pop(0)
        snake.body_dir.pop(0)

    # Snake head on Bonus element
    if grid.cell(snake.head) == BONUS_DOUBLE_SPEED:
        double_speed_timer = DOUBLE_SPEED_TIME
        grid.set_cell(snake.head, EMPTY)
    elif grid.cell(snake.head) == BONUS_INFINITE_RABBITS:
        infinite_rabbits = True
        grid.set_cell(snake.head, EMPTY)

    # Make move according to snake's direction
    snake.update()

    # Game Over
    if snake.head in snake.body or grid.cell(snake.head) == WALL:
        die_sound.play()

        if end_game(screen, score):
            running = False
            break
        else:
            grid = Grid()
            snake = Snake()
            infinite_rabbits = False
            double_speed_timer = 0
            score_lvl = [0] * LEVELS
            score = 0

    if infinite_rabbits:
        rabbit_pos = grid.next_empty_pos(rabbit_pos)

        if rabbit_pos:
            grid.set_rabbit(rabbit_pos)
        else:
            infinite_rabbits = False
            grid.clear_rabbits()
            grid.set_random_rabbit()
    elif False:
        pass
    else:
        # advance to next level if accumulated score per level > MAX_SCORE_PER_LVL
        if score - score_lvl[grid.lvl - 1] > MAX_SCORE_PER_LVL[grid.lvl]:
            score_lvl[grid.lvl] = score
            snake.reset()
            grid.advance_level()

    # instantiate bonus drop item with given probability
    if not infinite_rabbits and not double_speed_timer:
        r = random.uniform(0, 1)

        if r < 0.0025:
            row, col = grid.random_empty_pos()

            if r < 0.0015:
                grid.grid[row][col] = BONUS_DOUBLE_SPEED
            else:
                grid.grid[row][col] = BONUS_INFINITE_RABBITS
                rabbit_pos = (0, 0)

    # Draw / render
    draw(screen, snake, grid, score)


pygame.quit()
