from django.shortcuts import render

from rest_framework import status, viewsets


from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from delivery.models import DeliveryTask
from delivery.serializers import DeliveryTaskSerializer

from django.contrib.auth import authenticate


class TaskView(APIView):
    def post(self, request, format=None, *args, **kwargs):
        try:
            if request.user.user_profile.user_type==1:
                if hasattr(request.data, 'dict'):
                    data = request.data.dict()
                else:
                    data = request.data

                title = data.pop('title', None)
                priority = data.pop('priority', None)
                state = data.pop('state', None)
                if not title:
                    raise ValueError('title not found')
                if not priority:
                    raise ValueError('priority not found')
                if not state:
                    raise ValueError('state not found')

                DeliveryTask.objects.create(created_by=request.user, title=title, priority=priority, state=state)
                response = {'status':status.HTTP_200_OK, 'message':'Task added'}

            else:
                raise ValueError('You are not authorized to create task!!')

        except ValueError as err:
            response = {'status': status.HTTP_400_BAD_REQUEST, 'error_message': str(err)}
        except RuntimeError as err:
            response = {'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'error_message': str(err)}

        return Response(response, status=response['status'])

    def get(self, request, format=None, *args, **kwargs):
        try:
            task_id = request.GET.get('task_id', None)

            if not task_id:
                if request.user.user_profile.user_type==1:
                    delivery_tasks = DeliveryTask.objects.all()
                    serializer = DeliveryTaskSerializer(delivery_tasks, many=True)
                else:
                    delivery_tasks = DeliveryTask.objects.filter(accepted_by=request.user)
                    serializer = DeliveryTaskSerializer(delivery_tasks, many=True)
            else:
                delivery_task = DeliveryTask.objects.filter(id=task_id).first()
                serializer = DeliveryTaskSerializer(delivery_task)


            response = {'status':status.HTTP_200_OK, 'data':serializer.data}


        except ValueError as err:
            response = {'status': status.HTTP_400_BAD_REQUEST, 'error_message': str(err)}
        except RuntimeError as err:
            response = {'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'error_message': str(err)}

        return Response(response, status=response['status'])

class UpdateTaskState(APIView):
    def post(self, request, format=None, *args, **kwargs):
        try:
            print('ss')
            if hasattr(request.data, 'dict'):
                data = request.data.dict()
            else:
                data = request.data

            task_id = data.pop('task_id', None)
            if not task_id:
                raise ValueError('task_id not found')

            new_state = data.pop('new_state', None)
            print('ssss')

            if new_state:
                if int(new_state) == 5:
                    if request.user.user_profile.user_type==1:
                        delivery_task = DeliveryTask.objects.filter(id=task_id).first()
                        if delivery_task and delivery_task.state == 1:
                            delivery_task.state=new_state
                            delivery_task.save()

                            response = {'status':status.HTTP_200_OK, 'message':'task cancelled'}

                        else:
                            raise ValueError('Task already accepted could not be cancelled')
                    else:
                        raise ValueError('You are not authorized to cancel a task')

                if int(new_state) == 4:
                    if request.user.user_profile.user_type==2:
                        print(new_state)

                        delivery_task = DeliveryTask.objects.filter(id=task_id).first()

                        if delivery_task and delivery_task.state != 3:

                            delivery_task.state=new_state
                            delivery_task.save()
                            response = {'status':status.HTTP_200_OK, 'message':'task declined'}

                        else:
                            raise ValueError('Task already completed could not be declined')
                    else:
                        raise ValueError('You are not authorized to decline a task')
                if int(new_state) == 3:
                    print(new_state)

                    if request.user.user_profile.user_type==2:
                        delivery_task = DeliveryTask.objects.filter(id=task_id).first()
                        if delivery_task and delivery_task.state == 2:
                            delivery_task.state=new_state
                            delivery_task.save()
                            response = {'status':status.HTTP_200_OK, 'message':'task accepted'}

                        else:
                            raise ValueError('Task has not been accepted')
                    else:
                        raise ValueError('You are not authorized to decline a task')



            else:
                raise ValueError('new_state not found')

        except ValueError as err:
            response = {'status': status.HTTP_400_BAD_REQUEST, 'error_message': str(err)}
        except RuntimeError as err:
            response = {'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'error_message': str(err)}

        return Response(response, status=response['status'])

class TaskGetView(APIView):
    def get(self, request):
        task_with_hp = Task.objects.filter(priority=1, task_state=1).order_by('created_on').first()
        if task_with_hp:
            serializer = TaskSerializer(task_with_hp)
            return Response(serializer.data)
        else:
            task_with_mp = Task.objects.filter(priority=2, task_state=1).order_by('created_on').first()
            if task_with_mp:
                serializer = TaskSerializer(task_with_mp)
                return Response(serializer.data)
            else:
                lp_task = Task.objects.filter(priority=3, task_state=1).order_by('created_on').first()
                if lp_task:
                    serializer = TaskSerializer(task_with_lp)
                    return Response(serializer.data)
        return Response(
            {"message": "No new task available"})

# Authentication views
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request, format=None, *args, **kwargs):
        try:
            if hasattr(request.data, 'dict'):
                data = request.data.dict()
            else:
                data = request.data

            username = data.pop('username', None)
            password = data.pop('password', None)



            if not username:
                raise ValueError('username not found')
            if not password:
                raise ValueError('password not found')

            user = authenticate(username=username, password=password)
            if not user:
                return Response({'error': 'Invalid Credentials'},
                                status=status.HTTP_404_NOT_FOUND)
            token, _ = Token.objects.get_or_create(user=user)

            response = {'token': token.key, 'status': status.HTTP_200_OK}

        except User.DoesNotExist as err:
            response = {'status': status.HTTP_400_BAD_REQUEST, 'error_message': 'User does not exist'}
        except ValueError as err:
            response = {'status': status.HTTP_400_BAD_REQUEST, 'error_message': str(err)}
        except RuntimeError as err:
            response = {'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'error_message': str(err)}

        return Response(response, status=response['status'])

class LogoutView(APIView):
    def post(self, request, format=None, *args, **kwargs):
        try:
            user = request.user
            if not user:
                raise ValueError('user not found')
            Token.objects.get(user=user).delete()
            response = {'message': "Logged out successfully", 'status': status.HTTP_200_OK}
        except ValueError as err:
            response = {'status': status.HTTP_400_BAD_REQUEST, 'error_message': str(err)}
        except RuntimeError as err:
            response = {'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'error_message': str(err)}

        return Response(response, status=response['status'])
