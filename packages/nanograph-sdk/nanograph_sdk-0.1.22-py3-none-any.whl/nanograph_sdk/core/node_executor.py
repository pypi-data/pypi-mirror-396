import asyncio
from typing import Dict, Callable, Optional, Coroutine, Any
from types import SimpleNamespace

from .interfaces import (
    GraphNode,
    NodeInputs,
    NodeOutputs,
    NodeStatus,
    NodeInstance,
    ExecutionContext,
    ExecutionContextData
)
from .logger import StructuredLogger

# Map to store active asyncio.Tasks for cancellable node executions
active_node_execution_tasks: Dict[str, asyncio.Task] = {}
# Map to store AbortController-like events for signaling cancellation
active_node_abort_events: Dict[str, asyncio.Event] = {}


def get_execution_key(instance_id: str, node_id: int) -> str:
    return f"{instance_id}-{node_id}"


def _scoped_logger(server_uid: str, logger: Optional[StructuredLogger], segment: str) -> StructuredLogger:
    return logger.child(segment) if logger else StructuredLogger(f"NanoSDK@{server_uid}/{segment}")


async def execute_node(
    instance_id: str,
    node_uid: str,
    graph_node: GraphNode,
    inputs: NodeInputs,
    on_status_update: Callable[[NodeStatus], Coroutine[Any, Any, None]],
    node_registry: Dict[str, NodeInstance],
    logger: Optional[StructuredLogger] = None
) -> NodeOutputs:
    server_uid = graph_node.get('serverUid', 'unknown') or 'unknown'
    base_logger = _scoped_logger(server_uid, logger, 'NodeExecutor')
    exec_logger = base_logger.child(f"Instance:{instance_id}")

    execution_key = get_execution_key(instance_id, graph_node['id'])
    abort_event = asyncio.Event()
    active_node_abort_events[execution_key] = abort_event
    exec_logger.debug(
        f"Prepared abort event for key {execution_key} (object_id={id(abort_event)})"
    )

    node_instance = node_registry.get(node_uid)
    if not node_instance:
        error_msg = f"Node definition not found: {node_uid}"
        await on_status_update({'type': 'error', 'message': error_msg})
        active_node_abort_events.pop(execution_key, None)
        raise ValueError(error_msg)

    try:
        await on_status_update({'type': 'running', 'message': 'Starting execution...'})

        def is_aborted_with_logging() -> bool:
            is_set = abort_event.is_set()
            exec_logger.debug(
                f"Abort check for {execution_key} -> {is_set}"
            )
            return is_set

        context_data: ExecutionContextData = {
            'send_status': lambda status: asyncio.create_task(on_status_update(status)),
            'is_aborted': is_aborted_with_logging,
            'graph_node': graph_node,
            'instance_id': instance_id
        }

        execution_context_dict: ExecutionContext = {
            'inputs': inputs,
            'parameters': graph_node['parameters'],
            'context': context_data
        }
        execution_context_obj = SimpleNamespace(**execution_context_dict)

        node_execute_fn = node_instance['execute']
        exec_logger.debug(
            f"Executing node {graph_node['id']} (UID: {node_uid}) with key {execution_key}"
        )

        if asyncio.iscoroutinefunction(node_execute_fn):
            outputs = await node_execute_fn(execution_context_obj)
        else:
            loop = asyncio.get_event_loop()
            outputs = await loop.run_in_executor(None, node_execute_fn, execution_context_obj)

        if not abort_event.is_set():
            await on_status_update({
                'type': 'complete',
                'message': 'Execution finished.',
                'outputs': outputs
            })
            exec_logger.info(
                f"Node {graph_node['id']} (UID: {node_uid}) execution successful"
            )
        else:
            exec_logger.warn(
                f"Node {graph_node['id']} (UID: {node_uid}) execution aborted"
            )

        return outputs

    except Exception as exc:
        error_message = str(exc)
        exec_logger.error(
            f"Error executing node {graph_node['id']} (UID: {node_uid}): {error_message}"
        )
        if not abort_event.is_set():
            await on_status_update({'type': 'error', 'message': error_message})
            raise
        return {}

    finally:
        active_node_abort_events.pop(execution_key, None)
        active_node_execution_tasks.pop(execution_key, None)
        exec_logger.debug(
            f"Cleaned up execution key {execution_key}; remaining abort events: {len(active_node_abort_events)}"
        )


def abort_node_execution(
    instance_id: str,
    node_id: int,
    server_uid: str,
    logger: Optional[StructuredLogger] = None
) -> bool:
    base_logger = logger or StructuredLogger(f"NanoSDK@{server_uid}/NodeExecutor")
    abort_logger = base_logger.child('Abort')

    key = get_execution_key(instance_id, node_id)
    abort_event = active_node_abort_events.get(key)
    if abort_event:
        abort_logger.info(f"Aborting execution for key {key}")
        abort_event.set()
        task = active_node_execution_tasks.get(key)
        if task and not task.done():
            task.cancel()
            abort_logger.debug(f"Cancelled task associated with key {key}")
        return True

    abort_logger.debug(f"No active execution found to abort for key {key}")
    return False


def abort_executions_for_instance(
    instance_id: str,
    server_uid: str,
    logger: Optional[StructuredLogger] = None
) -> int:
    base_logger = logger.child('NodeExecutor') if logger else StructuredLogger(f"NanoSDK@{server_uid}/NodeExecutor")
    abort_logger = base_logger.child(f"AbortInstance:{instance_id}")

    aborted_count = 0
    abort_logger.info(f"Attempting to abort executions for instance {instance_id}")

    keys_to_check = [key for key in active_node_abort_events.keys() if key.startswith(f"{instance_id}-")]

    for key in keys_to_check:
        node_id_str = key.split('-')[-1]
        try:
            node_id = int(node_id_str)
            if abort_node_execution(instance_id, node_id, server_uid, base_logger):
                aborted_count += 1
        except ValueError:
            abort_logger.error(f"Failed to parse node id from key {key}")
        except Exception as exc:
            abort_logger.error(f"Error aborting node for key {key}: {exc}")

    if aborted_count > 0:
        abort_logger.info(f"Aborted {aborted_count} node execution(s) for instance {instance_id}")
    else:
        abort_logger.debug(f"No active node executions found to abort for instance {instance_id}")

    return aborted_count
