import logging
from functools import wraps
from typing import Dict, Any, Callable, Optional

from opentelemetry import trace
from opentelemetry.semconv.trace import SpanAttributes
from opentelemetry.trace import Status, StatusCode

from neofin_toobox.configs.otel_tracing.config import define_tracing, setup_span_event
from neofin_toobox.configs.otel_tracing.span_events import SpanEvent


def create_otel_middleware(service_name: str, otel_endpoint: str):
    """
    Factory para criar middleware OpenTelemetry configurado.
    
    Args:
        service_name: Nome do serviço para identificação nos traces
        otel_endpoint: Endpoint do coletor OpenTelemetry
    
    Returns:
        Função middleware configurada
    """
    # Configura o tracer e span events
    tracer = define_tracing(service_name)
    span_event = setup_span_event(tracer, otel_endpoint)
    
    def otel_middleware(event, context=None, get_response: Optional[Callable] = None):
        """
        Middleware universal que detecta e instrumenta diferentes tipos de eventos AWS.
        
        Args:
            event: Evento AWS Lambda ou objeto Request do Chalice
            context: Contexto Lambda (opcional)
            get_response: Função para executar o processamento (opcional para uso em decorators)
        
        Returns:
            Resposta do processamento instrumentada com OpenTelemetry
        """
        
        # Converter o objeto Request em dict para análise
        event_dict = _convert_event_to_dict(event, context)
        
        # Detecta o tipo de evento usando a classe SpanEvent
        event_type = SpanEvent.detect_event_type(event_dict)
        
        # Cria span apropriado para o tipo de evento
        span = span_event.create_span_for_event(event_dict, event_type)
        
        try:
            with span:
                # Adiciona atributos básicos do evento
                span.set_attribute("event.type", event_type)
                
                # Adiciona atributos específicos do Chalice para eventos HTTP
                _add_chalice_attributes(span, event, event_type)
                
                # Adiciona informações do contexto Lambda se disponível
                _add_lambda_context_attributes(span, context)
                
                # Log do evento processado
                logging.info(f"Processando evento do tipo: {event_type}")
                
                # Executa a função
                if get_response:
                    response = get_response(event)
                else:
                    # Para uso como decorator, retorna o event processado
                    response = event
                
                # Adiciona atributos da resposta
                _add_response_attributes(span, response, event_type)
                
                return response
                
        except Exception as e:
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.record_exception(e)
            logging.error(f"Erro processando evento {event_type}: {str(e)}")
            raise
    
    return otel_middleware


def otel_decorator(service_name: str, otel_endpoint: str):
    """
    Decorator para instrumentar funções com OpenTelemetry.
    
    Args:
        service_name: Nome do serviço para identificação nos traces
        otel_endpoint: Endpoint do coletor OpenTelemetry
    
    Returns:
        Decorator configurado
    """
    middleware = create_otel_middleware(service_name, otel_endpoint)
    
    def decorator(func):
        @wraps(func)
        def wrapper(event, context=None, *args, **kwargs):
            def get_response(event):
                return func(event, context, *args, **kwargs)
            
            return middleware(event, context, get_response)
        return wrapper
    return decorator


def _convert_event_to_dict(event, context=None) -> Dict[str, Any]:
    """
    Converte diferentes tipos de eventos em dict para análise.
    
    Args:
        event: Evento AWS Lambda ou objeto Request do Chalice
        context: Contexto Lambda (opcional)
    
    Returns:
        Dict representando o evento
    """
    # Converter o objeto Request em dict para análise
    if hasattr(event, 'to_dict'):
        event_dict = event.to_dict()
    elif hasattr(event, '__dict__'):
        event_dict = event.__dict__
    else:
        # Para eventos HTTP do Chalice, criamos um dict manualmente
        event_dict = {
            'httpMethod': getattr(event, 'method', None),
            'path': getattr(event, 'path', None),
            'headers': getattr(event, 'headers', {}),
            'queryStringParameters': getattr(event, 'query_params', {}),
        }
    
    # Adiciona informações do contexto se disponível  
    if context:
        event_dict['requestContext'] = {
            'requestId': context.aws_request_id,
            'functionName': context.function_name,
            'functionVersion': context.function_version,
        }
    
    return event_dict


def _add_chalice_attributes(span, event, event_type: str):
    """
    Adiciona atributos específicos do Chalice para eventos HTTP.
    
    Args:
        span: Span ativo do OpenTelemetry  
        event: Evento original
        event_type: Tipo do evento detectado
    """
    if event_type == 'http':
        # Adiciona atributos HTTP básicos
        if hasattr(event, 'method'):
            span.set_attribute(SpanAttributes.HTTP_METHOD, event.method)
        if hasattr(event, 'path'):
            span.set_attribute(SpanAttributes.HTTP_TARGET, event.path)
        
        # Adiciona headers importantes (sem dados sensíveis)
        if hasattr(event, 'headers'):
            user_agent = event.headers.get('user-agent', '')
            if user_agent:
                span.set_attribute(SpanAttributes.HTTP_USER_AGENT, user_agent)
            
            content_type = event.headers.get('content-type', '')
            if content_type:
                span.set_attribute('http.request.header.content_type', content_type)


def _add_lambda_context_attributes(span, context):
    """
    Adiciona atributos do contexto Lambda ao span.
    
    Args:
        span: Span ativo do OpenTelemetry
        context: Contexto Lambda
    """
    if context:
        span.set_attribute("faas.execution", context.aws_request_id)
        span.set_attribute("faas.name", context.function_name)
        span.set_attribute("faas.version", context.function_version)
        span.set_attribute("cloud.provider", "aws")
        span.set_attribute("cloud.platform", "aws_lambda")


def _add_response_attributes(span, response, event_type: str):
    """
    Adiciona atributos da resposta ao span.
    
    Args:
        span: Span ativo do OpenTelemetry
        response: Resposta do processamento
        event_type: Tipo do evento detectado
    """
    # Para respostas HTTP, adiciona código de status
    if event_type == 'http' and hasattr(response, 'status_code'):
        span.set_attribute(SpanAttributes.HTTP_STATUS_CODE, response.status_code)
        
        # Define status do span baseado no código HTTP
        if response.status_code >= 400:
            span.set_status(Status(StatusCode.ERROR, f"HTTP {response.status_code}"))
        else:
            span.set_status(Status(StatusCode.OK))
    else:
        # Para outros tipos de eventos, assume sucesso se não houve exceção
        span.set_status(Status(StatusCode.OK))


# Função para compatibilidade com código legado
def otel_middleware():
    """
    Função de compatibilidade para código legado.
    
    DEPRECATED: Use create_otel_middleware() ou otel_decorator() para novas implementações.
    """
    import warnings
    warnings.warn(
        "otel_middleware() está depreciada. Use create_otel_middleware() ou otel_decorator()",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Retorna um middleware com configurações padrão
    return create_otel_middleware("default-service", "http://localhost:4317")
