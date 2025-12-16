from ._node import Node
from .items_page import ItemsPage
from .columns import Columns

class Boards(Node):
    def __init__(self, **kwargs):
        self.activity_logs = Node(parent=self, name='activity_logs')
        self.board_folder_id = Node(parent=self, name='board_folder_id')
        self.board_kind = Node(parent=self, name='board_kind')
        self.columns = Columns(parent=self, name='columns')
        self.communication = Node()
        self.creator = Node()
        self.description = Node()
        self.groups = Node()
        self.id = Node(parent=self, name='id')
        self.item_terminology = Node()
        self.items_count = Node()
        self.items_page = ItemsPage(parent=self, name='items_page')
        self.name = Node(parent=self, name='name')
        self.owners = Node()
        self.permissions = Node()
        self.state = Node()
        self.subscribers = Node()
        self.tags = Node()
        self.team_owners = Node()
        self.team_subscribers = Node()
        self.top_group = Node()
        self.type = Node()
        self.updated_at = Node()
        self.updates = Node()
        self.url = Node()
        self.views = Node()
        self.workspace = Node()
        self.workspace_id = Node()

        super().__init__(**kwargs)





