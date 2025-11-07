import json
import boto3
import os
from datetime import datetime
from boto3.dynamodb.conditions import Key

dynamo = boto3.resource('dynamodb')
tabela = dynamo.Table(os.environ['TABELA_VAGAS'])

def lambda_handler(event, context):
    for record in event['Records']:
        mensagem = json.loads(record['body'])
        evento_id = mensagem['evento_id']
        usuario_id = mensagem['usuario_id']

        # Buscar o registro de controle do evento
        controle = tabela.get_item(
            Key={'evento_id': evento_id, 'tipo': 'controle'}
        ).get('Item')

        if not controle:
            # Se o evento ainda não tiver controle, cria com X ingressos
            tabela.put_item(
                Item={
                    'evento_id': evento_id,
                    'tipo': 'controle',
                    'quantidade_disponivel': 30 # 30 ing.
                }
            )
            controle = {'quantidade_disponivel': 30}

        # Verificar se ainda há ingressos disponíveis
        qtd_atual = controle.get('quantidade_disponivel', 0)
        if qtd_atual <= 0:
            print(f"Ingressos esgotados para {evento_id}.")
            tabela.put_item(
                Item={
                    'evento_id': evento_id,
                    'usuario_id': usuario_id,
                    'tipo': 'compra',
                    'status': 'esgotado',
                    'data_confirmacao': datetime.utcnow().isoformat()
                }
            )
            continue  

        # Atualizar a contagem de ingressos restantes
        nova_qtd = qtd_atual - 1
        tabela.update_item(
            Key={'evento_id': evento_id, 'tipo': 'controle'},
            UpdateExpression='SET quantidade_disponivel = :q',
            ExpressionAttributeValues={':q': nova_qtd}
        )

        # Registrar a compra do usuário
        tabela.put_item(
            Item={
                'evento_id': evento_id,
                'usuario_id': usuario_id,
                'tipo': 'compra',
                'status': 'confirmado',
                'data_confirmacao': datetime.utcnow().isoformat()
            }
        )

        print(f"Ingresso confirmado para {usuario_id}. Restam {nova_qtd} ingressos.")

    return {'status': 'ok'}
