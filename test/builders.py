from doublex import Spy, ANY_ARG
from hamcrest import ends_with

from twoboards import TwoBoards
from twoboards.client import TwoBoardsTrelloClient, Board, List, Card
from trello import Checklist, Label, TrelloClient


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
        http_service.request('GET', ends_with('dateLastActivity'), ANY_ARG).returns(FakeHttpResponse(200))

    trello_client = TrelloClient(api_key='an_api_key', token='a_token', http_service=http_service)
    twoboards_client = TwoBoardsTrelloClient(trello_client, 'a_product_board_id', 'a_tech_board_id')

    def _populate_twoboard_lists(board, list_atribute):

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

        for list_name, list_data in data[board.name].items():
            list = create_list(board, list_name)
            list_atribute[list_name] = list

            for card_name in list_data:
                list._cards.append(_create_card(list, card_name))

    twoboards = TwoBoards(twoboards_client, pipeline, pre_pipeline=pre_pipeline, post_pipeline=post_pipeline)

    twoboards._product_board = create_board(twoboards_client, 'product')
    twoboards._tech_board = create_board(twoboards_client, 'tech')

    twoboards._product_lists = {}
    _populate_twoboard_lists(twoboards._product_board, twoboards._product_lists)
    twoboards._tech_lists = {}
    _populate_twoboard_lists(twoboards._tech_board, twoboards._tech_lists)

    return twoboards


def create_board(trello_client, name):
    json_obj = {
        'id': 'a_board_id',
        'name': name,
        'closed': False,
        'url': 'an_url'
    }
    return Board.from_json(trello_client=trello_client, json_obj=json_obj)


def create_list(board, name):
    json_obj = {
        'id': 'a_list_id',
        'name': name,
        'closed': False,
        'pos': 'the_position'
    }
    list = List.from_json(board, json_obj)
    list._cards = []
    return list


def create_card(list, name, desc=None):
    json_obj = {
        'id': 'a_card_id',
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
        'idBoard': 'the_board_id',
        'idList': 'the_list_id',
        'idShort': 'the_id_short',
        'labels': [],
        'dateLastActivity': '2018-03-16T13:42:41.734Z'
    }
    card = Card.from_json(list, json_obj)
    card.contained._checklists = []
    return card


def create_label(client, name):
    return Label(client, 'a_label_id', name)


def create_checklist(trello_client, card, name, items):
    checked = False
    json_obj = {
        'id': 'a_checklist_id',
        'name': name,
        'idBoard': 'a_board_id',
        'idCard': 'a_card_id',
        'pos': 0,
        'checkItems': []
    }
    for item_name in items:
        json_obj['checkItems'].append({
            'state': 'incomplete',
            'idChecklist': 'a_checklist_id',
            'id': 'an_item_id',
            'name': item_name,
            'nameData': None,
            'pos': 0
        })
    return Checklist(trello_client, [], json_obj, trello_card=card.id)
