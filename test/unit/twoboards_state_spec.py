from expects import *
from test.builders import create_twoboards

with description("TwoBoards State"):
    with description('Basic User Stories info'):
        with it('shows the User Stories'):
            data = {
                'product': {
                    'Todo': {
                        '1st_card': {},
                    }
                },
                'tech': {}
            }
            twoboards = create_twoboards(data, pipeline=['Todo'])

            state = twoboards.get_user_stories_state()

            expect(state['Todo']).to(be_a(list))
            expect(state['Todo']).to(have_len(1))
            expect(state['Todo'][0]['name']).to(equal('1st_card'))

        with it('shows the Definition of Done'):
            data = {
                'product': {
                    'Todo': {
                        '1st_card': {
                            'checklists': {
                                'DoD': ['Task1', 'Task2']
                            }
                        }
                    }
                },
                'tech': {}
            }
            twoboards = create_twoboards(data, pipeline=['Todo'])

            state = twoboards.get_user_stories_state()

            expect(state['Todo']).to(be_a(list))
            expect(state['Todo']).to(have_len(1))
            expect(state['Todo'][0]['dod']).to(be_a(list))
            expect(state['Todo'][0]['dod']).to(have_len(2))
            expect(state['Todo'][0]['dod'][0]['name']).to(equal('Task1'))
            expect(state['Todo'][0]['dod'][1]['name']).to(equal('Task2'))

    with description('Inconsistent user story states between boards'):

        with it('detects a missing user story'):
            data = {
                'product': {
                    'Todo': {
                        '1st_card': {},
                        '2nd_card': {}
                    }
                },
                'tech': {
                    'Todo': {
                        '1st_card': {},
                    }
                }
            }

            twoboards = create_twoboards(data, pipeline=['Todo'])
            state = twoboards.get_user_stories_state()
            expect(state['Todo'][1]['error']['type']).to(equal('missing'))

        with it('detects a user story in a different status'):
            data = {
                'product': {
                    'Todo': {
                        '1st_card': {},
                        '2nd_card': {}
                    },
                    'Doing': {
                    }
                },
                'tech': {
                    'Todo': {
                        '1st_card': {},
                    },
                    'Doing': {
                        '2nd_card': {}
                    }
                }
            }

            twoboards = create_twoboards(data, pipeline=['Todo', 'Doing'])
            state = twoboards.get_user_stories_state()
            expect(state['Todo'][1]['error']).to(have_keys(
                {'type': 'wrong_status', 'actual': 'Todo', 'required': 'Doing'})
            )

    with description('DoD management'):
        with it("manages DoD with one element as a normal User Story"):
            data = {
                'product': {
                    'Todo': {
                        'card1': {
                            'checklists': {
                                'DoD': ['Task1']
                            }
                        }
                    }
                },
                'tech': {
                    'Todo': {
                        'card1': {},
                    }
                }
            }

            twoboards = create_twoboards(data, pipeline=['Todo'])
            state = twoboards.get_user_stories_state()
            expect(state['Todo'][0]['error']).to(be_none)

        with it("does'nt report anything when a DoD task is in the tech board"):
            data = {
                'product': {
                    'Todo': {
                        '1st_card': {
                            'checklists': {
                                'DoD': ['Task1', 'Task2']
                            }
                        }
                    }
                },
                'tech': {
                    'Todo': {
                        'Task1': {},
                        'Task2': {}
                    }
                }
            }

            twoboards = create_twoboards(data, pipeline=['Todo'])
            state = twoboards.get_user_stories_state()
            expect(state['Todo'][0]['error']).to(be_none)

        with it('reports a missing DoD taks'):
            data = {
                'product': {
                    'Todo': {
                        '1st_card': {
                            'checklists': {
                                'DoD': ['Task1', 'Task2']
                            }
                        }
                    }
                },
                'tech': {
                    'Todo': {}
                }
            }

            twoboards = create_twoboards(data, pipeline=['Todo'])
            state = twoboards.get_user_stories_state()
            expect(state['Todo'][0]['error']).to(have_keys(
                {'type': 'missing_dod_tasks', 'tasks': ['Task1', 'Task2']}
            ))
