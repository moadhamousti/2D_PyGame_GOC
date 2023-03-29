#import pygame and os
import pygame
import os
os.environ['SDL_VIDEODRIVER']='windib'
pygame.init()


# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)
LIGHTBLUE    = (   133, 214,   255)

#define dimensions
WIN_WIDTH = 800
WIN_HEIGHT = 550
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

#set window size
size = (WIN_WIDTH, WIN_HEIGHT)

#create camera class
class Camera(object):
    def __init__(self, camera_func, width, height): 
        self.camera_func = camera_func
        self.state = pygame.Rect(0, 0, width, height)

    def apply(self, target): 
        return target.rect.move(self.state.topleft)

    def update(self, target): 
        self.state = self.camera_func(self.state, target.rect)

def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l+HALF_WIDTH, -t+HALF_HEIGHT, w, h

    l = min(0, l)                           
    l = max(-(camera.width-WIN_WIDTH), l)   
    t = max(-(camera.height-WIN_HEIGHT), t) 
    t = min(0, t)                           
    return pygame.Rect(l, t, w, h)

#create thing class
class Thing(pygame.sprite.Sprite):
    def __init__(self): 
        pygame.sprite.Sprite.__init__(self)

#create character class
class Character(Thing):
    def __init__(self, x, y):
   
        Thing.__init__(self)
       
        self.xspeed = 0
        self.yspeed = 0
    
        self.onGround = False
        self.image = pygame.Surface((25,25))
        self.image.fill(WHITE)
        self.image.convert()
        self.rect = pygame.Rect(x, y, 25, 25)

    def update(self, up, left, right, platforms):
        if up:
            
            if self.onGround: self.yspeed -= 9

      
        if left:
            self.xspeed = -8
       
        if right:
            self.xspeed = 8

        if not self.onGround:
           
            self.yspeed += 0.3
           
            if self.yspeed > 100: self.yspeed = 100

        if not(left or right):
            self.xspeed = 0

      
        self.rect.left += self.xspeed

       
        self.collide(self.xspeed, 0, platforms)

       
        self.rect.top += self.yspeed

       
        self.onGround = False;

       
        self.collide(0, self.yspeed, platforms)

    
    def collide(self, xspeed, yspeed, platforms):
        for p in platforms: 
            if pygame.sprite.collide_rect(self, p):
                if xspeed > 0:
                    self.rect.right = p.rect.left
                if xspeed < 0:
                    self.rect.left = p.rect.right
                if yspeed > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yspeed = 0
                if yspeed < 0:
                    self.rect.top = p.rect.bottom


class Platform(Thing):
    def __init__(self, x, y):
        
        Thing.__init__(self)
        
        self.image = pygame.Surface((25, 25))
        self.image.convert()
        self.image.fill(LIGHTBLUE)
        self.rect = pygame.Rect(x, y, 25, 25)

    def update(self): 
        pass


class coinSprite(Platform):
    def __init__(self, x, y): 
        Platform.__init__(self, x, y)
        self.image = pygame.Surface((25, 25))
        self.image = pygame.image.load("coin.png")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)
        self.rect.centerx = x 
        self.rect.centery = y 

    def update(self):
        self.rect.center = pygame.image.load() 


class fireSprite(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = pygame.Surface((25, 25))
        self.image = pygame.image.load("fireball.png")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)
        self.rect.centerx = x 
        self.rect.centery = y 

    def update(self):
        self.rect.center = pygame.image.load() 

#create win class
class winSprite(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        
        self.image = pygame.Surface((25, 25))
        self.image = pygame.image.load("winsprite.png")
        self.image = self.image.convert()
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK)
        self.rect.centerx = x 
        self.rect.centery = y 

    def update(self):
        self.rect.center = pygame.image.load() 

#def gameworld function, 'level' parameter being which gameworld file is opened
def gameWorld(level):
    
    global cameraX, cameraY
    
    timer = pygame.time.Clock()

    
    up = left = right = False

    
    bg = pygame.Surface((25,25))
    bg.convert()
    bg.fill(BLACK)

    
    allSprites = pygame.sprite.Group()

    character = Character(25, 25)

    
    platforms = []
    coins = []
    fires = []
    wins = []

    
    x = y = 0

   
    designlevel = []

    
    file = open(level,"r")
    world = file.readlines()
    for line in world:
        designlevel.append(line[:-1])

    # build the level
    for row in designlevel:
        for i in row:
            if i == "P": 
                p = Platform(x, y)
                platforms.append(p)
                allSprites.add(p)
            if i == "C":
                c = coinSprite(x, y)
                coins.append(c)
                allSprites.add(c)
            if i == "F":
                f = fireSprite(x, y)
                fires.append(f)
                allSprites.add(f)
            x += 25 
        y += 25
        x = 0

    #set game level dimensions
    total_level_width  = len(designlevel[0])*25
    total_level_height = len(designlevel)*25

    #set camera function into a variable
    camera = Camera(complex_camera, total_level_width, total_level_height)

    #add character sprite to all sprites group
    allSprites.add(character)

    #set accumulator variables to 0
    global score
    score = 0
    totalcoins = 0

    #load sound effects
    pygame.mixer.init()

    coin = pygame.mixer.Sound("coinsound.wav")
    jump = pygame.mixer.Sound("jumpsound.wav")
    pygame.mixer.music.load("amazinbgmusic.mp3")

    #play background music
    pygame.mixer.music.play(-1,0)


    #--------------main program loop-------------
    done = False
    while not done:


        #game logic
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT:
                done = True
                pygame.quit()
                quit()

            #keyboard controls
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    up = True
                    
                    pygame.mixer.Sound.play(jump)
                if event.key == pygame.K_LEFT:
                    left = True
                if event.key == pygame.K_RIGHT:
                    right = True


            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    up = False
                if event.key == pygame.K_RIGHT:
                    right = False
                if event.key == pygame.K_LEFT:
                    left = False

        # draw background
        for y in range(60):
            for x in range(100):
                screen.blit(bg, (x * 25, y * 25))

        #when character hits coin, collect points
        for c in coins:
            if pygame.sprite.collide_rect(character, c):
               
                pygame.mixer.Sound.play(coin)
               
                c.rect.centerx = -10
                c.rect.centery = -10
              

                score += 4

                print (score)
                totalcoins +=1
                
                if totalcoins == 25:
                    w = winSprite(2450, 250)
                    wins.append(w)
                    allSprites.add(w)


        #when character hits a fire, user loses game
        for f in fires:
            if pygame.sprite.collide_rect(character,f):
                lose()


        #when character hits crown, user wins game
        for w in wins:
            if pygame.sprite.collide_rect(character,w):
                
                win()


        #call and update camera
        camera.update(character)

        #call and update character
        character.update(up, left, right, platforms)

        #draw all sprites and platforms
        for e in allSprites:
            screen.blit(e.image, camera.apply(e))


        #update screen
        pygame.display.update()

        #update screen every 60 seconds
        timer.tick(60)



#if user collides with fire sprite, lose screen is called
def lose():
   
    losescreen=pygame.image.load("lose.jpg").convert()
    button1=pygame.image.load("playagainbutton.png").convert()
    button1.set_colorkey(WHITE)
    button2=pygame.image.load("playagainbutton2.png").convert()
    button2.set_colorkey(WHITE)
  
    scoreimage=pygame.image.load("score"+str(score)+".jpg").convert()
    scoreimage.set_colorkey(WHITE)

    
    pygame.mixer.init()
    pygame.mixer.music.load("losesound.wav")
    playagain = pygame.mixer.Sound("instructsound.wav")

    
    pygame.mixer.music.play(0)


    #-----------------lose screen loop------------------------------
    done=False
    while not done:

        #allows user to close window and shut down game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                pygame.quit()
                quit()

        #pastes background and button and score
        screen.blit(losescreen, [0,0])
        screen.blit(button1, [300, 400])
        screen.blit(scoreimage,[300, 250])
        #gets mouse coordiantes
        mouse=pygame.mouse.get_pos()
        mousex=mouse[0]
        mousey=mouse[1]

        #if user moves over button, highlight it, if user clickes button load the level select screen
        if (300<mousex<500) and (400<mousey<500):
            screen.blit(button2, [300, 400])
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                   
                    pygame.mixer.Sound.play(playagain)
                    done==True
                    levelselect(screen)
        #update screen
        pygame.display.flip()


#win screen, if user wins game
def win():
    #load all images
    winscreen=pygame.image.load("win.jpg").convert()
    button1=pygame.image.load("playagainbutton.png").convert()
    button1.set_colorkey(WHITE)
    button2=pygame.image.load("playagainbutton2.png").convert()
    button2.set_colorkey(WHITE)
    screen.blit(button1, [300, 400])
    screen.blit(winscreen, [0,0])

    #score image
    scoreimage=pygame.image.load("score"+str(score)+".jpg").convert()
    scoreimage.set_colorkey(WHITE)

    #load sound effects
    pygame.mixer.init()
    pygame.mixer.music.load("winsound.mp3")
    playagain = pygame.mixer.Sound("instructsound.wav")

    #play win sound effect
    pygame.mixer.music.play(0)

    #-----------------win screen loop------------------------------
    done=False
    while not done:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                pygame.quit()
                quit()

        #gets mouse coordinates
        mouse=pygame.mouse.get_pos()
        mousex=mouse[0]
        mousey=mouse[1]
        #pastes button and score to screen
        screen.blit(button1, [100,400])
        screen.blit(scoreimage, [300, 400])

        #if user moves over button, highlight it, if user clickes button load the level select screen
        if (100<mousex<300) and (400<mousey<500):
            screen.blit(button2, [100, 400])
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    
                    pygame.mixer.Sound.play(playagain)
                    done==True
                    levelselect(screen)
        #update screen
        pygame.display.flip()


#instruction manual screen
def Instructionscreen(screen):
    #load all images
    background_position = [0, 0]
    field_image = pygame.image.load("instructionscreen.jpg").convert()
    button1=pygame.image.load("startbutton.png").convert()
    button1.set_colorkey(WHITE)
    button2=pygame.image.load("startbutton2.png").convert()
    button2.set_colorkey(WHITE)
    screen.blit(field_image, background_position)
    screen.blit(button1, [100, 400])

    #load sound effects
    pygame.mixer.init()
    instructsound = pygame.mixer.Sound("instructsound.wav")
    pygame.mixer.music.load("coolbeansbgmusic.mp3")

    #play background music
    pygame.mixer.music.play(-1,0)

    #-----------------instruction screen loop------------------------------
    instructions=True
    while instructions==True:
        #allows user to close window and shut down game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                instructions==False
                pygame.quit()
                quit()

        #pastes start button to screen
        screen.blit(button1, [100, 400])
        #gathers mouse coordinates
        mouse=pygame.mouse.get_pos()
        mousex=mouse[0]
        mousey=mouse[1]

        #if user moves over button, highlight it, if user clickes button load level select screen
        if (100<mousex<300) and (400<mousey<500):
            screen.blit(button2, [100, 400])
            if event.type == pygame.MOUSEBUTTONDOWN:
                #play start sound effect
                pygame.mixer.Sound.play(instructsound)
                Instructionscreen==False
                levelselect(screen)
                #stops loop, brings up level select screen

        #update screen
        pygame.display.flip()



#level select screen
def levelselect(screen):
    #loads all image files
    background=pygame.image.load("selectscreen.jpg").convert()
    level1=pygame.image.load("level1v1.png").convert()
    level1.set_colorkey(WHITE)
    level1_1=pygame.image.load("level1v2.png").convert()
    level1_1.set_colorkey(WHITE)
    level2=pygame.image.load("level2v1.png").convert()
    level2.set_colorkey(WHITE)
    level2_2=pygame.image.load("level2v2.png").convert()
    level2_2.set_colorkey(WHITE)
    level3=pygame.image.load("level3v1.png").convert()
    level3.set_colorkey(WHITE)
    level3_2=pygame.image.load("level3v2.png").convert()
    level3_2.set_colorkey(WHITE)

    #load sound effects
    pygame.mixer.init()
    instructsound = pygame.mixer.Sound("instructsound.wav")
    pygame.mixer.music.load("coolbeansbgmusic.mp3")

    #play background music
    pygame.mixer.music.play(-1,0)


    #----------------- level selection screen loop -----------------
    levelselectscreen=True
    while levelselectscreen==True:
        #allows user to close window and shut down game
        for event in pygame.event.get():
            print(event)
            if event.type == pygame.QUIT:
                levelselectscreen==False
                pygame.quit()
                quit()

        #pastes background and button images
        screen.blit(background, [0,0])
        screen.blit(level1, [45,400])
        screen.blit(level3, [570, 400])
        screen.blit(level2, [300, 400])

        #gets mouse coordiantes
        mouse=pygame.mouse.get_pos()
        mousex=mouse[0]
        mousey=mouse[1]

        #if user moves over button, highlight it, if user clickes button load the selected level
        if (45<mousex<245) and (400<mousey<500):
            screen.blit(level1_1, [45,400])
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #play start sound effect
                    pygame.mixer.Sound.play(instructsound)
                    #stops loop, calls game loop
                    levelselectscreen==False
                    gameWorld("designlevel.txt")
                    #level 1 file
        if (570<mousex<770) and (400<mousey<500):
            screen.blit(level3_2, [570,400])
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #play start sound effect
                    pygame.mixer.Sound.play(instructsound)
                    #stops loop, calls game loop
                    levelselectscreen==False
                    gameWorld("designlevel3.txt")
                    #level 2 file
        if (300<mousex<500) and (400<mousey<500):
            screen.blit(level2_2, [300,400])
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #play start sound effect
                    pygame.mixer.Sound.play(instructsound)
                    #stops loop, calls game loop
                    levelselectscreen==False
                    gameWorld("designlevel2.txt")
                    #level 3 file
        #update the screen
        pygame.display.flip()



#initial start screen
def Startscreen(screen):
    #loads all images
    background_image = pygame.image.load("coolbackground.jpg").convert()
    startbutton=pygame.image.load("startbutton.png").convert()
    startbutton.set_colorkey(WHITE)
    startbutton2=pygame.image.load("startbutton2.png").convert()
    startbutton2.set_colorkey(WHITE)
    instrucbutton=pygame.image.load("instructionbutton.png").convert()
    instrucbutton.set_colorkey(WHITE)
    instrucbutton2=pygame.image.load("instructionbutton2.png").convert()
    instrucbutton2.set_colorkey(WHITE)

    #load sound effects
    pygame.mixer.init()
    instructsound = pygame.mixer.Sound("instructsound.wav")
    pygame.mixer.music.load("coolbeansbgmusic.mp3")

    #play background music
    pygame.mixer.music.play(-1,0)

    #----------------- startscreen loop------------------------------
    startscreen=True
    while startscreen==True:
        #allows user to close window and shut down game
        for event in pygame.event.get():
            print(event)
            if event.type == pygame.QUIT:
                startscreen==False
                pygame.quit()
                quit()

        # Load and set up graphics.
        background_position = [0, 0]

        #pastes background & button images to screen
        screen.blit(background_image, background_position)
        screen.blit(startbutton, [43, 395])
        screen.blit(instrucbutton, [567, 395])

        #gets mouse coordiantes
        mouse=pygame.mouse.get_pos()
        mousex=mouse[0]
        mousey=mouse[1]

        #if user moves over button, highlight it, if user clickes button load the selected screen
        if (43<mousex<243) and (395<mousey<495):
            screen.blit(startbutton2, [43,395])
            if event.type == pygame.MOUSEBUTTONDOWN:
                #play start sound effect
                pygame.mixer.Sound.play(instructsound)
                startscreen==False
                levelselect(screen)
                #stops loop, calls level select screen
        if (567<mousex<767) and (395<mousey<495):
            screen.blit(instrucbutton2, [567,395])
            if event.type == pygame.MOUSEBUTTONDOWN:
                #play instructions sound
                pygame.mixer.Sound.play(instructsound)
                startscreen==False
                Instructionscreen(screen)
                #stops loop, calls instruction screen
        #update screen
        pygame.display.flip()



#Set screen name and creates window
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Game of Crowns")

try:
    #This starts the game
    Startscreen(screen)

except: #exception handling
    pass
