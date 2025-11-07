import json
import boto3
import os
from datetime import datetime

dynamo = boto3.resource('dynamodb')
tabela = dynamo.Table(os.environ['TABELA_VAGAS'])

def lambda_handler(event, context):
    for record in event['Records']:
        mensagem = json.loads(record['body'])
        
        # lógica do pagamento
        tabela.put_item(
            Item={
                'evento_id': mensagem['evento_id'],
                'usuario_id': mensagem['usuario_id'],
                'status': 'confirmado',
                'data_confirmacao': datetime.utcnow().isoformat()
            }
        )
    return {'status': 'ok'}
