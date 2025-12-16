class Node:
    """
    Represents a node in a hierarchical structure. A `Node` can have nested
    child Nodes, track its activation status, and maintain a reference to its
    parent, if any.

    Attributes:
        _fields (list[str]): Names of the attributes within this instance that
            are themselves `Node` objects. This is dynamically assigned in
            __init__.
        _active (bool): Indicates whether the Node is considered active.
        level (int): The depth level of the Node in the hierarchy (0-based).
    """

    def __init__(self, active: bool = False, parent: "Node" = None, name: str = ""):
        """
        Initialize a new Node instance.

        Args:
            active (bool, optional): Initial activation state of the Node.
                Defaults to False.
            parent (Node, optional): Parent Node in the hierarchy. If None,
                the Node is treated as a root. Defaults to None.
            name (str, optional): An alias or label for this Node. Default to an empty string.
        """
        self._active = active
        self._name = name
        self._parent = parent
        self._terminals = []
        self.level = 0

        # Dynamically determine which attributes are other Node instances.
        self._fields = [
            key for key, val in self.__dict__.items()
            if isinstance(val, Node) and key[0] != "_"
        ]

        self.arguments = {}

        # Increase the level of each child Node by 1 relative to this Node.
        for field in self._fields:
            child = self.__dict__[field]
            child.level = self.level + 1
            if child.is_terminal:
                self._terminals.append(field)

    def __iter__(self) -> iter:
        """
        Allow iteration over the names of child Nodes that are active.

        Yields:
            str: The attribute name of an active child Node.
        """
        for key in self._fields:
            if self.__dict__[key].active:
                yield key

    def __str__(self) -> str:
        """
        Return a string representation of the Node, including nested child Nodes.

        Returns:
            str: A formatted string that shows the Node's arguments (if any)
                 and recursively prints active child Nodes with indentation.
        """
        # Build a list of string representations of child Nodes
        fields = [key + str(self.__dict__[key]) for key in self]

        # Format the Node's arguments
        arguments = ', '.join([f'{key}: {val}' for key, val in self.arguments.items()])
        arguments = f'({arguments})' if arguments else ''

        # If the Node has child fields, format them with indentation
        if fields:
            tabs = '\t' * (self.level + 1)
            fields = f'\n{tabs}'.join(fields)
            return arguments + ' {' + f'\n{tabs}' + fields + '\n' + '\t' * self.level + '}'

        return ''

    def activate(self):
        """
        Activate this Node. If it has a parent, also activate the parent
        recursively to ensure the entire path up the hierarchy is active.
        """
        self._active = True
        if self._parent:
            self._parent.activate()

    def set(self, level=0):
        """
        Set the level (depth) of this Node and its active descendants.

        Args:
            level (int, optional): The new hierarchy level for this Node.
                Default to 0.
        """
        self.level = level
        for field in self:
            self.__dict__[field].set(level + 1)

    def copy_active(self, node: 'Node'):
        if self._name == node._name:
            for field in self._fields:
                self.__dict__[field].copy_active(node.__dict__[field])

        self._active = node._active

    @property
    def active(self) -> bool:
        """
        bool: Indicates whether this Node is currently active.
        """
        return self._active

    @property
    def parent(self) -> "Node":
        """
        Node: The parent Node of this Node, or None if this Node is a root.
        """
        return self._parent

    @property
    def alias(self) -> str:
        """
        str: An alias or label for this Node.
        """
        return self._name

    @property
    def is_terminal(self) -> bool:
        return len(self._fields) == 0
