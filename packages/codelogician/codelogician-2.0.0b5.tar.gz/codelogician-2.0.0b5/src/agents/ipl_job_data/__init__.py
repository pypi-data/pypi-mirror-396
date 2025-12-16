"""
An agent which allows one to perform one to check the status and grab the \
data of a long-running IPL job.
These currently are:
- IPL Decomposition
- Unsat Analysis

A job UUID is required by the `InputState`. The agent determines which of the \
above job types the UUID is associated with
and returns the associated data if it has succeeded. Because these jobs often \
take a long time to run,
you can use the `wait` param in the `InputState` to determine whether to \
agent should hang until the job has completed,
or if it should immediately return with an indication of the status.
"""
