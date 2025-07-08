import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from orders.models import Order

class AdminOrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Check if user is staff
        if self.scope["user"].is_anonymous or not (self.scope["user"].is_staff or self.scope["user"].is_superuser):
            await self.close()
        else:
            # Join admin orders group
            self.room_group_name = 'admin_orders'
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        # Leave admin orders group
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'get_orders':
            # Send current orders to this specific client
            orders = await self.get_current_orders()
            await self.send(text_data=json.dumps({
                'type': 'orders_list',
                'orders': orders
            }))

    async def new_order(self, event):
        # Send new order notification to admin
        await self.send(text_data=json.dumps({
            'type': 'new_order',
            'order': event['order']
        }))

    async def order_update(self, event):
        # Send order update to admin
        await self.send(text_data=json.dumps({
            'type': 'order_update',
            'order': event['order']
        }))

    async def counter_payment_notification(self, event):
        # Send counter payment notification to admin
        await self.send(text_data=json.dumps({
            'type': 'counter_payment_notification',
            'notification': event['notification']
        }))

    @database_sync_to_async
    def get_current_orders(self):
        orders = Order.objects.filter(
            status__in=['pending', 'confirmed', 'preparing']
        ).select_related('customer', 'table').order_by('-created_at')[:20]
        
        orders_data = []
        for order in orders:
            orders_data.append({
                'id': order.id,
                'customer': order.customer.username,
                'table_number': order.table.table_number,
                'status': order.status,
                'status_display': order.get_status_display(),
                'total_amount': str(order.total_amount),
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        return orders_data