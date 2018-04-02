from expects import *
from test.builders import create_twoboards

with description("TwoBoards State"):
    with description('Basic User Stories info'):
        with it('shows the User Stories'):
            data = {
                'product': {
                    'Todo': {
                        '1st_card': {'labels': ['US']},
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
                            'labels': ['US'],
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

    with description("Additional visualizations"):

        with it("shows non user story cards in product board"):
            data = {
                'product': {
                    'Todo': {
                        'card1': {
                            'labels': ['US']
                        },
                        'card2': {}
                    }
                },
                'tech': {
                    'Todo': {}
                }
            }
            twoboards = create_twoboards(data, pipeline=['Todo'])
            non_us_tasks = twoboards.get_product_not_user_stories_tasks()
            expect(non_us_tasks['Todo']).to(be_a(list))
            expect(non_us_tasks['Todo']).to(have_len(1))
            expect(non_us_tasks['Todo'][0]['name']).to(equal('card2'))

        with it("shows orphan tasks in tech board"):
            data = {
                'product': {
                    'Todo': {}
                },
                'tech': {
                    'Todo': {
                        'card1': {}
                    }
                }
            }
            twoboards = create_twoboards(data, pipeline=['Todo'])
            orphan_tasks = twoboards.get_tech_orphan_tasks()
            expect(orphan_tasks['Todo']).to(be_a(list))
            expect(orphan_tasks['Todo']).to(have_len(1))
            expect(orphan_tasks['Todo'][0]['name']).to(equal('card1'))

        with it("show pre pipeline tasks"):
            data = {
                'product': {
                    'Backlog': {
                        'card1': {},
                    },
                    'Todo': {}
                },
                'tech': {}
            }
            twoboards = create_twoboards(data, pre_pipeline=['Backlog'], pipeline=['Todo'])

            state = twoboards.get_pre_pipeline_state()
            expect(state['Backlog']).to(be_a(list))
            expect(state['Backlog']).to(have_len(1))
            expect(state['Backlog'][0]['name']).to(equal('card1'))

        with it("shows post pipeline tasks"):
            data = {
                'product': {
                    'Todo': {},
                    'Archived': {
                        'card1': {},
                    },
                },
                'tech': {}
            }
            twoboards = create_twoboards(data, pipeline=['Todo'], post_pipeline=['Archived'], )

            state = twoboards.get_post_pipeline_state()
            expect(state['Archived']).to(be_a(list))
            expect(state['Archived']).to(have_len(1))
            expect(state['Archived'][0]['name']).to(equal('card1'))

    with description('Inconsistent user story states between boards'):

        with it('detects a missing user story'):
            data = {
                'product': {
                    'Todo': {
                        '1st_card': {'labels': ['US']},
                        '2nd_card': {'labels': ['US']}
                    }
                },
                'tech': {
                    'Todo': {
                        '1st_card': {'labels': ['US']},
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
                        '1st_card': {'labels': ['US']},
                        '2nd_card': {'labels': ['US']}
                    },
                    'Doing': {
                    }
                },
                'tech': {
                    'Todo': {
                        '1st_card': {'labels': ['US']},
                    },
                    'Doing': {
                        '2nd_card': {'labels': ['US']}
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
                            'labels': ['US'],
                            'checklists': {
                                'DoD': ['Task1']
                            }
                        }
                    }
                },
                'tech': {
                    'Todo': {
                        'card1': {'labels': ['US']},
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
                            'labels': ['US'],
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
                            'labels': ['US'],
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
