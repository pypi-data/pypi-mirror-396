from .hmd_lib_telemetry import HmdMetric, HmdTracer


def named_lambda_wrapper(
    name: str,
    info_def: callable = None,
):
    """
    Decorator to wrap a lambda function with telemetry and logging.
    """
    assert name and len(name) > 0, "named_lambda_wrapper name is required"
    info_def = info_def if info_def else lambda evt, ctx: str(evt)

    def decorator(func):
        def wrapper(*args, **kwargs):
            tracer = HmdTracer(name)
            metric = HmdMetric(name)
            with tracer.start_span(name) as span:
                try:
                    if info_def:
                        span.add_event(
                            f"{name} Event", {"info": info_def(args[0], args[1])}
                        )
                    with metric.timer(f"{name}"):
                        # Call the original function
                        # and measure its execution time
                        result = func(*args, **kwargs)
                        span.add_event(f"{name} Success", {"result": str(result)})
                        return result
                except Exception as e:
                    span.record_exception(e)
                    span.add_event(f"{name} Error", {"type": "error", "error": str(e)})
                    raise e

        return wrapper

    return decorator
