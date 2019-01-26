import asyncio
import json
from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from delivery.models import Task
from delivery.serializers import TaskSerializer


class DeliveryConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        await self.channel_layer.group_add("task_manager", self.channel_name)

        await self.send({
            "type": "websocket.accept",
        })

    async def websocket_receive(self, event):
        tasks = {}
        text = event.get('text', None)
        if text is not None:
            text = json.loads(text)
            if text['type'] == "get_updated_tasks":
                tasks = await self.get_tasks()
                await self.channel_layer.group_send(
                    "task_management",
                    {
                        "type": "task_details",
                        "text": json.dumps(tasks)
                    }
                )
            if text['type'] == "getcreatedTasks":
                task_id = text['task_id']

                tasks = await self.get_created_tasks(task_id)
                await self.channel_layer.group_send(
                    "task_manager",
                    {
                        "type": "task_details",
                        "text": json.dumps(tasks)
                    }
                )

    async def task_details(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event["text"]
        })

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            "task_managemer", self.channel_name)

    @database_sync_to_async
    def get_tasks(self):
        hp_task = Task.objects.filter(priority=1, task_state=1).order_by('created_on').first()
        if hp_task:
            serializer = TaskSerializer(hp_task)
            self.data = serializer.data
            return serializer.data
        else:
            mp_task = Task.objects.filter(
                priority=2, task_state=1).order_by('created_on').first()
            if mp_task:
                serializer = TaskSerializer(mp_task)
                return serializer.data
            else:
                lp_task = Task.objects.filter(
                    priority=3, task_state=1).order_by('created_on').first()
                if lp_task:
                    serializer = TaskSerializer(lp_task)
                    return serializer.data

    @database_sync_to_async
    def get_created_tasks(self, task_id):
        task = Task.objects.get(id=task_id)
        tasks = Task.objects.filter(created_by=task.created_by)
        serializer = TaskSerializer(tasks, many=True)
        return serializer.data
