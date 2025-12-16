from ._node import Node

class Users(Node):
    """
    Represents a collection of users in Monday.com, with each field initialized
    as a Node for hierarchical and recursive data management.

    Attributes:
        id (Node): Unique identifier of the user.
        name (Node): The user's name as displayed in Monday.com.
        email (Node): The user's email address.
        enabled (Node): Indicates if the user is active in Monday.com.
        kind (Node): The type of user (e.g., 'regular', 'guest').
        is_guest (Node): Whether the user is a guest.
        is_pending (Node): Whether the user has not yet accepted the invite.
        created_at (Node): The date/time the user account was created.
        url (Node): Link to the user's profile in Monday.com.
        teams (Node): Teams that the user is part of (if applicable).
    """

    def __init__(self, **kwargs):
        # Basic user fields
        self.id = Node(parent=self, name='id')
        self.name = Node(parent=self, name='name')
        self.email = Node(parent=self, name='email')
        self.enabled = Node(parent=self, name='enabled')
        self.kind = Node(parent=self, name='kind')
        self.is_guest = Node(parent=self, name='is_guest')
        self.is_pending = Node(parent=self, name='is_pending')
        self.created_at = Node(parent=self, name='created_at')
        self.url = Node(parent=self, name='url')

        # Example of referencing a list of teams or other nested objects
        self.teams = Node(parent=self, name='teams')

        # Call the base class constructor last to initialize fields and level
        super().__init__(**kwargs)
