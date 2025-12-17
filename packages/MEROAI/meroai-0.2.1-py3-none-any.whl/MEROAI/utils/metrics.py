import functools
import logging
import time
from enum import Enum
from typing import Any, Callable, Optional, Union
class RequestStatus(Enum):
    PENDING = "pending"
    PREFILLING = "prefilling"
    PREFILLING_SPLIT = "prefilling_split"
    SPLIT_PENDING_REMAINDER = "split_pending_remainder"
    DECODING = "decoding"
    FINISHED = "finished"
    FAILED = "failed"
try:
    from opentelemetry import metrics
    from opentelemetry.trace import Status, StatusCode, get_tracer
    _has_opentelemetry = True
except ImportError:
    _has_opentelemetry = False
def attach_tracer(tracer_name_template=None):
    if not _has_opentelemetry:
        return lambda cls: cls
    def decorator(cls):
        original_init = cls.__init__
        @functools.wraps(original_init)
        def init_with_tracer(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            module_name = cls.__module__
            class_name = cls.__qualname__
            if tracer_name_template is None:
                if module_name.startswith("MEROAI."):
                    tracer_name = f"{module_name}.{class_name}"
                else:
                    tracer_name = f"MEROAI.{module_name}.{class_name}"
            else:
                tracer_name = tracer_name_template.format(module=module_name, class_name=class_name)
            self.tracer = get_tracer(tracer_name)
        cls.__init__ = init_with_tracer
        return cls
    return decorator
def traced(
    func=None,
    *,
    span_name=None,
    standalone=False,
    additional_attributes: Optional[list[tuple[str, str, Union[Any, Callable[[Any], Any]]]]] = None,
):
    def decorator(func):
        if not _has_opentelemetry:
            return func
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            instance = args[0] if args and (hasattr(func, "__self__") and func.__self__ is not None) else None
            is_method = instance is not None
            if is_method and hasattr(instance, "tracer"):
                tracer = instance.tracer
            else:
                tracer = get_tracer(f"MEROAI.{func.__module__}.{func.__name__}")
            name = span_name or func.__name__
            span_fn = tracer.start_span if standalone else tracer.start_as_current_span
            with span_fn(name) as span:
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                span.set_attribute("function.is_method", is_method)
                if args:
                    for i, arg in enumerate(args):
                        if isinstance(arg, (str, int, float, bool)) or arg is None:
                            span.set_attribute(f"args.{i}", str(arg))
                        else:
                            span.set_attribute(f"args.{i}", str(type(arg)))
                if kwargs:
                    for key, value in kwargs.items():
                        if isinstance(value, (str, int, float, bool)) or value is None:
                            span.set_attribute(f"kwargs.{key}", str(value))
                        else:
                            span.set_attribute(f"kwargs.{key}", str(type(value)))
                if additional_attributes and is_method:
                    for attr_config in additional_attributes:
                        instance_attribute_name, span_attribute_key, value_or_transform_function = attr_config
                        if hasattr(instance, instance_attribute_name):
                            attribute_value = getattr(instance, instance_attribute_name)
                            if callable(value_or_transform_function):
                                transformed_value = value_or_transform_function(attribute_value)
                            else:
                                transformed_value = value_or_transform_function
                            span.set_attribute(span_attribute_key, transformed_value)
                try:
                    result = func(*args, **kwargs)
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR))
                    span.record_exception(e)
                    raise
        return wrapper
    if func is None:
        return decorator
    return decorator(func)
logger = logging.getLogger(__name__)
@attach_tracer()
class ContinuousBatchProcessorMetrics:
    def __init__(self, max_batch_tokens: int):
        self.max_batch_tokens = max_batch_tokens
        self._setup_metrics()
    def _setup_metrics(self):
        if not _has_opentelemetry:
            logger.info("OpenTelemetry is not installed. Metrics and tracing will not be recorded.")
            return
        self.meter = metrics.get_meter("MEROAI.generation.continuous_batch_processor")
        ttft_buckets = [10, 25, 50, 75, 100, 150, 200, 300, 500, 750, 1000, 2000, 5000, 10000]
        self.ttft_histogram = self.meter.create_histogram(
            name="ttft_milliseconds",
            description="Time to first token in milliseconds",
            unit="ms",
            explicit_bucket_boundaries_advisory=ttft_buckets,
        )
        self.active_requests_gauge = self.meter.create_gauge(
            name="active_requests_count",
            description="Number of active requests currently being processed",
            unit="requests",
        )
        self.waiting_requests_gauge = self.meter.create_gauge(
            name="waiting_requests_count",
            description="Number of requests waiting to be processed",
            unit="requests",
        )
        latency_buckets = [50, 100, 250, 500, 1000, 2000, 5000, 10000, 20000, 30000, 60000]
        self.request_latency_histogram = self.meter.create_histogram(
            name="request_latency_milliseconds",
            description="End-to-end latency for completed requests in milliseconds",
            unit="ms",
            explicit_bucket_boundaries_advisory=latency_buckets,
        )
        self.decode_prefill_ratio_gauge = self.meter.create_gauge(
            name="decode_prefill_ratio",
            description="Ratio of decode tokens to prefill tokens in a batch",
            unit="ratio",
        )
        self.prefill_tokens_counter = self.meter.create_counter(
            name="prefill_tokens_processed",
            description="Number of prefill tokens processed",
            unit="tokens",
        )
        self.decode_tokens_counter = self.meter.create_counter(
            name="decode_tokens_processed",
            description="Number of decode tokens processed",
            unit="tokens",
        )
        batch_fill_buckets = [5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 98, 100]
        self.batch_fill_percentage_histogram = self.meter.create_histogram(
            name="batch_fill_percentage",
            description="Percentage of max_batch_tokens utilized in each batch",
            unit="percent",
            explicit_bucket_boundaries_advisory=batch_fill_buckets,
        )
        self.kv_cache_free_memory_gauge = self.meter.create_gauge(
            name="kv_cache_free_memory_bytes",
            description="Free memory of the PagedAttentionCache in bytes",
            unit="bytes",
        )
        self.kv_cache_memory_gauge = self.meter.create_gauge(
            name="kv_cache_memory_bytes",
            description="Memory usage of the PagedAttentionCache in bytes",
            unit="bytes",
        )
    @traced
    def record_ttft_metric(self, created_time: float, request_id: str) -> None:
        if not _has_opentelemetry:
            return
        ttft_ms = (time.time() - created_time) * 1000.0
        try:
            self.ttft_histogram.record(ttft_ms)
            logger.debug(f"Recorded TTFT for request {request_id}: {ttft_ms:.2f}ms")
        except Exception as e:
            logger.warning(f"Failed to record TTFT metric: {e}")
    @traced
    def record_batch_metrics(self, requests_in_batch: list) -> None:
        if not _has_opentelemetry or not requests_in_batch:
            return
        decode_tokens = 0
        prefill_tokens = 0
        for state in requests_in_batch:
            if state.status == RequestStatus.DECODING:
                decode_tokens += 1
            elif state.status in [RequestStatus.PREFILLING, RequestStatus.PREFILLING_SPLIT]:
                prefill_tokens += len(state.prompt_ids)
        total_batch_tokens = decode_tokens + prefill_tokens
        try:
            if prefill_tokens > 0:
                self.prefill_tokens_counter.add(prefill_tokens)
            if decode_tokens > 0:
                self.decode_tokens_counter.add(decode_tokens)
            if prefill_tokens > 0:
                ratio = decode_tokens / prefill_tokens
                self.decode_prefill_ratio_gauge.set(ratio)
            fill_percentage = (total_batch_tokens / self.max_batch_tokens) * 100.0
            self.batch_fill_percentage_histogram.record(fill_percentage)
            logger.debug(
                f"Batch metrics: {decode_tokens} decode tokens, {prefill_tokens} prefill tokens, "
                f"batch fill: {fill_percentage:.2f}% ({total_batch_tokens}/{self.max_batch_tokens})"
            )
        except Exception as e:
            logger.warning(f"Failed to record batch metrics: {e}")
    @traced
    def record_kv_cache_memory_metrics(self, cache) -> None:
        if not _has_opentelemetry:
            return
        try:
            page_size = cache.head_dim * cache.num_key_value_heads
            page_mem_in_bytes = page_size * cache.dtype.itemsize
            block_mem_in_bytes = 2 * len(cache.key_cache) * cache.block_size * page_mem_in_bytes
            free_blocks = cache.get_num_free_blocks()
            used_blocks = cache.num_blocks - free_blocks
            used_memory_bytes = used_blocks * block_mem_in_bytes
            free_memory_bytes = free_blocks * block_mem_in_bytes
            self.kv_cache_memory_gauge.set(used_memory_bytes)
            self.kv_cache_free_memory_gauge.set(free_memory_bytes)
            logger.debug(
                f"KV Cache memory: {used_memory_bytes / (1024 * 1024):.2f}MB, "
                f"Used blocks: {used_blocks}/{cache.num_blocks} "
                f"({used_blocks / cache.num_blocks * 100:.1f}%)"
            )
        except Exception as e:
            logger.warning(f"Failed to record KV cache memory metrics: {e}")
    @traced
    def record_queue_metrics(self, active_requests: int, waiting_requests: int) -> None:
        if not _has_opentelemetry:
            return
        try:
            self.active_requests_gauge.set(active_requests)
            self.waiting_requests_gauge.set(waiting_requests)
            logger.debug(f"Queue metrics: {active_requests} active requests, {waiting_requests} waiting requests")
        except Exception as e:
            logger.warning(f"Failed to record queue metrics: {e}")
    @traced
    def record_request_completion(self, created_time: float, request_id: str) -> None:
        if not _has_opentelemetry:
            return
        latency_ms = (time.time() - created_time) * 1000.0
        try:
            self.request_latency_histogram.record(latency_ms)
            logger.debug(f"Recorded request completion for {request_id}: {latency_ms:.2f}ms")
        except Exception as e:
            logger.warning(f"Failed to record request completion metric: {e}")