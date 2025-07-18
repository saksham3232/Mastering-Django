from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import TemplateView, FormView, CreateView
from django.core.exceptions import ValidationError
from firstapp.forms import ContactUsForm, RegistrationForm, RegistrationFormSeller2
from django.urls import reverse_lazy
from firstapp.models import SellerAdditional, CustomUser
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


def index(request):
    context = {
        'age': 25,
        'array': [1, 2, 3, 4, 5],
        'dic': {'name': 'Saksham', 'age': 22, 'city': 'Lucknow'}
    }
    return render(request, 'seller/index.html', context)


class LoginViewUser(LoginView):
    template_name = 'seller/login.html'


class RegisterViewSeller(LoginRequiredMixin, CreateView):
    template_name = 'seller/register.html'
    form_class = RegistrationFormSeller2
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        user = self.request.user
        user.type.append(user.Types.SELLER)
        user.save()
        form.instance.user = self.request.user
        return super().form_valid(form)
    

class LogoutViewUser(LogoutView):
    # success_url = reverse_lazy('index')
    next_page = reverse_lazy('index')


class RegisterView(CreateView):
    template_name = 'seller/registerbaseuser.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('index')