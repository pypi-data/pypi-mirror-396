# Taken from https://github.com/statelyai/xstate/blob/main/examples/tic-tac-toe-react/src/ticTacToeMachine.ts

# Translate this Cucumber feature to Formal Feature.

```
Given the tic-tac-toe game is ongoing
When <player> makes a move
And it's <player>'s turn
And the move is valid
Then the game board is updated to reflect the move
And we proceed to perform post-move checks

Given we are running post-move checks
When we check for a winner
And the game board shows player 1 is the winner
Then player 1 is declared winner
And the game ends

Given we are running post-move checks
When we check for a winner
And the game board shows player 2 is the winner
Then player 1 is declared winner
And the game ends

Given we are running post-move checks
When we check for a winner
And the game board shows a draw
Then the game ends

Given we are running post-move checks
When we check for a winner
And the game board does not show a win or draw
Then the game continues

When the game is reset
Then the game board is set to its initial state
And the game is ongoing
```

# When doing the translation, follow these instructions:
# - represent the board as a string matrix (list of list of strings)
# - represent the two players' moves on the board as strings 'x' and 'o', using
#   the empty string otherwise
# - bracket syntax to access lists is not supported, so remember to define custom
#   functions to access and modify the game board given a pair of indices
# - moreover, define custom functions for
#   - checking move validity
#   - checking whether the board is in a winning state (and for which player), or a draw state, or neither of those.
#   - updating the board given a move
# - use those functions to implement the scenarios
