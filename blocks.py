from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
import threading
import time
import pyglet
# import numpy as np

__all__ = (
    'stone_block', 'sand_block', 'brick_block', 'bedrock_block', 'acacia_leaves_block', 'acacia_sapling_block','blue_concrete_powder_block', 'grass_block', 'water_block', 'dirt_block', 'snow_block', 'diamondore_block', 'coalore_block', 'gravel_block','ironore_block','lapisore_block', 'quartz_block','clay_block','nether_block','nether_quartz_ore_block' ,'soulsand_block', 'sandstone_block', 'ice_block', 'snowgrass_block', 'air_block', 'melon_block','pumpkin_block', 'yflowers_block', 'potato_block', 'carrot_block', 'rose_block', 'fern_block', 'wildgrass0_block','wildgrass1_block', 'wildgrass0_block', 'wildgrass2_block', 'wildgrass3_block', 'wildgrass4_block', 'wildgrass5_block','wildgrass6_block','wildgrass7_block', 'deadbush_block', 'cactus_block', 'tallcactus_block','reed_block','oakwood_block','oakleaf_block','junglewood_block','jungleleaf_block','birchwood_block','birchleaf_block', 'potato_stage0_block', 'bell', 'beacon', 'ancient_debris', 'blackstone', 'cartography_table', 'crying_obsidian', 'cyan_stained_glass', 'cobweb', 'observer_block','chest')

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
    v1x = x + n
    v2x = x - n
    v1y = y + n
    v2y = y - n
    v1z = z + n
    v2z = z - n
    return [
        [v2x, v1y, v2z, v2x, v1y, v1z, v1x, v1y, v1z, v1x, v1y, v2z],  # top
        [v2x, v2y, v2z, v1x, v2y, v2z, v1x, v2y, v1z, v2x, v2y, v1z],  # bottom
        [v2x, v2y, v2z, v2x, v2y, v1z, v2x, v1y, v1z, v2x, v1y, v2z],  # left
        [v1x, v2y, v1z, v1x, v2y, v2z, v1x, v1y, v2z, v1x, v1y, v1z],  # right
        [v2x, v2y, v1z, v1x, v2y, v1z, v1x, v1y, v1z, v2x, v1y, v1z],  # front
        [v1x, v2y, v2z, v2x, v2y, v2z, v2x, v1y, v2z, v1x, v1y, v2z],  # back
    ]
def chest_cube_vertices_with_sides(x,y,z,n=0.5,lid_space=6):
    v1x = x + n
    v2x = x - n
    v1y = y + n-(n*(lid_space/16))
    v2y = y - n
    v1z = z + n
    v2z = z - n
    return [
        [v2x, v1y, v2z, v2x, v1y, v1z, v1x, v1y, v1z, v1x, v1y, v2z],  # top
        [v2x, v2y, v2z, v1x, v2y, v2z, v1x, v2y, v1z, v2x, v2y, v1z],  # bottom
        [v2x, v2y, v2z, v2x, v2y, v1z, v2x, v1y, v1z, v2x, v1y, v2z],  # left
        [v1x, v2y, v1z, v1x, v2y, v2z, v1x, v1y, v2z, v1x, v1y, v1z],  # right
        [v2x, v2y, v1z, v1x, v2y, v1z, v1x, v1y, v1z, v2x, v1y, v1z],  # front
        [v1x, v2y, v2z, v2x, v2y, v2z, v2x, v1y, v2z, v1x, v1y, v2z],  # back
    ]

def cactus_cube_vertices_with_sides(x, y, z, n=0.5, value_reduction=(2,16), extra = 0):
    """ Return the vertices of the cube at position x, y, z with size 2*n.
    """

    change = n*((value_reduction[0]+extra)/value_reduction[1]) #adding 1

    return [
        [x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n],  # top
        [x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n],  # bottom
        [x-n+change,y-n,z-n, x-n+change,y-n,z+n, x-n+change,y+n,z+n, x-n+change,y+n,z-n],  # left
        [x+n-change,y-n,z+n, x+n-change,y-n,z-n, x+n-change,y+n,z-n, x+n-change,y+n,z+n],  # right
        [x-n,y-n,z+n-change, x+n,y-n,z+n-change, x+n,y+n,z+n-change, x-n,y+n,z+n-change],  # front
        [x+n,y-n,z-n+change, x-n,y-n,z-n+change, x-n,y+n,z-n+change, x+n,y+n,z-n+change],  # back
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
        vertex_data = cactus_cube_vertices_with_sides(*pos, extra=1)
        shown = []

        # vertex_data[0]
        for sde in range(0, 6):
            shown += [batch.add(4, GL_QUADS, block_tex[sde], ('v3f/static', vertex_data[sde]),
                            ('t2f/static', texture_data))]

        return shown
class chest(Block):

    def show(self, pos, batch):
        block_tex = self.get_textures()
        block_cols = self.get_colors()
        # print("block cols:", block_cols)
        texture_data = (0, 0, 1, 0, 1, 1, 0, 1)
        vertex_data = chest_cube_vertices_with_sides(*pos)
        shown = []

        # vertex_data[0]
        for sde in range(0, 6):
            shown += [batch.add(4, GL_QUADS, block_tex[sde], ('v3f/static', vertex_data[sde]),
                            ('t2f/static', texture_data))]

        return shown
BLOCKS = {
    'stone_block':( 'pinecraft:stone_block', ['textures/block/stone.png'] * 6),
    'birchleaf_block':('pinecraft:birchleaf_block', ['textures/block/birch_leaves.png']*6),
    'yellow_wool':('pinecraft:yellow_wool', ['textures/block/yellow_wool.png']*6),
    'yellow_terracotta':('pinecraft:yellow_terracotta', ['textures/block/yellow_terracotta.png']*6),
    'smithing_table':('pinecraft:smithing_table', ['textures/block/smithing_table_top.png', 'textures/block/smithing_table_bottom.png'] +['textures/block/smithing_table_side.png']*3 + ['textures/block/smithing_table_front.png']),
    'oakwood_block':('pinecraft:oak_wood', ['textures/block/oak_log_top.png']*2+['textures/block/oak_log.png']*4),
    'oakleaf_block':('pinecraft:oak_leaves', ['textures/block/oak_leaves.png']*6),
    'junglewood_block':('pinecraft:jungle_wood', ['textures/block/jungle_log_top.png']* 2 +['textures/block/jungle_log.png']*4),
    'jungleleaf_block':('pinecraft:jungle_leaves', ['textures/block/jungle_leaves.png']*6),
    'birchwood_block':('pinecraft:birch_wood', ['textures/block/birch_log_top.png']* 2 +['textures/block/birch_log.png']*4),
    'yflower_block':('pinecraft:yellow_flower', ['textures/block/dandelion.png']*6),
    'white_terracotta':('pinecraft:white_terracotta', ['textures/block/white_terracotta.png']*6),
    'stripped_acacia_log':('pinecraft:stripped_acacia_log', ['textures/block/stripped_acacia_log_top.png']* 2 +['textures/block/stripped_acacia_log.png']*4),
    'basalt':('pinecraft:basalt', ['textures/block/basalt_top.png']*2 + ['textures/block/basalt_side.png']*4),
    'beacon':('pinecraft:beacon', ['textures/block/beacon.png']*6),
    'ancient_debris':('pinecraft:ancient_debris', ['textures/block/ancient_debris_top.png']*2 + ['textures/block/ancient_debris_side.png']*4),
    'anvil':('pinecraft:anvil', ['textures/block/anvil_top.png'] + ['textures/block/anvil.png']*5),
    'bell':('pinecraft:bell', ['textures/block/bell_top.png', 'textures/block/bell_bottom.png'] + ['textures/block/bell_side.png']*4),
    'black_concrete':('pinecraft:black_concrete', ['textures/block/black_concrete.png']*6),
    'blackstone':('pinecraft:blackstone', ['textures/block/blackstone_top.png']*2 +['textures/block/blackstone.png']*4),
    'bone_block':('pinecraft:bone_block', ['textures/block/bone_block_top.png']*2 +['textures/block/bone_block_side.png']*4),
    'bookshelf':('pinecraft:bookshelf', ['textures/block/oak_planks.png']*2 +['textures/block/bookshelf.png']*4),
    'cartography_table':('pinecraft:cartography_table', ['textures/block/cartography_table_top.png', 'textures/block/dark_oak_planks.png']+ ['textures/block/cartography_table_side1.png']*2+ ['textures/block/cartography_table_side2.png', 'textures/block/cartography_table_side3.png']),
    'crafting_table':('pinecraft:crafting_table', ['textures/block/crafting_table_front.png', 'textures/block/oak_planks.png']+ ['textures/block/crafting_table_front.png']+['textures/block/crafting_table_side.png']*3),
    'crying_obsidian':('pinecraft:crying_obsidian', ['textures/block/crying_obsidian.png']*6),
    'cyan_concrete':('pinecraft:cyan_concrete', ['textures/block/cyan_concrete.png']*6),
    'cyan_stained_glass':('pinecraft:cyan_stained_glass', ['textures/block/cyan_stained_glass.png']*6),
    'dark_prismarine':('pinecraft:dark_prismarine', ['textures/block/dark_prismarine.png']*6),
    'smooth_stone':('pinecraft:smooth_stone', ['textures/block/smooth_stone.png']*6),
    'coarse_dirt':('pinecraft:coarse_dirt', ['textures/block/coarse_dirt.png']*6),
    'cobblestone':('pinecraft:cobblestone', ['textures/block/cobblestone.png']*6),
    'cobweb':('pinecraft:cobweb', ['textures/block/cobweb.png']*6),
    'crimson_planks':('pinecraft:crimson_planks', ['textures/block/crimson_planks.png']*6),
    'emerald_block':('pinecraft:emerald_block', ['textures/block/emerald_block.png']*6),
    'end_stone':('pinecraft:end_stone', ['textures/block/end_stone.png']*6),
    'granite':('pinecraft:granite', ['textures/block/granite.png']*6),
    'hay_block':('pinecraft:hay_block', ['textures/block/hay_block_top.png']*2 +['textures/block/hay_block_side.png']*4),
    'honey_block':('pinecraft:honey_block', ['textures/block/honey_block_top.png']*2+ ['textures/block/honey_block_side.png']*4),
    'iron_block':('pinecraft:iron_block', ['textures/block/iron_block.png']*6),
    'lapis_block':('pinecraft:lapis_block', ['textures/block/lapis_block.png']*6),
    'observer_block':('pinecraft:observer', ['textures/block/observer_top.png']*2 +['textures/block/observer_side.png']*2 +['textures/block/observer_front.png', 'textures/block/observer_back.png']),
    'pink_concrete':('pinecraft:pink_concrete', ['textures/block/pink_concrete.png']*6),
    'pink_concrete_powder':('pinecraft:pink_concrete_powder', ['textures/block/pink_concrete_powder.png']*6),
    'pink_wool':('pinecraft:pink_wool', ['textures/block/pink_wool.png']*6),
    'polished_andesite':('pinecraft:polished_andesite', ['textures/block/polished_andesite.png']*6),
    'polished_basalt':('pinecraft:polished_basalt', ['textures/block/polished_basalt_top.png']*2+ ['textures/block/polished_basalt_side.png']*4),
    'podzol_block':('pinecraft:podzol', ['textures/block/podzol_top.png', 'textures/block/dirt.png']+['textures/block/podzol_side.png']*4),
    'polished_diorite':('pinecraft:polished_diorite', ['textures/block/polished_diorite.png']*6),
    'polished_granite':('pinecraft:polished_granite', ['textures/block/polished_granite.png']*6),
    'purple_wool':('pinecraft:purple_wool', ['textures/block/purple_wool.png']*6),
    'purpur_block':('pinecraft:purpur_block', ['textures/block/purpur_block.png']*6),
    'purpur_pillar':('pinecraft:purpur_pillar', ['textures/block/purpur_pillar_top.png']*2+ ['textures/block/purpur_pillar.png']*4),
    'red_mushroom':('pinecraft:red_mushroom_block', ['textures/block/red_mushroom_block.png']*6),
    'red_nether_bricks':('pinecraft:red_nether_bricks', ['textures/block/red_nether_bricks.png']*6),
    'red_sand':('pinecraft:red_sand', ['textures/block/red_sand.png']*6),
    'red_sandstone':('pinecraft:red_sandstone', ['textures/block/red_sandstone_top.png', 'textures/block/red_sandstone_bottom.png']+['textures/block/red_sandstone.png']*4),
    'red_wool':('pinecraft:red_wool', ['textures/block/red_wool.png']*6),
    'sea_lantern':('pinecraft:sea_lantern', ['textures/block/sea_lantern.png']*6),
    'shroomlight':('pinecraft:shroomlight', ['textures/block/shroomlight.png']*6),
    'slime_block': ('pinecraft:slime_block', ['textures/block/slime_block.png']*6),
    'sponge': ('pinecraft:sponge', ['textures/block/sponge.png']*6),
    'stone_bricks': ('pinecraft:stone_bricks', ['textures/block/stone_bricks.png']*6),
    'tnt':('pinecraft:tnt', ['textures/block/tnt_top.png', 'textures/block/tnt_bottom.png']+['textures/block/tnt_side.png']*4),
    'warped_nylium':('pinecraft:warped_nylium', ['textures/block/warped_nylium.png', 'textures/block/netherrack.png']+ ['textures/block/warped_nylium_side.png']*4),
    'warped_planks': ('pinecraft:warped_planks', ['textures/block/warped_planks.png']*6),
    'mossy_cobblestone':('pinecraft:mossy_cobblestone', ['textures/block/mossy_cobblestone.png']*6),
    'magenta_concrete':('pinecraft:magenta_concrete', ['textures/block/magenta_concrete.png']*6),
    'magenta_wool':('pinecraft:magenta_wool', ['textures/block/magenta_wool.png']*6),
    'lime_concrete':('pinecraft:lime_concrete', ['textures/block/lime_concrete.png']*6),
    'lime_wool':('pinecraft:lime_wool', ['textures/block/lime_wool.png']*6),

}

PLANTS = {
    "wild_grass":("pinecraft:wild_grass", ['textures/block/tall_grass_top.png']*6),
    "potato_stage0_block":("pinecraft:potato", ['textures/block/potatoes_stage0.png']*6),
    "carrot_stage0_block":("pinecraft:carrot", ['textures/block/carrots_stage0.png']*6),
    "rose_bush_bottom_block":("pinecraft:rose", ['textures/block/rose_bush_bottom.png']*6),
    "fern_block":("pinecraft:fern", ['textures/block/fern.png']*6),
    "tall_grass_top_block":("pinecraft:tall_grass", ['textures/block/tall_grass_top.png']*6),
    "wildgrass_block":("pinecraft:wildgrass", ['textures/block/tall_grass_top.png']*6),
    "deadbush_block":("pinecraft:dead_bush", ['textures/block/dead_bush.png']*6),
    "cactus_block":("pinecraft:cactus", ['textures/block/cactus_top.png','textures/block/cactus_bottom.png']+['textures/block/cactus_side.png']*4),
    "sugarcane_block":("pinecraft:sugarcane", ['textures/block/sugar_cane.png']*6),




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

grass_block = Block(16,
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


potato_stage0_block = potato_block = Plant(*PLANTS['potato_stage0_block'])
carrot_stage0_block = carrot_block = Plant(*PLANTS['carrot_stage0_block'])
rose_bush_bottom_block = rose_block = Plant(*PLANTS['rose_bush_bottom_block'])
fern_block = Plant(*PLANTS['fern_block'], colors=[(0, 124/255, 0, 1)]*6) #TODO: fern add color
tall_grass_top_block = wildgrass0_block = Plant(*PLANTS['wild_grass'], colors=[(	0, 124/255, 0, 1)]*6)
wildgrass1_block = Plant(*PLANTS["wild_grass"], colors=[(	0, 124/255, 0, 1)]*6)
wildgrass2_block = Plant(30, ['textures/block/tall_grass_top.png']*6, colors=[(	0, 124/255, 0, 1)]*6)
wildgrass3_block = Plant(31, ['textures/block/tall_grass_top.png']*6, colors=[(	0, 124/255, 0, 1)]*6)
wildgrass4_block = Plant(32, ['textures/block/tall_grass_top.png']*6, colors=[(	0, 124/255, 0, 1)]*6)
wildgrass5_block = Plant(33, ['textures/block/tall_grass_top.png']*6, colors=[(	0, 124/255, 0, 1)]*6)
wildgrass6_block = Plant(34, ['textures/block/tall_grass_top.png']*6, colors=[(	0, 124/255, 0, 1)]*6)
wildgrass7_block = Plant(35, ['textures/block/tall_grass_top.png']*6, colors=[(	0, 124/255, 0, 1)]*6)
deadbush_block = Plant(*PLANTS['deadbush_block'])
cactus_block = Cactus(*PLANTS['cactus_block'], transparent=True)
tallcactus_block = cactus_block
reed_block = sugarcane_block = Plant(*PLANTS['sugarcane_block'])
chest=chest(46,['textures/entity/chest/Chest inside.jpg']*2+['textures/entity/chest/Chest side.jpg']*4,transparent=True)

oakwood_block = Block(*BLOCKS['oakwood_block'])
oakleaf_block = Block(*BLOCKS['oakleaf_block'],  transparent=True, colors=[(0, 124/255, 0, 1)]*6)

junglewood_block = Block(*BLOCKS['junglewood_block'])
jungleleaf_block = Block(*BLOCKS['jungleleaf_block'],  transparent=True, colors=[(0, 124/255, 0, 1)]*6)

birchwood_block = Block(*BLOCKS['birchwood_block'])
birchleaf_block = Block(*BLOCKS['birchleaf_block'],  transparent=True, colors=[(0, 124/255, 0, 1)]*6)
yflowers_block = Plant(*BLOCKS['yflower_block'])
yellow_wool = Block(*BLOCKS['yellow_wool'])
yellow_terracotta = Block(*BLOCKS['yellow_terracotta'])
smithing_table = Block(*BLOCKS['smithing_table'])
white_terracotta = Block(*BLOCKS['white_terracotta'])
stripped_acacia_log = Block(*BLOCKS['stripped_acacia_log'])
basalt = Block(*BLOCKS['basalt'])
beacon = Block(*BLOCKS['beacon'])
ancient_debris = Block(*BLOCKS['ancient_debris'])
anvil = Block(*BLOCKS['anvil'])
bell = Block(*BLOCKS['bell'])
black_concrete = Block(*BLOCKS['black_concrete'])
blackstone = Block(*BLOCKS['blackstone'])
bone_block = Block(*BLOCKS['bone_block'])
bookshelf = Block(*BLOCKS['bookshelf'])
cartography_table = Block(*BLOCKS['cartography_table'])
crafting_table = Block(*BLOCKS['crafting_table'])
crying_obsidian = Block(*BLOCKS['crying_obsidian'])
cyan_concrete = Block(*BLOCKS['cyan_concrete'])
cyan_stained_glass = Block(*BLOCKS['cyan_stained_glass'], transparent=False)
dark_prismarine = Block(*BLOCKS['dark_prismarine'])
smooth_stone = Block(*BLOCKS['smooth_stone'])
coarse_dirt = Block(*BLOCKS['coarse_dirt'])
cobblestone = Block(*BLOCKS['cobblestone'])
cobweb = Block(*BLOCKS['cobweb'], transparent=True, rigid=False)
crimson_planks = Block(*BLOCKS['crimson_planks'])
emerald_block = Block(*BLOCKS['emerald_block'])
end_stone = Block(*BLOCKS['end_stone'])
granite = Block(*BLOCKS['granite'])
hay_block = Block(*BLOCKS['hay_block'])
honey_block = Block(*BLOCKS['honey_block'])
iron_block = Block(*BLOCKS['iron_block'])
lapis_block = Block(*BLOCKS['lapis_block']) #30
observer_block = Block(*BLOCKS['observer_block'])
pink_concrete = Block(*BLOCKS['pink_concrete'])
pink_concrete_powder = Block(*BLOCKS['pink_concrete_powder'])
pink_wool = Block(*BLOCKS['pink_wool'])
polished_andesite = Block(*BLOCKS['polished_andesite']) #35
polished_basalt = Block(*BLOCKS['polished_basalt'])
podzol_block = Block(*BLOCKS['podzol_block'])
polished_granite = Block(*BLOCKS['polished_granite'])
polished_diorite = Block(*BLOCKS['polished_diorite'])
purple_wool = Block(*BLOCKS['purple_wool']) #40
purpur_block = Block(*BLOCKS['purpur_block'])
purpur_pillar_block = Block(*BLOCKS['purpur_pillar'])
red_mushroom_block = Block(*BLOCKS['red_mushroom'])
red_nether_bricks = Block(*BLOCKS['red_nether_bricks'])
red_sand = Block(*BLOCKS['red_sand']) #45
red_sandstone = Block(*BLOCKS['red_sandstone'])
red_wool = Block(*BLOCKS['red_wool'])
# sea_lantern = Block(*BLOCKS['sea_lantern'])
shroomlight = Block(*BLOCKS['shroomlight'])
slime_block = Block(*BLOCKS['slime_block']) #50
sponge = Block(*BLOCKS['sponge'])
stone_bricks = Block(*BLOCKS['stone_bricks'])
tnt = Block(*BLOCKS['tnt'])
warped_nylium = Block(*BLOCKS['warped_nylium'])
warped_planks = Block(*BLOCKS['warped_planks'])#55
mossy_cobblestone = Block(*BLOCKS['mossy_cobblestone'])
magenta_concrete = Block(*BLOCKS['magenta_concrete'])
magenta_wool = Block(*BLOCKS['magenta_wool'])
lime_wool = Block(*BLOCKS['lime_wool'])
lime_concrete = Block(*BLOCKS['lime_concrete'])#60






















oakwood_block = Block(39, ['textures/block/oak_log_top.png']*2+['textures/block/oak_log.png']*4)
oakleaf_block = Block(40, ['textures/block/oak_leaves.png']*6,  transparent=True, colors=[(0, 124/255, 0, 1)]*6)

junglewood_block = Block(41, ['textures/block/jungle_log_top.png']*2+['textures/block/jungle_log.png']*4)
jungleleaf_block = Block(42, ['textures/block/jungle_leaves.png']*6,  transparent=True, colors=[(0, 124/255, 0, 1)]*6)

birchwood_block = Block(43, ['textures/block/birch_log_top.png']*2+['textures/block/birch_log.png']*4)
birchleaf_block = Block(44, ['textures/block/birch_leaves.png']*6,  transparent=True, colors=[(0, 124/255, 0, 1)]*6)
yflowers_block = Plant(45, ['textures/block/dandelion.png']*6)
