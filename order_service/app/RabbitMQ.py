import pika
import json
from bson import Binary
from datetime import datetime
import uuid
import os

username = os.getenv('rabbit_username')
password = os.getenv('rabbit_password')
ip = os.getenv('ip')

def encodeSpecialFields(orderData):
    for key, value in orderData.items():
        if isinstance(value, Binary):
            orderData[key] = str(uuid.UUID(bytes=value))
        elif isinstance(value, datetime):
            orderData[key] = value.isoformat()
        elif isinstance(value, dict):
            encodeSpecialFields(value)
    return orderData

def publishMessage(orderData: dict): 
    orderData = encodeSpecialFields(orderData)
    
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=ip,
            port=5672,
            virtual_host='/',
            credentials=pika.PlainCredentials(username, password)
        )
    )
    channel = connection.channel()
    
    channel.queue_declare(queue='order_audit_log', durable=True)
    
    message = json.dumps(orderData)
    channel.basic_publish(
        exchange='',
        routing_key='order_audit_log',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )
    
    connection.close()