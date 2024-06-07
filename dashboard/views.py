from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from edupulse.celery import add
from dashboard.tasks import sub,sub2

from django.http import JsonResponse
from celery.result import AsyncResult
from report.models import Attendance
import json
from django.core.serializers.json import DjangoJSONEncoder

# Create your views here.



class DashboardView(LoginRequiredMixin,TemplateView):
    template_name='dashboard/dashboard.html'

    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        # result=sub.apply_async(args=[20,3])
        result=sub.apply_async(kwargs={ 'y': 3,'x': 20})
        context["result"] = result
        context["task_id"] = result.id
        
        
        
        
        result_attendance_report=sub2.apply_async(kwargs={"y":17, "x":32})
        attendances=Attendance.objects.all()
        # result_attendance_report=sub2.apply_async(kwargs={"attendances":attendances})
        context['result_attendance_report']=result_attendance_report
        context['result_attendance_report_task_id']=result_attendance_report.id
        

        return context

def check_status_attendance_status_report_chart_data(request):
    task_id=request.GET.get('result_attendance_report_task_id')
    # task_id=request.GET.get('task_id')
    result=AsyncResult(task_id)
    response_data={
        'status':result.status,
        'result':result.result if result.successful() else None
    }
    
    return JsonResponse(response_data)
    
def check_task_status(request):
    task_id = request.GET.get('task_id')
    result = AsyncResult(task_id)
    response_data = {
        'status': result.status,
        'result': result.result if result.successful() else None
    }
    return JsonResponse(response_data)
    

