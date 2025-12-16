from typing import Dict, Any, Optional
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.trace import SpanAttributes

class SpanEvent:
    def __init__(self, tracer: trace.Tracer, otel: str):
        self.tracer = tracer
        self.otel = otel

    @staticmethod
    def detect_event_type(event: Dict[str, Any]) -> str:
      """Detecta o tipo de evento AWS baseado na estrutura do evento."""

      # Evento HTTP (API Gateway)
      if 'httpMethod' in event or 'requestContext' in event:
          return 'http'

      # Evento SQS
      if 'Records' in event and event['Records']:
          record = event['Records'][0]
          if 'eventSource' in record and record['eventSource'] == 'aws:sqs':
              return 'sqs'
          # Evento S3
          elif 'eventSource' in record and record['eventSource'] == 'aws:s3':
              return 's3'
          # Evento DynamoDB
          elif 'eventSource' in record and record['eventSource'] == 'aws:dynamodb':
              return 'dynamodb'
          # Evento SNS
          elif 'EventSource' in record and record['EventSource'] == 'aws:sns':
              return 'sns'

      # Evento CloudWatch (Schedule/EventBridge)
      if 'source' in event and event['source'] == 'aws.events':
          return 'eventbridge'

      # Evento de Schedule/Cron
      if 'detail-type' in event and event['detail-type'] == 'Scheduled Event':
          return 'schedule'

      # Evento genérico
      return 'unknown'

    def create_span_for_event(self, event: Dict[str, Any], event_type: str) -> Any:
        """Cria um span personalizado baseado no tipo de evento."""

        if event_type == 'http':
            return self.create_http_span(event)
        elif event_type == 'sqs':
            return self.create_sqs_span(event)
        elif event_type == 's3':
            return self.create_s3_span(event)
        elif event_type == 'dynamodb':
            return self.create_dynamodb_span(event)
        elif event_type == 'sns':
            return self.create_sns_span(event)
        elif event_type == 'eventbridge':
            return self.create_eventbridge_span(event)
        elif event_type == 'schedule':
            return self.create_schedule_span(event)
        else:
            return self.create_generic_span(event, event_type)

    def create_http_span(self, event: Dict[str, Any]) -> Any:
        """Cria span para eventos HTTP."""
        span = self.tracer.start_span("http_request")

        if 'httpMethod' in event:
            span.set_attribute(SpanAttributes.HTTP_METHOD, event['httpMethod'])
        if 'path' in event:
            span.set_attribute(SpanAttributes.HTTP_TARGET, event['path'])
        if 'requestContext' in event and 'requestId' in event['requestContext']:
            span.set_attribute("aws.request_id", event['requestContext']['requestId'])

        return span

    def create_sqs_span(self, event: Dict[str, Any]) -> Any:
        """Cria span para eventos SQS."""
        span = self.tracer.start_span("sqs_message_processing")

        if 'Records' in event and event['Records']:
            record = event['Records'][0]
            span.set_attribute("messaging.system", "sqs")
            span.set_attribute("messaging.operation", "process")

            if 'eventSourceARN' in record:
                queue_name = record['eventSourceARN'].split(':')[-1]
                span.set_attribute("messaging.destination.name", queue_name)
                span.set_attribute("aws.sqs.queue_name", queue_name)

            if 'messageId' in record:
                span.set_attribute("messaging.message.id", record['messageId'])

            if 'body' in record:
                # Não loggar o body completo por segurança, apenas o tamanho
                span.set_attribute("messaging.message.body_size", len(record['body']))

            span.set_attribute("aws.sqs.message_count", len(event['Records']))

        return span

    def create_s3_span(self, event: Dict[str, Any]) -> Any:
        """Cria span para eventos S3."""
        span = self.tracer.start_span("s3_event_processing")

        if 'Records' in event and event['Records']:
            record = event['Records'][0]

            if 's3' in record:
                s3_info = record['s3']

                if 'bucket' in s3_info and 'name' in s3_info['bucket']:
                    span.set_attribute("aws.s3.bucket", s3_info['bucket']['name'])

                if 'object' in s3_info and 'key' in s3_info['object']:
                    span.set_attribute("aws.s3.key", s3_info['object']['key'])

                if 'object' in s3_info and 'size' in s3_info['object']:
                    span.set_attribute("aws.s3.object_size", s3_info['object']['size'])

            if 'eventName' in record:
                span.set_attribute("aws.s3.event_name", record['eventName'])

        return span

    def create_dynamodb_span(self, event: Dict[str, Any]) -> Any:
        """Cria span para eventos DynamoDB."""
        span = self.tracer.start_span("dynamodb_stream_processing")

        if 'Records' in event and event['Records']:
            record = event['Records'][0]

            if 'eventName' in record:
                span.set_attribute("aws.dynamodb.event_name", record['eventName'])

            if 'dynamodb' in record:
                dynamodb_info = record['dynamodb']

                if 'StreamViewType' in dynamodb_info:
                    span.set_attribute("aws.dynamodb.stream_view_type", dynamodb_info['StreamViewType'])

            if 'eventSourceARN' in record:
                # Extrair nome da tabela do ARN
                table_name = record['eventSourceARN'].split('/')[-3]
                span.set_attribute("aws.dynamodb.table_name", table_name)

        return span

    def create_sns_span(self, event: Dict[str, Any]) -> Any:
        """Cria span para eventos SNS."""
        span = self.tracer.start_span("sns_message_processing")

        if 'Records' in event and event['Records']:
            record = event['Records'][0]

            if 'Sns' in record:
                sns_info = record['Sns']

                if 'TopicArn' in sns_info:
                    topic_name = sns_info['TopicArn'].split(':')[-1]
                    span.set_attribute("messaging.destination.name", topic_name)
                    span.set_attribute("aws.sns.topic_name", topic_name)

                if 'MessageId' in sns_info:
                    span.set_attribute("messaging.message.id", sns_info['MessageId'])

                if 'Subject' in sns_info:
                    span.set_attribute("aws.sns.subject", sns_info['Subject'])

        return span

    def create_eventbridge_span(self, event: Dict[str, Any]) -> Any:
        """Cria span para eventos EventBridge."""
        span = self.tracer.start_span("eventbridge_event_processing")

        if 'source' in event:
            span.set_attribute("aws.eventbridge.source", event['source'])

        if 'detail-type' in event:
            span.set_attribute("aws.eventbridge.detail_type", event['detail-type'])

        if 'account' in event:
            span.set_attribute("aws.account_id", event['account'])

        if 'region' in event:
            span.set_attribute("aws.region", event['region'])

        return span

    def create_schedule_span(self, event: Dict[str, Any]) -> Any:
        """Cria span para eventos de schedule/cron."""
        span = self.tracer.start_span("schedule_event_processing")

        if 'detail-type' in event:
            span.set_attribute("aws.schedule.type", event['detail-type'])

        if 'resources' in event and event['resources']:
            span.set_attribute("aws.schedule.rule", event['resources'][0])

        return span

    def create_generic_span(self, event: Dict[str, Any], event_type: str) -> Any:
        """Cria span genérico para eventos não identificados."""
        span = self.tracer.start_span(f"{event_type}_event_processing")

        # Adiciona alguns atributos básicos se disponíveis
        if 'account' in event:
            span.set_attribute("aws.account_id", event['account'])

        if 'region' in event:
            span.set_attribute("aws.region", event['region'])

        # Log do evento para debug (apenas estrutura, não dados sensíveis)
        span.set_attribute("event.keys", ",".join(event.keys()))

        return span

