# Taken from https://github.com/tlaplus/Examples/blob/master/specifications/CoffeeCan/CoffeeCan.tla

Given there are at least two beans in the can
When I randomly select two beans from the can
And they are the same color
Then I throw them out
And put another black bean in

Given there are at least two beans in the can
When I randomly select two beans from the can
And they are different colors
Then I place the white one back into the can
And throw the black one away
