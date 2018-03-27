from doublex import Stub, ANY_ARG

from twoboards import TwoBoards
from twoboards.client import Board, List, Card
from trello import Checklist


def create_twoboards(data, pipeline=None):
    with Stub() as trello_client:
        # Avoid to retrieve the last_activity when building the board
        trello_client.fetch_json(ANY_ARG).returns({'_value': None})

    def _populate_twoboard_lists(board, list_atribute):

        def _create_card(list, card_name):
            card = create_card(list, card_name)
            card_data = data[board.name][list.name][card_name]
            if 'checklists' in card_data and 'DoD' in card_data['checklists']:
                dod = create_checklist(trello_client, card, 'DoD', card_data['checklists']['DoD'])
                card.contained._checklists.append(dod)
            return card

        for list_name, list_data in data[board.name].items():
            list = create_list(board, list_name)
            list_atribute[list_name] = list

            for card_name in list_data:
                list._cards.append(_create_card(list, card_name))

    twoboards = TwoBoards(trello_client, pipeline=pipeline)

    twoboards._product_board = create_board(trello_client, 'product')
    twoboards._tech_board = create_board(trello_client, 'tech')

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
    # TODO pending the creation of the labels
    # labels = Label.from_json_list(card.board, json_obj['labels'])
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
