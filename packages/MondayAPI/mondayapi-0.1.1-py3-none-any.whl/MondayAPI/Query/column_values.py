from ._node import Node
from .columns import Columns


class ColumnValues(Node):
    def __init__(self, **kwargs):
            self.column = Columns(parent=self, name='column')
            self.id = Node(parent=self, name='id')
            self.text = Node(parent=self, name='text')
            self.type = Node(parent=self, name='type')
            self.value = Node(parent=self, name='value')
            self.title = Node(parent=self, name='title')

            super().__init__(**kwargs)
