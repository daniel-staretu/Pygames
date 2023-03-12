import pygame
from pytmx.util_pygame import load_pygame
import os

pygame.init()

#Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
WINDOW_TITLE = "Dungeon game"
FRAME_RATE = 60

#Window
display = pygame.display
display.set_caption(WINDOW_TITLE)
screen = display.set_mode(WINDOW_SIZE)

#Backgrounds
GRASS_GREEN = (16, 120, 38)
def draw_background():
    screen.fill(GRASS_GREEN)

#Clock
CLOCK = pygame.time.Clock()

#Player actions
moving_left = False
moving_right = False
moving_up = False
moving_down = False

#ENTITY CLASS
class Entity(pygame.sprite.Sprite):
    def __init__(self, entity_type, x, y, scale, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.entity_type = entity_type
        self.speed = speed
        self.direction_x = 1
        self.direction_y = 1
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        #Loading animations
        #structure {animation:index}
        animation_types = {'walking_down':0,'walking_horizontally':1,'walking_up':2}
    
        for animation in animation_types:
            #reset temp list of images
            temp_list = []
            #count number of files in the folder
            num_of_frames = len(os.listdir(f'gfx/{self.entity_type}/{animation}'))
            #add image lists to array
            for i in range(num_of_frames):
                img = pygame.image.load(f'gfx/{self.entity_type}/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect() 
        self.rect.center = (x,y)

    def move(self, moving_up, moving_left, moving_down, moving_right):
        #reset movement variables
        dx = 0
        dy = 0

        #assign movement variables
        if moving_up:
            dy = -self.speed
            self.direction_y = -1
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction_x = -1
        if moving_down:
            dy = self.speed
            self.direction_y = 1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction_x = 1

        #update rect position
        self.rect.x += dx
        self.rect.y += dy

    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 200
        #update image to current frame
        self.image = self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def update_action(self, new_action):
        #if idle, keep facing last position
        if new_action == 'idle':
            self.frame_index = 0
        #check if new action is different to the previous one
        elif new_action != self.action:
            self.action = new_action
            #update the animation from the start
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

#PROJECTILE CLASS
class Projectile(pygame.sprite.Sprite):
    def __init__(self, projectile_type, x, y, scale, speed, direction):

        self.projectile_type = projectile_type
        self.speed = speed
        self.animation_list = []
        self.frame_index = 0

        #add image lists to array
        #count number of files in the folder
        num_of_frames = len(os.listdir(f'gfx/{self.projectile_type}'))
        temp_list = []
        for i in range(num_of_frames):
            img = pygame.image.load(f'gfx/{self.projectile_type}/{i}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)


        self.image = self.animation_list[self.frame_index]
        self.rect = self.image.get_rect() 
        self.rect.center = (x,y)
        self.direction = direction

#TMX Map data
tmxdata = load_pygame("map/test.tmx")

#Create sprite groups
projectile_group = pygame.sprite.Group()

#Declaring entities
player = Entity('player', 640, 360, 3, 5)



#GAME LOOP
while True:

    CLOCK.tick(FRAME_RATE)

    draw_background()

    #update and draw sprite groups
    projectile_group.update()
    projectile_group.draw(screen)

    player.update_animation()
    player.draw()

    #update animation
    if player.alive:
        if moving_down:
            player.update_action(0)
        elif moving_right or moving_left:
            player.update_action(1)
        elif moving_up:
            player.update_action(2)
        else:
            player.update_action('idle')
        player.move(moving_up, moving_left, moving_down, moving_right)

    #CHECK FOR EVENTS
    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            pygame.quit()
        #keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                moving_up = True
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                moving_down = True
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
        #mouse presses   
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: #left mouse button
            shoot = True

        #keyboard released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                moving_up = False
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                moving_down = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                moving_right = False
        #mouse released
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1: #left mouse button
            shoot = False
            
    display.update()