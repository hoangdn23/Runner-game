import pygame
import serial
from sys import exit
from random import randint, choice

# Connect Arduino to play
ser = serial.Serial('COM3', baudrate=9600, timeout=0)
serial_buffer = ""


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        player_walk1 = pygame.image.load("Runner_game/images/player_walk_1.png").convert_alpha()
        player_walk2 = pygame.image.load("Runner_game/images/player_walk_2.png").convert_alpha()
        self.player_walk = [player_walk1, player_walk2]
        self.player_index = 0
        self.player_jump = pygame.image.load("Runner_game/images/jump.png").convert_alpha()

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom = (80, 300))
        self.gravity = 0
        self.button_pressed = 1

    def player_input(self):
        global serial_buffer
        serial_buffer += ser.read(ser.in_waiting or 1).decode('utf-8', errors='ignore')
    
        while "\n" in serial_buffer:
            line, serial_buffer = serial_buffer.split("\n", 1)
            line = line.strip()
            if " " in line: 
                try:
                    y_str, button_str = line.split(" ") 
                    joystick_y = int(y_str)
                    self.button_pressed = int(button_str)
                
                    # print(joystick_y, self.button_pressed)
                    if joystick_y <= 0 and self.rect.bottom >= 300:
                        self.gravity = -20
                    
                except ValueError:
                    pass 

        # keys = pygame.key.get_pressed()
        # if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
        #     self.gravity = -20
        
    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300

    def animation_state(self):
        if self.rect.bottom < 300:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]


    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()

        if type == "fly":
            fly_frame_1 = pygame.image.load("Runner_game/images/Fly1.png").convert_alpha()
            fly_frame_2 = pygame.image.load("Runner_game/images/Fly2.png").convert_alpha()
            self.frames = [fly_frame_1, fly_frame_2]
            y_pos = 210
        else:
            snail_frame_1 = pygame.image.load("Runner_game/images/snail1.png").convert_alpha()
            snail_frame_2 = pygame.image.load("Runner_game/images/snail2.png").convert_alpha()
            self.frames = [snail_frame_1, snail_frame_2]
            y_pos = 300

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom = (randint(900,1100), y_pos))

    def animation_state(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        self.rect.x -= 6
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()
            

class Clouds(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        if type == "cloud_1":
            cloud_1 = pygame.image.load("Runner_game/images/cloud1.png").convert_alpha()
            cloud_1 = pygame.transform.scale(cloud_1, (50, 25))
            self.image = cloud_1

        elif type == "cloud_2":
            cloud_2 = pygame.image.load("Runner_game/images/cloud1.png").convert_alpha()
            cloud_2 = pygame.transform.scale(cloud_2, (100, 50))
            self.image = cloud_2

        else:
            cloud_3 = pygame.image.load("Runner_game/images/cloud1.png").convert_alpha()
            cloud_3 = pygame.transform.scale(cloud_3, (200, 100))
            self.image = cloud_3

        self.rect = self.image.get_rect(midbottom = (randint(900, 1000), randint(100, 290)))

    def destroy(self):
        if self.rect.x <= -250:
            self.kill()

    def update(self):
        self.rect.x -= 2
        self.destroy()

def display_score():
    current_time = int(pygame.time.get_ticks() / 100) - start_time
    score_surf = test_font.render(f"Score: {current_time}", False, (64, 64, 64))
    score_rect = score_surf.get_rect(center = (400, 50))
    screen.blit(score_surf, score_rect)
    return current_time

def collision_sprite():
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        obstacle_group.empty()
        return False
    else:
        return True
    
pygame.init()

screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption("Runner")
clock = pygame.time.Clock()
test_font = pygame.font.Font("Runner_game/images/Pixeltype.ttf", 50)
game_active = False
start_time = 0
score = 0

# Groups
player = pygame.sprite.GroupSingle()
player.add(Player())

obstacle_group = pygame.sprite.Group()

cloud = pygame.sprite.Group()

# Background
sky_surface = pygame.image.load("Runner_game/images/Sky.png").convert()
ground_surface = pygame.image.load("Runner_game/images/ground.png").convert()
ground_surface = pygame.transform.scale(ground_surface, (900, ground_surface.get_height()))
ground_surface_rect = ground_surface.get_rect(topright = (900,300))

# Menu screen - player
player_stand = pygame.image.load("Runner_game/images/player_stand.png").convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand, 0, 2)
player_stand_rect = player_stand.get_rect(center = (400, 200))

# Menu screen - game title
game_title_surf = test_font.render("Runner", False, (64, 64, 64))
game_title_rect = game_title_surf.get_rect(center = (400, 65))

# Menu screen - press Space to start
game_menu_start_surf = test_font.render("Press Joystick to start", False, (64, 64, 64))
game_menu_start_rect = game_menu_start_surf.get_rect(center = (400, 350))

# Timer
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1400)

cloud_timer = pygame.USEREVENT + 2
pygame.time.set_timer(cloud_timer, 2700)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if game_active == True:
            if event.type == obstacle_timer:
                obstacle_group.add(Obstacle(choice(["fly", "snail", "snail"])))
            if event.type == cloud_timer:
                cloud.add(Clouds(choice(["cloud_1", "cloud_2", "cloud_3"])))

                    
    # Game Active Loop
    if game_active ==  True:
        screen.blit(sky_surface, (0,0))
        screen.blit(ground_surface, ground_surface_rect)

        ground_surface_rect.x -= 5
        if ground_surface_rect.x <= -70:
            ground_surface_rect.x = -6

        cloud.draw(screen)
        cloud.update()

        score = display_score()

        player.draw(screen)
        player.update()

        obstacle_group.draw(screen)
        obstacle_group.update()

        # Collision
        game_active = collision_sprite()

    # Menu    
    else:
        # 94, 129, 162
        screen.fill((255, 204, 204))
        screen.blit(player_stand, player_stand_rect)
        screen.blit(game_title_surf, game_title_rect)

        menu_score_surf = test_font.render(f"Score: {score}", False, (64, 64, 64))
        menu_score_rect = menu_score_surf.get_rect(center = (400, 350))

        cloud.empty()

        if score == 0:
            screen.blit(game_menu_start_surf, game_menu_start_rect)
        else:
            screen.blit(menu_score_surf, menu_score_rect)
        
        player.sprite.player_input()
        if player.sprite.button_pressed == 0:
            game_active = True
            start_time = int(pygame.time.get_ticks() / 100)

    pygame.display.update()
    clock.tick(60)