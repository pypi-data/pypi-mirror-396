from ._node import Node
from .boards import Boards
from .items import Items
from .users import Users
import requests
from pathlib import Path
from ._datum import construct, Datum
from .next_items_page import NextItemsPage
from ..Exceptions import TokenEmptyError, TokenMissingError


def detect_token() -> str:
    """
    Tries to find a complete token file.
    Will produce a TokenMissingError or TokenEmptyError if the file does not exist or exists but is empty.
    :return: Token Value
    :rtype: str
    """
    here = Path(__file__).resolve().parent
    token = here / '__TOKEN__'

    if token.is_file():
        with token.open('r') as f:
            token_value = f.read()

        if token_value != '':
            return token_value

        else:
            raise TokenEmptyError

    with token.open('w') as f:
        f.write('')

    raise TokenMissingError


class Query(Node):
    url = 'https://api.monday.com/v2'

    def __init__(self):
        self.boards = Boards(parent=self, name='boards')
        self.items = Items(parent=self, name='items')
        self.users = Users(parent=self, name='users')
        self.next_items_page = NextItemsPage(parent=self, name='next_items_page')
        self.headers = {"Authorization": detect_token()}

        super().__init__(active=True, name='query')

    def __str__(self) -> str:
        return 'query ' + super().__str__()

    def _execute(self) -> requests.Response:
        payload = {'query': str(self)}
        response = requests.post(url=self.url, json=payload, headers=self.headers)

        return response

    def execute(self) -> Datum:
        return construct(self._execute().json())
