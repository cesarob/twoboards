import sys
import argparse

from twoboards.client import TrelloClient
from twoboards import TwoBoards
from twoboards import Syncer
from twoboards.cli.console import print_table
from twoboards.config import API_KEY, TOKEN
from twoboards.cli.color import green, colorize_row, red


class TwoBoardsCli:
    def __init__(self, twoboards, syncer):
        self.twoboards = twoboards
        self.syncer = syncer

    def show(self):
        print()
        header = ['User Story', 'Task', 'Info']
        user_stories_state = self.twoboards.get_user_stories_state()
        # TODO if passed a verbose flag how the user_stories_state
        for status, user_stories in user_stories_state.items():
            rows = []
            for user_story in user_stories:
                info = _get_info(user_story)
                row = [user_story['name'], format_dod(user_story['dod']), info]
                if user_story['error']:
                    colorized_row = colorize_row(row, red)
                else:
                    colorized_row = colorize_row(row, green)
                rows.append(colorized_row)
            print_table(status, header, rows)

    def show_pre_pipeline():
        self._show_board(self.twoboards.get_pre_pipeline_state)

    def show_post_pipeline():
        self._show_board(self.twoboards.get_post_pipeline_state)

    def show_tech(self):
        self._show_board(self.twoboards.get_tech_orphan_tasks)

    def show_prod(self):
        self._show_board(self.twoboards.get_product_not_user_stories_tasks)

    def _show_board(self, callable):
        print()
        header = ['Task', 'Labels']
        orphan_tasks = callable()
        for status, tasks in orphan_tasks.items():
            rows = []
            for task in tasks:
                row = [task['name'], ', '.join(task['labels'])]
                rows.append(colorize_row(row, green))
            print_table(status, header, rows)

    def sync(self, dry_run):
        self.syncer.sync(dry_run)


def _get_info(user_story):
    # TODO make 'error' optional
    if user_story['error']:
        if user_story['error']['type'] == 'wrong_status':
            return "status is '{}' instead of '{}'".format(
                user_story['error']['actual'], user_story['error']['required']
            )
        elif user_story['error']['type'] == 'missing_dod_tasks':
            # TODO We just show first one in order to avoid a long message
            #      Otherwise we can break the table in the console
            #      Other option is to use the inner_row_border property in the table
            return "Missing Tasks: '{}'".format(user_story['error']['tasks'][0])
        else:
            return user_story['error']['type']

    return ''


def format_dod(dod):
    if not dod:
        return ''
    tasks = []
    for task in dod:
        tasks.append(task['name'])
    return "\n".join(tasks)


def create_cli():
    client = TrelloClient(
        api_key=API_KEY,
        api_secret=TOKEN
    )
    twoboards = TwoBoards(client)
    return TwoBoardsCli(twoboards, Syncer(twoboards))


cli = create_cli()


def show(args):
    if args.target == 'pipeline':
        cli.show()
    elif args.target == 'pre':
        cli.show_pre_pipeline()
    elif args.taget == 'post':
        cli.show_post_pipeline()
    elif args.target == 'tech':
        cli.show_tech()
    elif args.target == 'product':
        cli.show_prod()
    else:
        raise ValueError("Not supported 'target' for show operation")


def sync(args):
    cli.sync(args.dry_run)
    if args.show:
        class Args:
            target = 'pipeline'
        show(Args())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TwoBoards Client')
    subparsers = parser.add_subparsers(help='sub-command help')

    show_parser = subparsers.add_parser('show', help='Shows status')
    show_parser.add_argument('target', default='pipeline', nargs='?', choices=['pre', 'post', 'pipeline', 'tech', 'product'],
        help="Shows the tasks that are in the 'pipeline', or the ones that are outside the pipeline in 'tech' or " +
        "'product' boards")
    show_parser.set_defaults(func=show)

    sync_parser = subparsers.add_parser('sync', help='Syncs boards')
    sync_parser.add_argument('--dry-run', action='store_true', help="If provided the commands aren't executed")
    sync_parser.add_argument('--show', action='store_true', help="Shows pipeline status after a sync")
    sync_parser.set_defaults(func=sync)

    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit()
    args = parser.parse_args()
    args.func(args)
