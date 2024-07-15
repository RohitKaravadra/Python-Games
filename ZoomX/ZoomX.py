import pygame
import numpy
import random
import time

pygame.init()

bg = pygame.image.load("background.png")
enemy = pygame.image.load("enemy.png")
rocket = pygame.image.load("rocket.png")
explosion = pygame.image.load("explosion.png")
win = pygame.display.set_mode((500, 500))
pygame.display.set_caption("ZoomX")
clock = pygame.time.Clock()

""" Joystick Setup """
if not pygame.joystick.get_count() == 0:
    myjoy = pygame.joystick.Joystick(0)
    myjoy.init()


class Game:
    """Main class"""
    x = 240
    y = 400
    run = False
    is_on = True
    score = 0
    vx = numpy.array([], 'i')
    vy = numpy.array([], 'i')
    deltaTime = 0
    gameSpeed = 10
    spawnRate = 1
    speedUpdate = {500: [10, 1], 1000: [11, 0.9], 1500: [12, 0.8], 2000: [13, 0.7], 3000: [14, 0.7], 3500: [15, 0.6],
                   4000: [16, 0.5], 4500: [17, 0.4], 5000: [18, 0.3], 5500: [19, 0.2]}
    maxSpeed = [20, 0.1]

    @classmethod
    def initialize(cls):
        cls.run = True
        cls.vx = numpy.array([], 'i')
        cls.vy = numpy.array([], 'i')
        cls.frames = 27
        cls.score = 0
        cls.x = 240
        cls.y = 400
        cls.gameSpeed = 10
        cls.spawnRate = 1

    @classmethod
    def createtext(cls, text, size, color, position):
        """Function to create Text box"""
        msg = pygame.font.SysFont("Times New Roman", size)
        text_surface = msg.render(text, True, color)
        win.blit(text_surface, position)

    @classmethod
    def updatescore(cls):
        """Function to print score"""
        cls.createtext("Score - " + str(int(cls.score)), 20, (255, 255, 0), (0, 0))

    @classmethod
    def checkcollision(cls):
        """ Function to detect collision"""
        removed = list()
        for i in range(0, len(cls.vx) - 1):
            win.blit(enemy, (cls.vx[i], cls.vy[i]))
            rect = pygame.Rect(cls.vx[i], cls.vy[i], 20, 30)
            if rect.colliderect((cls.x, cls.y, 20, 30)) and cls.run:
                cls.run = False
            if cls.vy[i] < 500:
                cls.vy[i] += cls.gameSpeed * cls.deltaTime
            else:
                removed.append(i)

        for index in removed:
            cls.vx = numpy.delete(cls.vx, index)
            cls.vy = numpy.delete(cls.vy, index)

    @classmethod
    def playermovement(cls):
        """Function to move player"""
        direction = pygame.Vector2()
        k = pygame.key.get_pressed()
        if k[pygame.K_RIGHT] or k[pygame.K_d]:
            direction.x = 1
        if k[pygame.K_LEFT] or k[pygame.K_a]:
            direction.x = -1
        if k[pygame.K_UP] or k[pygame.K_w]:
            direction.y = -1
        if k[pygame.K_DOWN] or k[pygame.K_s]:
            direction.y = 1

        if not pygame.joystick.get_count() == 0:
            direction.x = int(round(myjoy.get_axis(0), 0))
            direction.y = int(round(myjoy.get_axis(1), 0))

        if direction.magnitude() > 0:
            direction = direction.normalize()
            cls.x += direction.x * cls.gameSpeed * cls.deltaTime
            cls.y += direction.y * cls.gameSpeed * cls.deltaTime
            if not (0 < cls.x < 480):
                cls.x -= direction.x * cls.gameSpeed * cls.deltaTime
            if not (0 < cls.y < 480):
                cls.y -= direction.y * cls.gameSpeed * cls.deltaTime

    @classmethod
    def update_speed(cls):
        for score in cls.speedUpdate:
            if score > cls.score:
                cls.gameSpeed = cls.speedUpdate[score][0]
                cls.spawnRate = cls.speedUpdate[score][1]
                break
        else:
            cls.gameSpeed = cls.maxSpeed[0]
            cls.spawnRate = cls.maxSpeed[1]


while Game.is_on:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Game.is_on = False

    win.blit(bg, (0, 0))
    Game.createtext("ZoomX", 40, (255, 255, 0), (190, 200))
    Game.createtext("Press SPACE/START to Run", 20, (255, 255, 0), (130, 300))
    Game.createtext("Score - " + str(int(Game.score)), 20, (255, 255, 0), (0, 0))
    pygame.display.update()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        Game.initialize()
    if not pygame.joystick.get_count() == 0:
        if myjoy.get_button(7):
            Game.initialize()
    elif keys[pygame.K_BACKSPACE]:
        Game.is_on = False

    last_time = time.time()
    last_spawn_time = 0
    while Game.run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                Game.run = False
                Game.is_on = False

        Game.playermovement()

        if time.time() - last_spawn_time >= Game.spawnRate:
            Game.vx = numpy.append(Game.vx, random.randint(0, 480))
            Game.vy = numpy.append(Game.vy, 0)
            last_spawn_time = time.time()

        win.blit(bg, (0, 0))
        Game.checkcollision()

        Game.score += 2 * Game.deltaTime
        Game.update_speed()
        win.blit(rocket, (Game.x, Game.y))
        # pygame.draw.rect(win, (0, 255, 0), (game.x, game.y, 20, 20))
        Game.updatescore()
        if not Game.run:
            win.blit(explosion, (Game.x, Game.y))
            pygame.display.update()
            pygame.time.delay(700)
        else:
            pygame.display.update()

        Game.deltaTime = (time.time() - last_time) * Game.frames
        last_time = time.time()

