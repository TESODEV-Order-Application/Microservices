import pika
import json
import asyncio
import os

from MongoDB import mongodb

username = os.getenv('rabbit_username')
password = os.getenv('rabbit_password')
ip = os.getenv('ip')

async def save_to_mongodb(order_data): 
    await mongodb.collections['AuditLog'].insert_one(order_data)

def callback(ch, method, properties, body):
    order_data = json.loads(body)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(save_to_mongodb(order_data))
    ch.basic_ack(delivery_tag=method.delivery_tag)

def consume():
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
    
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='order_audit_log', on_message_callback=callback)
    
    print(' [*] Waiting for messages. To exit press CTRL+C') 
    channel.start_consuming()

if __name__ == "__main__":
    consume()