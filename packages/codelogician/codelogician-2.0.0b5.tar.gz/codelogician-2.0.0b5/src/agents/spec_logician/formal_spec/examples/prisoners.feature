# Taken from https://github.com/tlaplus/Examples/blob/master/specifications/Prisoners/Prisoners.tla

# Translate this Cucumber feature to Formal Feature.

Given no prisoner is visiting the room
When <count> is 2 * (number of prisoners - 1)
Then there are no more prisoners

Given no prisoner is visiting the room
When a prisoner with <id> is selected
Then the visiting prisoner is set to <id>
And the room is being visited

Given the romm is being visited
And the visitor is not the counter prisoner
When he performs a switch
And <switch A> is down
And this prisoner's counter is less than 2
Then he moves <switch A> up
And this prisoner's counter is incremented by one
And the room is not being visited anymore

Given the romm is being visited
And the visitor is not the counter prisoner
When he performs a switch
And either <switch A> up or his counter is >= 2
Then he flips <switch B>
And the room is not being visited anymore

Given the romm is being visited
And the visitor is the counter prisoner
When he performs a switch
And <switch A> is up
Then he moves <switch A> down
And <count> is incremented by 1
And the room is not being visited anymore

Given the romm is being visited
And the visitor is the counter prisoner
When he performs a switch
And <switch A> is down
Then he flips <switch B>
And the room is not being visited anymore

# Further instructions:
# - represent the two switches as boolean properties
# - use two states `empty` and `visited` for the `room` entity
# - keep track of each (non-counter) prisoner's count using a list of integers
# - use global properties for the counter prisoner's ID, and for the total number of prisoners
