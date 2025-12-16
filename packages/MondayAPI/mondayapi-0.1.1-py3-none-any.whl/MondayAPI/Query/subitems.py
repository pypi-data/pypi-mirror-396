from ._node import Node
from .column_values import ColumnValues

class SubItems(Node):
    def __init__(self, **kwargs):
        self.assets = Node(parent=self, name='assets')
        self.board = Node(parent=self, name='board')
        self.column_values  = ColumnValues(parent=self, name='column_values')
        self.created_at  = Node(parent=self, name='created_at')
        self.creator_id  = Node(parent=self, name='creator_id')
        self.email  = Node(parent=self, name='email')
        self.group  = Node(parent=self, name='group')
        self.id  = Node(parent=self, name='id')
        self.name  = Node(parent=self, name='name')
        self.parent_item  = Node(parent=self, name='parent_item')
        self.relative_link  = Node(parent=self, name='relative_link')
        self.subscribers  = Node(parent=self, name='subscribers')
        self.updated_at  = Node(parent=self, name='updated_at')
        self.updates  = Node(parent=self, name='updates')

        super().__init__(**kwargs)