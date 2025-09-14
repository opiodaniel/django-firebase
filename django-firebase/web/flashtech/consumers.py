# In flashtech/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ClientScreenConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'client_screen_group'
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # We need to handle ping messages from the new front-end
    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('action') == 'ping':
            # Optionally send a pong back
            await self.send(text_data=json.dumps({'action': 'pong'}))

    # This method is what gets called from the view function
    async def send_order_details(self, event):
        """
        Sends the client data to the connected WebSocket in the
        format the new frontend expects.
        """
        order_details = event['order_details']

        # New message structure to match the frontend
        await self.send(text_data=json.dumps({
            'type': 'order_updated',
            'data': order_details
        }))


    async def send_reset_message(self, event):
        """
        Sends a reset message to the client screen to revert to the default state.
        """
        await self.send(text_data=json.dumps({
            'type': 'reset',
        }))
