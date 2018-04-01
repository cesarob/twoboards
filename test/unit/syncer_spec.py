from expects import *
from test.builders import create_twoboards
from twoboards.syncer import Syncer

with description("TwoBoards Sync"):

    with description("Tasks creation in tech board"):
        with it("creates missing User stories in tech board"):
            data = {
                'product': {
                    'Todo': {
                        'card1': {},
                    }
                },
                'tech': {
                    'Todo': {}
                }
            }
            syncer = Syncer(create_twoboards(data, pipeline=['Todo']))

            commands = syncer.sync(dry_run=True)
            expect(commands[0]).to(have_keys({
                'type': 'copy_user_story',
                'user_story': have_keys({
                    'name': 'card1',
                    'status': 'Todo',
                })
            }))

        with it("creates missing DoD tasks in tech board"):
            data = {
                'product': {
                    'Todo': {
                        'card1': {
                            'checklists': {
                                'DoD': ['Task1', 'Task2']
                            }
                        },
                    }
                },
                'tech': {
                    'Todo': {}
                }
            }
            syncer = Syncer(create_twoboards(data, pipeline=['Todo']))

            commands = syncer.sync(dry_run=True)
            expect(commands).to(have_len(2))
            expect(commands[0]).to(have_keys({
                'type': 'create_dod_task',
                'task': have_keys({
                    'name': 'Task1',
                    'status': 'Todo',
                })
            }))

    with description("Change of User Story state"):

        with it("changes its state when the User Story has changed in Tech board"):
            data = {
                'product': {
                    'Todo': {
                        'card1': {},
                    },
                    'Doing': {}
                },
                'tech': {
                    'Todo': {},
                    'Doing': {
                        'card1': {},
                    }
                }
            }
            syncer = Syncer(create_twoboards(data, pipeline=['Todo', 'Doing']))

            commands = syncer.sync(dry_run=True)
            expect(commands[0]).to(have_keys({
                'type': 'move_user_story',
                'user_story': have_keys({
                    'name': 'card1',
                    'status': 'Doing',
                })
            }))

        with it("changes its state because DoD tasks have changed their state"):
            data = {
                'product': {
                    'Todo': {
                        'card1': {
                            'checklists': {
                                'DoD': ['Task1', 'Task2']
                            }
                        },
                    },
                    'Doing': {}
                },
                'tech': {
                    'Todo': {
                        'Task1': {}
                    },
                    'Doing': {
                        'Task2': {},
                    }
                }
            }
            syncer = Syncer(create_twoboards(data, pipeline=['Todo', 'Doing']))

            commands = syncer.sync(dry_run=True)
            expect(commands[0]).to(have_keys({
                'type': 'move_user_story',
                'user_story': have_keys({
                    'name': 'card1',
                    'status': 'Doing',
                })
            }))
