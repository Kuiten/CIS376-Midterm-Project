#! /Users/noah/opt/anaconda3/envs/pybox2d/bin/python
#NOTE: USE python to launch NOT python3 (i.e., python main.py NOT python3 main.py)

#Noah Kuite
import os
import pygame as pg
from engine import Engine
from scene import Scene
from Box2D import *

#convert to and from pixels
w2b = 1/100 #convert from pixels to B2D
b2w = 100 # convert from B2D to pixels

#world creation
gravity = b2Vec2(0.5, -10.0)
world = b2World(gravity,doSleep=False)

#world time step
timeStep = 1.0 / 60
#number of iterations
vel_iters, pos_iters = 6, 2

"""
The platform class is a drawable and updateable game object that is the platform at the bottom the player moves 
to bounce the ball back towards the bricks
"""
class Platform(pg.sprite.Sprite):
    def __init__(self):
        super(Platform, self).__init__()
        w = 0.5 # width of the platform
        h = 0.1 # height of the platform
        #Create box2d body -- Kinematic body so the ball doesn't push it off the screen
        self.body = world.CreateKinematicBody(position=(4, 0.5))
        shape = b2PolygonShape(box=(w, h))
        fixDef = b2FixtureDef(shape=shape, friction=1.0, restitution=1, density=.5)
        box = self.body.CreateFixture(fixDef)
        # Load the image asset for the platform
        self.image = pg.image.load(os.path.join('Assets', 'PNG', '07-Breakout-Tiles.png')).convert_alpha()
        #scale the image to the correct size(slightly larger than box2d body)
        self.image = pg.transform.scale(self.image, ((2*w*b2w) + 10, (2*h*b2w) + 10))
        self.rect = self.image.get_rect()
        self.rect.center = self.body.position.x * b2w, 820 - self.body.position.y * b2w
        #ignore gravity
        self.body.gravityScale = 0.0

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update(self):
        #Update center of rect for drawing purposes
        self.rect.center = self.body.position[0] * b2w, 820 - self.body.position[1] * b2w
        #Events the consume
        for event in Engine.events:
            if event.type == pg.KEYDOWN:
                #move the platform left if 'a' is pressed
                if event.key == pg.K_a:
                    self.body.linearVelocity = b2Vec2(-8.5, 0)
                #move the platform right if 'd' is pressed
                if event.key == pg.K_d:
                    self.body.linearVelocity = b2Vec2(8.5, 0)

"""
The ball class is a drawable and updateable game object the creates and controls the ball for breaking the bricks
"""
class Ball(pg.sprite.Sprite):
    def __init__(self, platforms):
        super(Ball, self).__init__()
        #Platform objects used for collision detection between ball and platform
        self.platforms = platforms
        #create body for the ball
        self.body = world.CreateDynamicBody(position=(4, 1.5))
        shape=b2CircleShape(radius=.2)
        fixDef = b2FixtureDef(shape=shape, friction=0.3, restitution=1, density=.3)
        box = self.body.CreateFixture(fixDef)
        d=.2*b2w*2  # 40
        #load ball image asset
        self.image = pg.image.load(os.path.join('Assets', 'PNG', '58-Breakout-Tiles.png')).convert_alpha()
        #scale the ball image to be slightley larger than the body
        self.image = pg.transform.scale(self.image, (d + 5, d + 5))
        self.rect = self.image.get_rect()
        self.body.ApplyLinearImpulse( b2Vec2(0, 0.8), self.body.position, True)

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)

    def update(self):
        #Update balls position
        self.rect.center = self.body.position[0] * b2w, 820 - self.body.position[1] * b2w
        #If the ball falls off the map end the game
        if(800 - self.body.position[1] * b2w > 820):
            Engine.running = False
        #if collision with platform occurs add some linear velocity
        collide = pg.sprite.spritecollide(self, self.platforms, False)
        if collide:
            self.body.ApplyLinearImpulse( b2Vec2(0, 0.2), self.body.position, True)

"""
The walls class is a drawable game object used to create walls on the sides and top of the screen for the ball to bounce off of
"""
class Walls():
    def __init__(self, x, y, w, h):
        #create the box2D body
        self.body = world.CreateStaticBody(position=(x, y), shapes=b2PolygonShape(box=(w, h)))
        self.image = pg.Surface((2*w*b2w, 2*h*b2w))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self.body.position.x * b2w, 820 - self.body.position.y * b2w

    def draw(self, screen):
        screen.blit(self.image, self.rect)

"""
The bricks class is a drawable and updateable game object that creates a brick for the ball to break
"""
class Bricks(pg.sprite.Sprite):
    #Class variable used for tracking when win condition should trigger
    num_bricks = 0
    def __init__(self, x, y, img , ball):
        super(Bricks, self).__init__()
        #Update number of bricks
        Bricks.num_bricks = Bricks.num_bricks + 1
        #load the break sound effect for when a brick is destroyed
        self.breakSound = pg.mixer.Sound("break.wav")
        #The ball object, used to detect when a brick is hit
        self.ball = ball
        #status color
        self.color = (255, 255, 255)
        #name of image asset for the brick
        self.asset = img
        #status of brick
        self.destroyed = False
        w = 0.25 # width of the brick
        h = 0.1 # height of the brick
        #create the box2d body
        self.body = world.CreateStaticBody(position=(x, y), shapes=b2PolygonShape(box=(w, h)))
        #load image asset
        self.image = pg.image.load(os.path.join('Assets', 'PNG', self.asset)).convert_alpha()
        #Scale the image to slightly larger than box2d body
        self.image = pg.transform.scale(self.image, ((2*w*b2w) + 10, (2*h*b2w) + 15))
        self.rect = self.image.get_rect()
        self.rect.center = self.body.position.x * b2w, 820 - self.body.position.y * b2w

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)

    def update(self):
        #if number of bricks is 0, end the game
        if Bricks.num_bricks <= 0:
            Engine.running = False
        #if currently alive check for collision
        if self.color != (0, 0, 0):
            collide = pg.sprite.spritecollide(self, self.ball, False)
            if collide:
                #if colliion occurred set the color to black and change the image to black
                self.color = (0, 0, 0)
                self.image.fill(self.color)
        #if color is black and self.destroyed is false delete the box2d body
        #This is done to delete the body after the ball has already bounced off the object
        elif self.color == (0, 0, 0) and not self.destroyed:
            #destroy body
            world.DestroyBody(self.body)
            #set status destroyed
            self.destroyed = True
            Bricks.num_bricks = Bricks.num_bricks - 1 # decrement number of bricks
            self.breakSound.play() # play break sound
"""
The Updater class is an updateable game object to updates the world state of box2d
"""
class Updater():
    def update(self):
        world.Step(timeStep, vel_iters, pos_iters)
        world.ClearForces()

def main():
    #run code here. 
    #Create engine and scene
    engine = Engine()
    scene = Scene()

    # "player" platform
    platform = Platform()
    platforms = pg.sprite.Group()
    platforms.add(platform)

    #Box2D world updater
    updater = Updater()

    #bounding walls for the ball to bounce off of
    left_wall = Walls(-0.4, 0, 0.1, 8)
    right_wall = Walls(8.2, 0, 0.1, 8)
    top_wall = Walls(0, 8, 8.2, 0.1)

    #Ball that destroys the bricks
    ball = Ball(platforms)
    balls = pg.sprite.Group()
    balls.add(ball)

    #add drawables to the scene
    scene.drawables.append(platform)
    scene.drawables.append(left_wall)
    scene.drawables.append(right_wall)
    scene.drawables.append(top_wall)
    scene.drawables.append(ball)

    #add updateables to the scene
    scene.updateables.append(platform)
    scene.updateables.append(updater)
    scene.updateables.append(ball)

    # Images for the bricks
    images = [
        '24-Breakout-Tiles.png',
        '27-Breakout-Tiles.png',
        '28-Breakout-Tiles.png',
        '23-Breakout-Tiles.png',
        '25-Breakout-Tiles.png',
        '30-Breakout-Tiles.png'
    ]
    #Add 6 rows of bricks to the scene
    color = 0
    i = 0
    j = 8
    while(color < len(images)):
        while(i < 8):
            brick = Bricks(i, j, images[color], balls)
            scene.drawables.append(brick)
            scene.updateables.append(brick)
            i = i + 0.55
        j = j - 0.3
        i = 0
        color = color + 1

    #add scene to the engine
    Engine.scene = scene

    #Play music
    pg.mixer.music.load("cpu-talk.mp3")
    pg.mixer.music.play(-1)

    #start the game loop
    engine.loop()

if __name__ == "__main__":
    main()