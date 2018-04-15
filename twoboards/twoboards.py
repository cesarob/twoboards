import sys
from collections import defaultdict

from .syncer import Syncer


class TwoBoards:
    def __init__(self, client, pipeline, pre_pipeline=None, post_pipeline=None):
        self.client = client

        self.pipeline = pipeline
        self.pre_pipeline = pre_pipeline if pre_pipeline else []
        self.post_pipeline = post_pipeline if post_pipeline else []
        self.full_pipeline = self.pre_pipeline + self.pipeline + self.post_pipeline

        self._product_board = None
        self._tech_board = None
        self._product_lists = None
        self._tech_lists = None

        self.syncer = Syncer(self.client)

    def _init_boards(self):
        self._product_board = self.client.get_product_board()
        self._tech_board = self.client.get_tech_board()

        if self._tech_board is None:
            raise Exception("Tech board not found. Id: {}".format(TECH_BOARD_ID))

        if self._product_board is None:
            raise Exception("Product board not found. Id: {}".format(PRODUCT_BOARD_ID))

    def _init_lists(self, board):
        result = {}
        for name in self.pipeline:
            column = board.get_list_by_name(name)
            if column is None:
                raise Exception("List {} not found in board".format(name, board.name))
            result[name] = column
        return result

    @property
    def product_board(self):
        if self._product_board is None:
            self._init_boards()
        return self._product_board

    @property
    def tech_board(self):
        if self._tech_board is None:
            self._init_boards()
        return self._tech_board

    @property
    def product_lists(self):
        if self._product_lists is None:
            self._product_lists = self._init_lists(self.product_board)
        return self._product_lists

    @property
    def tech_lists(self):
        if self._tech_lists is None:
            self._tech_lists = self._init_lists(self.tech_board)
        return self._tech_lists

    def get_user_stories_by_status(self, status):
        user_stories = []
        for card in self.get_product_cards_by_status(status):
            if card.is_user_story:
                user_stories.append(card)
        return user_stories

    def get_product_cards_by_status(self, status):
        column = self.product_lists[status]
        return column.get_cards()

    def get_tech_cards_by_status(self, status):
        column = self.tech_lists[status]
        return column.get_cards()

    def get_user_story_by_name(self, name):
        for status in self.pipeline:
            for card in self.get_user_stories_by_status(status):
                if card.name == name:
                    return card
        return None

    def _check_user_story_in_tech(self, status, name):
        # TODO
        #   - we should check that the label is 'US'
        #   - move this stuff to board (locate card with some conditions)
        found = None
        for tech_status in self.pipeline:
            if tech_status in self.tech_lists:
                for card in self.tech_lists[tech_status].get_cards():
                    if card.name.find(name) != -1:
                        found = card
                        break
                if found:
                    break
            if found:
                break

        return 'missing' if found is None else tech_status

    def _check_dod_task_in_tech(self, name):
        # TODO
        #   - refactor as it is a similar implementation than _check_user_story_in_tech
        found = None
        for tech_status in self.pipeline:
            if tech_status in self.tech_lists:
                for card in self.tech_lists[tech_status].get_cards():
                    if card.name.find(name) != -1:
                        found = card
                        break
                if found:
                    break
            if found:
                break
        return 'missing' if found is None else tech_status

    def get_tech_orphan_tasks_report(self):
        result = {}
        for status in self.pipeline:
            result[status] = []
            for card in self.get_tech_cards_by_status(status):
                labels = [label.name for label in card.labels]
                if not ('DoD' in labels or 'US' in labels or 'Issue' in labels):
                    result[status].append({
                        'name': card.name,
                        'labels': labels
                    })
        return result

    def get_product_not_user_stories_tasks_report(self):
        result = {}
        for status in self.pipeline:
            result[status] = []
            for card in self.get_product_cards_by_status(status):
                if not card.is_user_story:
                    result[status].append({
                        'name': card.name,
                        'labels': [label.name for label in card.labels]
                    })
        return result

    def get_user_stories_without_updated_dod_task_report(self):
        result = []
        for status in self.pipeline:
            for card in self.get_product_cards_by_status(status):
                if card.is_user_story and card.definition_of_done:
                    for item in card.definition_of_done.items:
                        status = self._check_dod_task_in_tech(item['name'])
                        if status == 'Done':
                            if item['state'] == 'incomplete':
                                result.append({
                                    'user_story': {
                                        'name': card.name,
                                        'id': card.id
                                    },
                                    'task': item['name'],
                                    'expected_state': 'complete'
                                })
                        elif item['state'] == 'complete':
                            result.append({
                                'user_story': {
                                    'name': card.name,
                                    'id': card.id
                                },
                                'task': item['name'],
                                'expected_state': 'incomplete'
                            })
        return result

    def get_pre_pipeline_state(self):
        """Report with cards of the pre pipeline"""
        result = {}
        for status in self.pre_pipeline:
            result[status] = []
            for card in self.get_product_cards_by_status(status):
                labels = [label.name for label in card.labels]
                result[status].append({
                    'name': card.name,
                    'labels': [label.name for label in card.labels]
                })
        return result

    def get_post_pipeline_state(self):
        """Report with cards of the post pipeline"""
        result = {}
        for status in self.post_pipeline:
            result[status] = []
            for card in self.get_product_cards_by_status(status):
                result[status].append({
                    'name': card.name,
                    'labels': [label.name for label in card.labels]
                })
        return result

    def get_user_stories_state(self):
        """Report with the status of the user stories"""
        def us_error(status, tech_state):
            if tech_state == 'missing':
                return {'type': 'missing'}
            if status == tech_state:
                return None
            else:
                return {
                    'type': 'wrong_status',
                    'actual': status,
                    'required': tech_state
                }

        def dod_error(status, user_story):
            missing_tasks = []
            # TODO hardcoded for my actual statuses
            #      I need to thing if we can implement a general algorith. If no we just force this statuses
            #      and we just allow to have pre and post pipeline statuses but not the one in the pipeline
            pos_tasks = {'Todo': 0, 'Doing': 0, 'OnHold': 0, 'Acceptance': 0, 'Done': 0}

            for task in user_story['dod']:
                if task['state'] == 'missing':
                    missing_tasks.append(task['name'])
                else:
                    pos_tasks[task['state']] += 1

            if missing_tasks:
                return {
                    'type': 'missing_dod_tasks',
                    'tasks': missing_tasks
                }
            else:
                required_status = None
                for task_status, num in pos_tasks.items():
                    if task_status == 'Doing' and num:
                        required_status = task_status
                    if num == len(user_story['dod']):
                        required_status = task_status
                        break
                if required_status is None:
                    required_status = 'Doing'
                if required_status != status:
                    return {
                        'type': 'wrong_status',
                        'actual': status,
                        'required': required_status
                    }
            return None

        result = {}
        for status in self.pipeline:
            result[status] = []
            for card in self.get_user_stories_by_status(status):
                user_story = {
                    'name': card.name,
                    'id': card.id,
                    'dod': [],
                    'error': None
                }
                if card.definition_of_done:
                    for item in card.definition_of_done.items:
                        user_story['dod'].append({
                            'name': item['name'],
                            'state': self._check_dod_task_in_tech(item['name'])
                        })
                    user_story['error'] = dod_error(status, user_story)
                else:
                    tech_state = self._check_user_story_in_tech(status, card.name)
                    user_story['error'] = us_error(status, tech_state)
                result[status].append(user_story)
        return result
