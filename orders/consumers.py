import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Order

class CustomerOrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check if user is authenticated
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            # Join customer's personal order group
            self.user_id = self.scope["user"].id
            self.room_group_name = f'customer_orders_{self.user_id}'
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        # Leave customer's personal order group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'get_orders':
            # Send current orders to this specific customer
            orders = await self.get_customer_orders()
            await self.send(text_data=json.dumps({
                'type': 'orders_list',
                'orders': orders
            }))

    async def order_status_update(self, event):
        # Send order status update to customer
        await self.send(text_data=json.dumps({
            'type': 'order_status_update',
            'order': event['order']
        }))

    async def new_order_notification(self, event):
        # Send new order notification to customer (when they place an order)
        await self.send(text_data=json.dumps({
            'type': 'new_order_notification',
            'order': event['order']
        }))

    @database_sync_to_async
    def get_customer_orders(self):
        orders = Order.objects.filter(
            customer_id=self.user_id
        ).select_related('customer', 'table').order_by('-created_at')[:20]
        
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.id,
                'status': order.status,
                'status_display': order.get_status_display(),
                'total_amount': str(order.total_amount),
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'table_number': order.table.table_number,
            })
        
        return orders_data