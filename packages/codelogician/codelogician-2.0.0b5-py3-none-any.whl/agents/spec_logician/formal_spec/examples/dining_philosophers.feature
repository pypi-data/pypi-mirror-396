Translate this Cucumber feature to Formal Feature.

```
Given <philosopher> is thinking
When he tries to pick up forks
And the forks to his left and to his right are free
Then those forks are in use
And <philosopher> is eating

Given <philosopher> number N is eating
When he releases the forks
Then the forks to his left and to his right are free
And <philosopher> is thinking
```

Further instructions:
- there are 5 philosophers and 5 forks
- represent the philosophers as a list of booleans, where `true` means the philosopher is eating
- represent the forks and their free/occupied status as a list of booleans
- use a single entity 'table' with a single state 'ready'
