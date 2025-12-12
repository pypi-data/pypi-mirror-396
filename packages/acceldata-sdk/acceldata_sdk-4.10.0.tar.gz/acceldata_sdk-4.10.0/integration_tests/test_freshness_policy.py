import logging
import os

import acceldata_sdk.constants as const
from acceldata_sdk.constants import FailureStrategy
from acceldata_sdk.events.generic_event import GenericEvent
from acceldata_sdk.models.common_types import PolicyExecutionRequest, ExecutionType
from acceldata_sdk.models.job import CreateJob, Node
from acceldata_sdk.models.pipeline import CreatePipeline, PipelineMetadata
from acceldata_sdk.models.pipeline import PipelineRunResult, PipelineRunStatus
from acceldata_sdk.models.ruleExecutionResult import PolicyFilter, RuleType
from acceldata_sdk.torch_client import TorchClient

import test_constants as test_const
# --- Your retry + constants ---
from test_commons import retry_operation

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

LOGGER = logging.getLogger(__name__)

torch_credentials = {
    'url': os.getenv('TORCH_CATALOG_URL'),
    'access_key': os.getenv('TORCH_ACCESS_KEY'),
    'secret_key': os.getenv('TORCH_SECRET_KEY')
}

freshness_policy_name = "EMPLOYEE-fresh-and-vol-policy-62267665"
torch_client = TorchClient(**torch_credentials)
LOGGER.info("Torch client connected")


def test_get_freshness_policy_by_name():
    def operation():
        return torch_client.get_policy(const.PolicyType.DATA_CADENCE, freshness_policy_name)

    freshness_policy = retry_operation(operation, test_const.MAX_RETRIES, test_const.RETRY_INTERVAL)
    LOGGER.info(freshness_policy)


def test_get_freshness_policy_by_filter():
    filter = PolicyFilter(policyType=RuleType.DATA_CADENCE, enable=True)

    def operation():
        return torch_client.list_all_policies(filter=filter)

    freshness_rules = retry_operation(operation, test_const.MAX_RETRIES, test_const.RETRY_INTERVAL)
    LOGGER.info(freshness_rules)


def execute_freshness_policy():
    def get_policy_op():
        return torch_client.get_policy(identifier=freshness_policy_name)

    freshness_policy = retry_operation(get_policy_op, test_const.MAX_RETRIES, test_const.RETRY_INTERVAL)

    def execute_op():
        return torch_client.execute_freshness_rule(rule_id=freshness_policy.id)

    policy_execution_result = retry_operation(execute_op, test_const.MAX_RETRIES, test_const.RETRY_INTERVAL)
    LOGGER.info(policy_execution_result)

    return policy_execution_result


def test_get_freshness_policy_executions_by_rule_object():
    def get_policy_op():
        return torch_client.get_policy(identifier=freshness_policy_name)

    freshness_policy = retry_operation(get_policy_op, test_const.MAX_RETRIES, test_const.RETRY_INTERVAL)

    def operation():
        return freshness_policy.get_executions()

    executions = retry_operation(operation, test_const.MAX_RETRIES, test_const.RETRY_INTERVAL)
    LOGGER.info(executions)


def test_freshness_policy_rule_result(freshness_execution_id):
    def operation():
        return torch_client.get_freshness_rule_result(freshness_execution_id)

    result = retry_operation(operation, test_const.MAX_RETRIES, test_const.RETRY_INTERVAL)
    LOGGER.info(result)


def execute_policy_sync():
    def get_policy_op():
        return torch_client.get_policy(identifier=freshness_policy_name)

    freshness_policy = retry_operation(get_policy_op, test_const.MAX_RETRIES, test_const.RETRY_INTERVAL)

    def execute_op():
        return torch_client.execute_policy(
            const.PolicyType.DATA_CADENCE,
            freshness_policy.id,
            sync=True,
            failure_strategy=FailureStrategy.DoNotFail
        )

    async_executor = retry_operation(execute_op, test_const.MAX_RETRIES, test_const.RETRY_INTERVAL)

    def get_result_op():
        return async_executor.get_result(failure_strategy=FailureStrategy.DoNotFail)

    result = retry_operation(get_result_op, test_const.MAX_RETRIES, test_const.RETRY_INTERVAL)
    LOGGER.info(result)

    LOGGER.info(async_executor.get_status())


def execute_policy_async_and_cancel():
    async_executor = None

    try:
        # Step 1: Get policy
        def get_policy_op():
            return torch_client.get_policy(identifier=freshness_policy_name)

        freshness_policy = retry_operation(
            get_policy_op,
            test_const.MAX_RETRIES,
            test_const.RETRY_INTERVAL
        )

        # Step 2: Execute async
        def execute_op():
            return torch_client.execute_policy(
                const.PolicyType.DATA_CADENCE,
                freshness_policy.id,
                sync=False,
                failure_strategy=FailureStrategy.DoNotFail
            )

        async_executor = retry_operation(
            execute_op,
            test_const.MAX_RETRIES,
            test_const.RETRY_INTERVAL
        )

        # ---- IMPORTANT FIX ----
        # Cancel ONLY if execution actually started → async_executor.id is not None
        if not async_executor or not getattr(async_executor, "id", None):
            LOGGER.warning(
                "Skipping cancel(): async execution did not start "
                "(executor.id is None — server rejected the execution)."
            )
            return

        # Step 3: Cancel
        def cancel_op():
            return async_executor.cancel()

        result = retry_operation(
            cancel_op,
            test_const.MAX_RETRIES,
            test_const.RETRY_INTERVAL
        )

        LOGGER.info(result)

    except Exception as ex:
        LOGGER.error(f"Error during async execute/cancel: {ex}", exc_info=True)
        raise


def execute_policy_async():
    def get_policy_op():
        return torch_client.get_policy(identifier=freshness_policy_name)

    freshness_policy = retry_operation(get_policy_op, test_const.MAX_RETRIES, test_const.RETRY_INTERVAL)

    def execute_op():
        return torch_client.execute_policy(
            const.PolicyType.DATA_CADENCE,
            freshness_policy.id,
            sync=False,
            failure_strategy=FailureStrategy.DoNotFail
        )

    async_executor = retry_operation(execute_op, test_const.MAX_RETRIES, test_const.RETRY_INTERVAL)

    def get_result_op():
        return async_executor.get_result(failure_strategy=FailureStrategy.DoNotFail)

    result = retry_operation(get_result_op, test_const.MAX_RETRIES, test_const.RETRY_INTERVAL)
    LOGGER.info(result)

    LOGGER.info(async_executor.get_status())


if __name__ == "__main__":
    test_get_freshness_policy_by_name()
    test_get_freshness_policy_by_filter()
    freshness_result = execute_freshness_policy()
    test_freshness_policy_rule_result(freshness_result.id)
    execute_policy_sync()
    execute_policy_async_and_cancel()
