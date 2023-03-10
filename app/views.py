from django.shortcuts import redirect, render
from django.views import View   
from .models import Costumer
from .models import *
from .forms import CustumerRegistrationForm,CustomerProfileForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator





@method_decorator(login_required, name='dispatch')
class ProductView(View):
    def get(self,request):
        bottom_wears = Product.objects.filter(categary='BW')
        mobiles= Product.objects.filter(categary='M')
        top_wears = Product.objects.filter(categary='TW')
        return render(request,'app/home.html',{'top':top_wears,'bottom':bottom_wears,'mobile':mobiles})


class ProductDetailView(View):
    def get(self,request,pk):
        product = Product.objects.get(pk=pk)
        return render(request,'app/productdetail.html',{'product':product})

# def home(request):
#  return render(request, 'app/home.html')

# def product_detail(request):
#  return render(request, 'app/productdetail.html')

def add_to_cart(request):
    user =request.user
    product_id=request.GET.get('prod_id')
    product=Product.objects.get(id=product_id)
    Cart(user=user,product=product).save()

    return render(request, 'app/addtocart.html')

def show_cart(request):
    if request.user.is_authenticated:
        user=request.user
        cart=Cart.objects.filter(user=user)
        amount=0.0
        shipping_amount=80.0
        total_amount=0.0
        cart_product =[p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                temp_amount=(p.quantity * p.product.discounted_price)
                amount+=temp_amount
                total_amount=amount+shipping_amount
            return render(request,'app/addtocart.html',{'carts':cart,'total_amount':total_amount,'amount':amount})
        return render(request,'app/empty_cart.html')

def buy_now(request):
    return render(request, 'app/buynow.html')

# def profile(request):
#     return render(request, 'app/profile.html')

class ProfileView(View):
    def get(self,request):
        form =CustomerProfileForm()
        return render(request,'app/profile.html',{'form':form ,'active':'btn-primary'})
    
    def post(self,request):
        form=CustomerProfileForm(request.POST)
        if form.is_valid():
            usr=request.user
            name=form.cleaned_data['name']
            locality=form.cleaned_data['locality']
            city=form.cleaned_data['city']
            state=form.cleaned_data['state']
            zipcode=form.cleaned_data['zipcode']
            reg = Costumer(user=usr,name=name,locality=locality,city=city,state=state,zipcode=zipcode)
            reg.save()
            messages.success(request,'conguralation')
        return render(request,'app/profile.html',{'form':form ,'active':'btn-primary'})

            

def address(request):
    print(request.user,'gdytddyyjsdryr')
    add = Costumer.objects.filter(user=request.user)
    print(add)
    return render(request, 'app/address.html',{'add':add,'active':'btn-primary'}) 


def orders(request):
    op=OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html',{'order_placed':op})

def change_password(request):
    return render(request, 'app/changepassword.html')

def mobile(request,data=None):
    if data == None:
        mobiles = Product.objects.filter(categary='M')
    elif data =="Redmi" or data =="Samsung":
        mobiles = Product.objects.filter(categary='M').filter(brand=data)
    return render(request, 'app/mobile.html',{'m':mobiles})

class CustumerLoginView(View):
    pass

# def customerregistration(request):
#  return render(request, 'app/customerregistration.html')
class CustumerRegistrationView(View):
    def get(self,request):
        form = CustumerRegistrationForm()
        return render(request,'app/customerregistration.html',{'form':form})
    def post(self,request):
        form = CustumerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request,'congrualation ! celebration registerd')
            form.save()
        return render(request,'app/customerregistration.html',{'form':form})   

def checkout(request):
    user=request.user
    add=Costumer.objects.filter(user=user)
    cart_items= Cart.objects.filter(user=user)
    amount=0.0
    shipping_amount=80
    total_amount=0.0
    cart_prouct=[p for p in Cart.objects.all() if p.user == request.user]
    if cart_prouct:
        for p in cart_prouct:
            tempamount=(p.quantity*p.product.discounted_price)
            amount+=tempamount
        total_amount=amount+shipping_amount  
    return render(request, 'app/checkout.html',{'add':add,"total_amount":total_amount,'cart_items':cart_items})




def payment_done(request):
    user=request.user
    custid=request.GET.get('custid')
    customer=Costumer.objects.get(id=custid)
    cart=Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user,customer=customer,product=c.product,quantity=c.quantity).save()
        c.delete()
    return redirect('orders')



def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c=Cart.objects.filter(product=prod_id,user=request.user.id).last()
        if c:
            c.quantity+=1
            c.save()
            quantity = c.quantity
        else:
            quantity = 1
        amount =0.0
        shipping_amount = 80.0
        cart_product =[p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            temp_amount=(p.quantity * p.product.discounted_price)
            amount+=temp_amount
        data ={
            'quantity':quantity,
            'total_amount':amount+shipping_amount,
            'amount':amount,
        }
        return JsonResponse(data)
            


def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c=Cart.objects.filter(product=prod_id,user=request.user)
        if c:
            c.quantity-=1
            c.save()
            quantity = c.quantity
        else:
            quantity = 1
        amount =0.0
        shipping_amount = 80.0
        cart_product =[p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            temp_amount=(p.quantity * p.product.discounted_price)
            amount+=temp_amount
        data ={
            'quantity':quantity,
            'total_amount':amount+shipping_amount,
            'amount':amount,
        }
        return JsonResponse(data)
    




def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c=Cart.objects.filter(product=prod_id,user=request.user)
        c.delete()
        amount =0.0
        shipping_amount = 80.0
        cart_product =[p for p in Cart.objects.all() if p.user == request.user]
        for p in cart_product:
            temp_amount=(p.quantity * p.product.discounted_price)
            amount+=temp_amount
        data ={
            'total_amount':amount+shipping_amount,
            'amount':amount,
        }
        return JsonResponse(data)
            