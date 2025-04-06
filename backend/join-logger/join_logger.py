import pika
import json

def callback(ch, method, properties, body):
    message = json.loads(body)
    print(f"📥 LOG: Player {message['player_id']} joined Team {message['team_id']} in Tournament {message['tournament_id']} at {message['timestamp']}")

connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='player_events', durable=True)
channel.basic_consume(queue='player_events', on_message_callback=callback, auto_ack=True)

print("🔁 join_logger is listening for player events...")
channel.start_consuming()
