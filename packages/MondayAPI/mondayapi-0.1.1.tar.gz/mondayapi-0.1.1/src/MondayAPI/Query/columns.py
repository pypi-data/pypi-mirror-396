from ._node import Node


class Columns(Node):
    def __init__(self, **kwargs):
            self.archived = Node(parent=self, name='archived')
            self.description = Node(parent=self, name='description')
            self.id = Node(parent=self, name='id')
            self.settings_str = Node(parent=self, name='settings_str')
            self.title = Node(parent=self, name='title')
            self.type = Node(parent=self, name='type')
            self.width = Node(parent=self, name='width')

            super().__init__(**kwargs)
