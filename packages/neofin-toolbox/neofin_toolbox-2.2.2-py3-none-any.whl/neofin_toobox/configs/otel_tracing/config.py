import logging
import json
from typing import Dict, Any, Optional
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.trace import SpanAttributes

# --- Imports de Trace ---
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# --- Imports de Metrics ---
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter

# --- Imports de Logs (Versão Estável) ---
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter

# --- Imports de Instrumentação Automática ---
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from neofin_toobox.configs.otel_tracing.span_events import SpanEvent


def define_tracing(name: str):
    return trace.get_tracer(name)

def define_resource(service_name: str) -> Resource:
    return Resource.create({
        "service.name": service_name,
    })

def setup_span_event(tracer: trace.Tracer, otel: str):
    return SpanEvent(tracer, otel)

def setup_telemetry(resource: Optional[Resource], OTEL_COLLECTOR_ENDPOINT: str):
    """Configura Traces, Métricas e Logs para enviar ao OTel Collector."""

    # --- Configuração de TRACES ---
    tracer_provider = TracerProvider(resource=resource)
    # Envia traces via gRPC para o collector (localhost:4317)
    span_exporter = OTLPSpanExporter(endpoint=OTEL_COLLECTOR_ENDPOINT, insecure=True)
    tracer_provider.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(tracer_provider)
    print("TracerProvider configurado.")

    # --- Configuração de MÉTRICAS ---
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=OTEL_COLLECTOR_ENDPOINT, insecure=True)
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
    print("MeterProvider configurado.")

    # --- Configuração de LOGS ---
    logger_provider = LoggerProvider(resource=resource)
    log_exporter = OTLPLogExporter(endpoint=OTEL_COLLECTOR_ENDPOINT, insecure=True)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    # Conecta o OTel ao sistema de logging padrão do Python
    handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)

    # Instrumenta o logging para adicionar automaticamente o trace_id e span_id
    LoggingInstrumentor().instrument(set_logging_format=True, logger_provider=logger_provider)
    print("LoggerProvider configurado.")

    # --- Instrumentação Automática ---
    # Instrumenta a biblioteca 'requests' para criar spans automaticamente
    RequestsInstrumentor().instrument()
    print("Instrumentação automática (Requests) aplicada.")

def instrument_chalice():
    """Adiciona a instrumentação automática do OpenTelemetry ao Chalice."""
    setup_telemetry()

