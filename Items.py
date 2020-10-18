import pyglet

class Item:
    def __init__(self,  id,item_name, icon,dur=-1, stack_size=64,name=None):
        self.durability = dur
        self.stack_size = stack_size
        self.name = name
        self.id = id
        self.item_name = item_name
        self.icon = pyglet.image.load(icon)

    # def set_icon(self, icon):
    #     self.icon = icon


    def get_icon(self):
        return self.icon

# class BlockItem(Item):
#     def __init__(self, *args, **kwargs):
#         super(BlockItem, self).__init__(*args, **kwargs)
        # pass