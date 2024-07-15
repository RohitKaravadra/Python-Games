import pygame
import random

pygame.init()


def text_box(msg):
    font = pygame.font.SysFont("Calibri", 45)
    box = font.render(msg, 1, pygame.Color('red'))
    return box


win = pygame.display.set_mode((500, 550))
pygame.display.set_caption("Snake Game")
GAMEOVER = True


class Snake:
    spawn = (20, 20)
    fruit_pos = (random.randrange(20, 490, 10), random.randrange(20, 490, 10))
    fruit = pygame.Surface((10, 10))
    fruit.fill(pygame.Color('RED'))

    def __init__(self):
        self.length = list()
        self.speed = 10
        self.score = 0
        self.size = 10
        self.direction = pygame.Vector2(0, 1)
        self.pos = (20, 20)
        self.box((20, 20), self)

    class box:
        def __init__(self, pos, parent):
            self.image = pygame.Surface((parent.size - 1, parent.size - 1))
            self.rect = pygame.Rect(0, 0, 10, 10)
            self.rect.center = pos
            self.image.fill(pygame.Color("blue"))
            parent.length.append(self)

    def update(self):
        self.update_pos()
        self.pos += self.direction * self.size
        if self.pos.x > 500:
            self.pos.x -= 500
        elif self.pos.x < 0:
            self.pos.x += 500
        if self.pos.y > 500:
            self.pos.y -= 500
        elif self.pos.y < 0:
            self.pos.y += 500

        self.box(self.pos, self)
        self.length.pop(0)
        length = [i.rect for i in self.length]
        length.pop(-1)
        try:
            length.pop(-1)
        except IndexError:
            pass
        if self.length[-1].rect.collidelist(length) > 0:
            global GAMEOVER
            GAMEOVER = True
        # elif not (-5 < self.pos[0] < 500 and -5 < self.pos[1] < 500):
        #     GAMEOVER = True
        if pygame.Rect(self.fruit_pos[0] - self.size // 2, self.fruit_pos[1] - self.size // 2, 10, 10).colliderect(
                self.length[-1].rect):
            self.score += 5
            self.speed += 0.1
            self.box(self.length[-1].rect.center + self.direction * self.size, self)
            self.fruit_pos = (random.randrange(20, 490, 10), random.randrange(20, 490, 10))
        self.draw()

    def update_pos(self):
        key = pygame.key.get_pressed()
        if (key[pygame.K_w] or key[pygame.K_UP]) and not self.direction == (0, 1):
            self.direction = pygame.Vector2(0, -1)
        elif (key[pygame.K_a] or key[pygame.K_LEFT]) and not self.direction == (1, 0):
            self.direction = pygame.Vector2(-1, 0)
        elif (key[pygame.K_s] or key[pygame.K_DOWN]) and not self.direction == (0, -1):
            self.direction = pygame.Vector2(0, 1)
        elif (key[pygame.K_d] or key[pygame.K_RIGHT]) and not self.direction == (-1, 0):
            self.direction = pygame.Vector2(1, 0)

    def draw(self):
        self.length[-1].image.fill(pygame.Color("green"))
        for i in self.length:
            win.blit(i.image, i.rect.topleft)
        self.length[-1].image.fill(pygame.Color("blue"))
        win.blit(self.fruit, self.fruit_pos - pygame.Vector2(self.size // 2, self.size // 2))
        pygame.draw.line(win, pygame.Color('white'), (0, 500), (500, 500), 3)
        win.blit(text_box('Score - ' + str(self.score)), (10, 510))


snake = Snake()


def game_loop():
    while not GAMEOVER:
        pygame.time.Clock().tick_busy_loop(snake.speed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        win.fill((100, 100, 100))
        snake.update()
        pygame.display.update()
    return True


def main_loop():
    global GAMEOVER
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    GAMEOVER = False
                    if not game_loop():
                        return
                    snake.__init__()
        win.fill((100, 100, 100))
        win.blit(text_box("Press SPACE to START"), (60, 250))
        pygame.display.update()


main_loop()
pygame.display.quit()
