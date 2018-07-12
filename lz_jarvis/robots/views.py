from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.viewsets import ViewSet
from rest_framework.exceptions import ValidationError

from robots.tasks import google, duck, yahoo, bing, sendmail

from celery import group, chord, chain

from robots.models import RSeoStatus, TaskRun
from robots.api.serializers import (TaskResultSerializer, TaskResultStatusSerializer,
                                    TaskRunSerializer, TaskRunStateSerializer)
from robots.api.permissions import IsOwnerOrReadOnly

from django_celery_results.models import TaskResult

robot_info = {
    "keyword": "pizzeta",
    "domain": "pizzeria.com",
    "google": True,
    "yahoo": True,
    "bing": True,
    "duckduck": True,
    "destination": "pruebadajngo@gmail.com"
}


class TaskResultViewSet(ViewSet):

    def list(self, request):
        results = TaskResult.objects.all()
        serializer = TaskResultSerializer(results,
                                          context={'request': request},
                                          many=True
                                          )
        return JsonResponse(serializer.data, safe=False, status=200)

    def retrieve(self, request, task_id):
        try:
            result = TaskResult.objects.get(task_id=task_id)
        except ObjectDoesNotExist:
            raise ValidationError(detail='Task don\'t found')
        else:
            serializer = TaskResultStatusSerializer(result,
                                                    context={'request': request}
                                                    )
            return JsonResponse(serializer.data, status=200)


task_result_list = TaskResultViewSet.as_view(
    {'get': 'list'}
)

task_result_detail = TaskResultViewSet.as_view(
    {'get': 'retrieve'}
)


class TaskOptions(ViewSet):
    permission_classes = (IsOwnerOrReadOnly,)

    def create(self, request, *args, **kwargs):

        rseo = request.data

        tasks_exec = (google, yahoo, bing, duck, )

        browser_nav = list(filter(lambda x: request.data[x] is True, ('google', 'yahoo', 'duckduck', 'bing', )))

        chord((task.s(keyword=request.data['keyword']) for task in tasks_exec if task.name in browser_nav))(sendmail.s())


        return JsonResponse({'message': 'Task send successfully'})

    def list(self, request):
        tasks = TaskRun.objects.all()
        serializer = TaskRunSerializer(tasks,
                                       context={'request': request},
                                       many=True)
        return JsonResponse(serializer.data, status=200, safe=False)

    def status(self, request, task_id):
        try:
            task = TaskRun.objects.get(task_id=task_id)
        except ObjectDoesNotExist:
            raise ValidationError(detail='Task not found')
        else:
            serializer = TaskRunStateSerializer(task, context={'request': request})
            return JsonResponse(serializer.data, status=200)


run_task = TaskOptions.as_view(
    {'post': 'create'}
)

task_execution_list = TaskOptions.as_view(
    {'get': 'list'}
)

task_execution_detail = TaskOptions.as_view(
    {'get': 'status'}
)
