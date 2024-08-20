import pika
import json
import base64
from bson import Binary
from datetime import datetime


def encodeSpecialFields(orderData):
    for key, value in orderData.items():
        if isinstance(value, Binary):
            orderData[key] = base64.b64encode(value).decode('utf-8')
        elif isinstance(value, datetime):
            orderData[key] = value.isoformat()  # Convert datetime to ISO 8601 string
        elif isinstance(value, dict):
            encodeSpecialFields(value)
    return orderData

def publishMessage(orderData: dict): 
    orderData = encodeSpecialFields(orderData)
    
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host='193.164.4.17',
            port=5672,
            virtual_host='/',
            credentials=pika.PlainCredentials('guest', 'Xdm@LtkdEoa5FHkM')
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