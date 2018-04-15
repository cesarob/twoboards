from doublex import Spy, ANY_ARG
from hamcrest import ends_with

import json
from twoboards import TwoBoards
from twoboards.client import TwoBoardsTrelloClient, Board, List, Card
from trello import Checklist, Label, TrelloClient


class HttpStubResponse:
    def __init__(self, response_text, status_code=200, headers=None):
        self.text = response_text
        self.status_code = status_code
        self.content = self.text
        self.headers = headers if headers else {}

    def raise_for_status(self):
        if 400 <= self.status_code < 600:
            raise HttpRequestError()

    def json(self):
        return json.loads(self.text)


def create_twoboards(data, pre_pipeline=None, pipeline=None, post_pipeline=None):
    class FakeHttpResponse:

        def __init__(self, status_code, data='', headers=[]):
            self.status_code = status_code
            self.headers = headers
            self.data = data.encode(encoding='UTF-8', errors='strict')

        def json(self):
            return {'_value': None}

    with Spy() as http_service:
        # Avoid to retrieve the last_activity when building the board
        # TODO use HttpStubResponse
        http_service.request('GET', ends_with('dateLastActivity'), ANY_ARG).returns(FakeHttpResponse(200))

    trello_client = TrelloClient(api_key='an_api_key', token='a_token', http_service=http_service)
    twoboards_client = TwoBoardsTrelloClient(trello_client, 'a_product_board_id', 'a_tech_board_id')

    def _populate_twoboard_lists(board):

        def _create_card(list, card_name):
            card = create_card(list, card_name)
            card_data = data[board.name][list.name][card_name]
            if 'checklists' in card_data and 'DoD' in card_data['checklists']:
                dod = create_checklist(twoboards_client, card, 'DoD', card_data['checklists']['DoD'])
                card.contained._checklists.append(dod)
            if 'labels' in card_data:
                for label in card_data['labels']:
                    card.labels.append(create_label(twoboards_client, label))
            return card

        board._lists = {}
        for list_name, list_data in data[board.name].items():
            list = create_list(board, list_name)
            board._lists[list_name] = list

            for card_name in list_data:
                list._cards.append(_create_card(list, card_name))

    twoboards = TwoBoards(twoboards_client, pipeline, pre_pipeline=pre_pipeline, post_pipeline=post_pipeline)

    twoboards._product_board = create_board(twoboards_client, 'product')
    twoboards._tech_board = create_board(twoboards_client, 'tech')

    _populate_twoboard_lists(twoboards._product_board)
    _populate_twoboard_lists(twoboards._tech_board)

    return twoboards


def create_board(trello_client, name):
    board_id = 'id_' + name
    json_obj = {
        'id': board_id,
        'name': name,
        'closed': False,
        'url': 'an_url'
    }
    http_service = trello_client.http_service
    with http_service:
        http_service.request('GET', ends_with('/boards/{}'.format(board_id)), ANY_ARG).returns(
            HttpStubResponse(json.dumps(json_obj))
        )
    return Board.from_json(trello_client=trello_client, json_obj=json_obj)


def create_list(board, name):
    list_id = 'id_' + name
    json_obj = {
        'id': list_id,
        'name': name,
        'closed': False,
        'pos': 'the_position'
    }
    list = List.from_json(board, json_obj)
    list._cards = []

    http_service = board.client.http_service
    with http_service:
        http_service.request('GET', ends_with('/lists/{}'.format(list_id)), ANY_ARG).returns(
            HttpStubResponse(json.dumps(json_obj))
        )
    return list


def create_card(list, name, desc=None):
    card_id = 'id_' + name
    json_obj = {
        'id': card_id,
        'name': name,
        'desc': desc,
        'dueComplete': False,
        'closed': False,
        'url': 'a_card_url',
        'pos': 'the_card_position',
        'shortUrl': 'https://trello.com/c/the_id_short',
        'idMembers': [],
        'member_ids': [],
        'idLabels': [],
        'idBoard': list.board.id,
        'idList': list.id,
        'idShort': card_id,
        'labels': [],
        'dateLastActivity': '2018-03-16T13:42:41.734Z',
        'badges': None,
        'checkItemStates': []
    }
    card = Card.from_json(list, json_obj)
    card.contained._checklists = []

    http_service = list.client.http_service
    with http_service:
        http_service.request('GET', ends_with('/cards/{}'.format(card_id)), ANY_ARG).returns(
            HttpStubResponse(json.dumps(json_obj))
        )

    # We need to hack this, as as we are using our own instances of List that doesn't inherit from List
    # Ref: https://github.com/sarumont/py-trello/blob/master/trello/card.py#L126-L127
    card.trello_list = list
    card.board = list.board

    return card


def create_label(client, name):
    return Label(client, 'a_label_id', name)


def create_checklist(trello_client, card, name, items):
    checked = False
    id = 'id_' + name
    json_obj = {
        'id': id,
        'name': name,
        'idBoard': card.board.id,
        'idCard': card.id,
        'pos': 0,
        'checkItems': []
    }
    for item_name in items:
        json_obj['checkItems'].append({
            'state': 'incomplete',
            'idChecklist': id,
            'id': 'id_' + item_name,
            'name': item_name,
            'nameData': None,
            'pos': 0
        })

    # We can do it here as we are just creating a checklist, the DoD
    http_service = card.client.http_service
    with http_service:
        http_service.request('GET', ends_with('cards/id_card1/checklists'.format(card.id)), ANY_ARG).returns(
            HttpStubResponse(json.dumps([json_obj]))
        )

    return Checklist(trello_client, [], json_obj, trello_card=card.id)
