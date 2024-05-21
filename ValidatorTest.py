# # starts a local RabbitMQ node
# brew services start rabbitmq
#
# # highly recommended: enable all feature flags on the running node
# /opt/homebrew/sbin/rabbitmqctl enable_feature_flag all

import pika, json, uuid

class StringValidatorClient(object):
    """Class used to send data to/receive data from the StringValidator microservice, via the .call()
    function. As shown in the example iteration below, .call takes one parameter, a list containing: a user's string,
    a lower bound of acceptability, and an upper bound of acceptability."""

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, string_list):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='StringValidation',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=str(string_list))
        while self.response is None:
            self.connection.process_data_events(time_limit=None)
        return self.response

# EXAMPLE IMPLEMENTATION BELOW

# stringvalidator_rpc = StringValidatorClient()
# test_string = "Do your homework"
# test_lower = 0
# test_upper = 40
# test_body = [test_string, test_lower, test_upper]
# send_body = json.dumps(test_body)
# response = stringvalidator_rpc.call(send_body)
# print(response)
# jresp = json.loads(response)
# print(jresp)
# if jresp == "Just Right":
#     print("yay")
# else:
#     print("nay")
