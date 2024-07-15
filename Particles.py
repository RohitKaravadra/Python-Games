import pygame
import time
import random

pygame.init()

win = pygame.display.set_mode((800, 450))
FPS = 30
DelTime = 0

AllSprites = pygame.sprite.Group()
AllEnemies = pygame.sprite.Group()
StaticBodies = pygame.sprite.Group()


class CollisionObjects(pygame.sprite.Sprite):
    """ colliding parts of a body"""

    def __init__(self, parent):
        self.ground = self.GroundObject(parent)
        self.side = self.SideObject(parent)

    class GroundObject(pygame.sprite.Sprite):
        """ ground collide object"""

        def __init__(self, parent):
            pygame.sprite.Sprite.__init__(self)
            self.parent = parent
            self.rect = pygame.Rect((0, 0, parent.rect.width, 3))
            self.rect.center = parent.rect.midbottom

        def update(self):
            if self.parent.V_direction < 0:
                self.rect.center = self.parent.rect.midtop
            else:
                self.rect.center = self.parent.rect.midbottom

    class SideObject(pygame.sprite.Sprite):
        """ side collide object"""

        def __init__(self, parent):
            pygame.sprite.Sprite.__init__(self)
            self.parent = parent
            self.rect = pygame.Rect((0, 0, 3, parent.rect.height // 2))
            self.rect.center = parent.rect.center

        def update(self):
            if self.parent.H_direction > 0:
                self.rect.center = self.parent.rect.midright
            elif self.parent.H_direction < 0:
                self.rect.center = self.parent.rect.midleft
            else:
                self.rect.center = self.parent.rect.center

    def update(self):
        self.ground.update()
        self.side.update()


class Platforms(pygame.sprite.Sprite):
    """ creates platforms """

    def __init__(self, pos, size=(100, 20), color=pygame.Color((150, 75, 0))):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface(size)
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = pos

        AllSprites.add(self)
        StaticBodies.add(self)


class Droplet(pygame.sprite.Sprite):
    def __init__(self, spawn, size):
        pygame.sprite.Sprite.__init__(self)
        if size < 2:
            self.kill()
            return

        self.image = pygame.Surface((size, size))
        self.image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.image, 'cyan', (size / 2, size / 2), size / 2)

        self.rect = self.image.get_rect()
        self.pos = spawn
        self.rect.center = self.pos

        self.H_speed = random.randint(-10, 10)
        self.V_direction = 1
        self.V_speed = 0

        self.max_time = 3
        self.time = 0

        self.on_ground = False

        self.ground_object = CollisionObjects.GroundObject(self)

        AllSprites.add(self)

    def update(self):
        if self.V_direction == 1:
            if self.V_speed < 20:
                self.V_speed += 1 * DelTime * FPS

        elif self.V_direction == -1:
            if self.V_speed <= 0:
                self.V_speed = 0
                self.V_direction = 1
            else:
                self.V_speed -= 1 * DelTime * FPS

        self.check_on_ground()

        self.pos += pygame.Vector2(self.H_speed, self.V_direction * (self.V_speed ** 2) / 2) * DelTime * FPS

        self.time += DelTime
        if self.max_time < self.time:
            self.kill()
            return

        if self.pos[1] > 450:
            self.kill()
        self.rect.center = self.pos
        self.ground_object.update()

    def check_on_ground(self):
        collision = pygame.sprite.spritecollideany(self.ground_object, StaticBodies)
        if collision:
            if self.V_speed > 1:
                self.V_speed /= 2 + random.random()
                self.V_direction = -1
                self.H_speed /= 2
            else:
                self.kill()
            self.rect.midbottom = (
                self.rect.midbottom[0], collision.rect.midtop[1] - 1)
            self.pos = self.rect.center
            return True
        return False


last_time = time.time()
Platforms((400, 444), (801.5, 22.5)), ((638, 378), (140.0, 9.5))
Platforms((400, 300), (200, 20))


def mainloop():
    mode = True
    timer = time.time()
    global last_time, DelTime

    while True:
        if time.time() - timer > 0.001:
            if mode:
                Droplet((random.randint(100, 700), 0), 3)
            else:
                Droplet(pygame.mouse.get_pos(), 3)
        timer = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mode = not mode

        win.fill('black')
        AllSprites.update()
        AllSprites.draw(win)
        pygame.display.flip()

        DelTime = time.time() - last_time
        last_time = time.time()

mainloop()