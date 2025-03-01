import pygame
import os
import time
import random
pygame.font.init() #import fonts
pygame.mixer.init() #import music

# Set up the display for the game
WIDTH, HEIGHT = 1440, 900
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cosmic Defenders")

#Load fonts
main_font = pygame.font.Font(os.path.join("assets", "retropix.ttf"), 50)
Game_Over = retropix_font = pygame.font.Font(os.path.join("assets", "retropix.ttf"), 70)
lost_score = retropix_font = pygame.font.Font(os.path.join("assets", "retropix.ttf"), 50)
Winning_Screen = retropix_font = pygame.font.Font(os.path.join("assets", "retropix.ttf"), 50)

# Load Alien images
Red_Alien = pygame.image.load(os.path.join("assets", "RedAlien.gif"))
Green_Alien = pygame.image.load(os.path.join("assets", "GreenAlien.gif"))
Yellow_Alien = pygame.image.load(os.path.join("assets", "YellowAlien.gif"))
Boss_Alien = pygame.image.load(os.path.join("assets", "FinalBoss.png"))
Boss_Alien = pygame.transform.scale(Boss_Alien, (300, 300))

# Load Player image
Spaceship = pygame.image.load(os.path.join("assets", "Spaceship.png"))

# Lasers
Red_Beam = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
Red_Beam = pygame.transform.scale(Red_Beam, (150, 150))
Green_Beam = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
Green_Beam = pygame.transform.scale(Green_Beam, (150, 150))
Yellow_Beam = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
Yellow_Beam = pygame.transform.scale(Yellow_Beam, (150, 150))

# Player Laser
Player_Beam = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
Player_Beam = pygame.transform.scale(Player_Beam, (150, 150))

# Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "SpaceBackground.jpg")), (WIDTH, HEIGHT))

#this is used to create the laser for the game
class Laser:
    def __init__(self, x, y, img): #initialize the laser
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window): #draw the laser
        window.blit(self.img, (self.x, self.y))

    def move(self, vel): #move the laser
        self.y += vel

    def off_screen(self, height): #check if the laser is off the screen
        return not(self.y <= height and self.y >= 0)

    def collision(self, obj): #check if the laser has collided with an object
        return collide(self, obj)


class Ship: #this is used to create the ships for the game
    COOLDOWN = 30 #cooldown for the laser to shoot

    def __init__(self, x, y, health=100): #initialize the ship
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window): #draw the ship
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj): #move the laser and check if it has collided with an object
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self): #cooldown for the laser to shoot
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self): #shoot the laser from the ship
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 52, self.y - 50, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self): #get the width of the ship
        return self.ship_img.get_width()

    def get_height(self): #get the height of the ship
        return self.ship_img.get_height()

#this is used to create the player for the game
class Player(Ship): 
    def __init__(self, x, y, health=100): #initialize the player
        super().__init__(x, y, health)
        self.ship_img = Spaceship
        self.laser_img = Player_Beam
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.score = 0
        self.hit_point = 0

    def move_lasers(self, vel, objs): #move the laser and check if it has collided with an object
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else: 
                for obj in objs: 
                    if laser.collision(obj): #this is used to check the collissions between the player and the different types of enemies
                        self.hit_point += 1 
                        if self.hit_point >= 1 and isinstance(obj, Enemy) and obj.ship_img == Green_Alien:
                            objs.remove(obj) 
                            self.score += 1
                            self.hit_point = 0 #when the alien has been defeated, their hit point is reset to 0
                        elif self.hit_point >= 1 and isinstance(obj, Enemy) and obj.ship_img == Yellow_Alien:
                                obj.health -= 50
                                if obj.health <= 0: 
                                    objs.remove(obj)
                                    self.score += 1
                        elif self.hit_point >= 1 and isinstance(obj, Enemy) and obj.ship_img == Red_Alien:
                            obj.health -= 34
                            if obj.health <= 0:
                                objs.remove(obj)
                                self.score += 1
                        elif self.hit_point >= 1 and isinstance(obj, Enemy) and obj.ship_img == Boss_Alien:
                            obj.health -= 2 #the boss has more health than the other aliens
                            self.hit_point = 0
                            if obj.health <= 0:
                                objs.remove(obj)
                                self.score += 1

                                #This is used to create the winning screen for the game, since the player needs to defeat the boss to win the game
                                WIN.blit(BG, (0,0))
                                Clear_Music = pygame.mixer.music.load(os.path.join("assets", "Clear_Music.mp3"))
                                Clear_Music = pygame.mixer.music.play(-1)
                                win_label = Winning_Screen.render("Congratulations! you have defeated the aliens and saved the galaxy!", 1, (0,255,0))
                                WIN.blit(win_label, (WIDTH/2 - win_label.get_width()/2, 350)) 
                                score_label = lost_score.render(f"Score: {self.score}", 1, (255,255,255))
                                WIN.blit(score_label, (WIDTH/2 - score_label.get_width()/2, 450))
                                End_label = lost_score.render("THE END - See you next mission!", 1, (255,255,255))
                                WIN.blit(End_label, (WIDTH/2 - End_label.get_width()/2, 550))
                                pygame.display.update() 
                                time.sleep(10)
                                main_menu()
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        

    def draw(self, window): #draw the player
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window): #create the healthbar for the player
        pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10)) 


class Enemy(Ship): #this is used to create the enemies for the game
    COLOR_MAP = {
                "Red": (Red_Alien, Red_Beam), 
                "Green": (Green_Alien, Green_Beam),
                "Yellow": (Yellow_Alien, Yellow_Beam),
                "Boss": (Boss_Alien, Red_Beam)
                }
    
    def __init__(self, x, y, color, health=100): #initialize the enemy
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.hit_point = 0
        self.max_health = health

        if color == "Boss": #boss enemy behaviours
            self.vel = 1
            self.y = 50
            self.direction = 1

    def draw(self, window): #healthbar for the boss, red and yellow aliens
        super().draw(window)
        #boss healthbar
        if self.ship_img == Boss_Alien: 
            pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
            pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10) )
            #red alien healthbar 
        elif self.ship_img == Red_Alien:
            pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
            pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10) )
            #yellow alien healthbar
        elif self.ship_img == Yellow_Alien:
            pygame.draw.rect(window, (255,0,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
            pygame.draw.rect(window, (0,255,0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10) )

    def move(self, vel): #move the enemies, with the boss enemy moving left and right and the other enemies moving down
        if self.ship_img == Boss_Alien:
            self.x += self.vel * self.direction
            if self.x <= 0 or self.x + self.get_width() >= WIDTH:
                self.direction *= -1
        else:
            self.y += vel 

    def shoot(self): #shoot the laser from the enemy
        if self.cool_down_counter == 0:
            laser1 = Laser(self.x - 10, self.y + 30, self.laser_img)
            laser2 = Laser(self.x + self.get_width() - 140, self.y + 30, self.laser_img)
            self.lasers.append(laser1)
            self.lasers.append(laser2)
            self.cool_down_counter = 1


def collide(obj1, obj2): #check if the objects have collided with each other
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main(): #main game loop
    run = True
    FPS = 60 
    level = 0
    lives = 3
    main_theme = pygame.mixer.music.load(os.path.join("assets", "Main_Theme.mp3")) #load the main theme for the game
    main_theme = pygame.mixer.music.play(-1)
    
    enemies = []
    wave_length = 5 #number of enemies in each wave
    enemy_vel = 1 #speed of the enemies

    player_vel = 5 #speed of the player
    laser_vel = 5 #speed of the laser

    player = Player(600, 630) #player starting position
    player.score = 0

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    paused = False

    def redraw_window(): #Main HUD for the game
        WIN.blit(BG, (0,0))
        # draw text
        lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        score_label = main_font.render(f"Score: {player.score}", 1, (255,255,255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(score_label, (WIDTH/2 - score_label.get_width()/2, 10))

        if not paused:
            main_theme = pygame.mixer.music.unpause()
            for enemy in enemies:
                enemy.draw(WIN)

            player.draw(WIN)

        if lost: #Game Over screen
            lost_label = Game_Over.render("GAME OVER", 1, (255,0,0)) 
            score_label = lost_score.render(f"Score: {player.score}", 1, (255,255,255))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))
            WIN.blit(score_label, (WIDTH/2 - score_label.get_width()/2, 450))
            Main_theme = pygame.mixer.music.pause()
            Game_Over_Sound = pygame.mixer.music.load(os.path.join("assets", "Game_Over.mp3"))
            Game_Over_Sound = pygame.mixer.music.play()
        
        if paused: #Pause screen
            main_theme = pygame.mixer.music.pause()
            pause_label = main_font.render("PAUSED", 1, (255,255,255))
            WIN.blit(pause_label, (WIDTH/2 - pause_label.get_width()/2, 350))
            continue_label = main_font.render("ENTER - Continue", 1, (255,255,255))
            WIN.blit(continue_label, (WIDTH/2 - continue_label.get_width()/2, 450))
            exit_label = main_font.render("BACKSPACE - Exit", 1, (255,255,255))
            WIN.blit(exit_label, (WIDTH/2 - exit_label.get_width()/2, 550))

        pygame.display.update()

    while run: #game loop
        clock.tick(FPS)
        redraw_window()

        if player.health <= 0: #player health
            lives -= 1
            player.health = 100

        if lives <= 0: #game over
            lost = True
            lost_count += 1

        if lost: #game over screen
            if lost_count > FPS * 3:
                run = False
            else:
                continue
        
        if player.score <= 0: #spawn green aliens and each level for the game
           if len(enemies) == 0: 
                level += 1
                wave_length += 5

                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["Green"]))
                    enemies.append(enemy)
        elif player.score <= 10: #spawn yellow aliens
            if len(enemies) == 0:
                level += 1
                lives += 1
                wave_length += 0

                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["Yellow"]))
                    enemies.append(enemy)
        elif player.score <= 20: #spawn red aliens
            if len(enemies) == 0:
                level += 1
                lives += 1
                wave_length += 0

                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["Red"]))
                    enemies.append(enemy)
        elif player.score <= 30: #spawn green, yellow and red aliens
            if len(enemies) == 0:
                level += 1
                lives += 1
                wave_length += 0

                for i in range(wave_length):
                    enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500, -100), random.choice(["Green", "Yellow", "Red"]))
                    enemies.append(enemy)
        elif player.score <= 40: #spawn the boss alien
            if len(enemies) == 0: 
                level += 1
                lives += 1
                wave_length += 0

                boss_spawned = False
                for enemy in enemies:
                    if isinstance(enemy, Enemy) and enemy.ship_img == Boss_Alien:
                        boss_spawned = True
                        break
                if not boss_spawned:
                    Boss_Music = pygame.mixer.music.load(os.path.join("assets", "Final_Boss_Music.mp3"))
                    Boss_Music = pygame.mixer.music.play(-1)
                    Main_Theme = pygame.mixer.music.pause()
                    enemy = Enemy(600, 50, "Boss") #boss enemy spawn position
                    enemies.append(enemy)
            
        for event in pygame.event.get(): #game controls
            if event.type == pygame.QUIT:
                quit()

            # Pause and unpause when Enter is pressed
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    Pause_Sound = pygame.mixer.Sound(os.path.join("assets", "Pause_Sound.mp3"))
                    Pause_Sound.play()
                    paused = not paused
                elif event.key == pygame.K_BACKSPACE and paused: #exit the game
                    main_menu()

        if paused:
            continue

        # Player controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a] and player.x - player_vel > 0: # left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] or keys[pygame.K_d] and player.x + player_vel + 190 < WIDTH: # right
            player.x += player_vel
        if keys[pygame.K_UP] or keys[pygame.K_w] and player.y - player_vel > 0: # up
            player.y -= player_vel
        if keys[pygame.K_DOWN] or keys[pygame.K_s] and player.y + player_vel + player.get_height() + 15 < HEIGHT: # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        # Enemy controls
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)
            
            if random.randrange(0, 2*60) == 1: #randomly shoot the laser
                enemy.shoot()

            if collide(enemy, player): #check if the enemy has collided with the player
                if enemy.ship_img == Boss_Alien:
                    player.health -= 1
                else:
                    lives -= 1
                    player.score += 1
                    enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
    
        player.move_lasers(-laser_vel, enemies) #move the player laser

# Main Menu
def main_menu():
    title_font = pygame.font.Font(os.path.join("assets", "retropix.ttf"), 90)
    secondary_font = pygame.font.Font(os.path.join("assets", "retropix.ttf"), 70)
    Title_Music = pygame.mixer.music.load(os.path.join("assets", "Title_Theme.mp3"))
    Title_Music = pygame.mixer.music.play(-1)

    run = True
    while run:
        WIN.blit(BG, (0,0))
        title_label = secondary_font.render("Press Enter...", 1, (255,255,255))
        WIN.blit(title_label, (WIDTH -380 - title_label.get_width()/2.4, 430))
        Game_Logo = title_font.render("Cosmic Defenders", 1, (255,255,255))
        WIN.blit(Game_Logo, (WIDTH - 370 - Game_Logo.get_width()/2, 300))
        Space_Protagonist = pygame.transform.scale(pygame.image.load(os.path.join("assets", "Protagonist.png")), (800, 800))
        WIN.blit(Space_Protagonist, (WIDTH -1300 - title_label.get_width()/2, 1))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    Tutorial()
    pygame.quit() 

# Tutorial
def Tutorial():
    Tutorial = pygame.image.load(os.path.join("assets", "Game_Tutorial.png"))

    run = True
    while run:
        WIN.blit(Tutorial, (0,0))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    main()
    pygame.quit()

main_menu()