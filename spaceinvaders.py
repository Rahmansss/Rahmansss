import os
import pygame
import random

MOVEDOWNEVENT = pygame.USEREVENT + 1
MOVEVENT = pygame.USEREVENT + 2


class Game:
    def __init__(self):
        self.move_right = False
        self.move_left = False
        self.lasers = []
        self.score = 0
        self.game_over = False

    def collision(self, target, projectile):
        if target.colliderect(projectile):
            return True
        else:
            return False

    def spawn_aliens(self, aliens):
        for i in range(settings.enemy_amount):
            alien = Alien()
            alien.position[0] += i * alien.size[0] + i * alien.space_between_aliens
            alien.hitbox = pygame.Rect(alien.position, alien.size)
            aliens.append(alien)

    def controls(self, ship, lasers, aliens, enemy_lasers):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            ship.moving_left = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            ship.moving_right = True
        if not keys[pygame.K_d]:
            ship.moving_right = False
        if not keys[pygame.K_a]:
            ship.moving_left = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.game_over:
                        ship.fire(lasers)
                    else:
                        self.__init__()
                        self.game_loop()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
            if event.type == pygame.USEREVENT:
                if not self.game_over:
                    if len(aliens) > 0:
                        aliens[random.randint(0, len(aliens) - 1)].fire(enemy_lasers)
            if event.type == MOVEDOWNEVENT:
                if not self.game_over:
                    for enemies in aliens:
                        enemies.moving_down = True
            if event.type == MOVEVENT:
                if not self.game_over:
                    for enemies in aliens:
                        enemies.moving_horizontal = True
        ship.move_left()
        ship.move_right()

    def game_loop(self):
        ship = Ship()
        speed = settings.speed
        background = settings.background
        screen = settings.screen
        pygame.init()
        pygame.font.init()
        font = pygame.font.SysFont("impact", 25)
        game_over_font = pygame.font.SysFont("impact", 50)
        pygame.display.set_caption("Spaceinvaders")
        clock = pygame.time.Clock()
        aliens = []
        lasers = []
        enemy_lasers = []
        while True:
            screen.blit(background, [0, 0])
            self.controls(ship, lasers, aliens, enemy_lasers)
            if not aliens:
                self.spawn_aliens(aliens)
            for laser in lasers:
                laser.hitbox = pygame.Rect(laser.position, laser.size)
                laser.move()
                screen.blit(laser.laser_sprite, laser.hitbox)
                if laser.position[1] < 0 - laser.size[1]:
                    lasers.remove(laser)
                for enemy in aliens:
                    if self.collision(enemy.hitbox, laser.hitbox):
                        if not enemy.exploding:
                            if laser in lasers:
                                lasers.remove(laser)
                            enemy.play_sound()
                            self.score += 100
                        enemy.exploding = True
            for laser in enemy_lasers:
                laser.hitbox = pygame.Rect(laser.position, laser.size)
                laser.move()
                screen.blit(laser.laser_sprite, laser.hitbox)
                if laser.position[1] > settings.screen_size[1] + laser.size[1]:
                    enemy_lasers.remove(laser)
                if self.collision(ship.hitbox, laser.hitbox):
                    ship.lives -= 1
                    enemy_lasers.remove(laser)
                    if ship.lives <= 0:
                        self.game_over = True
            for enemy in aliens:
                enemy.move_vertical()
                enemy.move_horizontal()
                enemy.explode()
                screen.blit(enemy.alien_sprite, enemy.hitbox)
                if enemy.explosion_frame == 7:
                    aliens.remove(enemy)
                if self.collision(ship.hitbox,enemy.hitbox):
                    if not enemy.exploding:
                        enemy.play_sound()
                        self.score += 100
                        ship.lives -= 1
                    enemy.exploding = True
                if enemy.position[1] > settings.screen_size[1]:
                    self.game_over = True
            status_surface = font.render(f"lives:   {ship.lives}    score:  {self.score}", True, (0, 255, 0))
            if self.game_over:
                while True:
                    game_over_surface = game_over_font.render(f"GAME OVER Score: {self.score}", True, (0, 255, 0))
                    text_rect = game_over_surface.get_rect(
                        center=(settings.screen_size[0] / 2, settings.screen_size[1] / 2))
                    screen.fill((0, 0, 0))
                    screen.blit(game_over_surface, text_rect)
                    pygame.display.update()
                    self.controls(ship, lasers, aliens, enemy_lasers)
            screen.blit(ship.ship_sprite, ship.hitbox)
            screen.blit(status_surface, (0, 0))
            pygame.display.update()
            clock.tick(speed)


class Settings:
    def __init__(self):
        self.screen_size = (1920 // 2, 1080 // 2)
        self.screen = pygame.display.set_mode(self.screen_size)
        self.background = pygame.image.load(os.path.join(os.getcwd(), r"pictures\background.png"))
        self.background = pygame.transform.scale(self.background, self.screen_size)
        self.speed = 60
        self.enemy_amount = 20
        self.lives = 5


class Ship(pygame.sprite.Sprite):
    def __init__(self):
        pygame.mixer.init()
        pygame.sprite.Sprite.__init__(self)
        self.laser = Laser()
        self.moving_right = False
        self.moving_left = False
        self.size = (settings.screen_size[0] // 12, settings.screen_size[1] // 7)
        self.position = [settings.screen_size[0] // 2 - self.size[0],
                         settings.screen_size[1] - self.size[1] - self.size[1] // 3]
        self.ship_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join(os.getcwd(), r"pictures\ship.png")), self.size)
        self.step = settings.screen_size[0] // 200
        self.shoot_sound = pygame.mixer.Sound(r"sounds\laser_sound.ogg")
        self.lives = settings.lives
        self.hitbox = pygame.Rect(self.position, self.size)

    def move_left(self):
        if self.moving_left:
            if self.position[0] > 0:
                self.position[0] = self.position[0] - self.step
        self.hitbox = pygame.Rect(self.position, self.size)

    def move_right(self):
        if self.moving_right:
            if self.position[0] < settings.screen_size[0] - self.size[0]:
                self.position[0] = self.position[0] + self.step
        self.hitbox = pygame.Rect(self.position, self.size)

    def fire(self, lasers):
        self.laser = Laser()
        self.laser.position = [(self.position[0] + self.size[0] // 2) - self.laser.size[0] // 2, (self.position[1])]
        self.shoot_sound.play()
        lasers.append(self.laser)


class Laser(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.size = (settings.screen_size[0] // 80, settings.screen_size[1] // 21)
        self.laser_sprite = pygame.transform.scale(pygame.image.load(os.path.join(os.getcwd(), r"pictures\laser.png")),
                                                   self.size)
        self.step = settings.screen_size[1] // 180
        self.position = (0, 0)
        self.hitbox = pygame.Rect(self.position, self.size)

    def move(self):
        self.position[1] -= self.step
        self.hitbox = pygame.Rect(self.position, self.size)


class Enemy_laser(Laser):
    def __init__(self):
        super().__init__()
        self.laser_sprite = self.laser_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join(os.getcwd(), r"pictures\enemy_laser.png")),
            self.size)

    def move(self):
        self.position[1] += self.step
        self.r = pygame.Rect(self.position, self.size)


class Alien(pygame.sprite.Sprite):
    def __init__(self):
        self.step_size = settings.screen_size[1] / 500
        self.explosion_sounds = []
        self.exploding = False
        self.explosion_frame = 0
        self.explosion_frames = []
        pygame.sprite.Sprite.__init__(self)
        self.size = [ship.size[0] // 2, ship.size[1] // 2]
        self.space_between_aliens = ((settings.screen_size[0] - self.size[0] * settings.enemy_amount) - self.size[
            0]) // settings.enemy_amount
        self.position = [0, settings.screen_size[1] // 10]
        self.hitbox = pygame.Rect(self.position, self.size)
        self.vertical_steps = 50
        self.horizontal_steps = 40
        self.moving_down = False
        self.moving_horizontal = False
        self.isleft = True
        self.alien_sprite = pygame.transform.scale(
            pygame.image.load(os.path.join(os.getcwd(), r"pictures\enemy.png")), self.size)
        for i in range(8):
            self.explosion_frames.append(pygame.transform.scale(
                pygame.image.load(os.path.join(os.getcwd(), fr"pictures\explosion\regularExplosion0{i}.png")),
                self.size))
        for i in range(3):
            self.explosion_sounds.append(os.path.join(os.getcwd(), fr"Sounds\explosion{i}.ogg"))
        self.shoot_sound = pygame.mixer.Sound(r"sounds\laser_sound.ogg")

    def explode(self):
        if self.explosion_frame <= 7:
            if self.exploding:
                self.alien_sprite = self.explosion_frames[int(self.explosion_frame)]
                self.explosion_frame += 0.25

    def play_sound(self):
        pygame.mixer.init()
        sound = pygame.mixer.Sound(self.explosion_sounds[random.randint(0, 2)])
        sound.play()

    def move_vertical(self):
        if not self.exploding:
            if self.moving_down:
                self.position[1] += self.step_size
                self.hitbox = pygame.Rect(self.position, self.size)
                self.vertical_steps -= 1
                if self.vertical_steps == 0:
                    self.moving_down = False
            else:
                self.vertical_steps = 50

    def move_horizontal(self):
        if not self.exploding:
            if self.moving_horizontal:
                if self.isleft:
                    self.position[0] += (self.space_between_aliens + self.size[0]) / 40
                else:
                    self.position[0] -= (self.space_between_aliens + self.size[0]) / 40
                self.hitbox = pygame.Rect(self.position, self.size)
                self.horizontal_steps -= 1
                if self.horizontal_steps == 0:
                    if self.isleft:
                        self.isleft = False
                    else:
                        self.isleft = True
                    self.moving_horizontal = False
            else:
                self.horizontal_steps = 40

    def fire(self, lasers):
        laser = Enemy_laser()
        laser.position = [(self.position[0] + self.size[0] // 2) - laser.size[0] // 2, (self.position[1])]
        self.shoot_sound.play()
        lasers.append(laser)


pygame.init()
pygame.time.set_timer(pygame.USEREVENT, 1000)
pygame.time.set_timer(MOVEDOWNEVENT, 5000)
pygame.time.set_timer(MOVEVENT, 7500)
game = Game()
settings = Settings()
ship = Ship()
game.game_loop()
