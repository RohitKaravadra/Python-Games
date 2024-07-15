import pygame
import time

pygame.init()

win = pygame.display.set_mode((1280, 720))
all_bodies = pygame.sprite.Group()
all_rigid_bodies = pygame.sprite.Group()
all_static_bodies = pygame.sprite.Group()
all_kinemetic_bodies = pygame.sprite.Group()
FPS = 90
GAMEON = False
joy = 0
del_time = 0


class ground_object(pygame.sprite.Sprite):
    def __init__(self, parent):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect((0, 0, parent.rect.width // 2, 3))
        self.rect.center = parent.rect.midbottom


class side_object(pygame.sprite.Sprite):
    def __init__(self, parent):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect((0, 0, 3, parent.rect.height // 2))
        self.rect.center = parent.rect.center


class platforms(pygame.sprite.Sprite):
    def __init__(self, pos, size=(100, 20), type='wall'):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface(size)
        self.image.fill(pygame.Color('yellow'))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.type = type

        all_static_bodies.add(self)
        all_bodies.add(self)


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface((30, 30))
        pygame.draw.circle(self.image, 'blue', (15, 15), 15)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.pos = pygame.Vector2(640, 50)
        self.rect.center = self.pos
        self.type = 'ball'

        self.v = 0
        self.m = 1
        self.on_ground = False
        self.damp = 0.5
        self.drag = 0.3
        self.speed = 0
        self.direction = 0
        self.grab = False
        self.grabbed_by = object
        self.apply_force = False

        self.bottom = ground_object(self)
        self.leftright = side_object(self)

        all_rigid_bodies.add(self)
        all_bodies.add(self)

    def update(self):
        if not self.grab:
            self.hit_object()
            self.update_pos()
        else:
            if self.snetch():
                return

            if self.apply_force:
                self.force()
            if self.grabbed_by.direction > 0:
                self.rect.bottomleft = self.grabbed_by.rect.midright + pygame.Vector2(2, 0)
            else:
                self.rect.bottomright = self.grabbed_by.rect.midleft - pygame.Vector2(2, 0)

            self.pos = self.rect.center

        self.bottom.rect.center = self.rect.midbottom
        if self.direction > 0:
            self.leftright.rect.center = self.rect.midright
        else:
            self.leftright.rect.center = self.rect.midleft

    def update_pos(self):

        F = (1 / 2) * self.m * (self.v ** 2)

        if not self.on_ground:
            if self.m > 0:
                self.v += 0.02
            else:
                self.v -= 0.02
            if self.v < 0:
                self.m = 1

        else:
            if self.speed < 0:
                self.speed = 0
                self.direction = 0
            elif not self.speed == 0:
                self.speed -= self.drag

            F = 0
            if not self.v == 0:
                self.v = 0

        temp = pygame.Vector2(self.speed * self.direction, F) * del_time * FPS
        if temp.magnitude():
            self.pos += temp
            self.rect.center = self.pos

    def hit_object(self):
        collision = pygame.sprite.spritecollideany(self, all_static_bodies)
        if collision:
            self.v *= self.damp
            collision = pygame.sprite.spritecollideany(self.bottom, all_static_bodies)
            if collision:
                if self.v.__round__(3):
                    self.m = -1
                else:
                    self.on_ground = True
                    self.m = 1
                    self.v = 0
                self.rect.midbottom = (self.rect.midbottom[0], collision.rect.midtop[1] + 1)
            else:
                collision = pygame.sprite.spritecollideany(self.leftright, all_static_bodies)
                if collision:
                    if self.direction < 0:
                        self.rect.midleft = (collision.rect.midright[0] + 1, self.rect.midleft[1])
                    else:
                        self.rect.midright = (collision.rect.midleft[0] - 1, self.rect.midright[1])
                    self.direction *= -1
                    self.speed *= self.drag * 2
            self.pos = self.rect.center

    def grabbed(self, obj):
        if not self.grab:
            self.v = 0
            self.m = 1
            self.grab = True
            self.grabbed_by = obj
            self.direction = obj.direction

    def ungrab(self, direction=0):
        self.apply_force = False
        if self.grab:
            self.grab = False
            self.on_ground = False
            if not direction:
                self.direction = self.grabbed_by.direction
            else:
                self.direction = 0
            self.m = -1
            self.speed = 2.8 * self.v

    def force(self):
        if self.v <= 0:
            self.v = 2
        elif self.v < 5:
            self.v += 0.1
        else:
            self.v = 5

    def snetch(self):
        collision = pygame.sprite.spritecollide(self, all_kinemetic_bodies, False)
        try:
            collision.remove(self.grabbed_by)
        except ValueError:
            pass
        if collision:
            self.rect.midbottom = (self.pos[0], collision[0].rect.midtop[1] - 1)
            self.pos = self.rect.center
            self.v = 6
            self.ungrab(1)
            return True
        else:
            return False


class Player(pygame.sprite.Sprite):
    def __init__(self, spawn, control_type='keyboard', color='green'):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.surface.Surface(size=(30, 80))
        self.image.fill(pygame.Color(color))
        self.type = 'player'

        self.speed = 4
        self.pos = spawn
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.direction = 0
        self.control_type = control_type

        self.leftright = side_object(self)
        self.bottom = ground_object(self)

        self.on_ground = False
        self.is_jumping = False
        self.v = 0
        self.m = 1
        self.jump_height = 6
        self.double_jump = 2

        all_kinemetic_bodies.add(self)
        all_bodies.add(self)

    def update(self):
        if not (self.is_jumping or self.on_ground):
            self.check_on_ground()
        self.check_ball_collision()
        self.update_pos()

    def update_pos(self):
        dir = pygame.Vector2()
        key = pygame.key.get_pressed()

        if self.control_type in 'joystick':
            if joy:
                x = joy.get_axis(0)
            else:
                x = 0
            if x > 0:
                dir.x = self.speed
            if x < 0:
                dir.x = -self.speed
        else:
            if key[pygame.K_d]:
                dir.x = self.speed
            if key[pygame.K_a]:
                dir.x = -self.speed

        if dir.x > 0:
            self.leftright.rect.center = self.rect.midright
            self.direction = 1
        elif dir.x < 0:
            self.leftright.rect.center = self.rect.midleft
            self.direction = -1
        else:
            self.leftright.rect.center = self.rect.center

        self.bottom.rect.center = self.rect.midbottom

        if self.check_collision():
            if dir.x == 0 and self.is_jumping:
                self.m = 1
                self.v = 0
                self.is_jumping = False
            dir.x = 0

        F = (1 / 2) * self.m * (self.v ** 2)
        if self.is_jumping:
            self.v -= 0.02
            if self.v < 0:
                self.m = 1
                self.v = 0
                self.is_jumping = False
        elif not self.on_ground:
            self.v += 0.02
        else:
            F = 0

        dir.y += F

        self.pos += dir * del_time * FPS
        self.rect.center = self.pos

    def jump(self):
        self.is_jumping = True
        self.on_ground = False
        self.v = self.jump_height
        self.m = -1
        self.double_jump -= 1

    def check_on_ground(self):
        collision = pygame.sprite.spritecollide(self.bottom, all_static_bodies, False)
        if collision and collision[0].type in 'ground':
            self.on_ground = True
            self.rect.midbottom = (
                self.rect.midbottom[0], collision[0].rect.midtop[1] + 1)
            self.pos = self.rect.center
            if not self.v == 0:
                self.v = 0
            if self.double_jump != 2:
                self.double_jump = 2

    def check_collision(self):
        bodies = all_static_bodies.copy()
        for i in bodies:
            if i.type == 'ground':
                bodies.remove(i)
        collision = pygame.sprite.spritecollideany(self.leftright, bodies)
        if collision:
            return True
        else:
            return False

    def check_ball_collision(self):
        collision = pygame.sprite.spritecollideany(self, all_rigid_bodies)

        if collision and collision.type == 'ball':
            collision.grabbed(self)


def main():
    global GAMEON, joy, del_time

    platforms((640, 705), (1280, 30), 'ground')
    platforms((640, 15), (1280, 30))
    platforms((10, 345), (30, 690))
    platforms((1270, 345), (30, 690))
    platforms((300, 400), (30, 300))
    platforms((980, 400), (30, 300))

    p = Player((100, 100))
    c = Player((1180, 100), 'joystick', 'red')
    b = Ball()

    last_time = time.time()
    while True:
        # pygame.time.Clock().tick(30)
        del_time = time.time() - last_time
        last_time = time.time()
        if not pygame.joystick.get_count() == 0:
            if not joy:
                joy = pygame.joystick.Joystick(0)
                joy.init()
        else:
            joy = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if joy:
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0 and c.double_jump:
                        c.jump()

                    if event.button == 1 and b.grabbed_by == c:
                        b.apply_force = True

                if event.type == pygame.JOYBUTTONUP:
                    if event.button == 1 and b.grabbed_by == c:
                        b.ungrab()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and p.double_jump:
                    p.jump()

                if event.key == pygame.K_k and b.grabbed_by == p:
                    b.apply_force = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_k and b.grabbed_by == p:
                    b.ungrab()

        win.fill(pygame.Color('grey'))
        all_bodies.update()
        all_bodies.draw(win)
        pygame.display.update()


main()
pygame.display.quit()
quit()
