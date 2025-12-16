# Taken from https://github.com/statelyai/xstate/blob/main/examples/persisted-donut-maker/donutMachine.ts

# TODO: this might benefit from allowing more than one Given/state clauses

Given the machine is fetching the ingredients
When all the ingredients have been fetched
Then it can start the assembling process
And begins with making dough

Given the machine is assembling the ingredients
And it's making dough
When the dough is ready
Then it moves on to the mixing stage

Given the machine is assembling the ingredients
And mixing dry
When it's done
Then we have a finished dry mix

Given the machine is assembling the ingredients
And mixing wet
When it's done
Then we have a finished wet mix

Given the machine is assembling the ingredients
And both dry mixing and wet mixing are done
When it completes the assembling process
Then it moves on to the frying stage

Given the machine is frying
When it's done
Then it moves on to flip the donuts

Given the machine is flipping the donuts
When it's done
Then it moves on to drying them

Given the machine is drying the donuts
When it's done
Then it moves on to glazing them

Given the machine is glazing the donuts
When it's done
Then it moves on to serving them

Given the machine is serving the donuts
When it's done
Then it starts again from the beginning
