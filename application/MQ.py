import json
from datetime import datetime

from application.ext import RabbitMQ_channel, async
from config import 国恒信创采集MQ, logger


class Pro:

    def __init__(self, RabbitMQconfig):
        self.channel = RabbitMQ_channel(RabbitMQconfig)

    def send(self, queue, data):
        self.channel.basic_publish(
            exchange='',
            routing_key=queue,
            # body=serialized_value(data),
            body=json.dumps(data, ensure_ascii=False),
        )


class Cus:
    queue = 国恒信创采集MQ.Q.vdq

    def __init__(self, RabbitMQconfig):
        self.channel = RabbitMQ_channel(RabbitMQconfig)

    @staticmethod
    def callback(ch, method, properties, body):
        # ch.basic_ack(delivery_tag=method.delivery_tag)
        data = json.loads(body.decode())
        print(data)
        print(type(data))
        print(f'==========={datetime.now()}============')
        print()

    @async
    def run(self):
        self.channel.queue_declare(queue=self.queue)
        # self.channel.basic_consume(self.queue, self.callback)
        self.channel.basic_consume(
            queue=self.queue,
            on_message_callback=self.callback,
            auto_ack=True
        )
        # 开始接收信息，并进入阻塞状态，队列里有信息才会调用callback进行处理
        self.channel.start_consuming()



if __name__ == '__main__':
    consumer = Cus(国恒信创采集MQ.config)
    consumer.run()
    # pro = Pro(国恒信创采集MQ.config)
    # data = dict(
    #     abc='abc',
    #     time=str(datetime.now())
    # )
    # q = 'test'
    # pro.send(q, data)
    # print(666)
