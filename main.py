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

def load_image(path):
    image = pygame.image.load(path).convert()
    return image

def get_distance(obj_a, obj_b):
    return math.sqrt((obj_b.x - obj_a.x) ** 2 + (obj_b.y - obj_a.y) ** 2)

class PhysicsEntity(pygame.sprite.Sprite):
    def __init__(self, texture, xpos, ypos, *args, **kwargs):
        super().__init__()

        self.image = load_image(texture)
        self.x = xpos
        self.y = ypos
        self.dx = 0
        self.dy = 0

    def render(self, surface):
        surface.blit(self.image, (self.x, self.y))

class Player(PhysicsEntity):
    def __init__(self, texture, xpos, ypos, *args, **kwargs):
        PhysicsEntity.__init__(self, texture, xpos, ypos)

    def update(self):
        self.x += self.dx
        
class Enemy(PhysicsEntity):
    def __init__(self, texture, xpos, ypos, *args, **kwargs):
        PhysicsEntity.__init__(self, texture, xpos, ypos)

    def update(self):
        self.x += self.dx
        self.y += self.dy

class SonarWave:
    def __init__(self, sub):
        self.x = sub.x
        self.y = sub.y
        self.r = 1
        self.color = RED
        self.width = 2

    def update(self):
        self.r += 1

    def render(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.r, self.width) 

player_texture = "data/sprites/sub.png"
player = Player(player_texture, 200, 200)

enemies = []
enemy_texture = "data/sprites/enemy.png"
enemy = Enemy(enemy_texture, 300, 200)
enemies.append(enemy)

sonar_waves = []

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
            if event.key == pygame.K_SPACE:
                wave = SonarWave(player)
                sonar_waves.append(wave)
        if event.type == KEYUP:
            if event.key == pygame.K_LEFT:
                player.dx = 0

    screen.fill(BLACK)

    player.update()
    player.render(screen)

    enemy.update()
    enemy.render(screen)

    for wave in sonar_waves:
        wave.update()
        if wave.r > 200:
            sonar_waves.remove(wave)
        #next bit causes everything to crash because it just makes too many waves and needs a limit
        '''
        for enemy in enemies:
            dist = get_distance(wave, enemy)
            if wave.r >= dist:
                echo = SonarWave(enemy)
                sonar_waves.append(echo)
        '''        
        wave.render(screen)
        

    pygame.display.flip()

    clock.tick(FPS)