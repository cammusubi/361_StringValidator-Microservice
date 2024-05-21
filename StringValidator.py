import pika
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='StringValidation')


def callback(ch, method, props, body):
    """Microservice function that receives a list with [User's String, Lower Bound
    of acceptable string length, Upper Bound of acceptable string length] and returns
    whether the string is valid or invalid."""
    real_body = json.loads(body)
    user_string = real_body[0]
    string_lower = real_body[1]
    string_upper = real_body[2]
    count = 0
    for char in user_string:
        count += 1
    if count <= string_lower:
        resp = "Too Small"
    elif count >= string_upper:
        resp = "Too Big"
    else:
        resp = "Just Right"
    response = json.dumps(resp)
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id=props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_consume(queue='StringValidation', on_message_callback=callback)
print('Waiting for messages...')
channel.start_consuming()
