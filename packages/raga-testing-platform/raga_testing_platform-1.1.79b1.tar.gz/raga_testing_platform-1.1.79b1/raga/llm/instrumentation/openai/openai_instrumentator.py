from openinference.instrumentation.openai import \
    OpenAIInstrumentor as BaseInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

from raga.llm.instrumentation.openai.s3exporter import S3Exporter


class OpenAIInstrumentor(BaseInstrumentor):
    def __init__(self, test_session) -> None:
        self.s3Exporter = S3Exporter(test_session)
        super().__init__()

    def instrument(self):
        tracer_provider = trace_sdk.TracerProvider()
        tracer_provider.add_span_processor(
            SimpleSpanProcessor(self.s3Exporter))
        # Optionally, you can also print the spans to the console.
        trace_api.set_tracer_provider(tracer_provider)
        super().instrument(tracer_provider=tracer_provider)

    def get_dataframe(self):
        return self.s3Exporter.get_dataframe()
