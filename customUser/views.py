from django.shortcuts import render
from django.contrib.auth.views import LoginView,LogoutView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.
class UserLoginView(LoginView):
    redirect_authenticated_user=True
    success_url=reverse_lazy("dashboard")
    template_name="auth/login.html"

    def form_invalid(self, form):
        print ("Invalid Login Credentials ")
        messages.error(self.request, " Invalid username or password")
        return self.render_to_response(self.get_context_data(form=form))
    

class UserLogOutView(LoginRequiredMixin,LogoutView):
    success_url=reverse_lazy('dashboard')
    template_name='auth/logout.html'