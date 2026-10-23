import logfire
from fastapi import FastAPI


def setup_observability(app: FastAPI) -> None:
    print("LOGFIRE ENABLED...")

    logfire.configure(service_name="CLAIRA", distributed_tracing=True)

    # system metrics tracing
    logfire.instrument_system_metrics()

    # FastAPI tracing
    logfire.instrument_fastapi(app)

    # HTTP requests tracing
    logfire.instrument_httpx()

    # Pydantic AI tracing
    logfire.instrument_pydantic_ai(include_content=False)

    # redis
    logfire.instrument_redis()
