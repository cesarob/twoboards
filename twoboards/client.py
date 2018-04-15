from trello import Board as _Board
from trello import Card as _Card
from trello import List as _List

LABEL_DOD = 'DoD'
LABEL_COLOR = 'purple'

USER_STORY_LABELS = ['US', 'Issue']


class Wrapper:
    """Allows to tune wrapped classes

    Non defined methods are proxixed to contained instance
    """
    def __init__(self, contained):
        self.contained = contained

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            return getattr(self.contained, item)


class Board(Wrapper):
    def __init__(self, contained):
        super().__init__(contained)
        self._lists = None
        self._labels = None

    def _get_lists(self):
        if self._lists is None:
            self._lists = {}
            # TODO check if we can optimize the call in order to avoid to retrieve all the lists as we need
            #      to check if the list is closed or not
            for list in self.all_lists():
                if not list.closed:
                    self._lists[list.name] = List(list)
        return self._lists

    def _get_labels(self):
        if self._labels is None:
            self._labels = {}
            for label in self.get_labels():
                self._labels[label.name] = label
        return self._labels

    def add_label(self, name, color):
        if name not in self._get_labels():
            label = self.contained.add_label(name, color)
            self._labels[name] = label
        return self._labels[name]

    def get_list(self, list_id):
        list = self.contained.get_list(list_id)
        return List(list)

    def get_list_by_name(self, name):
        lists = self._get_lists()
        for key in lists.keys():
            if key.startswith(name):
                return lists[key]
        return None

    def get_card(self, id):
        """Returns a card
        :id: The id of the card
        :return: Card
        """
        # TODO make PR to py-trello
        json_obj = self.client.fetch_json(
            '/boards/' + self.id + '/cards/' + id
        )
        parent = self.get_list(json_obj['idList'])
        return Card.from_json(parent, json_obj)

    @classmethod
    def from_json(cls, trello_client=None, organization=None, json_obj=None):
        return Board(_Board.from_json(trello_client=trello_client, organization=organization, json_obj=json_obj))


class TechBoard(Board):
    def get_dod_label(self):
        if LABEL_DOD not in self._get_labels():
            label = self.add_label(LABEL_DOD, LABEL_COLOR)
        return self._labels[LABEL_DOD]


class List(Wrapper):
    def __init__(self, contained):
        super().__init__(contained)
        self._cards = None

    def _get_cards(self):
        if self._cards is None:
            self._cards = []
            for card in self.list_cards():
                # it is not retrieving archived chards
                self._cards.append(Card(card))
        return self._cards

    def get_cards(self):
        return self._get_cards()

    def copy_card(self, idCard):
        """Copies a card into the list

        :id_card: The id of the card to copy into this list
        :return: the card
        """
        # TODO add_card allows to copy a card but it doesn't copy all the data, so we
        #      are adding this new operation to make usage of keepFromSource parameter.
        #      We should make a PR to py-trello in order to add that parameter
        post_args = {
            'idList': self.id,
            'idCardSource': idCard,
            'keepFromSource': 'all'
        }

        json_obj = self.client.fetch_json(
            '/cards',
            http_method='POST',
            post_args=post_args)
        return self.from_json(self, json_obj)

    @classmethod
    def from_json(cls, board, json_obj):
        return List(_List.from_json(board, json_obj))


class Card(Wrapper):
    def __init__(self, contained):
        super().__init__(contained)

    @property
    def definition_of_done(self):
        """Returns Definition of Done if present"""
        # TODO Issue https://github.com/sarumont/py-trello/issues/93
        # We need to call it twice
        self.contained.checklists
        if self.contained.checklists:
            for checklist in self.contained.checklists:
                if checklist.name == 'DoD':
                    if len(checklist.items) > 1:
                        return checklist.items
        return []

    @property
    def is_user_story(self):
        for label in self.contained.labels:
            if label.name in USER_STORY_LABELS:
                return True
        return False

    @classmethod
    def from_json(cls, parent, json_obj):
        return Card(_Card.from_json(parent, json_obj))


class TwoBoardsTrelloClient(Wrapper):
    """Tuned version of TrelloClient for TwoBoards"""

    def __init__(self, trello_client, product_board_id, tech_board_id):
        super().__init__(trello_client)
        self.product_board_id = product_board_id
        self.tech_board_id = tech_board_id
        self._boards = None

    def _get_boards(self):
        if self._boards is None:
            self._boards = self.contained.list_boards()
        return self._boards

    def get_board_by_name(self, name):
        # TODO find a way to avoid the retrieval of all boards
        for board in self._get_boards():
            if board.name.startswith(name):
                return Board(board)
        return None

    def get_board(self, board_id):
        board = self.contained.get_board(board_id)
        return Board(board)

    def get_product_board(self):
        return self.get_board(self.product_board_id)

    def get_tech_board(self):
        board = self.get_board(self.tech_board_id)
        return TechBoard(board)
