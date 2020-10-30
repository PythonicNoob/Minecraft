
from __future__ import division

import sys
import math
import random
import time
import os
import psutil
import threading
import pickle
import multiprocessing
import concurrent.futures
import pyautogui

from collections import deque
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import Pool

from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse

# from blocks import grass_block, sand_block, stone_block, bedrock_block, brick_block, acacia_leaves_block, acacia_sapling_block, blue_concrete_powder_block, water_block
from blocks import *
from blocks import Plant, Liquid

from terrain import TerrainGeneratorSimple
from nature import Trunk, Tree, SmallPlant

from hotbar import Hotbar

# import threading

TICKS_PER_SEC = 60
anim=pyglet.image.load_animation('loading screen.gif')
wi,he=pyautogui.size()
loading=pyglet.sprite.Sprite(anim)
# Size of sectors used to ease block loading.
SECTOR_SIZE = 16

WALKING_SPEED = 5
FLYING_SPEED = 15
start=time.time()
GRAVITY = 20.0
MAX_JUMP_HEIGHT = 1.0 # About the height of a block.pip install pyglet
# To derive the formula for calculating jump speed, first solve
#    v_t = v_0 + a * t
# for the time at which you achieve maximum height, where a is the acceleration
# due to gravity and v_t = 0. This gives:
#    t = - v_0 / a
# Use t and the desired MAX_JUMP_HEIGHT to solve for v_0 (jump speed) in
#    s = s_0 + v_0 * t + (a * t^2) / 2
JUMP_SPEED = math.sqrt(2 * GRAVITY * MAX_JUMP_HEIGHT)
TERMINAL_VELOCITY = 50
PLAYER_HEIGHT = 2

def sector_to_blockpos(secpos):
    x,y,z = secpos
    return x*8, y*8, z*8

if sys.version_info[0] >= 3:
    xrange = range

def cube_vertices(x, y, z, n):
    """ Return the vertices of the cube at position x, y, z with size 2*n.
    """
    return [
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,  # back
    ]

def cube_vertices_with_sides(x, y, z, n):
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


def tex_coord(x, y, n=4):
    """ Return the bounding vertices of the texture square.
    """
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


def tex_coords(top, bottom, side):
    """ Return a list of the texture squares for the top, bottom and side.
    """
    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    side = tex_coord(*side)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(side * 4)
    return result

def grass_verts(pos,n=0.5):
    x,y,z = pos; v = tuple((x+X,y+Y,z+Z) for X in (-n,n) for Y in (-n,n) for Z in (-n,n))
    return tuple(tuple(k for j in i for k in v[j]) for i in ((0,5,7,2),(1,4,6,3)))


TEXTURE_PATH = 'texture.png'

# GRASS = tex_coords((1, 0), (0, 1), (0, 0))
# SAND = tex_coords((1, 1), (1, 1), (1, 1))
# BRICK = tex_coords((2, 0), (2, 0), (2, 0))
# STONE = tex_coords((2, 1), (2, 1), (2, 1))

FACES = [
    ( 0, 1, 0), # TOP
    ( 0,-1, 0), # BOTTOM
    (-1, 0, 0), # LEFT
    ( 1, 0, 0), # RIGHT
    ( 0, 0, 1), # FRONT
    ( 0, 0,-1), # BACK
]


def normalize(position): #gets block pos from vector
    """ Accepts `position` of arbitrary precision and returns the block
    containing that position.
    Parameters
    ----------
    position : tuple of len 3
    Returns
    -------
    block_position : tuple of ints of len 3
    """
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return (x, y, z)


def sectorize(position): #basically chunks
    """ Returns a tuple representing the sector for the given `position`.
    Parameters
    ----------
    position : tuple of len 3
    Returns
    -------
    sector : tuple of len 3
    """
    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return (x, y, z)


class Model(object):

    def __init__(self):

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()
        self.transparent_batch = pyglet.graphics.Batch()
        # self.plants_batch = pyglet.graphics.Batch()
        # water_block.set_transparent(self.transparent_batch)
        # A TextureGroup manages an OpenGL texture.
        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture())

        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.world = {}

        # Same mapping as `world` but only contains blocks that are shown.
        self.shown = {}

        # Mapping from position to a pyglet `VertextList` for all shown blocks.
        self._shown = {}

        # Mapping from sector to a list of positions inside that sector.
        self.sectors = {}

        self.to_draw_nature = set()

        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()

        self._initialize()

    def generate_vegetation(self, pos, veg):
        x, y, z = pos
        if veg is None: return
        below_block = self.world.get((x, y - 1, z), None)
        # print("veg:", veg, "type veg: ", type(veg))
        if issubclass(veg, SmallPlant):

            # print("Is subclass veg of smallplant")

            block = veg.block
            # print("block:",block)
            grows_on = veg.grows_on
            if below_block is None or below_block in grows_on:
                self.init_block(pos, block)
                # if pos in self.world:
                #     self.remove_block(pos, immediate=False)
                # self.world[pos] = block
                # self.sectors.setdefault(sectorize(pos), []).append(pos)
                # self.to_draw_nature.add( (pos, block) )
                # pass
                # self.add_block_new(pos, grass_block)

        elif issubclass(veg, Tree):
            # print("tree subclass")
            trunk_block = veg.trunk_block
            leaf_block = veg.leaf_block
            height = random.randint(*veg.trunk_height_range)

            if below_block is None or below_block not in veg.grows_on:
                return

            leafs = veg.generate_leafs(x, y+height-1, z)
            #

            for h in range(height):
                self.init_block((x,y+h,z), trunk_block)

            for pos in leafs:
                self.init_block(pos, leaf_block)

            # d = height // 3 + 1
            # treetop = y + height
            # for xl in range(x - d, x + d):
            #     dx = abs(xl - x)
            #     for yl in range(treetop - d, treetop + d):
            #         for zl in range(z - d, z + d):
            #             # Don't replace existing blocks
            #             if (xl, yl, zl) in self.world:
            #                 continue
            #             # Avoids orphaned leaves
            #             if not self.has_neighbors((xl, yl, zl),
            #                                        set((trunk_block,
            #                                             leaf_block))):
            #                 continue
            #             dz = abs(zl - z)
            #             # The farther we are (horizontally) from the trunk,
            #             # the least leaves we can find.
            #             if random.uniform(0, dx + dz) > 0.6:
            #                 continue
            #             # world.add_block((xl, yl, zl), cls.leaf_block, force=False,
            #             #                 sync=sync)
            #             self.init_block((xl, yl, zl), leaf_block,)

        elif issubclass(veg, Trunk):
            # print("truunk subclass")
            block = veg.block
            grows_on = veg.grows_on
            height = random.randint(*veg.height_range)
            # below_block = self.world.get((x, y - 1, z), None)

            if below_block is None or below_block in grows_on:
                # x, y, z = pos
                for dy in range(0, height):
                    new_pos = x, y+dy, z
                    self.init_block(new_pos, block)
                    # if new_pos in self.world:
                    #     self.remove_block(new_pos, immediate=False)
                    # self.world[new_pos] = block
                    # self.sectors.setdefault(sectorize(new_pos), []).append(new_pos)

        # print("gen_vegetation:",*args)
        # pass
        # TODO: implement gen vegetation

    def init_block(self, position, block):
        if position in self.world:
            self.remove_block(position, immediate=False)
        self.world[position] = block
        self.sectors.setdefault(sectorize(position), []).append(position)

    def _initialize(self):
        """ Initialize the world by placing all the blocks.
        """
        # n = 10  # 1/2 width and height of world
        # s = 1  # step size
        # y = 0  # initial y height

        self.terraingen = TerrainGeneratorSimple(self, "573947210")
        # a = time.time()
        # print(sectorize((0,60, 0)))
        with ThreadPoolExecutor(max_workers=200) as executor:
            for x in range(-8, 8):
                for y in range(2,5):
                    for z in range(-8, 8):
                        executor.submit(self.open_sector, (x,y,z) )
        # print("time take to generate sector 0,60,0 :", time.time()-a)
        # self.open_sector((0,0,1))
        # self.open_sector((0,0,5))

        # self.open_sector((-1, 0, 0))
        # self.open_sector((0, -1, 0))
        # self.open_sector((-1, -1, 0))
        # self.open_sector((-1, 0, 0))
        # self.open_sector((0, -1, 0))

        # self.terraingen = TerrainGenerator(573947210)
        # self.sectors[0,0,0] = self.terraingen.generate_chunk(0,0,0).blocks


        # self.open_sector((0, 0, 33))
        # self.open_sector((0, 0, 66))
        # self.open_sector((0, 0, 99))
        # for x in xrange(-n, n + 1, s):
        #     for z in xrange(-n, n + 1, s):
        #         # create a layer stone an grass everywhere.
        #         self.add_block_new((x, y - 2, z), grass_block, immediate=False)
        #         self.add_block_new((x, y - 3, z), bedrock_block, immediate=False)
        #         if x in (-n, n) or z in (-n, n):
        #             # create outer walls.
        #             for dy in xrange(-2, 3):
        #                 self.add_block_new((x, y + dy, z), bedrock_block, immediate=False)
        #
        # # generate the hills randomly
        # o = n - 10
        # for _ in xrange(120):
        #     a = random.randint(-o, o)  # x position of the hill
        #     b = random.randint(-o, o)  # z position of the hill
        #     c = -1  # base of the hill
        #     h = random.randint(1, 6)  # height of the hill
        #     s = random.randint(4, 8)  # 2 * s is the side length of the hill
        #     d = 1  # how quickly to taper off the hills
        #     # t = random.choice([GRASS, SAND, BRICK])
        #     t = random.choice([grass_block, sand_block, brick_block])
        #     for y in xrange(c, c + h):
        #         for x in xrange(a - s, a + s + 1):
        #             for z in xrange(b - s, b + s + 1):
        #                 if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
        #                     continue
        #                 if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
        #                     continue
        #                 self.add_block_new((x, y, z), t, immediate=False)
        #         s -= d  # decrement side lenth so hills taper off

    def open_sector(self, sector):
        #The sector is not in memory, load or create it
            #The sector doesn't exist yet, generate it!

        # print("opening sector: ",sector)

        # bx, by, bz = sector_to_blockpos(sector)
        # rx, ry, rz = bx//32*32, by//32*32, bz//32*32

        x,y,z = sector
        # print("generating sector: ",sector)
        self.terraingen.generate_sector((x, y, z))

        #For ease of saving/loading, queue up generation of a whole region (4x4x4 sectors) at once
        # yiter, ziter = range(ry//8,ry//8+4), range(rz//8,rz//8+4)
        # for secx in range(rx//8,rx//8+4):
        #     for secy in yiter:
        #         for secz in ziter:
        #             self.terraingen.generate_sector((secx,secy,secz))

    def hit_test(self, position, vector, max_distance=8):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.
        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in xrange(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and key in self.world:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def exposed(self, position):
        """ Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.
        """
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
            else:
                if self.world[x + dx, y + dy, z + dz].transparent:
                    return True
        return False

    def add_block(self, position, texture, immediate=True):
        """ Add a block with the given `texture` and `position` to the world.
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        immediate : bool
            Whether or not to draw the block immediately.
        """
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = texture
        self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            self.check_neighbors(position)

    def add_block_new(self, position, block, immediate=True):
        """ Add a block with the given `texture` and `position` to the world.
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        immediate : bool
            Whether or not to draw the block immediately.
        """
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = block
        self.sectors.setdefault(sectorize(position), []).append(position)



        if immediate:
            if self.exposed(position):
                self.show_block_new(position)
            self.check_neighbors(position)

    def remove_block(self, position, immediate=True):
        """ Remove the block at the given `position`.
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether or not to immediately remove block from canvas.
        """


        # if self.world.get(position, None):
        del self.world[position]
        self.sectors[sectorize(position)].remove(position)
        if immediate:
            if position in self.shown:
                self.hide_block(position)
            self.check_neighbors(position)

    def has_neighbors(self, position, blocks_to_check: list, all=False):
        x, y, z = position
        not_found_faces = 0
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                not_found_faces += 1
                if all:
                    return False
                continue
            if self.world[key] not in blocks_to_check:
                not_found_faces += 1
                if all:
                    return False
            else:
                if not all:
                    return True
        return (False if not_found_faces == 6 else True) #If any of them don't find a block they will return false if all is true

    def check_neighbors(self, position, ):
        """ Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.
        """
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            if self.exposed(key):
                if key not in self.shown:
                    self.show_block_new(key)
            else:
                if key in self.shown: # TODO: Use seperate faces so that instead of rendering full block, only exposed sides are rendered
                    self.hide_block(key)

    def show_block(self, position, immediate=True):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.
        """
        texture = self.world[position]
        self.shown[position] = texture
        if immediate:
            self._show_block(position, texture)
        else:
            self._enqueue(self._show_block, position, texture)


    def show_block_new(self, position, immediate=True):
        """ Show the block at the given `position`. This method assumes the
        block has already been added with add_block()
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether or not to show the block immediately.
        """
        block = self.world[position]
        self.shown[position] = block
        if immediate:
            self._show_block_new(position, block)
        else:
            self._enqueue(self._show_block_new, position, block)


    def _show_block_new(self, position, block):
        """ Private implementation of the `show_block()` method.
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        """

        if isinstance(block, Liquid):
            self._shown[position] = block.show(position, self.transparent_batch)
        else:
            self._shown[position] = block.show(position, self.batch)
        # elif isinstance(block, Plant):
        #     self._shown[position] = block.show(position, self.plants_batch)
        # elif isinstance(block, Block):
        #     self._shown[position] = block.show(position, self.batch)

        # x, y, z = position
        # vertex_data = cube_vertices_with_sides(x, y, z, 0.5)
        # texture_data = (0,0, 1,0, 1,1, 0,1)
        # texture_data = list(texture)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        # block_tex = block.get_textures()
        # block_col = block.get_colors()
        # block_type = block.get_type()
        #
        # if block_type == 'block':
        #     self._show_block_block(position, block_tex)
        # elif block_type == 'plant':
        #     self._show_block_plant(position, block_tex[0])
        # elif block_type == 'liquid':
        #     self._shown[position] = block.show(position, vertex_data)


    def _show_block(self, position, texture):
        """ Private implementation of the `show_block()` method.
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        """
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(texture)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        self._shown[position] = self.batch.add(24, GL_QUADS, self.group,
            ('v3f/static', vertex_data),
            ('t2f/static', texture_data))

    def hide_block(self, position, immediate=True):
        """ Hide the block at the given `position`. Hiding does not remove the
        block from the world.
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        immediate : bool
            Whether or not to immediately remove the block from the canvas.
        """
        self.shown.pop(position)
        if immediate:
            self._hide_block(position)
        else:
            self._enqueue(self._hide_block, position)

    def _hide_block(self, position):
        """ Private implementation of the 'hide_block()` method.
        """
        try:
            [x.delete() for x in self._shown.pop(position)]
        except KeyError:
            pass

    def show_sector(self, sector, immediate=False):
        """ Ensure all blocks in the given sector that should be shown are
        drawn to the canvas.
        """

        if sector not in self.sectors:
            # a= time.time()
            self.open_sector(sector)
            # print("time taken to generate sector:", time.time()-a)

        with ThreadPoolExecutor(max_workers=20) as executor:
        # a = time.time()
        # print("Showing sector:", sector)
            for position in self.sectors.get(sector, []):

                if position not in self.shown and self.exposed(position):
                    executor.submit(self.show_block_new, position, False)
                    # self.show_block_new(position, immediate)
        # print("time taken to show 1 sector: ", time.time()-a)
    def hide_sector(self, sector):
        """ Ensure all blocks in the given sector that should be hidden are
        removed from the canvas.
        """

        for position in self.sectors.get(sector, []):
            if position in self.shown:
                self.hide_block(position, True)

    def change_sectors(self, before, after):
        """ Move from sector `before` to sector `after`. A sector is a
        contiguous x, y sub-region of world. Sectors are used to speed up
        world rendering.
        """
        before_set = set()
        after_set = set()

        before_set_instant = set()
        after_set_instant = set()

        pad = 2
        instant_loads = 1
        for dx in xrange(-pad, pad + 1):
            for dy in  [-1, 0, 1]:  # xrange(-pad, pad + 1):
                for dz in xrange(-pad, pad + 1):
                    if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                        continue
                    if -instant_loads <= dx <= instant_loads and -instant_loads <= dz <= instant_loads and dy==0:
                        #print("dx:", dx,"dy:", dy,"dz:",dz)
                        # if before:
                        #     x, y, z = before
                        #     before_set_instant.add((x + dx, y + dy, z + dz))
                        if after:
                            x, y, z = after
                            after_set_instant.add((x + dx, y + dy, z + dz))

                    if before:
                        x, y, z = before
                        before_set.add((x + dx, y + dy, z + dz))
                    if after:
                        x, y, z = after
                        after_set.add((x + dx, y + dy, z + dz))

        show = after_set - before_set
        hide = before_set - after_set

        show_instant = after_set_instant - show
        hide.union(before_set_instant-after_set_instant)

        # after_set_instant
        # hide - {after}
        # show_instant.add(after)

        # with ThreadPoolExecutor(max_workers=200) as executor:
        #     for sector in show:
                # print("threading  pool execut opening sector:",sector)
                # executor.submit(self.show_sector, sector)

        for sector in show_instant:
            self.show_sector(sector, True)
        for sector in show:
            self.show_sector(sector)
        for sector in hide:
            self.hide_sector(sector)

    def _enqueue(self, func, *args):
        """ Add `func` to the internal queue.
        """
        self.queue.append((func, args))

    def _dequeue(self):
        """ Pop the top function from the internal queue and call it.
        """
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self):
        """ Process the entire queue while taking periodic breaks. This allows
        the game loop to run smoothly. The queue contains calls to
        _show_block() and _hide_block() so this method should be called if
        add_block() or remove_block() was called with immediate=False
        """
        start = time.perf_counter() # TODO: .clock() vs process_time() vs perf_counter()
        # with ThreadPoolExecutor(max_workers=10) as executor:
        # with Pool() as p:
        while self.queue and time.perf_counter() - start < 2.0 / TICKS_PER_SEC:
                # print("processing queue")
                # p.apply(self._dequeue)
                self._dequeue()
                # executor.submit(self._dequeue)

    def process_entire_queue(self):
        """ Process the entire queue with no breaks.
        """
        while self.queue:
            self._dequeue()


class Window(pyglet.window.Window):

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        # Whether or not the window exclusively captures the mouse.
        self.exclusive = False
        self.v1=-1
        # When flying gravity has no effect and speed is increased.
        self.flying = True

        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.strafe = [0, 0]

        # Current (x, y, z) position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        self.position = (0, 60, 0)

        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.rotation = (0, 0)

        # Which sector the player is currently in.
        self.sector = None

        # The crosshairs at the center of the screen.
        self.reticle = None

        # hotbar
        # self.hotbar_image = pyglet.image.load('hotbar.png')
        # self.hotbar_image.anchor_x = self.hotbar_image.width // 2
        # self.hotbar_selection_image = pyglet.image.load('hotbar_selection.png')
        # self.hotbar_selection_image.anchor_x = self.hotbar_selection.width // 2
        # self.hotbar_selection_image.anchor_y = self.hotbar_selection.height // 2
        # self.hotbar = None
        # self.hotbar_selection = None



        # Velocity in the y (upward) direction.
        self.dy = -10

        # A list of blocks the player can place. Hit num keys to cycle.
        # self.inventory = [BRICK, GRASS, SAND]
        self.inventory = [chest, grass_block, lid, stone_block, acacia_leaves_block, acacia_sapling_block, blue_concrete_powder_block, water_block, yflowers_block]

        self.hotbar = Hotbar(self.inventory)

        # The current block the user can place. Hit num keys to cycle.
        # self.block = self.inventory[0]

        # Convenience list of num keys.
        self.num_keys = [
            key._1, key._2, key._3, key._4, key._5,
            key._6, key._7, key._8, key._9,] # key._0]

        # Instance of the model that handles the world.
        self.model = Model()

        # The label that is displayed in the top left of the canvas.
        self.label = pyglet.text.Label('', font_name='Arial', font_size=18,
            x=10, y=self.height - 10, anchor_x='left', anchor_y='top',
            color=(0, 0, 0, 255))

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)

    def set_exclusive_mouse(self, exclusive):
        """ If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.
        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def get_sight_vector(self): #TODO: Need t understand the math a bit more clearly
        """ Returns the current line of sight vector indicating the direction
        the player is looking.
        """
        x, y = self.rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return (dx, dy, dz)

    def get_motion_vector(self):
        """ Returns the current motion vector indicating the velocity of the
        player.
        Returns
        -------
        vector : tuple of len 3
            Tuple containing the velocity in x, y, and z respectively.
        """
        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if self.flying:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.strafe[1]:
                    # Moving left or right.
                    dy = 0.0
                    m = 1
                if self.strafe[0] > 0:
                    # Moving backwards.
                    dy *= -1
                # When you are flying up or down, you have less left and right
                # motion.
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return (dx, dy, dz)

    def update(self, dt):
        """ This method is scheduled to be called repeatedly by the pyglet
        clock.
        Parameters
        ----------
        dt : float
            The change in time since the last call.
        """
        self.model.process_queue()
        sector = sectorize(self.position)  #Gets the sector
        if sector != self.sector:
            self.model.change_sectors(self.sector, sector)
            if self.sector is None:
                self.model.process_entire_queue()
            self.sector = sector
        m = 8
        dt = min(dt, 0.2)
        for _ in xrange(m):
            self._update(dt / m)

    def _update(self, dt):

        # print("queue len:", len(self.model.queue))

        """ Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.
        Parameters
        ----------
        dt : float
            The change in time since the last call.
        """
        # walking
        # print("world: ",self.model.world)

        # [self.model.add_block_new(x[0], x[1], immediate=False) for x in self.model.to_draw_nature]

        speed = FLYING_SPEED if self.flying else WALKING_SPEED
        d = dt * speed # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        if not self.flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            self.dy -= dt * GRAVITY
            self.dy = max(self.dy, -TERMINAL_VELOCITY)
            dy += self.dy * dt
        # collisions
        x, y, z = self.position
        x, y, z = self.collide((x + dx, y + dy, z + dz), PLAYER_HEIGHT)
        self.position = (x, y, z)
        water_block.update(dt)

    def collide(self, position, height):
        """ Checks to see if the player at the given `position` and `height`
        is colliding with any blocks in the world.
        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check for collisions at.
        height : int or float
            The height of the player.
        Returns
        -------
        position : tuple of len 3
            The new position of the player taking into account collisions.
        """
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
        pad = 0.25
        p = list(position)
        np = normalize(position)

        # try:
        #     if not self.model.world[np].collision:
        #         return tuple(p)
        # except KeyError: # KeyError because block does not exist if block does not exist then no collision
        #     return tuple(p)

        # print("self.model.world[np]:",self.model.world[np])

        for face in FACES:  # check all surrounding blocks
            for i in xrange(3):  # check each dimension independently
                if not face[i]:
                    continue
                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                for dy in xrange(height):  # check each height
                    op = list(np)
                    op[1] -= dy
                    op[i] += face[i]
                    if tuple(op) not in self.model.world or not self.model.world[tuple(op)].collision:
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.dy = 0
                    break
        return tuple(p)

    def right_click(self, previous, click_pos):
        try:
            right_click_action = self.model.shown[click_pos].right_click_press()
            if right_click_action is not None:
                # Peform right click action, open chests, inventory, place water etc.
                #print("Performing action: ", right_click_action)
                pass
            else:
                # grass should turn to dirt.
                # Other conditions also can be added by checkking with blocks
                # Like for plants can be checked if growable nearby
                # Grass, Flowers etc. should be removed
                # Water should also bre removed

                x, y, z = previous
                y -= 1

                # if '*' in self.model.placeable_on

                this_block = self.hotbar.current_block

                if self.model.world.get((x, y, z), None):

                    if self.model.world[x, y, z] not in this_block.placeable_on and '*' not in this_block.placeable_on:
                        return

                    if self.model.world[x,y,z] == grass_block and isinstance(this_block, Plant) == False:
                        self.model.remove_block((x, y, z), immediate=True)
                        self.model.add_block_new((x, y, z), dirt_block, immediate=True)

                self.model.add_block_new(previous, this_block)
                this_block.on_place(previous, self.model)
        except:
            pass

    def on_mouse_press(self, x, y, button, modifiers):
        """ Called when a mouse button is pressed. See pyglet docs for button
        amd modifier mappings.
        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        button : int
            Number representing mouse button that was clicked. 1 = left button,
            4 = right button.
        modifiers : int
            Number representing any modifying keys that were pressed when the
            mouse button was clicked.
        """
        if self.exclusive:
            vector = self.get_sight_vector()
            block, previous = self.model.hit_test(self.position, vector)
            if (button == mouse.RIGHT) or \
                    ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
                # ON OSX, control + left click = right click.
                if previous:
                    # print("right click block:",self.block)
                    self.right_click(previous, block)
            elif button == pyglet.window.mouse.LEFT and block:
                texture = self.model.world[block]
                if texture != bedrock_block: #TODO: Over here make sure STONE is changed to stone if new system works!
                    # print("left click block:", block)
                    self.model.remove_block(block)

        else:
            self.set_exclusive_mouse(True)

    def on_mouse_motion(self, x, y, dx, dy):
        """ Called when the player moves the mouse.
        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        dx, dy : float
            The movement of the mouse.
        """
        if self.exclusive:
            m = 0.15
            x, y = self.rotation
            x, y = x + dx * m, y + dy * m
            y = max(-90, min(90, y))
            self.rotation = (x, y)

    def on_key_press(self, symbol, modifiers):
        """ Called when the player presses a key. See pyglet docs for key
        mappings.
        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.
        """
        if symbol == key.Q:
            self.v1=self.v1*-1
        if symbol == key.W and len(self.model._shown)>=9000:
            self.strafe[0] -= 1
        if symbol == key.S and len(self.model._shown)>=9000:
            self.strafe[0] += 1
        if symbol == key.A and len(self.model._shown)>=9000:
            self.strafe[1] -= 1
        if symbol == key.D and len(self.model._shown)>=9000:
            self.strafe[1] += 1
        if symbol == key.SPACE and len(self.model._shown)>=9000:
            if self.dy == 0:
                self.dy = JUMP_SPEED
        if symbol == key.ESCAPE:
            self.set_exclusive_mouse(False)
        if symbol == key.TAB and len(self.model._shown)>=9000   :
            self.flying = not self.flying
        if symbol in self.num_keys:
            index = (symbol - self.num_keys[0]) % self.hotbar.hotbar_size
            self.hotbar.index = index
            # self.block = self.hotbar.current_block #self.inventory[index]
            # self.hotbar_index = index

    def on_key_release(self, symbol, modifiers):
        """ Called when the player releases a key. See pyglet docs for key
        mappings.
        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.
        """
        if symbol == key.W:
            self.strafe[0] += 1
        elif symbol == key.S:
            self.strafe[0] -= 1
        elif symbol == key.A:
            self.strafe[1] += 1
        elif symbol == key.D:
            self.strafe[1] -= 1

    def on_resize(self, width, height):
        """ Called when the window is resized to a new `width` and `height`.
        """
        # label
        self.label.y = height - 10
        # reticle
        if self.reticle:
            self.reticle.delete()

        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(4,
                                                   ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
                                                   )

        self.hotbar.resize(width, height)

        # if self.hotbar:
        #     self.hotbar.delete()
        #         # update(x=self.hotbar.width, scale_x=(self.width * 0.4) // self.hotbar.width,
        #         #                scale_y=(self.height * 0.08) // self.hotbar.height)
        # self.hotbar = pyglet.sprite.Sprite(self.hotbar_image, x=x, y=0)

        # if self.hotbar_selection:
        #     self.hotbar_selection.delete()

        # self.hotbar_selection = pyglet.sprite.Sprite(self.hotbar_selection_image, x=s)

        # if self.width <= 800 and self.height <= 720 :
        #     # wdth = self.width
        #     self.hotbar.update(scale_x=(self.width * 0.6) // self.hotbar.width,
        #                        scale_y=(self.height * 0.08) // self.hotbar.height)  # *0% width and 10% height
        # elif self.height > 720:
        #     self.hotbar.update(scale_x=(self.width * 0.4) // self.hotbar.width,
        #                        scale_y=(self.height * 0.08) // self.hotbar.height)
        # elif self.height > 920:
        #     self.hotbar.update(scale_x=(self.width * 0.6) // self.hotbar.width,
        #                        scale_y=(self.height * 0.08) // self.hotbar.height)  # *0% width and 10% height
        # else:
        #     self.hotbar.update(scale_x=(800 * 0.6) // self.hotbar.width,
        #                        scale_y=(self.height * 0.08) // self.hotbar.height)



    def set_2d(self):
        """ Configure OpenGL to draw in 2d.
        """
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()



    def set_3d(self):
        """ Configure OpenGL to draw in 3d.

        """
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)

        # Extra for transparency from minecraft 4 from dlc.energy
        # -------
        glDepthFunc(GL_LEQUAL)
        glAlphaFunc(GL_EQUAL, 1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # --------

        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.position
        glTranslatef(-x, -y, -z)

    def on_draw(self):
        """ Called by pyglet to draw the canvas.
        """

        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        # Extra
        glEnable(GL_ALPHA_TEST)
        self.model.batch.draw()
        glDisable (GL_ALPHA_TEST)
        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE);
        self.model.transparent_batch.draw()
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE);
        self.model.transparent_batch.draw()

        # glDisable(GL_CULL_FACE)
        # self.model.plants_batch.draw()
        # glEnable(GL_CULL_FACE)
        #self.draw_shift()
        self.draw_focused_block()
        self.set_2d()
        #self.draw_label()
        #self.draw_cpu_usage()
        self.draw_reticle()
        # Experimental
        t = threading.Thread(target=self.draw_shift())
        t.start()
        if self.v1==1:
            self.draw_cpu_usage()
            t = threading.Thread(target=self.draw_label())
            t.start()
        self.loading()
        self.hotbar.draw()
    def loading(self):
        if len(self.model._shown)<9000:
            loading.draw()

    def draw_focused_block(self):
        """ Draw black edges around the block that is currently under the
        crosshairs.
        """
        vector = self.get_sight_vector()
        block = self.model.hit_test(self.position, vector)[0]
        if block:
            x, y, z = block
            vertex_data = cube_vertices(x, y, z, 0.51)
            glColor3d(0, 0, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


    def draw_cpu_usage(self):
        c = psutil.cpu_percent(interval=0)
        p=psutil.virtual_memory().percent
        d = "CPU: "+str(c)+"% "
        e = "RAM: "+str(p)+"%"
        f=psutil.sensors_battery().percent
        g = "BATT: "+str(f)+"%"

        color = (0,0,0,255) #default color

        if c<90:
            color = (0, 0, 0, 255)
        else:
            color = (255, 0, 0, 255)

        label = pyglet.text.Label(d, font_name="Arial", font_size=16, color=color)
        label.draw()
        #
        if p<90:
            color=(0,0,0,255)
        else:
            color=(255,0,0,255)
        label = pyglet.text.Label(e, font_name="Arial", font_size=16, color=color, x=0, y=20)
        label.draw()
        if f<20:
            color=(255,0,0,255)
        else:
            color=(0,0,0,255)
        label = pyglet.text.Label(g, font_name="Arial", font_size=16, color=color, x=0, y=40)
        label.draw()

    def draw_shift(self):
        end = time.time()
        t = end - start
        if t % 60 < 30:
            glClearColor(0.1, 0.2, 0.35, 0.1)
        else:
            glClearColor(0.5, 0.69, 1.0, 1)

    def draw_label(self):
        """ Draw the label in the top left of the screen.
        """
        x, y, z = self.position
        self.label.text = '%02d (%.2f, %.2f, %.2f) %d / %d %d %d' % (
            pyglet.clock.get_fps(), x, y, z,
            len(self.model._shown), len(self.model.world), self.get_size()[0], self.get_size()[1])
        self.label.draw()

    def draw_reticle(self):
        """ Draw the crosshairs in the center of the screen.
        """
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)

    def draw_inventory(self):

        # hotbar_image.anchor_y = hotbar_image.height

        glColor3d(1,1,1)
        self.hotbar.draw()
def setup_fog():
    """ Configure the OpenGL fog properties.
    """
    # Enable fog. Fog "blends a fog color with each rasterized pixel fragment's
    # post-texturing color."
    glEnable(GL_FOG)
    # Set the fog color.
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
    # Say we have no preference between rendering speed and quality.
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    # Specify the equation used to compute the blending factor.
    glFogi(GL_FOG_MODE, GL_LINEAR)
    # How close and far away fog starts and ends. The closer the start and end,
    # the denser the fog in the fog range.
    glFogf(GL_FOG_START, 20.0)
    glFogf(GL_FOG_END, 60.0)


def setup():
    """ Basic OpenGL configuration.
    """
    # Set the color of "clear", i.e. the sky, in rgba.
    glClearColor(0.5, 0.69, 1.0, 1)
    # Enable culling (not rendering) of back-facing facets -- facets that aren't
    # visible to you.
    glEnable(GL_CULL_FACE)
    # Set the texture minification/magnification function to GL_NEAREST (nearest
    # in Manhattan distance) to the specified texture coordinates. GL_NEAREST
    # "is generally faster than GL_LINEAR, but it can produce textured images
    # with sharper edges because the transition between texture elements is not
    # as smooth."

    # glDisable(GL_LIGHTING)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    setup_fog()
def optimize():
    try:
        pid = os.getpid()
        p = psutil.Process(pid)
        p.nice(-10)
    except:
        print("Optimisation did not work")


def main():
    width,height=pyautogui.size()
    window = Window(width, height, caption='Pyglet', resizable=True, fullscreen=True)
    # Hide the mouse cursor and prevent the mouse from leaving the window.
    optimize()
    window.set_exclusive_mouse(True)
    setup()
    pyglet.app.run()


if __name__ == '__main__':
    main()