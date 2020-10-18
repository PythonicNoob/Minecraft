import pyglet.image
from pyglet.gl import glColor3d, glEnable, GL_TEXTURE_2D, glTexParameteri, GL_TEXTURE_MAG_FILTER, GL_NEAREST

class Hotbar:

    hotbar_image = pyglet.image.load('hotbar.png')
    hotbar_selection_image = pyglet.image.load('hotbar_selection.png')

    def __init__(self, items, index=0, visible=True, hotbar_size=9):
        self.items = items[:9]
        self.__index = index
        self.visible = visible
        self.batch = pyglet.graphics.Batch()
        self.hotbar = None
        self.hotbar_selection =None
        
        self.hotbar_image.anchor_x = self.hotbar_image.width // 2
        self.hotbar_selection_image.anchor_x = self.hotbar_selection_image.width // 2
        self.hotbar_selection_image.anchor_y = self.hotbar_selection_image.height // 2
        self.hotbar_size = hotbar_size
        
    @property
    def index(self):
        return self.__index
    
    @index.setter
    def index(self, index):
        x = (self.hotbar.x - (self.hotbar.width/2) ) + (index * (self.hotbar.width/9)) + (self.hotbar.width/18)
        if self.hotbar_selection: self.hotbar_selection.x = x
        self.__index = index
        
    @property
    def current_block(self):
        return  self.items[self.__index]
    
    
    def resize(self, width, height):
        if self.hotbar: self.hotbar.delete()
        if self.hotbar_selection: self.hotbar_selection.delete()
        
        self.hotbar = pyglet.sprite.Sprite(self.hotbar_image, x=width//2, y=0, batch=self.batch)
        
        scale_x = 1
        scale_y = 1
        
        if width <= 800 and height <= 720 :
            # wdth = self.width
            # self.hotbar.update(scale_x=(width * 0.6) // self.hotbar.width,
            #                    scale_y=(height * 0.08) // self.hotbar.height)  # *0% width and 10% height
            scale_x = (width * 0.6) // self.hotbar.width
            scale_y = (height * 0.08) // self.hotbar.height
            
        elif height > 720:
            # self.hotbar.update(scale_x=(width * 0.4) // self.hotbar.width,
            #                    scale_y=(height * 0.08) // self.hotbar.height)
            scale_x = (width * 0.4) // self.hotbar.width
            scale_y = (height * 0.08) // self.hotbar.height
            
        elif height > 920:
            # self.hotbar.update(scale_x=(width * 0.6) // self.hotbar.width,
            #                    scale_y=(height * 0.08) // self.hotbar.height)  # *0% width and 10% height
            scale_x = (width * 0.6) // self.hotbar.width
            scale_y = (height * 0.08) // self.hotbar.height
        else:
            # self.hotbar.update(scale_x=(800 * 0.6) // self.hotbar.width,
            #                    scale_y=(height * 0.08) // self.hotbar.height)
            scale_x = (800 * 0.6) // self.hotbar.width
            scale_y = (height * 0.08) // self.hotbar.height
            
        self.hotbar.update(scale_x=scale_x,scale_y=scale_y)

        # x will be    starting point of hotbar + (index * size of one block which is size of hotbar divided by 9) + 1/2 width of block coz starting point should be a bit ahead
        selection_x = (self.hotbar.x - (self.hotbar.width/2) ) + (self.index * (self.hotbar.width/9)) + (self.hotbar.width/18) #(self.hotbar.x + (self.index * ( (self.hotbar.width / 9) / 2 ))) - (self.hotbar.width / 2) #+ (self.hotbar.x - (self.hotbar.width / 2))
        selection_y = self.hotbar.height / 2
        
        self.hotbar_selection = pyglet.sprite.Sprite(self.hotbar_selection_image, x=selection_x, y=selection_y, batch=self.batch, group=pyglet.graphics.OrderedGroup(1))
        self.hotbar_selection.update( scale_x=scale_x, scale_y=scale_y)

        print(self.hotbar_selection.x)
        print(self.hotbar_selection.y)
        
    def get_block(self, index):
        return  self.items[index]   

    def draw(self):
        glEnable(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glColor3d(1, 1, 1)
        self.batch.draw()