#define imported modules
import pygame
from pygame.locals import *
import sys
import time
import math

pygame.init()

SCREEN_W, SCREEN_H = 640, 480

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock = pygame.time.Clock()
running = True

BLACK = 0, 0, 0
RED = 255, 0, 0
GREEN = 0, 255, 0
FPS = 60
TILE_SIZE = 16

def load_image(path):
    image = pygame.image.load(path).convert()
    return image

def get_distance(obj_a, obj_b):
    return math.sqrt((obj_b.x - obj_a.x) ** 2 + (obj_b.y - obj_a.y) ** 2)

class PhysicsEntity(pygame.sprite.Sprite):
    def __init__(self, texture, xpos, ypos, *args, **kwargs):
        super().__init__()

        self.image = load_image(texture)
        self.rect = self.image.get_rect()
        self.x = xpos
        self.y = ypos
        self.dx = 0
        self.dy = 0
        self.flip = False
        self.dir = 'right'
        self.old_dir = None
        self.echo = False
        self.echo_timer = 0
        self.state = 'idle'
        self.state_timer = 0
        self.old_state = None

    def update(self):
        # set direction
        if self.dx > 0:
            self.dir = 'right'
        elif self.dx < 0 :
            self.dir = 'left'
        # set flip
        if self.dir != self.old_dir:
            self.flip = True
        elif self.dir == self.old_dir:
            self.flip = False

        # update old direction to current direction
        self.old_dir = self.dir

        self.x += self.dx
        self.y += self.dy
        self.echo_timer += 1    

    def render(self, surface):
        if self.flip:
            self.image = pygame.transform.flip(self.image, 1, 0)
        surface.blit(self.image, (self.x, self.y))

class Player(PhysicsEntity):
    def __init__(self, texture, xpos, ypos, *args, **kwargs):
        PhysicsEntity.__init__(self, texture, xpos, ypos)
        
class Enemy(PhysicsEntity):
    def __init__(self, texture, xpos, ypos, *args, **kwargs):
        PhysicsEntity.__init__(self, texture, xpos, ypos)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)

    def update(self):
        super().update()

        match self.state:
            case 'idle':
                if self.state != self.old_state:
                    self.dx = 1
                if self.state_timer < 30:
                    pass
                elif self.state_timer >= 30:
                    self.dx *= -1
                    self.state_timer = 0
                self.state_timer += 1

        self.old_state = self.state 

    def render(self, surface):
        if self.echo:
            super().render(surface)
        elif not self.echo:
            pass

class SonarWave:
    def __init__(self, sub):
        self.x = sub.x
        self.y = sub.y
        self.r = 1
        self.color = RED
        self.width = 2
        self.origin = sub

    def update(self):
        self.r += 1

    def render(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.r, self.width)

class Torpedo(pygame.sprite.Sprite):
    def __init__(self, sub):
        self.image = load_image("data/sprites/torpedo.png")
        self.x = sub.x
        self.y = sub.y
        self.dx = 2
        self.dir = sub.dir

        if sub.flip:
            self.dx *= -1

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 6.0, 3.0)

    def update(self):
        self.x += self.dx

    def render(self, surface):
        surface.blit(self.image, (self.x, self.y))

player_texture = "data/sprites/sub.png"
player = Player(player_texture, 200, 200)
player.image = pygame.transform.scale(player.image, (64, 64))

enemies = []
enemy_texture = "data/sprites/enemy.png"
enemy = Enemy(enemy_texture, 300, 200)
enemies.append(enemy)

sonar_waves = []
torpedos = []

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running == False
            pygame.quit()
            sys.exit()
            
        #input
        if event.type == KEYDOWN:
            if event.key == pygame.K_LEFT:
                player.dx = -1
            if event.key == pygame.K_RIGHT:
                player.dx = 1
            if event.key == pygame.K_UP:
                player.dy = -1
            if event.key == pygame.K_DOWN:
                player.dy = 1
            if event.key == pygame.K_SPACE:
                wave = SonarWave(player)
                sonar_waves.append(wave)
            if event.key == pygame.K_x:
                torpedo = Torpedo(player)
                torpedos.append(torpedo)
        if event.type == KEYUP:
            if event.key == pygame.K_LEFT:
                player.dx = 0
            if event.key == pygame.K_RIGHT:
                player.dx = 0
            if event.key == pygame.K_UP:
                player.dy = 0
            if event.key == pygame.K_DOWN:
                player.dy = 0

    screen.fill(BLACK)

    player.update()
    player.render(screen)

    enemy.update()
    enemy.render(screen)

    for wave in sonar_waves:
        wave.update()
        if wave.r > 200:
            sonar_waves.remove(wave)
        
        for enemy in enemies:
            dist = get_distance(wave, enemy)
            if wave.r >= dist and wave.r <= dist + TILE_SIZE:
                if enemy.echo == False and wave.origin != enemy: 
                    echo = SonarWave(enemy)
                    sonar_waves.append(echo)
                    enemy.echo = True
                if enemy.echo_timer > 30:
                    enemy.echo = False
                    enemy.echo_timer = 0

        print(enemy.echo)       
        wave.render(screen)

    for torpedo in torpedos:
        torpedo_rect = torpedo.get_rect()
        torpedo.update()
        for enemy in enemies:
            enemy_rect = enemy.get_rect()
            if enemy_rect.colliderect(torpedo_rect):
                print('collision!')
        torpedo.render(screen)

        #print('torpedo: ', torpedo)

    pygame.display.flip()

    clock.tick(FPS)
    
    '''
    print('player dir: ', player.dir)
    print('player old dir:', player.old_dir)
    print('player flip state: ', player.flip)
    '''