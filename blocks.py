from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
import pyglet
# import numpy as np

__all__ = (
    'stone_block', 'sand_block', 'brick_block', 'bedrock_block', 'acacia_leaves_block', 'acacia_sapling_block','blue_concrete_powder_block', 'grass_block', 'water_block', 'dirt_block', 'snow_block', 'diamondore_block', 'coalore_block', 'gravel_block','ironore_block','lapisore_block', 'quartz_block','clay_block','nether_block','nether_quartz_ore_block' ,'soulsand_block', 'sandstone_block', 'ice_block', 'snowgrass_block', 'air_block', 'melon_block','pumpkin_block', 'yflowers_block', 'potato_block', 'carrot_block', 'rose_block', 'fern_block', 'wildgrass0_block','wildgrass1_block', 'wildgrass0_block', 'wildgrass2_block', 'wildgrass3_block', 'wildgrass4_block', 'wildgrass5_block','wildgrass6_block','wildgrass7_block', 'deadbush_block', 'desertgrass_block', 'cactus_block', 'tallcactus_block','reed_block','oakwood_block','oakleaf_block','junglewood_block','jungleleaf_block','birchwood_block','birchleaf_block')

def grass_on_place(pos, model):
    x, y, z = pos
    if model.world.get((x, y+1, z), None):
        model.remove_block(pos, immediate=True)
        model.add_block_new(pos, dirt_block, immediate=True)


class PlantGroup(TextureGroup):

    def __init__(self, texture, parent=None, color=None):
        super(PlantGroup, self).__init__(texture, parent)
        self.color = color

    def set_state(self):
        TextureGroup.set_state(self)
        glDisable(GL_CULL_FACE)

        if self.color:
            glColor4f(*self.color)

    def unset_state(self):
        TextureGroup.unset_state(self)
        glEnable(GL_CULL_FACE)
        if self.color:
            glColor4f(1, 1, 1, 1)

class BiomeGroup(TextureGroup):

    def __init__(self, texture, color, parent=None):
        super(BiomeGroup, self).__init__(texture, parent)
        self.color = color

    def set_state(self):
        # print("BiomeGroup being rendered  yay!")
        TextureGroup.set_state(self)
        # glEnable(GL_COLOR_MATERIAL)
        # glColorMaterial(GL_FRONT, GL_DIFFUSE)
        # glColorMaterial(GL_FRONT, GL_SPECULAR)
        glColor4f(*self.color)
        # glColor4f(71/255, 205/255, 51/255, 1)
        # glEnable(GL_CULL_FACE)

    def unset_state(self):
        TextureGroup.unset_state(self)
        glColor4f(1, 1, 1, 1)
        # glDisable(GL_COLOR_MATERIAL)
        # glDisable(GL_CULL_FACE)


def sample():
    print("Sample Pressed")
    return "sample_action"

def grass_verts(pos,n=0.5):
    x,y,z = pos; v = tuple((x+X,y+Y,z+Z) for X in (-n,n) for Y in (-n,n) for Z in (-n,n))
    return tuple(tuple(k for j in i for k in v[j]) for i in ((0,5,7,2),(1,4,6,3)))

def cube_vertices_with_sides(x, y, z, n=0.5):
    """ Return the vertices of the cube at position x, y, z with size 2*n.
    """
    return [
        [x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n],  # top
        [x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n],  # bottom
        [x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n],  # left
        [x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n],  # right
        [x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n],  # front
        [x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n],  # back
    ]

class Block():

    def load_tex(self, filepath, color, transparent):

        GroupClass = TextureGroup
        if color:
            # print("using color")
            GroupClass = lambda x: BiomeGroup(x, color)

        if not transparent:
            tex = GroupClass(image.load(filepath).get_mipmapped_texture())
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        else:
            tex = GroupClass(image.load(filepath).get_texture())
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        return tex


    def __init__(self, id, filepath, colors=None, rigid=True, transparent=False, right_click=None, place_function=None, placeable_on=['*'], load_tex=True):
        # self.texture_front = TextureGroup(image.load(filepath[4]).get_texture())
        if load_tex:
            self.texture_top = self.load_tex(filepath[0], None if colors is None else colors[0], transparent, )
            self.texture_bottom = self.load_tex(filepath[1], None if colors is None else colors[1], transparent)
            self.texture_left = self.load_tex(filepath[2], None if colors is None else colors[2], transparent)
            self.texture_right = self.load_tex(filepath[3], None if colors is None else colors[3], transparent)
            self.texture_front = self.load_tex(filepath[4], None if colors is None else colors[4], transparent)
            self.texture_back = self.load_tex(filepath[5], None if colors is None else colors[5], transparent)


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
        self.transparent = transparent
        self.type = type
        self.right_click = right_click
        self.place_function = place_function
        self.placeable_on = placeable_on
        # self.size = size

    def get_id(self):
        return self.id

    def get_textures(self):
        return [self.texture_top, self.texture_bottom, self.texture_left, self.texture_right, self.texture_front,
                self.texture_back]  # format: top, bottom, left, right, front, back

    def get_colors(self):
        return [self.color_top, self.color_bottom, self.color_left, self.color_right, self.color_front, self.color_back]

    def get_collision(self):
        return self.collision

    def get_colors(self):
        return [self.color_top, self.color_bottom, self.color_left, self.color_right, self.color_front, self.color_back]

    def update(self):
        pass

    def right_click_press(self):
        if self.right_click is None:
            return None
        else:
            return self.right_click()

    def get_type(self):
        return self.type

    def on_place(self, pos, model):
        if self.place_function:
            self.place_function(pos, model)

    def show(self, pos, batch):

        block_tex = self.get_textures()
        block_cols = self.get_colors()
        # print("block cols:", block_cols)
        texture_data = (0, 0, 1, 0, 1, 1, 0, 1)
        vertex_data = cube_vertices_with_sides(*pos)
        shown = []


        # if not self.size:
        for sde in range(0,6): #sde meaning side. Add each side


            shown += [batch.add(4, GL_QUADS, block_tex[sde], ('v3f/static',vertex_data[sde]),
                                ('t2f/static', texture_data))]

            # if block_cols[sde]:
            #     # glEnable(GL_COLOR_MATERIAL)
            #     # glColorMaterial(GL_FRONT, GL_DIFFUSE)
            #     # glColorMaterial(GL_FRONT, GL_SPECULAR)
            #     # glColor4f(0.2,0.3,0.1,1)
            #
            #     batch = pyglet.graphics.Batch()
            #     batch.add(4, GL_QUADS, block_tex[sde], ('v3f/static', vertex_data[sde]),
            #                         ('t2f/static', texture_data))
            #     batch.draw()
            #     # pyglet.graphics.draw(4, GL_QUADS, block_tex[sde], ('v3f/static', vertex_data[sde]),
            #     #                     ('t2f/static', texture_data))
            #
            #     # shown += [batch.add(4, GL_QUADS, block_tex[sde], ('v3f/static', vertex_data[sde]),
            #     #                     ('t2f/static', texture_data))]
            #     # glColor4f(1,1,1,1)
            #     # glDisable(GL_COLOR_MATERIAL)
            # else:
            #     shown += [batch.add(4, GL_QUADS, block_tex[sde], ('v3f/static', vertex_data[sde]),
            #                         ('t2f/static', texture_data))]
            #     # print("block cols[sde]",block_cols[sde])
            #
            #     # shown += [batch.add(4, GL_QUADS, None, ('v3f/static', vertex_data[sde]), ('c3f', block_cols[sde])  )]

        return shown

    def hide(self, vertex_data):
        [x.delete() for x in vertex_data]

class TimeLoop:
    def __init__(self,duration): self.unit = 0; self.int = 0; self.duration = duration; self.prev = 0
    def update(self,dt):
        self.unit+=dt; self.unit-=int(self.unit); self.int = int(self.unit*self.duration)
        if self.prev!=self.int: self.prev = self.int; return True



class Liquid(Block): #TODO: proper implementation of breaking and adding water.
                    # TODO: add a blue cover over screen if player is in water
    def __init__(self, id, filepath,  ):
        super(Liquid, self).__init__(id,filepath, transparent=True, rigid=False)
        # self.transparent = transparent
        self.needs_transparent_batch = True
        self.time = {'still':TimeLoop(32),'flow':TimeLoop(32)}
        self.coords = {'still':[],'flow':[]}; self.still_faces = {}; self.flow_faces = {}
        for i in range(32-1,-1,-1):
            y0 = i/16; y1 = (i+1)/16; self.coords['still'] += [[0,y0, 1,y0, 1,y1, 0,y1]]
            y0 = i/32; y1 = (i+1)/32; self.coords['flow'] += [[0,y0, 1,y0, 1,y1, 0,y1]]
        a,b = self.time['still'],self.time['flow']; self.t = b,b,a,a,b,b
        a,b = self.coords['still'],self.coords['flow']; self.c = b,b,a,a,b,b


    # def set_transparent(self, transparent_batch):
    #     self.transparent_batch = transparent_batch

    def update(self,dt):
        if self.time['still'].update(dt*0.5):
            for face,i in self.still_faces.items(): face.tex_coords = self.c[i][self.t[i].int]
        if self.time['flow'].update(dt):
            for face,i in self.flow_faces.items(): face.tex_coords = self.c[i][self.t[i].int]

    def _show(self,v,t,i, transparent_batch):
        face = transparent_batch.add(4,GL_QUADS,t,('v3f',v),('t2f',self.c[i][0]))
        faces = self.still_faces if i==2 or i==3 else self.flow_faces
        faces[face] = i; return face

    def show(self, pos, batch):
        texs = self.get_textures() #Getting textures
        shown = []
        vertex_data = cube_vertices_with_sides(*pos)
        for i in range(0,6):
            shown += [self._show(vertex_data[i], texs[i], i, batch)]
        # print("Coords still:",self.coords['still'])
        # print("flow: ",self.coords['flow'])
        return shown


class Plant(Block):

    def load_tex(self, filepath, color, transparent):

        GroupClass = PlantGroup
        # if color:
        # #     print("using color")
        #     GroupClass = lambda x: PlantGroup(x, color)

        if not transparent:
            tex = PlantGroup(image.load(filepath).get_mipmapped_texture(), color=color)
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST_MIPMAP_LINEAR)
        else:
            tex = PlantGroup(image.load(filepath).get_texture(), color=color)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        return tex

    def __init__(self, id, filepath, colors=None ):
        super(Plant, self).__init__(id,filepath, transparent=True, rigid=False, colors=None, load_tex=False)

        self.texture_top = self.load_tex(filepath[0], None if colors is None else colors[0], transparent=True, )
        self.texture_bottom = self.load_tex(filepath[1], None if colors is None else colors[1], transparent=True)
        self.texture_left = self.load_tex(filepath[2], None if colors is None else colors[2], transparent=True)
        self.texture_right = self.load_tex(filepath[3], None if colors is None else colors[3], transparent=True)
        self.texture_front = self.load_tex(filepath[4], None if colors is None else colors[4], transparent=True)
        self.texture_back = self.load_tex(filepath[5], None if colors is None else colors[5], transparent=True)

    def show(self, pos, batch):
        v = grass_verts(pos)
        vl = []
        texture = self.get_textures()[0]

        for i in v:
            vl += [batch.add(4, GL_QUADS, texture, ('v3f', i), ('t2f', (0, 0, 1, 0, 1, 1, 0, 1)))]

        return vl

class Air():

    def __init__(self, id):
        self.id = id
        self.collision = True


    def show(self):
        pass


class Cactus(Block):

    def show(self, pos, batch):
        block_tex = self.get_textures()
        block_cols = self.get_colors()
        # print("block cols:", block_cols)
        texture_data = (0, 0, 1, 0, 1, 1, 0, 1)
        vertex_data = cube_vertices_with_sides(*pos)
        shown = []

        vertex_data[0]

        shown += [batch.add(4, GL_QUADS, block_tex[sde], ('v3f/static', [i * self.size for i in vertex_data[sde]]),
                            ('t2f/static', texture_data))]

BLOCKS = {
    'stone_block':( 'stone_block', ['textures/block/stone.png'] * 6),

}

PLANTS = {
    "wild_grass":("wild_grass", ['textures/block/tall_grass_top.png']*6)
}

LIQUIDS = {
    "water":("water_still", ['Minecraft_2/Minecraft/textures/water_still.png']*6)
}


stone_block = Block(*BLOCKS['stone_block'], right_click=sample,)
sand_block = Block(2, ['textures/block/sand.png'] * 6,)
brick_block = Block(3, ['textures/block/bricks.png'] * 6, placeable_on=[sand_block] )
bedrock_block = Block(4, ['textures/block/bedrock.png'] * 6, )
acacia_leaves_block = Block(5, ['textures/block/acacia_leaves.png']*6,  transparent=True, colors=[(0, 124/255, 0, 1)]*6)
acacia_sapling_block = Plant(6, ['textures/block/acacia_sapling.png']*6)
blue_concrete_powder_block = Block(7, ['textures/block/blue_concrete_powder.png']*6,  transparent=False)
dirt_block = Block(8, ['textures/block/dirt.png']*6 )
snow_block = Block(9, ['textures/block/snow.png']*6 )
diamondore_block = Block(10, ['textures/block/diamond_ore.png']*6)
coalore_block = Block(11, ['textures/block/coal_ore.png']*6)
gravel_block = Block(12, ['textures/block/gravel.png']*6)
ironore_block = Block(13, ['textures/block/iron_ore.png']*6)
lapisore_block = Block(14, ['textures/block/lapis_ore.png']*6)
quartz_block = Block(15, ['textures/block/quartz_block_top.png', 'textures/block/quartz_block_bottom.png']+['textures/block/quartz_block_side.png']*4 )
clay_block = Block(17, ['textures/block/clay.png']*6)
nether_block = Block(18, ['textures/block/netherrack.png']*6)
nether_quartz_ore_block = Block(19, ['textures/block/nether_quartz_ore.png']*6)
soulsand_block = Block(20, ['textures/block/soul_sand.png']*6)
ice_block = Block(21, ['textures/block/ice.png']*6)
sandstone_block = Block(21, ['textures/block/sandstone_top.png','textures/block/sandstone_bottom.png',]+['textures/block/sandstone.png']*4)

grass_top_color = (127/255, 178/255, 56/255, 1.1)  # Point 1 - 4
                   # 0, 153, 0, 0,  # Point 2
                   # 0, 153, 0, 0,  # Point 2
                   # 0, 153, 0, 0)  # Point 4

desertgrass_block = grass_block = Block(16,
              ['textures/block/grass_block_top.png', 'textures/block/dirt.png'] + ['textures/block/grass_block_side.png'] * 4,
              colors=[grass_top_color, None, None, None, None, None], place_function=grass_on_place)
snowgrass_block = Block(23,
              ['textures/block/snow.png', 'textures/block/dirt.png'] + ['textures/block/grass_block_snow.png'] * 4,
              colors=None)

water_block = Liquid(*LIQUIDS['water'])

air_block = Air(24)

melon_block = Block(23, ['textures/block/melon_top.png']*2+['textures/block/melon_side.png']*4)
pumpkin_block = Block(24, ['textures/block/pumpkin_top.png']*2+['textures/block/pumpkin_side.png']*4)

sunflower_block = Block(25, ['textures/block/sunflower_top.png', 'textures/block/sunflower_bottom.png', 'textures/block/sunflower_front.png', 'textures/block/sunflower_front.png', 'textures/block/sunflower_front.png', 'textures/block/sunflower_back.png']) #TODO: solve heavy mystery


potato_stage0_block = potato_block = Plant(26, ['textures/block/potatoes_stage0.png']*6)
# potato_block = Plant(26, ['textures/block/potatoes_stage0.png']*6)
carrot_stage0_block = carrot_block = Plant(27, ['textures/block/carrots_stage0.png']*6)
rose_bush_bottom_block = rose_block = Plant(27, ['textures/block/rose_bush_bottom.png']*6)
fern_block = Plant(28, ['textures/block/fern.png']*6, colors=[(0, 124/255, 0, 1)]*6) #TODO: fern add color
tall_grass_top_block = wildgrass0_block = Plant(29, ['textures/block/tall_grass_top.png']*6, colors=[(	0, 124/255, 0, 1)]*6)
wildgrass1_block = Plant(*PLANTS["wild_grass"], colors=[(	0, 124/255, 0, 1)]*6)
wildgrass2_block = Plant(30, ['textures/block/tall_grass_top.png']*6, colors=[(	0, 124/255, 0, 1)]*6)
wildgrass3_block = Plant(31, ['textures/block/tall_grass_top.png']*6, colors=[(	0, 124/255, 0, 1)]*6)
wildgrass4_block = Plant(32, ['textures/block/tall_grass_top.png']*6, colors=[(	0, 124/255, 0, 1)]*6)
wildgrass5_block = Plant(33, ['textures/block/tall_grass_top.png']*6, colors=[(	0, 124/255, 0, 1)]*6)
wildgrass6_block = Plant(34, ['textures/block/tall_grass_top.png']*6, colors=[(	0, 124/255, 0, 1)]*6)
wildgrass7_block = Plant(35, ['textures/block/tall_grass_top.png']*6, colors=[(	0, 124/255, 0, 1)]*6)
deadbush_block = Plant(36, ['textures/block/dead_bush.png']*6)
cactus_block = Block(37, ['textures/block/cactus_top.png','textures/block/cactus_bottom.png']+['textures/block/cactus_side.png']*4, transparent=True)
tallcactus_block = cactus_block
reed_block = sugarcane_block = Plant(38, ['textures/block/sugar_cane.png']*6)

oakwood_block = Block(39, ['textures/block/oak_log_top.png']*2+['textures/block/oak_log.png']*4)
oakleaf_block = Block(40, ['textures/block/oak_leaves.png']*6,  transparent=True, colors=[(0, 124/255, 0, 1)]*6)

junglewood_block = Block(41, ['textures/block/jungle_log_top.png']*2+['textures/block/jungle_log.png']*4)
jungleleaf_block = Block(42, ['textures/block/jungle_leaves.png']*6,  transparent=True, colors=[(0, 124/255, 0, 1)]*6)

birchwood_block = Block(43, ['textures/block/birch_log_top.png']*2+['textures/block/birch_log.png']*4)
birchleaf_block = Block(44, ['textures/block/birch_leaves.png']*6,  transparent=True, colors=[(0, 124/255, 0, 1)]*6)
yflowers_block = Plant(45, ['textures/block/dandelion.png']*6)