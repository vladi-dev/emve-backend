import json
import gevent

from app import app, redis_client, REDIS_CHAN


class WebsocketEventService(object):
    """Interface for registering and updating WebSocket clients."""
    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                # app.logger.info(u'Sending message: {}'.format(data))
                yield data

    def register(self, client):
        """Register a WebSocket connection for Redis updates."""
        # app.logger.info(u'Registered...')
        self.clients.append(client)

    def send(self, client, data):
        """Send given data to the registered client.
        Automatically discards invalid connections."""
        try:
            # app.logger.info(u'Sending: ' + data)
            client.send(data)
        except Exception as e:
            app.logger.info(u'Client removed')
            self.clients.remove(client)

    def run(self):
        """Listens for new messages in Redis, and sends them to clients."""
        self.clients = list()
        self.pubsub = redis_client.pubsub()
        self.pubsub.subscribe(REDIS_CHAN)
        for data in self.__iter_data():
            for client, id in self.clients:
                if data:
                    msg = json.loads(data)
                    if not 'user_id' in msg or id == msg['user_id']:
                        gevent.spawn(self.send, client, json.dumps(msg))

    def start(self):
        """Maintains Redis subscription in the background."""
        gevent.spawn(self.run)

