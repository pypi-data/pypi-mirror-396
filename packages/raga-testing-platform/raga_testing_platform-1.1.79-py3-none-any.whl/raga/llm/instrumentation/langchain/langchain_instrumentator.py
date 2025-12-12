from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry import trace as trace_api
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry import trace as trace_api

from openinference.instrumentation.langchain._tracer import OpenInferenceTracer
from wrapt import wrap_function_wrapper
from importlib.util import find_spec
from typing import Type, Callable, Any

from raga.llm.exporter.s3exporter import *
from raga.llm.instrumentation.langchain import constants


class LangChainInstrumentor(BaseInstrumentor):
    def __init__(self, test_session) -> None:
        self.s3_exporter = S3Exporter(test_session)
        if find_spec(constants.LANGCHAIN_CORE) is None:
            raise PackageNotFoundError(
                "Missing `langchain-core`. Install with `pip install langchain-core`."
            )
        super().__init__()

    def instrument(self) -> None:
        tracer_provider = trace_sdk.TracerProvider(
            resource=Resource({"ResourceAttributes.PROJECT_NAME": "get_env_project_name()"})
        )
        tracer_provider.add_span_processor(SimpleSpanProcessor(self.s3_exporter))
        super().instrument(skip_dep_check=True, tracer_provider=tracer_provider)

    def instrumentation_dependencies(self):
        return constants.LANGCHAIN_VERSION

    def _instrument(self, **kwargs) -> None:
        if not (tracer_provider := kwargs.get(constants.TRACER_PROVIDER)):
            tracer_provider = trace_api.get_tracer_provider()
        tracer = trace_api.get_tracer(__name__, constants.INSTRUMENTATOR_VERSION, tracer_provider)

        wrap_function_wrapper(
            module="langchain_core.callbacks",
            name="BaseCallbackManager.__init__",
            wrapper=self.BaseCallbackManagerInit(tracer=tracer, cls=OpenInferenceTracer),
        )

    def _uninstrument(self, **kwargs) -> None:
        pass

    def get_dataframe(self):
        return self.s3_exporter.get_dataframe()

    class BaseCallbackManagerInit:
        __slots__ = ("_tracer", "_cls")

        def __init__(self, tracer: trace_api.Tracer, cls: Type["OpenInferenceTracer"]):
            self._tracer = tracer
            self._cls = cls

        def __call__(
                self,
                wrapped: Callable[..., None],
                instance: "BaseCallbackManager",
                args: Any,
                kwargs: Any,
        ) -> None:
            wrapped(*args, **kwargs)
            for handler in instance.inheritable_handlers:
                if isinstance(handler, self._cls):
                    break
            else:
                instance.add_handler(self._cls(tracer=self._tracer), True)
