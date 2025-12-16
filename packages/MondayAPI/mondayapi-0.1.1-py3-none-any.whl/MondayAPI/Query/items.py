from ._node import Node
from .subitems import SubItems
from .column_values import ColumnValues

class Items(Node):
    """
    Represents an Item object in Monday.com, with each field defined as a Node.

    Field References:
        assets (Node): The item's assets/files.
            - Supported arguments: assets_source (AssetsSource)
        board (Node): The board that contains the item.
        column_values (Node): The item's column values.
            - Supported arguments: ids (List of strings)
        column_values_str (Node): The item's string-formatted column values.
        created_at (Node): The item's creation date (Date).
        creator (Node): The user who created the item.
        creator_id (Node): The unique identifier of the item's creator.
        email (Node): The item's email.
        group (Node): The item's group.
        id (Node): The item's unique identifier (ID!).
        linked_items (Node): The item's linked items.
            - Supported arguments: linked_board_id (ID!), link_to_item_column_id (String!)
        name (Node): The item's name (String!).
        parent_item (Node): If this item is a subitem, its parent. Otherwise, null.
        relative_link (Node): The item's relative path (String).
        state (Node): The item's state (Enum: active, all, archived, deleted).
        subitems (Node): A list of subitems (Items).
        subscribers (Node): The item's subscribers (list of Users).
        updated_at (Node): The date the item was last updated (Date).
        updates (Node): The item's updates.
            - Supported arguments: limit (Int), page (Int)
        url (Node): The item's URL (String!).

    Usage Example:
        item = Items()
        # To add arguments for a field (e.g., 'updates'), you could do:
        # item.updates.arguments['limit'] = 10
        # item.updates.arguments['page'] = 2
    """

    def __init__(self, **kwargs):
        # Fields from your table
        self.assets = Node(parent=self, name='assets')
        self.board = Node(parent=self, name='board')
        self.column_values = ColumnValues(parent=self, name='column_values')
        self.column_values_str = Node(parent=self, name='column_values_str')
        self.created_at = Node(parent=self, name='created_at')
        self.creator = Node(parent=self, name='creator')
        self.creator_id = Node(parent=self, name='creator_id')
        self.email = Node(parent=self, name='email')
        self.group = Node(parent=self, name='group')
        self.id = Node(parent=self, name='id')
        self.linked_items = Node(parent=self, name='linked_items')
        self.name = Node(parent=self, name='name')
        self.parent_item = Node(parent=self, name='parent_item')
        self.relative_link = Node(parent=self, name='relative_link')
        self.state = Node(parent=self, name='state')
        self.subitems = SubItems(parent=self, name='subitems')
        self.subscribers = Node(parent=self, name='subscribers')
        self.updated_at = Node(parent=self, name='updated_at')
        self.updates = Node(parent=self, name='updates')
        self.url = Node(parent=self, name='url')

        # Call the base class constructor to finalize the setup
        super().__init__(**kwargs)
