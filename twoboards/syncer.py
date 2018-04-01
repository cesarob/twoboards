from twoboards.log import logger
import json
import uuid


class Syncer:
    def __init__(self, twoboards):
        self.twoboards = twoboards

    def sync(self, dry_run=False):
        """Syncs product and tech board.

        :return: The applied commands
        """
        state = self.twoboards.get_user_stories_state()
        commands = []
        for status, user_stories in state.items():
            for user_story in user_stories:
                if user_story['error']:
                    if user_story['error']['type'] == 'missing':
                        commands.append({
                            'id': str(uuid.uuid4()),
                            'type': 'copy_user_story',
                            'user_story': {
                                'name': user_story['name'],
                                'id': user_story['id'],
                                'status': status,
                            }
                        })
                    elif user_story['error']['type'] == 'wrong_status':
                        commands.append({
                            'id': str(uuid.uuid4()),
                            'type': 'move_user_story',
                            'user_story': {
                                'name': user_story['name'],
                                'id': user_story['id'],
                                'status': user_story['error']['required'],
                            }
                        })
                    elif user_story['error']['type'] == 'missing_dod_tasks':
                        for task_name in user_story['error']['tasks']:
                            commands.append({
                                'id': str(uuid.uuid4()),
                                'type': 'create_dod_task',
                                'task': {
                                    'name': task_name,
                                    'status': status,
                                }
                            })
                    else:
                        logger.error('Not possible to generate a command for {}'.format(json.dumps(user_story)))

        if not dry_run:
            commands = self._apply_commands(commands)
        else:
            for command in commands:
                logger.info('Applying command: {}'.format(json.dumps(command)))

        return commands

    def _apply_commands(self, commands):
        applied_commands = []
        for command in commands:
            try:
                logger.info('Applying command: {}'.format(json.dumps(command)))
                getattr(self, '_' + command['type'])(command)
            except Exception as e:
                # TODO avoid a general exception handler here
                logger.exception('Error applying command {}: {}'.format(command['id'], str(e)))
            applied_commands.append(command)
        return applied_commands

    def _copy_user_story(self, command):
        list = self.twoboards.tech_board.get_list_by_name(command['user_story']['status'])
        list.copy_card(command['user_story']['id'])

    def _move_user_story(self, command):
        card = self.twoboards.product_board.get_card(command['user_story']['id'])
        target_list = self.twoboards.product_board.get_list_by_name(command['user_story']['status'])
        card.change_list(target_list.id)

    def _create_dod_task(self, command):
        list = self.twoboards.tech_board.get_list_by_name(command['task']['status'])
        card = list.add_card(command['task']['name'])
        dod_label = self.twoboards.tech_board.get_dod_label()
        card.add_label(dod_label)
