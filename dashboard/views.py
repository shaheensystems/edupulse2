from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from edupulse.celery import add
from dashboard.tasks import sub

from django.http import JsonResponse
from celery.result import AsyncResult

# Create your views here.



class DashboardView(LoginRequiredMixin,TemplateView):
    template_name='dashboard/dashboard2.html'

    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        # result=sub.apply_async(args=[20,3])
        result=sub.apply_async(kwargs={ 'y': 3,'x': 20})
        context["result"] = result
        context["task_id"] = result.id
        return context

def student_attendance_engagement_action_report_check_task_status(request):
    student_attendance_engagement_action_report_task_id=request.GET.get('student_attendance_engagement_action_report_task_id')
    result=AsyncResult(student_attendance_engagement_action_report_task_id)
    
    response_data={
        'status':result.status,
        'result':result.result if result.successful() else None
    }
    
def check_task_status(request):
    task_id = request.GET.get('task_id')
    result = AsyncResult(task_id)
    response_data = {
        'status': result.status,
        'result': result.result if result.successful() else None
    }
    return JsonResponse(response_data)
    


def home(request):
    print("result ")
    result =add (5,7)
    print("result : ",result)
    return render(request,'dashboard/dashboard.html')