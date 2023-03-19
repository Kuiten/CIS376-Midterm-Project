#! /Users/noah/opt/anaconda3/envs/pybox2d/bin/python
#NOTE: USE python to launch NOT python3 (i.e., python main.py NOT python3 main.py)

#Noah Kuite
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

#Game object for platform moved by player
class Platform(pg.sprite.Sprite):
    def __init__(self):
        super(Platform, self).__init__()
        w = 0.5 # width of the platform
        h = 0.1 # height of the platform
        self.body = world.CreateKinematicBody(position=(4, 0.5))
        shape = b2PolygonShape(box=(w, h))
        fixDef = b2FixtureDef(shape=shape, friction=1.0, restitution=1, density=.5)
        box = self.body.CreateFixture(fixDef)
        # 100 x 20
        self.image = pg.Surface((2*w*b2w, (2*h*b2w) + 5))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self.body.position.x * b2w, 820 - self.body.position.y * b2w
        #ignore gravity
        self.body.gravityScale = 0.0

    def draw(self, screen):
        #pg.draw.rect(self.image, (255, 0, 0), self.rect)
        screen.blit(self.image, self.rect)

    def update(self):
        #Update center of rect for drawing purposes
        self.rect.center = self.body.position[0] * b2w, 820 - self.body.position[1] * b2w
        for event in Engine.events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_a:
                    #self.body.ApplyLinearImpulse( b2Vec2(-0.5, 0), self.body.position, True)
                    self.body.linearVelocity = b2Vec2(-8.5, 0)
                if event.key == pg.K_d:
                    self.body.linearVelocity = b2Vec2(8.5, 0)

#Game object for ball
class Ball(pg.sprite.Sprite):
    def __init__(self, platforms):
        super(Ball, self).__init__()
        self.platforms = platforms
        self.body = world.CreateDynamicBody(position=(4, 1.5))
        shape=b2CircleShape(radius=.2)
        fixDef = b2FixtureDef(shape=shape, friction=0.3, restitution=1, density=.3)
        box = self.body.CreateFixture(fixDef)
        d=.2*b2w*2  # 40
        # 40 x 40 square
        self.image = pg.Surface((d + 5,d+ 5), pg.SRCALPHA, 32)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        # 20
        pg.draw.circle(self.image,(0, 0, 255) , self.rect.center, .2*b2w)
        self.body.ApplyLinearImpulse( b2Vec2(0, 0.8), self.body.position, True)

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)

    def update(self):
        self.rect.center = self.body.position[0] * b2w, 820 - self.body.position[1] * b2w
        #If the ball falls off the map end the game
        if(800 - self.body.position[1] * b2w > 820):
            Engine.running = False
        collide = pg.sprite.spritecollide(self, self.platforms, False)
        if collide:
            self.body.ApplyLinearImpulse( b2Vec2(0, 0.2), self.body.position, True)

#Game object for walls
class Walls():
    def __init__(self, x, y, w, h):
        self.body = world.CreateStaticBody(position=(x, y), shapes=b2PolygonShape(box=(w, h)))
        self.image = pg.Surface((2*w*b2w, 2*h*b2w))
        self.image.fill((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self.body.position.x * b2w, 820 - self.body.position.y * b2w

    def draw(self, screen):
        screen.blit(self.image, self.rect)

#game objects for bricks to break
class Bricks(pg.sprite.Sprite):
    num_bricks = 0
    def __init__(self, x, y, color, ball):
        super(Bricks, self).__init__()
        Bricks.num_bricks = Bricks.num_bricks + 1
        self.fireSound = pg.mixer.Sound("break.wav")
        self.ball = ball
        self.color = color
        self.destroyed = False
        w = 0.25 # width of the brick
        h = 0.1 # height of the brick
        self.body = world.CreateStaticBody(position=(x, y), shapes=b2PolygonShape(box=(w, h)))
        self.image = pg.Surface(((2*w*b2w) + 10 , (2*h*b2w) + 15))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.center = self.body.position.x * b2w, 820 - self.body.position.y * b2w

    def draw(self, screen):
        screen.blit(self.image, self.rect.center)

    def update(self):
        if Bricks.num_bricks <= 0:
            Engine.running = False
        if self.color != (0, 0, 0):
            collide = pg.sprite.spritecollide(self, self.ball, False)
            if collide:
                self.color = (0, 0, 0)
                self.image.fill(self.color)
        elif self.color == (0, 0, 0) and not self.destroyed:
            world.DestroyBody(self.body)
            self.destroyed = True
            Bricks.num_bricks = Bricks.num_bricks - 1
            self.fireSound.play()

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

    #Colors for the bricks
    colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255), 
        (255, 0, 255),
        (245, 111, 66),
        (66, 245, 164)
    ]
    #Add 6 rows of bricks to the scene
    color = 0
    i = 0
    j = 8
    while(color < len(colors)):
        while(i < 8):
            brick = Bricks(i, j, colors[color], balls)
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