import pygame
import sys
from pygame.locals import *
import random

pygame.init()  # initialize pygame

#initialzize the background image
screenwidth, screenheight = (1000, 720)
screen = pygame.display.set_mode((screenwidth, screenheight))
picture = pygame.image.load('space_background.webp')
bg = pygame.transform.scale(picture, (screenwidth, screenheight))
pygame.display.set_caption('Space Invaders by Liam McCarthy')
font = pygame.font.Font(None, 36)

#class to control the player's ship
class PlayerShip:
    def __init__(self, imageFile):
        self.shape = pygame.transform.scale(pygame.image.load(imageFile), (100,100))
        self.position = 600
        self.score = 0
        self.lives = 3

    #method to display the PlayerShip on the game screen
    def show(self, surface):
        surface.blit(self.shape, (self.position, 600))

    #method to update PlayerShip coordinates on each clock tick
    def updateCoords(self, x):
        if self.position > 0 and self.position < 900:
            self.position += x
        elif self.position <= 0:
            self.position += 1
        else:
            self.position -= 1

    def enemyHit(self):
        self.score += 10

    def bonusEnemyHit(self):
        self.score += 100

    def playerHit(self): 
        self.lives -= 1

#class to control each individual enemy
class EnemyShip:
    def __init__(self, imageFile, x_pos, y_pos):
        self.shape = pygame.transform.scale(pygame.image.load(imageFile), (100,100))
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.alive = True

    #method to show the EnemyShip on the game screen
    def show(self, surface):
        surface.blit(self.shape, (self.x_pos, self.y_pos))

    #method to preven the EnemyShip from moving past the screen edge
    def touchingEdge(self):
        if self.x_pos <= 0:
            self.x_pos += 1
            return True
        elif self.x_pos >= 900:
            self.x_pos -= 1
            return True

    #method to move the EnemyShip down if it reaches the edge    
    def moveDown(self):
        self.y_pos += 20

    #method to move the EnemyShip on each clock tick
    def updateCoords(self, x):
        self.x_pos += x

    #method to remove an EnemyShip from the game
    def remove(self):
        transparent = (0,0,0,0)
        self.shape.fill(transparent)
        self.alive = False
    
    #method to determine if an EnemyShip is touching a PlayerShip
    def touchingPlayer(self, player_x):
        if abs(self.x_pos - player_x) < 40 and self.y_pos > 520 and self.alive == True:
            return True

#class to control a group of enemies
class EnemyGroup:
    def __init__(self):
        self.group_x = 125
        self.group_y = 50
        self.enemies = {}
        self.speed = 1

    #method to create a group of EnemyShips
    def makeShips(self):
        self.group_x = 125
        self.group_y = 50
        for i in range(10):
            for j in range(3):
                self.enemies[(i,j)] = EnemyShip('enemy_ship.png', self.group_x + 70 * i, self.group_y + 100 * j)

    #method to show a group of EnemyShips on the game screen
    def show(self):
        for num, enemy in self.enemies.items():
            enemy.show(screen)

    #method to move the EnemyGroup horizontally on each clock tick
    def updateCoords(self):
        for num, enemy in self.enemies.items():
            enemy.updateCoords(self.speed)
    
    #method to move the EnemyGroup down if it touches the edge
    def moveDown(self):
        for num, enemy in self.enemies.items():
            enemy.moveDown()
    
    #method to control the EnemyGroup's behavior when it touches the edge
    def checkDirection(self):
        for num, enemy in self.enemies.items():
            if enemy.touchingEdge():
                self.group_y += 100
                self.moveDown()
                self.speed = -self.speed

#class to represent a bonus enemy that the player can hit for extra points
class BonusEnemy:
    def __init__(self, imageFile, x_pos, y_pos):
        self.shape = pygame.transform.scale(pygame.image.load(imageFile), (100,90))
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.alive = True
        self.speed = 2

    #method to display a BonusEnemy on the game screen
    def show(self, surface):
        if self.alive:
            surface.blit(self.shape, (self.x_pos, self.y_pos))

    #method to control the BonusEnemy's movement
    def updateCoords(self):
        self.x_pos += self.speed 
        if self.x_pos < -200:
            self.speed = -self.speed
        elif self.x_pos > 1200:
            self.speed = -self.speed

    #method to remove the BonusShip
    def remove(self):
        transparent = (0,0,0,0)
        self.shape.fill(transparent)
        self.alive = False

#class to control the player's lasers
class Laser:
    def __init__(self, x_pos, imageFile):
        self.x_pos = x_pos
        self.shape = pygame.transform.scale(pygame.image.load(imageFile), (20,20))
        self.y_pos = 600
        self.speed = 5

    #method to show the laser on the game screen
    def show(self, surface):
        surface.blit(self.shape, (self.x_pos + 40, self.y_pos))

    #method to move the laser up on the screen
    def updateCoords(self):  
        self.y_pos -= 15

    #method to check if the laser collides with an enemy
    def checkCollision(self, enemy_x, enemy_y, enemy_alive):
        if abs(enemy_x - self.x_pos) < 40 and abs(self.y_pos - enemy_y) < 20 and enemy_alive == True:
            return True

    #method to check if the laser collides with a bonus enemy    
    def checkBonusCollision(self, enemy_x, enemy_y, enemy_alive):
        if abs(enemy_x - self.x_pos) < 50 and abs(self.y_pos - enemy_y) < 40 and enemy_alive == True:
            return True

#class that controls enemy lasers        
class EnemyLaser:
    def __init__(self, x_pos, y_pos, imageFile):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.shape = pygame.transform.scale(pygame.image.load(imageFile), (40,40))
        self.speed = 5

    #method to show an EnemyLaser on the game screen
    def show(self, surface):
        surface.blit(self.shape, (self.x_pos + 30, self.y_pos + 50))

    #method to move the EnemyLaser down on the screen
    def updateCoords(self):  
        self.y_pos += 10

    #method to check if an EnemyLaser collides with the player
    def checkCollision(self, player_x):
        if abs(player_x - self.x_pos) < 50 and abs(self.y_pos - 600) < 20:
            return True


#method to draw a starting menu that greets the player and provides game instructions
def draw_start_menu():
    screen.fill((15, 15, 15))
    font = pygame.font.SysFont('arial', 70)
    mediumFont = pygame.font.SysFont('arial', 50)
    smallFont = pygame.font.SysFont('arial', 30)
    title = font.render('Space Invaders: Star Wars Edition', True, (255, 255, 0))
    start_button = mediumFont.render('Press [SPACE] to start', True, (255, 255, 0))
    instructions = smallFont.render('Press left and right arrows to move, press [SPACE] to shoot', True, (255, 255, 255))
    darthVader = pygame.transform.scale(pygame.image.load("darth_vader.png"), (250, 250))
    lukeSkywalker = pygame.transform.scale(pygame.image.load("luke_skywalker.png"), (250, 300))
    deathStar = pygame.transform.scale(pygame.image.load("big_enemy.png"), (400,300))
    screen.blit(title, (screenwidth/2 - title.get_width()/2, 100))
    screen.blit(start_button, (screenwidth/2 - start_button.get_width()/2, 180))
    screen.blit(instructions, (180, 280))
    screen.blit(darthVader, (10, 450))
    screen.blit(lukeSkywalker, (770, 400))
    screen.blit(deathStar, (300, 300))
    pygame.display.update()

#method to draw a screen that appears between game levels
def draw_next_level(score, lives):
    screen.fill((15, 15, 15))
    font = pygame.font.SysFont('arial', 60)
    title = font.render('Press space to continue fighting the Empire!', True, (255, 255, 0))
    show_score = font.render(f'Score: {score}', True, (255, 255, 0))
    show_lives = font.render(f'Lives Remaining: {lives}', True, (255, 255, 0))
    darthMaul = pygame.transform.scale(pygame.image.load("darth_maul.png"), (400,300))
    screen.blit(title, (screenwidth/2 - title.get_width()/2, 200 - title.get_height()/2))
    screen.blit(show_score, (screenwidth/2 - show_score.get_width()/2, 200 + show_score.get_height()/2))
    screen.blit(show_lives, (screenwidth/2 - show_lives.get_width()/2, 200 + show_score.get_height() + show_lives.get_height()/2))
    screen.blit(darthMaul, (275, 400))
    pygame.display.update()

#method to draw a game over screen
def draw_game_over_screen(score):
    screen.fill((0, 0, 0))
    image = pygame.transform.scale(pygame.image.load("game_over.png"), (1000,500))
    screen.blit(image, (0, 50))
    font = pygame.font.SysFont('arial', 100)
    smallFont = pygame.font.SysFont('arial', 60)
    show_score = font.render(f'Score: {score}', True, (255, 255, 0))
    try_again = smallFont.render('Press [SPACE] to try again!', True, (255, 255, 0))
    screen.blit(show_score, (screenwidth/2 - show_score.get_width()/2, 400))
    screen.blit(try_again, (screenwidth/2 - try_again.get_width()/2, 500))
    pygame.display.update()    

# intialize the starting variables for the game
Player = PlayerShip('player_ship.png')
Enemies = EnemyGroup()
Enemies.makeShips()
BonusEnemy = BonusEnemy('big_enemy.png', 0, 40)
Laser = Laser(Player.position, 'laser.png')
laser_active = False
EnemyLaser = EnemyLaser(0, 0, 'enemy_laser.png')
enemyLaser_active = False
enemySize = len(Enemies.enemies)
game_state = "start_menu"

while True:
    #allow the user to exit the game by pressing the 'X' button
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

    #handle behavior for the game's start menu
    if game_state == "start_menu":
        draw_start_menu()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:       
            game_state = "game"
    
    #handle behavior for when the player completes a level
    if game_state == "next_level":
        draw_next_level(Player.score, Player.lives)
        Enemies.makeShips()
        BonusEnemy.alive = True
        laser_active = False
        enemyLaser_active = False
        enemySize = len(Enemies.enemies)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:       
            game_state = "game"

    #handle behavior when the player loses the game
    if game_state == "gameOver":
        draw_game_over_screen(Player.score)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            Player.lives = 3
            Player.score = 0       
            Enemies.makeShips()
            BonusEnemy.alive = True
            laser_active = False
            enemyLaser_active = False 
            enemySize = len(Enemies.enemies)
            game_state = "game"

    #handle behavior for when the game is active
    if game_state == "game":
        pygame.time.wait(20)
        screen.blit(bg, (0, 0))
        score_text = font.render(f'Score: {Player.score}', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))   
        lives_text = font.render(f'Lives: {Player.lives}', True, (255, 255, 255))
        screen.blit(lives_text, (10, 40)) 
        
        #display the player and enemies
        Player.show(screen)    
        Enemies.show()

        #control the enemies' movements and initialize an enemy to shoot a laser
        Enemies.updateCoords()
        Enemies.checkDirection()
        shootingEnemy = (random.randint(0, 10), random.randint(0,3))

        #show the bonus enemy once the enemy group reaches a set y-coord
        if Enemies.group_y > 500:
            BonusEnemy.show(screen)
            BonusEnemy.updateCoords()

        #end the level once all enemies are defeated
        if enemySize == 0:
            game_state = "next_level"

        #show the laser and control its movement
        if laser_active == True:
            Laser.show(screen)
            Laser.updateCoords()

        #reset the laser once it reaches the top of the screen
        if Laser.y_pos < 0:
            laser_active = False
            Laser.y_pos = 600

        #call the enemy laser
        if enemyLaser_active == True:
            EnemyLaser.show(screen)
            EnemyLaser.updateCoords()
            #reset the laser if it reaches the bottom of the screen
            if EnemyLaser.y_pos > 650:
                enemyLaser_active = False
            #handle case if the enemy laser hits the player
            elif EnemyLaser.checkCollision(Player.position) == True:
                enemyLaser_active = False
                screen.blit(pygame.transform.scale(pygame.image.load('explosion.png'), (200,200)), (Player.position - 50, 550))
                pygame.display.update()
                Player.playerHit()

        #hanndle the behavior for the group fo enemies
        for num, enemy in Enemies.enemies.items():
            #handle if the player hits an enemy 
            if Laser.checkCollision(enemy.x_pos, enemy.y_pos, enemy.alive):
                laser_active = False
                Laser.y_pos = 600
                screen.blit(pygame.transform.scale(pygame.image.load('explosion.png'), (100,100)), (enemy.x_pos, enemy.y_pos))
                pygame.display.update()
                enemy.remove()
                enemySize -= 1
                Player.enemyHit()
            
            #end the game if an enemy touches the player
            if enemy.touchingPlayer(Player.position):
                game_state = "gameOver"

            #assign the enemy laser to a random enemy
            if num == shootingEnemy and enemyLaser_active == False and enemy.alive == True:
                EnemyLaser.x_pos = enemy.x_pos
                EnemyLaser.y_pos = enemy.y_pos
                enemyLaser_active = True

        #handle if the player shoots the bonus enemy
        if Laser.checkBonusCollision(BonusEnemy.x_pos, BonusEnemy.y_pos, BonusEnemy.alive) and Enemies.group_y > 500:
            laser_active = False
            Laser.y_pos = 600
            screen.blit(pygame.transform.scale(pygame.image.load('explosion.png'), (300,300)), (BonusEnemy.x_pos - 100, BonusEnemy.y_pos - 100))
            BonusEnemy.alive = False
            Player.bonusEnemyHit()
        
        #end the game if the player runs out of lives
        if Player.lives == 0:
            game_state = "gameOver"

        # stores keys pressed 
        keys = pygame.key.get_pressed()
        
        # if left arrow key is pressed
        if keys[pygame.K_LEFT]:
            # decrement in x co-ordinate
            Player.updateCoords(-10)
        
        # if left arrow key is pressed
        if keys[pygame.K_RIGHT]:   
            # increment in x co-ordinate
            Player.updateCoords(10)

        # if space key is pressed
        if keys[pygame.K_SPACE] and laser_active == False:   
            # create a new laser
            Laser.x_pos = Player.position
            laser_active = True

        #update the game
        pygame.display.update()
