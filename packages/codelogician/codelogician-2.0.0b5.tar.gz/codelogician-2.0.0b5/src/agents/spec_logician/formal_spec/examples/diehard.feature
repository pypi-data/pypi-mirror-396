# Taken from https://github.com/tlaplus/Examples/blob/master/specifications/DieHard/DieHard.pdf

Translate this Cucumber feature to Formal Feature.

```
When I pour water from a faucet into <jar>
Then <jar> contains <max_units>

When I empty <jar>
Then <jar> contains 0 units

When I pour the contents of jar <source> into jar <target>
Then the contents of <target> are increased by the poured amount, up to <max_units>
And the contents of <source> are decreased by the poured amount.
```

Further instructions:
- `<jar>` should be either a small jar or a big jar
- `<max_units>` should be 3 and 5 for the small and big jar respectively
- Jars don't need to be empty to be filled from the faucet
- Water is always transferred between jars for the maximum possible amount
  that the source's contents and target's max units allow.
- Use a single entity `jars` with a single state `ready`.
