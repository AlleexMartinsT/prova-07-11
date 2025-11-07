import json
import boto3
import os
import time

sqs = boto3.client('sqs')

def lambdaHander(event, context):
    body = json.loads(event['body'])
    usuarioID = body.get('usuario_id')
    eventoID = body.get('evento_id')

    mensagem = {
        'usuario_id': usuarioID,
        'evento_id': eventoID,
        'timestamp': int(time.time())
    }

    sqs.send_message(
        QueueUrl=os.environ['FILA_URL'],
        MessageBody=json.dumps(mensagem)
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'mensagem': 'Compra recebida. Processando pagamento...'})
    }
