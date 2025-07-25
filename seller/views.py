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
    # context = {
    #     'age': 25,
    #     'array': [1, 2, 3, 4, 5],
    #     'dic': {'name': 'Saksham', 'age': 22, 'city': 'Lucknow'}
    # }
    return render(request, 'seller/index.html')



from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import localtime

class ContactUs(FormView):
    form_class = ContactUsForm
    template_name = 'seller/contactus.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        query = form.cleaned_data.get('query')

        # ✅ Check if query length is less than 10
        if len(query) < 10:
            form.add_error('query', 'Query must be at least 10 characters long')
            return render(self.request, 'firstapp/contactus2.html', {'form': form})

        # ✅ Save to DB
        form.save()

        # ✅ Prepare email
        subject = '📩 New Contact Form Submission'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = ['sakshammaurya678@gmail.com']
        context = {
            'name': form.cleaned_data.get('name'),
            'email': form.cleaned_data.get('email'),
            'phone': form.cleaned_data.get('phone'),
            'query': query,
            'timestamp': localtime(timezone.now()).strftime('%d %B %Y, %I:%M %p'),
        }

        # ✅ Load HTML template for email
        html_content = render_to_string('firstapp/email_template.html', context)
        text_content = f"""
        New contact form submission:

        Name: {context['name']}
        Email: {context['email']}
        Phone: {context['phone']}
        Query: {context['query']}
        """

        # ✅ Send email
        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)

        return super().form_valid(form)


    def form_invalid(self, form):
        query = form.cleaned_data.get('query')
        
        # ✅ Correct condition: show error if query is too short
        if query and len(query) < 10:
            form.add_error('query', 'Query must be at least 10 characters long')
        
        return render(self.request, 'firstapp/contactus2.html', {'form': form})





class LoginViewUser(LoginView):
    template_name = 'seller/login.html'

    def get_success_url(self):
        return self.get_redirect_url() or reverse_lazy('index')



class SellerLoginView(LoginView):
    template_name = 'seller/sellerlogin.html'  # ✅ Use a different template (you can duplicate the normal one)

    def form_valid(self, form):
        user = form.get_user()
        if CustomUser.Types.SELLER not in user.type:
            form.add_error(None, "You are not authorized to login as a seller.")
            return self.form_invalid(form)
        return super().form_valid(form)


from django.contrib import messages
from django.shortcuts import redirect

class RegisterViewSeller(LoginRequiredMixin, CreateView):
    template_name = 'seller/register.html'
    form_class = RegistrationFormSeller2
    success_url = reverse_lazy('index')
    login_url = reverse_lazy('login')  # Optional: overrides settings.LOGIN_URL

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if SellerAdditional.objects.filter(user=request.user).exists():
                messages.info(request, "You are already registered as a seller.")
                return redirect('index')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        if user.Types.SELLER not in user.type:
            user.type.append(user.Types.SELLER)
            user.save()
        form.instance.user = user
        return super().form_valid(form)




class LogoutViewUser(LogoutView):
    # success_url = reverse_lazy('index')
    next_page = reverse_lazy('index')


class RegisterView(CreateView):
    template_name = 'seller/registerbaseuser.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('index')