"""
An agent which allows one to perform one of the various long-running IPL \
analysis jobs. These currently are:
- IPL Decomposition
- Unsat Analysis

Which is run is determined by the `AnalysisMode` enum in the `InputState`. \
Because the job is long-running, the agent
simply returns the job UUID associated with the task. If you want to check \
for the completion of the task or grab the associated data, \
use the `ipl_job_data` agent.
"""
