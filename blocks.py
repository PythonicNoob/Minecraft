from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup


class Block():

    def __init__(self, id, filepath, colors=None, rigid=True):
        self.texture_top = TextureGroup(image.load(filepath[0]).get_texture())

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        self.texture_bottom = TextureGroup(image.load(filepath[1]).get_texture())

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        self.texture_left = TextureGroup(image.load(filepath[2]).get_texture())

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        self.texture_right = TextureGroup(image.load(filepath[3]).get_texture())

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        self.texture_front = TextureGroup(image.load(filepath[4]).get_texture())

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        self.texture_back = TextureGroup(image.load(filepath[5]).get_texture())

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        if colors is not None:
            self.color_top = colors[0]
            self.color_bottom = colors[1]
            self.color_left = colors[2]
            self.color_right = colors[3]
            self.color_front = colors[4]
            self.color_back = colors[5]
        else:
            self.color_top = None
            self.color_bottom = None
            self.color_left = None
            self.color_right = None
            self.color_front = None
            self.color_back = None

        self.files = filepath
        self.collision = rigid
        self.id = id

    def get_id(self):
        return self.id

    def get_textures(self):
        return [self.texture_top, self.texture_bottom, self.texture_left, self.texture_right, self.texture_front,
                self.texture_back]  # format: top, bottom, left, right, front, back

    def get_collision(self):
        return self.collision

    def get_colors(self):
        return [self.color_top, self.color_bottom, self.color_left, self.color_right, self.color_front, self.color_back]

    def update(self):
        pass


stone = Block(1, ['textures/block/stone.png'] * 6)
sand = Block(2, ['textures/block/sand.png'] * 6)
brick = Block(3, ['textures/block/bricks.png'] * 6)
bedrock = Block(4, ['textures/block/bedrock.png'] * 6)

grass_top_color = (0, 153, 0, 0,  # Point 1
                   0, 153, 0, 0,  # Point 2
                   0, 153, 0, 0,  # Point 2
                   0, 153, 0, 0)  # Point 4

grass = Block(4,
              ['textures/block/grass_top.png', 'textures/block/dirt.png'] + ['textures/block/grass_block_side.png'] * 4,
              colors=[grass_top_color, None, None, None, None, None])
