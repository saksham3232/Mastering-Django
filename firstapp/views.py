from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.views.generic import TemplateView, FormView, CreateView, ListView, DeleteView, DetailView, UpdateView
from django.core.exceptions import ValidationError
from .forms import ContactUsForm, RegistrationForm, RegistrationFormSeller2, CartForm
from django.urls import reverse_lazy
from .models import SellerAdditional, CustomUser, Product, ProductInCart, Cart
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin


from firstproject import settings
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
# def index(request):
#     age = 18
#     arr = ['saksham', 'vinay', 'shubham', 'amit']
#     dic = {'name': 'saksham', 'age': 18, 'city': 'jaunpur'}
#     return render(request, 'firstapp/index.html', {'age': age, 'array': arr, 'dic': dic})
#     # return HttpResponse("<h1>This is my first Django app</h1>")


class Index(TemplateView):
    template_name = 'firstapp/index.html'

    def get_context_data(self, **kwargs):
        age = 18
        arr = ['saksham', 'vinay', 'shubham', 'amit']
        dic = {'name': 'saksham', 'age': 18, 'city': 'jaunpur'}

        context_old = super().get_context_data(**kwargs)
        context = {'age': age, 'array': arr, 'dic': dic, 'context_old': context_old}
        return context
    

def testsessions(request):
    if request.session.get('test', False):
        print(request.session['test'])
    # request.session.set_expiry(1)
    request.session['test'] = 'testing'
    request.session['test2'] = 'testing2'
    return render(request, 'firstapp/sessiontesting.html')


def contactus(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        # phone = request.POST.get('phone')
        phone = request.POST['phone']
        if len(phone) != 10:
            # raise ValidationError('Phone number must be 10 digits long.')
            return HttpResponse('<b>Phone number must be 10 digits long.</b>')
        query = request.POST.get('query')
        print(name + " " + email + " " + phone + " " + query)
    return render(request, 'firstapp/contactus.html')


def contactus2(request):
    if request.method == "POST":
        form = ContactUsForm(request.POST)
        if form.is_valid():
            if len(form.cleaned_data.get('query')) > 10:
                form.add_error('query', 'Query length is not right')
                return render(request, 'firstapp/contactus2.html', {'form': form})
            form.save()
            return HttpResponse("Thank You")
        else:
            if len(form.cleaned_data.get('query')) > 10:
                form.add_error('query', 'Query length is not right')
                # form.errors['_all_'] = 'Query length is not right. Please enter a valid query.'
            return render(request, 'firstapp/contactus2.html', {'form':form})
    return render(request, 'firstapp/contactus2.html', {'form':ContactUsForm})



class ContactUs(FormView):
    form_class = ContactUsForm
    template_name = 'firstapp/contactus2.html'
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        if len(form.cleaned_data.get('query')) > 10:
            form.add_error('query', 'Query length is not right')
            return render(self.request, 'firstapp/contactus2.html', {'form': form})
        form.save()
        response = super().form_valid(form)
        return response
    

    def form_invalid(self, form):
        if len(form.cleaned_data.get('query')) > 10:
            form.add_error('query', 'Query length is not right')
            return render(self.request, 'firstapp/contactus2.html', {'form': form})
        response = super().form_invalid(form)
        return response



# class RegisterViewSeller(CreateView):
#     template_name = 'firstapp/register.html'
#     form_class = RegistrationForm
#     success_url = reverse_lazy('index')

#     def post(self, request, *args, **kwargs):
#         response = super().post(request, *args, **kwargs)
#         if response.status_code == 302:
#             gst = request.POST.get('gst')
#             warehouse_location = request.POST.get('warehouse_location')
#             user = CustomUser.objects.get(email=request.POST.get('email'))
#             s_add = SellerAdditional.objects.create(user=user, gst=gst, warehouse_location=warehouse_location)
#             return response
#         else:
#             return response
        

class RegisterView(CreateView):
    template_name = 'firstapp/registerbasicuser.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('signup')

    def post(self, request, *args, **kwargs):
        user_email = request.POST.get('email')
        try:
            existing_user = CustomUser.objects.get(email = user_email)
            if existing_user.is_active == False:
                existing_user.delete()
        except:
            pass
        response = super().post(request, *args, **kwargs)
        if response.status_code == 302:
            user = CustomUser.objects.get(email = user_email)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('firstapp/registration/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            print(message)
            to_email = user_email
            form = self.get_form()
            try:
                send_mail(
                    subject=mail_subject,
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[to_email],
                    fail_silently=False, # Set to True if you want to ignore errors in sending email
                )
                messages.success(request, 'Link has sent to your email, please verify your account!')
                return self.render_to_response({'form': form})
            except:
                form.add_error('', 'Error Occurred In Sending Email, Try Again!')
                messages.error(request, 'Error Occurred In Sending Email, Try Again!')
                return self.render_to_response({'form': form})
        else:
            return response
        

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist) as e:
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Successfully Logged In!!')
        return redirect(reverse_lazy('index'))
    else:
        return HttpResponse('Activation link is invalid or your account is already verified! Try to login!!')


class LoginViewUser(LoginView):
    template_name = 'firstapp/login.html'


# class RegisterViewSeller(LoginRequiredMixin, CreateView):
#     template_name = 'firstapp/registerseller.html'
#     form_class = RegistrationFormSeller2
#     success_url = reverse_lazy('index')

#     def form_valid(self, form):
#         user = self.request.user
#         user.type.append(user.Types.SELLER)
#         user.save()
#         form.instance.user = self.request.user
#         return super().form_valid(form)
    

class LogoutViewUser(LogoutView):
    # success_url = reverse_lazy('index')
    next_page = reverse_lazy('index')



class ListProducts(ListView):
    model = Product
    template_name = 'firstapp/listproducts.html'
    context_object_name = 'product'
    paginate_by = 2


from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
PRODUCTS_PER_PAGE = 2

def listProducts(request):
    ordering = request.GET.get('ordering', "")
    search = request.GET.get('search', "")
    price = request.GET.get('price', "")

    product = Product.objects.all()

    if search:
        product = product.filter(Q(product_name__icontains=search) | Q(brand__icontains=search))

    if ordering:
        product = product.order_by(ordering)

    if price:
        product = product.filter(price__lt=price)

    # Pagination AFTER filtering and ordering
    page = request.GET.get('page', 1)
    product_paginator = Paginator(product, PRODUCTS_PER_PAGE)
    try:
        product = product_paginator.page(page)
    except EmptyPage:
        product = product_paginator.page(product_paginator.num_pages)
    except:
        product = product_paginator.page(1)

    return render(request, 'firstapp/listproducts.html', {
        'product': product,
        'page_obj': product,
        'is_paginated': True,
        'paginator': product_paginator
    })


def suggestionApi(request):
    if 'term' in request.GET:
        search = request.GET.get('term')
        qs = Product.objects.filter(Q(product_name__icontains=search))[0:10]
        titles = list()
        for product in qs:
            titles.append(product.product_name)
        if len(qs) < 10:
            length = 10 - len(qs)
            qs2 = Product.objects.filter(Q(brand__icontains=search))[0:length]
            for product in qs2:
                titles.append(product.brand)
        return JsonResponse(titles, safe=False, encoder=DjangoJSONEncoder)



class ProductDetail(DetailView):
    model = Product
    template_name = 'firstapp/productdetail.html'
    context_object_name = 'product'


@login_required
def addToCart(request, id):
    try:
        cart = Cart.objects.get(user = request.user)
        try:
            product = Product.objects.get(product_id = id)
            try:
                productincart = ProductInCart.objects.get(cart=cart, product=product)
                productincart.quantity = productincart.quantity + 1
                productincart.save()
                messages.success(request, 'Successfully added to cart!')
                return redirect(reverse_lazy('displaycart'))
            except:
                productincart = ProductInCart.objects.create(cart=cart, product=product, quantity=1)
                messages.success(request, 'Successfully added to cart!')
                return redirect(reverse_lazy('displaycart'))
        except:
            messages.error(request, 'Product not found!')
            return redirect(reverse_lazy('listproducts'))
    except:
        cart = Cart.objects.create(user = request.user)
        try:
            product = Product.objects.get(product_id = id)
            productincart = ProductInCart.objects.create(cart=cart, product=product, quantity=1)
            messages.success(request, 'Successfully added to cart!')
            return redirect(reverse_lazy('displaycart'))
        except:
            messages.error(request, 'Product not found!')
            return redirect(reverse_lazy('listproducts'))


class DisplayCart(LoginRequiredMixin, ListView):
    model = ProductInCart
    template_name = 'firstapp/displaycart.html'
    context_object_name = 'cart'

    def get_queryset(self):
        queryset = ProductInCart.objects.filter(cart = self.request.user.cart)
        return queryset
    

class UpdateCart(LoginRequiredMixin, UpdateView):
    model = ProductInCart
    form_class = CartForm
    success_url = reverse_lazy('displaycart')

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 302:
            if int(request.POST.get('quantity')) <= 0:
                productincart = self.get_object()
                print(productincart)
                productincart.delete()
            return response
        else:
            messages.error(request, 'Error occurred while updating the cart. Please try again.')
            return redirect(reverse_lazy('displaycart'))
        
    
class DeleteFromCart(LoginRequiredMixin, DeleteView):
    model = ProductInCart
    success_url = reverse_lazy('displaycart')

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 302:
            messages.success(request, 'Item removed from cart successfully!')
            return response
        else:
            messages.error(request, 'Error occurred while removing the item from cart. Please try again.')
            return redirect(reverse_lazy('displaycart'))
