# from https://github.com/statelyai/xstate/blob/main/examples/todomvc-react/src/todosMachine.ts

# TODO: add scenario for filter.change event (needs enum support)
# TODO: implement markAll as a single action with parameterized filter (needs enum support)

Given I'm not adding a new TODO item
When I initiate the addition of a new TODO item
Then the "new item" field contains an empty string

Given I'm adding a new TODO item
When I type some characters on my keyboard
Then the "new item" field updates accordingly

Given I'm adding a new TODO item
When I commit the new item
Then it is inserted in the list of active TODO items
And I finish adding new TODO items

Given I'm not adding a new TODO item
And an item at position <index> exists in the completed list
When I delete it
Then that item is removed from the list

Given I'm not adding a new TODO item
And an item at position <index> exists in the active list
When I delete it
Then that item is removed from the list

Given I'm not adding a new TODO item
And an item at position <index> exists in the active list
When I mark it complete
Then that item is moved to the completed list

Given I'm not adding a new TODO item
And there are some active items
When I mark all items complete
Then all active items are moved to the completed list

Given I'm not adding a new TODO item
Given there are some completed items
When I mark all items active
Then all completed items are moved to the active list

Given I'm not adding a new TODO item
Given there are some completed items
When I clear all of them
Then there are no completed items
