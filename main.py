# define imported modules
import pygame
from pygame.locals import *
import sys
import time
import math

# get pygame going
pygame.init()

# set initial screen width and height
SCREEN_W, SCREEN_H = 640, 480

# make the screen, the game clock, and a running game loop variable
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
clock = pygame.time.Clock()
running = True

# define some constants for colors, FPS, and tile size
BLACK = 0, 0, 0
RED = 255, 0, 0
GREEN = 0, 255, 0
FPS = 60
TILE_SIZE = 16

# helper function to load images
def load_image(path):
    image = pygame.image.load(path).convert()
    return image

# helper function for getting an absolute distance between 2D objects
def get_distance(obj_a, obj_b):
    return math.sqrt((obj_b.x - obj_a.x) ** 2 + (obj_b.y - obj_a.y) ** 2)

# define the base class for physics sprites
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
        self.hit = False

    # get rect for collisions
    def get_rect(self):
        return pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)    

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

    # render based on if the sprite is flipped 
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

        # some basic state machine for the enemy with only an idle case
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
        self.echo = False

    def update(self):
        self.r += 1

    def render(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.r, self.width)

class Torpedo(pygame.sprite.Sprite):
    def __init__(self, sub):
        self.image = load_image("data/sprites/torpedo.png")
        self.x = sub.x
        self.y = sub.y
        self.dir = sub.dir
        self.origin = sub

        if sub.dir == 'left':
            self.dx = -2
        else:
            self.dx = 2

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 6.0, 3.0)

    def update(self):
        self.x += self.dx

    def render(self, surface):
        surface.blit(self.image, (self.x, self.y))

def update_sonar(waves, entities):
    for wave in waves:
        wave.update()
        if wave.r > 200:
            waves.remove(wave)
        
        for enemy in entities:
            dist = get_distance(wave, enemy)
            if wave.r >= dist and wave.r <= dist + TILE_SIZE:
                if enemy.echo == False and wave.origin != enemy and not wave.echo: 
                    echo = SonarWave(enemy)
                    waves.append(echo)
                    enemy.echo = True
                    echo.echo = True
                if enemy.echo_timer > 30:
                    enemy.echo = False
                    enemy.echo_timer = 0

        wave.render(screen)

def update_torpedos(torpedos, entities):
    for torpedo in torpedos:
        torpedo_rect = torpedo.get_rect()
        torpedo.update()
        for entity in entities:
            entity_rect = entity.get_rect()
            if entity_rect.colliderect(torpedo_rect) and torpedo.origin != entity:
                print('collision!')
                entity.state = 'hit'
        torpedo.render(screen)

def check_hits(entities):
    for entity in entities:
        if entity.state == 'hit':
            entities.remove(entity)

entities = []

player_texture = "data/sprites/sub.png"
player = Player(player_texture, 200, 200)
player.image = pygame.transform.scale(player.image, (64, 64))
entities.append(player)
enemy_texture = "data/sprites/enemy.png"
enemy = Enemy(enemy_texture, 300, 200) 
entities.append(enemy)

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

    update_sonar(sonar_waves, entities)
    update_torpedos(torpedos, entities)
    check_hits(entities)

    pygame.display.flip()

    clock.tick(FPS)
    
    '''
    print('player dir: ', player.dir)
    print('player old dir:', player.old_dir)
    print('player flip state: ', player.flip)
    '''