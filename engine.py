#Noah Kuite
import pygame as pg


class Engine:

    """
    Engine is a simple game engine that is made to be as separate from the scenes
    and game objects as possible.
    """

    #Time elapsed since last frame
    delta_time = 0
    #events to be handled this frame
    events = None
    #current scene being run
    scene = None

    running = None

    def __init__(self, width=820, height=820):
        self.width = width #width of the screen
        self.height = height #height of the screen
        Engine.running = False 
        pg.init() #initialize pygame
        self.screen = pg.display.set_mode((self.width, self.height)) # screen
        self.clock = pg.time.Clock() # clock
        self.fps = 60 #frames per second

    def loop(self):
        """
        The main game loop. 
        """
        Engine.running = True
        self.screen.fill((255, 255, 255))
        while Engine.running:
            Engine.events = pg.event.get()
            for event in Engine.events:
                if event.type == pg.QUIT:
                    Engine.running = False
            #update all game objects
            for current_object in Engine.scene.updateables:
                current_object.update()
            #draw all game objects
            for drawable in Engine.scene.drawables:
                drawable.draw(self.screen)
            #flip buffer -- updates the screen once drawing is finished
            pg.display.flip()
            self.screen.fill((0, 0, 0))
            #calculate delta time
            Engine.delta_time = self.clock.tick(self.fps) / 1000
            self.clock.tick(self.fps) #frame limit
