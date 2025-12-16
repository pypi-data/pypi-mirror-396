from ._node import Node
from .items import Items


class NextItemsPage(Node):
    def __init__(self, **kwargs):
        self.cursor = Node(parent=self, name='cursor')
        self.items = Items(parent=self, name='items')

        super().__init__(**kwargs)
