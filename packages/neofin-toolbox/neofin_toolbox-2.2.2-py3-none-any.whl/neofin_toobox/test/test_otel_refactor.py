#!/usr/bin/env python3
"""
Teste simples para verificar a funcionalidade do middleware refatorado.
"""

import os
import sys
from unittest.mock import Mock, patch

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_middleware_import():
    """Testa se os imports estão funcionando."""
    try:
        from neofin_toobox.configs.otel_tracing.otel_middleware import (
            create_otel_middleware, 
            otel_decorator, 
            otel_middleware
        )
        from neofin_toobox.configs.otel_tracing.span_events import SpanEvent
        print("✅ Imports funcionando corretamente")
        return True
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        return False

def test_span_event_detect_type():
    """Testa a detecção de tipos de evento."""
    try:
        from neofin_toobox.configs.otel_tracing.span_events import SpanEvent
        
        # Teste evento HTTP
        http_event = {
            'httpMethod': 'GET',
            'path': '/test',
            'headers': {'content-type': 'application/json'}
        }
        event_type = SpanEvent.detect_event_type(http_event)
        assert event_type == 'http', f"Esperado 'http', obtido '{event_type}'"
        
        # Teste evento SQS
        sqs_event = {
            'Records': [{
                'eventSource': 'aws:sqs',
                'messageId': '123',
                'body': 'test message'
            }]
        }
        event_type = SpanEvent.detect_event_type(sqs_event)
        assert event_type == 'sqs', f"Esperado 'sqs', obtido '{event_type}'"
        
        # Teste evento desconhecido
        unknown_event = {'some': 'data'}
        event_type = SpanEvent.detect_event_type(unknown_event)
        assert event_type == 'unknown', f"Esperado 'unknown', obtido '{event_type}'"
        
        print("✅ Detecção de tipos de evento funcionando")
        return True
    except Exception as e:
        print(f"❌ Erro na detecção de tipos: {e}")
        return False

def test_middleware_creation():
    """Testa a criação do middleware."""
    try:
        with patch('neofin_toobox.configs.otel_tracing.otel_middleware.define_tracing') as mock_tracer, \
             patch('neofin_toobox.configs.otel_tracing.otel_middleware.setup_span_event') as mock_span:
            
            from neofin_toobox.configs.otel_tracing.otel_middleware import create_otel_middleware
            
            # Mock dos objetos
            mock_tracer.return_value = Mock()
            mock_span.return_value = Mock()
            
            # Criar middleware
            middleware = create_otel_middleware("test-service", "http://localhost:4317")
            
            # Verificar se é uma função
            assert callable(middleware), "Middleware deve ser uma função"
            
            # Verificar se as funções de configuração foram chamadas
            mock_tracer.assert_called_once_with("test-service")
            mock_span.assert_called_once_with(mock_tracer.return_value, "http://localhost:4317")
            
            print("✅ Criação do middleware funcionando")
            return True
    except Exception as e:
        print(f"❌ Erro na criação do middleware: {e}")
        return False

def test_decorator():
    """Testa o decorator."""
    try:
        with patch('neofin_toobox.configs.otel_tracing.otel_middleware.define_tracing') as mock_tracer, \
             patch('neofin_toobox.configs.otel_tracing.otel_middleware.setup_span_event') as mock_span:
            
            from neofin_toobox.configs.otel_tracing.otel_middleware import otel_decorator
            
            mock_tracer.return_value = Mock()
            mock_span.return_value = Mock()
            
            # Criar decorator
            decorator = otel_decorator("test-service", "http://localhost:4317")
            assert callable(decorator), "Decorator deve ser uma função"
            
            # Aplicar decorator a uma função
            @decorator
            def test_function(event, context):
                return {"status": "ok"}
            
            assert callable(test_function), "Função decorada deve ser callable"
            
            print("✅ Decorator funcionando")
            return True
    except Exception as e:
        print(f"❌ Erro no decorator: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("🧪 Testando middleware OpenTelemetry refatorado...\n")
    
    tests = [
        test_middleware_import,
        test_span_event_detect_type,
        test_middleware_creation,
        test_decorator
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Erro inesperado no teste {test.__name__}: {e}")
    
    print(f"\n📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Refatoração bem-sucedida.")
        return True
    else:
        print("⚠️  Alguns testes falharam. Verifique os erros acima.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
