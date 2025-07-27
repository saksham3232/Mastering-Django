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



from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import localtime

class ContactUs(FormView):
    form_class = ContactUsForm
    template_name = 'firstapp/contactus2.html'
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
PRODUCTS_PER_PAGE = 4


# # this is apply filters on current page products
# def listProducts(request):
#     ordering = request.GET.get('ordering', "")
#     search = request.GET.get('search', "").lower()
#     price = request.GET.get('price', "")

#     all_products = Product.objects.all()
#     paginator = Paginator(all_products, PRODUCTS_PER_PAGE)

#     page = request.GET.get('page', 1)
#     try:
#         page_obj = paginator.page(page)
#     except PageNotAnInteger:
#         page_obj = paginator.page(1)
#     except EmptyPage:
#         page_obj = paginator.page(paginator.num_pages)

#     # Now work only on the products of the current page
#     current_page_products = list(page_obj.object_list)

#     # ✅ Filtering manually on current page products (Python-based, not ORM)
#     if search:
#         current_page_products = [
#             p for p in current_page_products
#             if search in p.product_name.lower() or search in p.brand.lower()
#         ]

#     if price:
#         try:
#             price = float(price)
#             current_page_products = [p for p in current_page_products if p.price < price]
#         except ValueError:
#             pass

#     if ordering:
#         reverse = ordering.startswith('-')
#         field = ordering.lstrip('-')
#         try:
#             current_page_products.sort(key=lambda p: getattr(p, field), reverse=reverse)
#         except AttributeError:
#             pass  # ignore invalid ordering field

#     return render(request, 'firstapp/listproducts.html', {
#         'product': current_page_products,
#         'page_obj': page_obj,
#         'is_paginated': True,
#         'paginator': paginator,
#     })

# this is apply filters on all products
# Uncomment this function if you want to use it instead of the above one
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


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import Cart, Product, ProductInCart

@login_required
def addToCart(request, id):
    next_url = request.GET.get('next', reverse_lazy('listproducts'))  # Preserve current URL

    try:
        cart, _ = Cart.objects.get_or_create(user=request.user)

        try:
            product = Product.objects.get(product_id=id)

            productincart, created = ProductInCart.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': 1}
            )

            if not created:
                productincart.quantity += 1
                productincart.save()

            messages.success(request, 'Successfully added to cart!')

        except Product.DoesNotExist:
            messages.error(request, 'Product not found!')

    except Exception as e:
        messages.error(request, 'Something went wrong while adding to cart.')

    return HttpResponseRedirect(next_url)


# @login_required
# def addToCart(request, id):
#     try:
#         cart = Cart.objects.get(user = request.user)
#         try:
#             product = Product.objects.get(product_id = id)
#             try:
#                 productincart = ProductInCart.objects.get(cart=cart, product=product)
#                 productincart.quantity = productincart.quantity + 1
#                 productincart.save()
#                 messages.success(request, 'Successfully added to cart!')
#                 return redirect(reverse_lazy('displaycart'))
#             except:
#                 productincart = ProductInCart.objects.create(cart=cart, product=product, quantity=1)
#                 messages.success(request, 'Successfully added to cart!')
#                 return redirect(reverse_lazy('displaycart'))
#         except:
#             messages.error(request, 'Product not found!')
#             return redirect(reverse_lazy('listproducts'))
#     except:
#         cart = Cart.objects.create(user = request.user)
#         try:
#             product = Product.objects.get(product_id = id)
#             productincart = ProductInCart.objects.create(cart=cart, product=product, quantity=1)
#             messages.success(request, 'Successfully added to cart!')
#             return redirect(reverse_lazy('displaycart'))
#         except:
#             messages.error(request, 'Product not found!')
#             return redirect(reverse_lazy('listproducts'))


class DisplayCart(LoginRequiredMixin, ListView):
    model = ProductInCart
    template_name = 'firstapp/displaycart.html'
    context_object_name = 'cart'

    def get_queryset(self):
        # Ensure the cart exists or create an empty one for the logged-in user
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return ProductInCart.objects.filter(cart=cart)


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



# Adding payment gateway
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from .models import Cart, ProductInCart, Order, ProductInOrder, CustomerAdditional
from .forms import CustomerCheckoutForm

import razorpay

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

@login_required
def payment(request):
    user = request.user

    try:
        customer_additional = CustomerAdditional.objects.get(user=user)
    except CustomerAdditional.DoesNotExist:
        customer_additional = None

    # Prepare initial form data
    initial_data = {
        'phone': user.phone or '',
        'address': customer_additional.address if customer_additional else ''
    }

    if request.method == 'POST':
        form = CustomerCheckoutForm(request.POST)

        if form.is_valid():
            # Save phone
            user.phone = form.cleaned_data['phone']
            user.save()

            # Save or update address
            CustomerAdditional.objects.update_or_create(
                user=user,
                defaults={'address': form.cleaned_data['address']}
            )

            # ✅ After saving, proceed directly to payment
            try:
                cart = Cart.objects.get(user=user)
                products_in_cart = ProductInCart.objects.filter(cart=cart)
                final_price = 0

                if not products_in_cart.exists():
                    return HttpResponse('No products in cart to proceed with payment.')

                # Create Order
                order = Order.objects.create(user=user, total_amount=0)
                for item in products_in_cart:
                    ProductInOrder.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )
                    final_price += item.product.price * item.quantity

                order.total_amount = final_price
                order.save()

                # Razorpay
                order_currency = 'INR'
                callback_url = 'http://' + str(get_current_site(request)) + "/handlerequest/"
                notes = {'order-type': 'basic order from the website'}

                razorpay_order = razorpay_client.order.create(dict(
                    amount=int(final_price * 100),
                    currency=order_currency,
                    notes=notes,
                    receipt=order.order_id,
                    payment_capture='0'
                ))

                order.razorpay_order_id = razorpay_order['id']
                order.save()

                return render(request, 'firstapp/payment/paymentsummaryrazorpay.html', {
                    'order': order,
                    'order_id': razorpay_order['id'],
                    'orderId': order.order_id,
                    'final_price': final_price,
                    'razorpay_merchant_id': settings.RAZORPAY_KEY_ID,
                    'callback_url': callback_url
                })

            except Exception as e:
                print("Payment error:", e)
                return HttpResponse('Error during payment setup.')

    else:
        # First-time GET request
        form = CustomerCheckoutForm(initial=initial_data)

    return render(request, 'firstapp/checkoutdetails.html', {'form': form})



# for generating pdf invoice
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os


def fetch_resources(uri, rel):
    path = os.path.join(uri.replace(settings.STATIC_URL, ""))
    return path


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)#, link_callback=fetch_resources)
    if not pdf.err:
        # return result.getvalue()
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None



from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template, render_to_string
from django.utils.timezone import now
from io import BytesIO
from xhtml2pdf import pisa
import logging
import os
from django.utils.timezone import localtime
from razorpay.errors import SignatureVerificationError, BadRequestError
from .models import Order, Cart, ProductInCart
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from collections import defaultdict
from .models import Seller, ProductInOrder

@csrf_exempt
def handlerequest(request):
    if request.method == 'POST':
        try:
            # Get POST data
            payment_id = request.POST.get('razorpay_payment_id', '')
            order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')

            if not payment_id or not order_id or not signature:
                return HttpResponse("Missing payment details.")

            params_dict = {
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            try:
                order_db = Order.objects.get(razorpay_order_id=order_id)
            except Order.DoesNotExist:
                return HttpResponse('Order not found in the database.')

            order_db.razorpay_payment_id = payment_id
            order_db.razorpay_signature = signature
            order_db.save()

            try:
                # Razorpay signature verification
                razorpay_client.utility.verify_payment_signature(params_dict)

                # Capture the payment
                amount = int(order_db.total_amount * 100)
                razorpay_client.payment.capture(payment_id, amount)

                # ✅ Payment successful
                order_db.payment_status = 1
                order_db.save()


                # For generating invoice pdf
                template = get_template('firstapp/payment/invoice.html')
                data = {
                    'order_id': order_db.order_id,
                    'transaction_id': order_db.razorpay_payment_id,
                    'user_email': order_db.user.email,
                    'date': localtime(order_db.datetime_of_payment).strftime('%d %B %Y, %I:%M %p'),
                    'name': order_db.user.name,
                    'order': order_db,
                    'amount': order_db.total_amount,
                }
                html = template.render(data)
                result = BytesIO()
                pdf = pisa.pisaDocument(BytesIO(html.encode("utf-8")), result)
                pdf = result.getvalue()
                filename = "Invoice_" + data['order_id'] + ".pdf"

                mail_subject = 'Your Order Invoice'
                message = render_to_string('firstapp/payment/emailinvoice.html', {
                    'user': order_db.user,
                    'order': order_db,
                })
                to_email = order_db.user.email
                email = EmailMultiAlternatives(
                    subject=mail_subject,
                    body="Please find attached your invoice.",
                    from_email=settings.EMAIL_HOST_USER,
                    to=[to_email]
                )
                email.attach_alternative(message, "text/html")
                email.attach(filename, pdf, 'application/pdf')
                email.send(fail_silently=False)

                seller_emails = set()
                seller_products = defaultdict(list)

                # Group products by seller
                for item in ProductInOrder.objects.filter(order=order_db):
                    seller = item.product.seller
                    if seller and seller.email:
                        seller_emails.add(seller.email)
                        seller_products[seller.email].append(item)

                # Send email to each seller
                for email in seller_emails:
                    items = seller_products[email]
                    seller_instance = Seller.objects.get(email=email)

                    grand_total = sum(item.price * item.quantity for item in items)
                    context = {
                        'grand_total': grand_total,
                        'seller_name': seller_instance.name,
                        'products': items,
                        'order_id': order_db.order_id,
                        'customer_name': order_db.user.name,
                        'customer_email': order_db.user.email,
                        'phone': order_db.user.phone,
                        'address': order_db.user.customeradditional.address if order_db.user.customeradditional else '',
                        'datetime_of_payment': localtime(order_db.datetime_of_payment).strftime('%d %B %Y, %I:%M %p'),
                        'transaction_id': order_db.razorpay_payment_id,
                    }

                    # Render HTML message
                    html_message = render_to_string('firstapp/seller_notification.html', context)
                    plain_message = strip_tags(html_message)

                    # ✅ Generate seller-specific PDF invoice
                    pdf_html = render_to_string('firstapp/payment/seller_invoice.html', context)
                    result = BytesIO()
                    pdf_status = pisa.pisaDocument(BytesIO(pdf_html.encode("utf-8")), result)
                    pdf = result.getvalue()
                    filename = f"SellerInvoice_{order_db.order_id}_{seller_instance.name.replace(' ', '_')}.pdf"

                    # Send Email with PDF attached
                    email_obj = EmailMultiAlternatives(
                        subject=f'New Order Received: {order_db.order_id}',
                        body=plain_message,
                        from_email=settings.EMAIL_HOST_USER,
                        to=[email],
                    )
                    email_obj.attach_alternative(html_message, "text/html")
                    email_obj.attach(filename, pdf, 'application/pdf')
                    email_obj.send(fail_silently=False)


                # ✅ EMPTY THE CART
                cart = Cart.objects.get(user=order_db.user)
                ProductInCart.objects.filter(cart=cart).delete()

                return render(request, 'firstapp/payment/paymentsuccess.html', 
                              {'id': order_db.id,}
                            )


            except SignatureVerificationError:
                order_db.payment_status = 2
                order_db.save()
                return render(request, 'firstapp/payment/paymentfailed.html')

        except Exception as e:
            print("🔴 Unexpected Error in payment:", e)
            return HttpResponse('Error occurred while processing the payment. Please try again.')

    return HttpResponse('Invalid request method.')

from django.views import View

class GenerateInvoice(View):
    def get(self, request, pk, *args, **kwargs):
        try:
            order_db = Order.objects.get(id=pk, user=request.user, payment_status=1)
        except:
            return HttpResponse('Order not found or payment not successful.')
        data = {
            'order_id': order_db.order_id,
            'transaction_id': order_db.razorpay_payment_id,
            'user_email': order_db.user.email,
            'date': localtime(order_db.datetime_of_payment).strftime('%d %B %Y, %I:%M %p'),
            'name': order_db.user.name,
            'order': order_db,
            'amount': order_db.total_amount,
        }
        pdf = render_to_pdf('firstapp/payment/invoice.html', data)
        # return HttpResponse(pdf, content_type='application/pdf')

        # force download
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "Invoice_%s.pdf" %(data['order_id'])
            # content = "inline; filename='%s'" %(filename)
            # content = "attachment; filename='%s'" %(filename)
            response['Content-Disposition'] = f"attachment; filename={filename}"
            return response
        return HttpResponse("Error generating PDF")


# Relating to Group

# to make a new group you can do that like any other models by creating a new record in it

# associating a user to a group
from django.contrib.auth.models import Group
@login_required
def addToPremiumGroup(request):
    group = Group.objects.get(name='premium')
    request.user.groups.add(group)
    return HttpResponse('Successfully Added')


from .models import PremiumProduct
# checking group not permission
# in function based view inside the view or "custom decorater"
# from .decorators import group_required
# @group_required('premium', login_url='/login/')
# def premiumProducts(request):
#     # if request.user.groups.filter(name='premium').exists():
#         product = PremiumProduct.objects.all()
#         return render(request, 'firstapp/listpremiumproducts.html', {'product': product})
#     # else:
#     #     messages.error(request, 'You do not have permission to view this page. Please upgrade to premium.')
#     #     return redirect(reverse_lazy('index'))


# # in class based view inside the view or a "custom mixin"
# from .mixins import CheckPremiumGroupMixin
# class PremiumProducts(CheckPremiumGroupMixin, ListView):
#     model = PremiumProduct
#     template_name = 'firstapp/listpremiumproducts.html'
#     context_object_name = 'product'
#     paginate_by = 2


# Relating To Permission
# checking permission and that permission can belong to that user or to the group that user is associated
from django.contrib.auth.decorators import permission_required
@permission_required('firstapp.view_premiumproduct')
def premiumProducts(request):
    # ct = ContentType.objects.get_for_model(PremiumProduct)     
    # if request.user.permissions.filter(codename = "view_premiumproducts" , contenttype = ct).exists():

    # if request.user.has_perm('firstapp.view_premiumproduct'):
        product = PremiumProduct.objects.all()
        return render(request, 'firstapp/listpremiumproducts.html', {'product': product})

    # else:
    #     return HttpResponse("Not allowed")


from django.contrib.auth.mixins import PermissionRequiredMixin
class PremiumProducts(PermissionRequiredMixin, ListView):
    template_name = 'firstapp/listpremiumproducts.html'
    model = PremiumProduct
    context_object_name = 'product'
    permission_required = 'firstapp.view_premiumproduct'


# for creating permissions
#1 Creating Custom Model Depenedent Permission through Code
#from django.contrib.auth.models import Group, ContentType, Permission
# ct = ContentType.objects.get_for_model(PremiumProduct)
# permission = Permission.objects.create(codename="can_do_this", contentype = ct)


#2 Creating Custom Model Dependent Permission by adding in Meta of that model

#3 Creating Custom Model Independent Permission by creating a separate model for permissions

# filtering existing permissions
# ct = ContentType.obejcts.get_for_model(PremiumProduct)
# permission = Permission.objects.get(codename='view_premiumproduct', content_type=ct)


# Adding permission to user
# user.permissions.add(permission)

# Adding permission to group
# new_group, created = Group.objects.get_or_create(name="new_group")
# new_group.permissions.add(permission)

# Removing permission from user
# user.permissions.remove(permission)

# Removing permission from group
# new_group.permissions.remove(permission)


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('productinorder_set__product')

    for order in orders:
        # Auto-update status
        if not order.datetime_of_payment:
            continue

        days_passed = (timezone.now().date() - order.datetime_of_payment.date()).days

        if days_passed <= 1:
            new_status = 1
        elif 2 <= days_passed <= 4:
            new_status = 2
        elif 5 <= days_passed <= 6:
            new_status = 3
        else:
            new_status = 4

        if order.status != new_status:
            order.status = new_status
            order.save()

        # Add dynamic subtotal and grand total
        grand_total = 0
        for item in order.productinorder_set.all():
            item.subtotal = item.price * item.quantity  # dynamic property
            grand_total += item.subtotal
        order.grand_total = grand_total  # dynamic property

    return render(request, 'firstapp/my_orders.html', {'orders': orders})
