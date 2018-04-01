# twoboards

Spike in order to be able to work with [Trello](https://trello.com/) with two boards.
I just wanted two experiment how to work with a couple of boards:

- A **product board**
- A **tech board**

So have in mind that this is an experiment and it is a **work in progress right now**, and for the flow I am trying.
The good thing about Trello and its api is that you could easily tune it to your own flow. I see Trello can be used
as a platform and with some effort you could implement your own flow.

So instead to adapt yourself to a tool you can implement a tooling adapted to a flow you have defined.

# Rationale
I have always worked with Trello with one board, but I assisted to a course and they mentioned that they were using two so
I wanted to give it a try.

The purpose is to have a Product Board with **User Stories** independent of a Tech Board, and then a **Tech Board** with tasks.
The problem I see in this is that I don't see it manageable. Or you automate it or there is no way you can manage it.

I want to have a simple solution so I am trying to avoid any external state. All the information needed for the process should be in Trello itself.
As synchronization is the main goal I have opted for a python implementation (instead of an extension for example) as I am more productive with python.

The idea is to have the sync command running periodically.

## Why two boards?
I see it interesting to have two as one is product focused and the stakeholders shouldn't need to have a look to tech one.
In tech board you could have not just *product tasks* but also other kind of tasks. It **facilitates to have a more clean product board**.


# How it works

**DISCLAIMER:** I am just describing actual version, but as I commented before this is a work in progress. Check *commit history* for a more fresh state of it.

Right now there is just a **cli** that can do a couple of things:

Show the status:
```
python cli.py show
```

Sync the boards:
```
python cli.py sync
```

Check the command help for additional help.


Product board pipeline gets sync with Tech Board (one way sync). The **pipeline** is the set of columns that you want to sync. You could have more columns in the boards and just the ones in the pipeline would be synced. If you want want to see what there is the other columns with the *cli* you can enumerate them as a *pre* or *post* pipeline.

It order to make it work properly all the changes of status in the cards should be done in the Tech Board.

## Running the client
In order to run it you need to set your environment (see [docker-compose.yml](https://github.com/cesarob/twoboards/blob/master/environment/dev/docker-compose.yml)) and enter in the container:

Lets assume you have an *environment/dev/env.sh*  file. Then you need to do:

```
source environment/dev/env.sh
make shell
```

Possible contents of the *env.sh* script:
```
export API_KEY="an_api_key"
export API_SECRET="an_api_secret"
export TOKEN="a_token"
export PRODUCT_BOARD_ID="a_product_board_id"
export TECH_BOARD_ID="a_tech_board_id"

# It is important to have a start and end states, from left to right.
# In other words we couldn't have: Todo, Doing, OnHold, Done
# Order matters
export PRE_PIPELINE="Backlog"
export PIPELINE="Todo, Doing, OnHold, Done"
export POST_PIPELINE="Archived"
```

In order to get the values for API_KEY, API_SECRET and TOKEN you can use the tools provided by [py-trello](https://github.com/sarumont/py-trello).
You can get the board ids using the **Print and Export** option in the board menu.

## User Stories
You define user stories that can have a Definition of Done (DoD) in the Product Board. You can have two kind of stories:
- Stories with a DoD (they should have at least two items to be considered a DoD)
- Stories without a DoD

When syncing boards stories without DoD are copyed to Tech Board.
When syncing boards stories with DoD get a Task created in Tech Board for each item of the DoD.

Product Board story gets updated with the changes of status in Tech Board.

As it is useful to have Cards in Product Board that don't get synced to Tech Board just a set of labels are considered for User Stories (right now hard coded in the code: US and Issue).

## Limitations and internals

Limitations:
- As I have mentioned all the changes in statuses should be done in Tech Board.
- Titles of tasks in tech board cannot be changed as the sync is made using the title

As syncs are done using User Stories if at some point you wish to break it, you just need to remove the label in the product board.

Imaging for example you wish to place some cards in *Todo* but don't wish to sync them. You can do it just postponing the setting of the label till the last moment.


# What could be next
I have several minor things in mind that I am not enumerating here, but probably one interesting change would be to implement a two way sync, so instead
of updating product board with tech one, one board would be updated with the changes in the other. Example: If you move a User Story to 'Done' in the product board all the related tasks in the Tech Board should be moved to 'Done'.

Example of things could be implemented: configurable user story labels, sync of comments, links between card, etc.


# Notes
- Python 3.6 is required

# Refs
- [Tello api](https://trello.readme.io/reference)
- [py-trello](https://github.com/sarumont/py-trello/)
