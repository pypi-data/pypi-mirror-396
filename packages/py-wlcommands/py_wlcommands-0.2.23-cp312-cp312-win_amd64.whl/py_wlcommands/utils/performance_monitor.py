"""Performance monitoring utilities for WL Commands."""

import functools
import json
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable


@dataclass
class PerformanceMetrics:
    """Performance metrics for a single operation."""

    operation_name: str
    execution_time: float
    start_time: float
    end_time: float
    success: bool
    additional_data: dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """A utility class for monitoring performance of operations."""

    def __init__(self):
        self._metrics: list[PerformanceMetrics] = []
        self._active_operations: dict[str, float] = {}

    def start_operation(self, operation_name: str) -> None:
        """
        Start timing an operation.

        Args:
            operation_name: Name of the operation to track
        """
        self._active_operations[operation_name] = time.perf_counter()

    def end_operation(
        self, operation_name: str, success: bool = True, **additional_data: Any
    ) -> PerformanceMetrics:
        """
        End timing an operation and record metrics.

        Args:
            operation_name: Name of the operation to track
            success: Whether the operation was successful
            **additional_data: Additional data to store with the metrics

        Returns:
            PerformanceMetrics object with the recorded metrics
        """
        if operation_name not in self._active_operations:
            raise ValueError(f"Operation '{operation_name}' was not started")

        start_time = self._active_operations.pop(operation_name)
        end_time = time.perf_counter()
        execution_time = end_time - start_time

        metrics = PerformanceMetrics(
            operation_name=operation_name,
            execution_time=execution_time,
            start_time=start_time,
            end_time=end_time,
            success=success,
            additional_data=additional_data,
        )

        self._metrics.append(metrics)
        return metrics

    def record_operation(
        self,
        operation_name: str,
        execution_time: float,
        success: bool = True,
        **additional_data: Any,
    ) -> PerformanceMetrics:
        """
        Record metrics for an operation without timing it.

        Args:
            operation_name: Name of the operation to track
            execution_time: Execution time in seconds
            success: Whether the operation was successful
            **additional_data: Additional data to store with the metrics

        Returns:
            PerformanceMetrics object with the recorded metrics
        """
        start_time = time.perf_counter() - execution_time
        end_time = start_time + execution_time

        metrics = PerformanceMetrics(
            operation_name=operation_name,
            execution_time=execution_time,
            start_time=start_time,
            end_time=end_time,
            success=success,
            additional_data=additional_data,
        )

        self._metrics.append(metrics)
        return metrics

    @contextmanager
    def monitor_operation(self, operation_name: str, **additional_data: Any):
        """
        Context manager for monitoring an operation.

        Args:
            operation_name: Name of the operation to track
            **additional_data: Additional data to store with the metrics
        """
        self.start_operation(operation_name)
        success = True
        try:
            yield
        except Exception:
            success = False
            raise
        finally:
            try:
                self.end_operation(operation_name, success, **additional_data)
            except ValueError:
                # Operation was not started, ignore
                pass

    def get_metrics(self) -> list[PerformanceMetrics]:
        """
        Get all recorded metrics.

        Returns:
            List of PerformanceMetrics objects
        """
        return self._metrics.copy()

    def get_average_execution_time(self, operation_name: str) -> float | None:
        """
        Get the average execution time for an operation.

        Args:
            operation_name: Name of the operation

        Returns:
            Average execution time in seconds, or None if no metrics found
        """
        times = [
            metric.execution_time
            for metric in self._metrics
            if metric.operation_name == operation_name
        ]

        if not times:
            return None

        return sum(times) / len(times)

    def clear_metrics(self) -> None:
        """Clear all recorded metrics."""
        self._metrics.clear()
        self._active_operations.clear()

    def export_metrics(self, file_path: Path) -> None:
        """
        Export metrics to a JSON file.

        Args:
            file_path: Path to the output file
        """
        try:
            metrics_data = [
                {
                    "operation_name": metric.operation_name,
                    "execution_time": metric.execution_time,
                    "start_time": metric.start_time,
                    "end_time": metric.end_time,
                    "success": metric.success,
                    "additional_data": metric.additional_data,
                }
                for metric in self._metrics
            ]

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False)
        except (OSError, TypeError) as e:
            # Handle file I/O errors and JSON serialization errors
            raise Exception(f"Failed to export metrics to {file_path}: {e}")


def monitor_performance(operation_name: str, **additional_data: Any):
    """
    Decorator for monitoring the performance of a function.

    Args:
        operation_name: Name of the operation to track
        **additional_data: Additional data to store with the metrics
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            with monitor.monitor_operation(operation_name, **additional_data):
                return func(*args, **kwargs)

        return wrapper

    return decorator


# Global instance
_performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """
    Get the global performance monitor instance.

    Returns:
        The global performance monitor instance
    """
    return _performance_monitor


def start_operation(operation_name: str) -> None:
    """
    Start timing an operation using the global monitor.

    Args:
        operation_name: Name of the operation to track
    """
    _performance_monitor.start_operation(operation_name)


def end_operation(
    operation_name: str, success: bool = True, **additional_data: Any
) -> PerformanceMetrics:
    """
    End timing an operation and record metrics using the global monitor.

    Args:
        operation_name: Name of the operation to track
        success: Whether the operation was successful
        **additional_data: Additional data to store with the metrics

    Returns:
        PerformanceMetrics object with the recorded metrics
    """
    return _performance_monitor.end_operation(
        operation_name, success, **additional_data
    )


@contextmanager
def monitor_operation(operation_name: str, **additional_data: Any):
    """
    Context manager for monitoring an operation using the global monitor.

    Args:
        operation_name: Name of the operation to track
        **additional_data: Additional data to store with the metrics
    """
    with _performance_monitor.monitor_operation(operation_name, **additional_data):
        yield
