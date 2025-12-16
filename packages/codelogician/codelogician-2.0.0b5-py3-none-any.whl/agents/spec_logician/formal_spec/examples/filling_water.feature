# From https://github.com/statelyai/xstate/blob/main/examples/workflow-filling-water/main.ts

Given I'm checking the glass' water level
And the water level is less than the maximum
When I inspect the water level
Then I proceed to add more water

Given I'm adding some water to the glass
When I add N units of water
Then the glass contains N more units of water
And I go back to check the glass's water level

Given I'm checking the glass' water level
And the water level is at the maximum
When I inspect the water level
Then I conclude that the glass is full
