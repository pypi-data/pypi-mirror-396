# Taken from https://stately.ai/docs/state-machines-and-statecharts#parallel-states

Given the dog is waiting
When we leave home
Then the dog is on a walk

Given the dog is on a walk
And it's walking
When it speeds up
Then it's running

Given the dog is on a walk
And it's running
When it slows down
Then it's walking

Given the dog is on a walk
And its tail is not wagging
When the wagging starts
Then its tail is wagging

Given the dog is on a walk
And its tail is wagging
When the wagging stops
Then its tail is not wagging

Given the dog is on a walk
When we arrive home
Then the walk is complete
