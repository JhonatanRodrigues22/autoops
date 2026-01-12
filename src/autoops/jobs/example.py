from autoops.core.job import Job


def example_handler():
    """
    Example job handler.
    """
    return {
        "status": "ok",
        "message": "Example job executed successfully",
    }


example_job = Job(
    name="example",
    description="Example job for demonstration purposes",
    handler=example_handler,
)
