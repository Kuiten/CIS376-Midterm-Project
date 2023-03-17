#Noah Kuite

class Scene:
    """
    The scene class is a simple scene that holds the game objects for one scene. This
    includes updateable game objects and drawable gameobjects
    """
    def __init__(self):
        self.updateables = []
        self.drawables = []
        