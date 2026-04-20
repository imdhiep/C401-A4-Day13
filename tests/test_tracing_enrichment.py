from contextlib import contextmanager
from types import SimpleNamespace

from app.agent import LabAgent
from app.pii import hash_user_id


class DummyLangfuseClient:
    def __init__(self) -> None:
        self.started_observations: list[dict] = []
        self.span_updates: list[dict] = []

    @contextmanager
    def start_as_current_observation(self, **kwargs):
        self.started_observations.append(kwargs)
        yield

    def update_current_span(self, **kwargs) -> None:
        self.span_updates.append(kwargs)


def test_agent_tracing_metadata(monkeypatch) -> None:
    client = DummyLangfuseClient()
    propagated: list[dict] = []

    @contextmanager
    def dummy_propagate_attributes(**kwargs):
        propagated.append(kwargs)
        yield

    monkeypatch.setattr("app.agent.get_langfuse_client", lambda: client)
    monkeypatch.setattr("app.agent.propagate_attributes", dummy_propagate_attributes)
    monkeypatch.setattr("app.agent.retrieve", lambda message: ["Da Nang itinerary context"])
    monkeypatch.setattr(
        "app.agent.FakeLLM.generate",
        lambda self, prompt: SimpleNamespace(
            text="Da Nang travel plan with beach stay and breakfast included.",
            usage=SimpleNamespace(input_tokens=120, output_tokens=180),
            model=self.model,
        ),
    )

    agent = LabAgent(model="claude-sonnet-4-5")
    agent.run(
        user_id="traveler-01",
        feature="qa",
        session_id="s-danang",
        message="Plan my Da Nang trip around My Khe beach",
    )

    assert client.started_observations == [
        {
            "name": "danang_travel_chat",
            "input": {
                "feature": "qa",
                "message_preview": "Plan my Da Nang trip around My Khe beach",
            },
        }
    ]
    assert propagated == [
        {
            "trace_name": "danang-travel-chat",
            "user_id": hash_user_id("traveler-01"),
            "session_id": "s-danang",
            "metadata": {
                "domain": "danang-travel",
                "city": "da-nang",
                "feature": "qa",
                "model": "claude-sonnet-4-5",
            },
            "tags": [
                "lab",
                "danang-travel-planner",
                "feature:qa",
                "model:claude-sonnet-4-5",
            ],
        }
    ]
    assert client.span_updates == [
        {
            "output": {
                "answer_preview": "Da Nang travel plan with beach stay and breakfast included.",
                "quality_score": 0.9,
                "latency_ms": 0,
                "cost_usd": 0.00306,
            },
            "metadata": {
                "doc_count": 1,
                "query_preview": "Plan my Da Nang trip around My Khe beach",
                "domain": "danang-travel",
                "city": "da-nang",
                "tokens_in": 120,
                "tokens_out": 180,
            },
        }
    ]
