from langchain_core.tracers.base import BaseTracer
from langchain_core.tracers.schemas import Run
from opentelemetry.metrics import get_meter


def _to_attributes(run: Run):
    return {
        "langgraph.graph.id": run.metadata.get("graph_id", ""),
        "langgraph.run.node": run.metadata.get("langgraph_node", ""),
        "langgraph.run.name": run.name,
    }


class OtelMetricsTracer(BaseTracer):
    meter = get_meter("imandra.langgraph")
    started_chains = meter.create_counter("langgraph.chains.started", unit="1")
    chain_errors = meter.create_counter("langgraph.chains.errors", unit="1")

    active_runs = meter.create_up_down_counter("langgraph.runs.active", unit="1")
    completed_runs = meter.create_histogram("langgraph.runs.processing_time", unit="s")

    def _persist_run(self, run: Run) -> None:
        if end_time := run.end_time:
            self.completed_runs.record(
                (end_time - run.start_time).total_seconds(),
                _to_attributes(run)
                | {
                    "status": "error" if run.error else "ok",
                },
            )

    def _start_trace(self, run: Run):
        super()._start_trace(run)
        self.active_runs.add(1, _to_attributes(run))

    def _end_trace(self, run: Run):
        self.active_runs.add(-1, _to_attributes(run))
        super()._end_trace(run)

    def _on_chain_start(self, run: Run):
        self.started_chains.add(1, _to_attributes(run))

    def _on_chain_error(self, run: Run):
        self.chain_errors.add(1, _to_attributes(run))
