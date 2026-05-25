from __future__ import annotations

import dacite
import pytest

from rossum_api.domain_logic.resources import Resource
from rossum_api.models.rules_execution_logs import RulesExecutionLog


@pytest.fixture
def dummy_log():
    return {
        "rule_id": 123,
        "rule_name": "freight_out_of_range",
        "queue_id": 456,
        "annotation_id": 789,
        "request_id": "6166deb3-2f89-4fc2-9359-56cc8e3838e4",
        "created_at": "2024-01-15T10:30:00.000000Z",
        "trigger_event": "annotation_imported",
        "trigger_condition": "field.freight_normalized >= 1000",
        "trigger_condition_results": [True],
        "trigger_condition_values": [{"freight_normalized": "1500.00"}],
        "execution_result": "success",
        "execution_error": None,
        "actions": [
            [
                {
                    "action_id": "a1",
                    "action_type": "add_automation_blocker",
                    "execution_result": "success",
                    "execution_error": None,
                    "payload": {"content": "Freight too high"},
                }
            ]
        ],
    }


@pytest.fixture
def dummy_line_item_log():
    return {
        "rule_id": 124,
        "rule_name": "line_item_check",
        "queue_id": 456,
        "annotation_id": 790,
        "request_id": "abc-line-items",
        "created_at": "2024-01-15T10:30:00.000000Z",
        "trigger_event": "annotation_imported",
        "trigger_condition": "field.item_price > 100",
        "trigger_condition_results": [False, True, True],
        "trigger_condition_values": [
            {"item_price": "80"},
            {"item_price": "150"},
            {"item_price": "90"},
        ],
        "execution_result": "partial_success",
        "execution_error": None,
        "actions": [
            None,
            [{"action_id": "a1", "action_type": "add_automation_blocker"}],
            None,
        ],
    }


@pytest.fixture
def expected_log(dummy_log):
    return dacite.from_dict(RulesExecutionLog, dummy_log)


@pytest.mark.asyncio
class TestRulesExecutionLogs:
    async def test_list_rules_execution_logs(
        self, elis_client, dummy_log, expected_log, mock_generator
    ):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_log)

        logs = client.list_rules_execution_logs()

        async for log in logs:
            assert log == expected_log

        http_client.fetch_all.assert_called_with(Resource.RulesExecutionLog, ())

    async def test_list_rules_execution_logs_passes_filters(
        self, elis_client, dummy_log, mock_generator
    ):
        client, http_client = elis_client
        http_client.fetch_all.return_value = mock_generator(dummy_log)

        logs = client.list_rules_execution_logs(rule=123, queue=456, execution_result="success")
        async for _ in logs:
            pass

        http_client.fetch_all.assert_called_with(
            Resource.RulesExecutionLog, (), rule=123, queue=456, execution_result="success"
        )


class TestRulesExecutionLogsSync:
    def test_list_rules_execution_logs(self, elis_client_sync, dummy_log, expected_log):
        client, http_client = elis_client_sync
        http_client.fetch_resources.return_value = iter((dummy_log,))

        logs = client.list_rules_execution_logs()

        for log in logs:
            assert log == expected_log

        http_client.fetch_resources.assert_called_with(Resource.RulesExecutionLog, ())


class TestRulesExecutionLogDeserialization:
    def test_regular_rule_deserializes(self, dummy_log):
        log = dacite.from_dict(RulesExecutionLog, dummy_log)
        assert log.rule_id == 123
        assert log.trigger_condition_results == [True]
        assert log.trigger_condition_values == [{"freight_normalized": "1500.00"}]
        assert log.execution_result == "success"

    def test_line_item_rule_deserializes(self, dummy_line_item_log):
        log = dacite.from_dict(RulesExecutionLog, dummy_line_item_log)
        assert log.execution_result == "partial_success"
        assert len(log.trigger_condition_results) == 3
        assert log.actions[0] is None
        assert log.actions[1][0]["action_type"] == "add_automation_blocker"
        assert log.actions[2] is None

    def test_nullable_fields_default_to_none(self):
        minimal = {
            "rule_id": 1,
            "rule_name": "r",
            "queue_id": 2,
            "annotation_id": 3,
            "request_id": "x",
            "created_at": "2024-01-15T10:30:00Z",
            "trigger_event": "annotation_imported",
            "trigger_condition": "True",
            "execution_result": "failure",
        }
        log = dacite.from_dict(RulesExecutionLog, minimal)
        assert log.trigger_condition_results is None
        assert log.trigger_condition_values is None
        assert log.execution_error is None
        assert log.actions is None
