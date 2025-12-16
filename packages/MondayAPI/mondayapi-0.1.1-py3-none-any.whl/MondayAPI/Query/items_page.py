from ._node import Node
from .items import Items

class ItemsPage(Node):
    def __init__(self, **kwargs):
        self.items = Items(parent=self, name='items')
        self.cursor = Node(parent=self, name='cursor')

        super().__init__(**kwargs)
