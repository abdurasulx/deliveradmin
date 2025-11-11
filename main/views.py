from django.shortcuts import render
# import htttp response 
from django.http import HttpResponse
from .models import Product, Category, ProductImage, Order, OrderItem, Employee, User  , ConOrder , Customer, OrderStatus
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django import forms
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required 
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
import requests
from django.utils import timezone


from django.core.paginator import Paginator
from django.db.models.functions import TruncDate


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        next_url = request.POST.get('next')
        if user is not None:
            login(request, user)
            return redirect(next_url if next_url else 'home')
        else:
            messages.error(request, "Login yoki parol xato!")

    return render(request, "auth/login.html")


@login_required(login_url='login')
def home(request):
    usr=Employee.objects.get(user=request.user)
    if usr.role == 'manager':
        return render(request, 'dashboard.html', {'next': 'home'})
    elif usr.role == 'supplier':
        today=timezone.now().date()
        delivering_orders = Order.objects.filter(status=OrderStatus.OUT_FOR_DELIVERY, delivery_person=request.user)
        delivered_orders = Order.objects.filter(status=OrderStatus.DELIVERED, delivery_person=request.user, delevery_date=today)
        canceled_orders = Order.objects.filter(status=OrderStatus.CANCELLED, delivery_person=request.user, delevery_date=today)

        context = {
            'active_orders_count': len(delivering_orders),
            'delivered_orders_count': len(delivered_orders),
            'canceled_orders_count': len(canceled_orders),
            'delivering_orders': delivering_orders,
            'delivered_orders': delivered_orders,
            'canceled_orders': canceled_orders,
             }

    # }
        

        return render(request, 'deliver/dashboart.html', context)
    
@login_required(login_url='login')
def order_mark_delivered(request, order_id):
    deliver=Employee.objects.get(user=request.user)
    order = get_object_or_404(ConOrder, id=order_id, deliver=deliver)
    if request.method == "POST":
        order.status = "accepted"
        order.save()
        messages.success(request, "Buyurtma topshirildi!")
        return redirect('home')
@login_required(login_url='login')



  
def get_orders_api(request,deliver_id):
    dlvr = get_object_or_404(Employee, id=deliver_id, role='supplier')
    orders = ConOrder.objects.filter(deliver=dlvr).values('id', 'orderlist__customer_name', 'delivery_address', 'status', 'created_at')
    
    return JsonResponse(list(orders), safe=False)
   

@login_required(login_url='login')  # login sahifasiga yo‘naltiradi
def profile(request):
    employee = request.user.employee  # endi bu faqat login bo‘lgan userlarda ishlaydi
    
    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save(commit=False)
            # Agar parol kiritilgan bo‘lsa — yangilaymiz
            if form.cleaned_data.get('password'):
                request.user.set_password(form.cleaned_data['password'])
                request.user.save()
            employee.save()
            return redirect('home')
    else:
        form = EmployeeProfileForm(instance=employee)
    
    return render(request, 'deliver/profile.html', {'form': form})

def order_detail_json(request, pk):
    order = get_object_or_404(Order, pk=pk)
    items = []
    for it in order.items.all():
        items.append({
            "product_name": it.product.name if it.product else "Noma'lum",
            "quantity": it.quantity,
            "price": str(it.price),
            "total_price": str(it.total_price),
        })
    total = sum([float(it['total_price']) for it in items]) if items else 0
    return JsonResponse({
        "order": {
            "id": order.id,
            "customer_name": order.customer_name,
            "phone_number": order.phone_number,
            "address": order.address,
            "latitude": str(order.latitude) if order.latitude else None,
            "longitude": str(order.longitude) if order.longitude else None,
            "deleviry_type": order.deleviry_type,
            "price": str(order.amount),
            "status": order.status,
       
        },
        "items": items,
        "total": str(total)
    })
@csrf_exempt
@login_required
def update_order_status(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body.decode('utf-8'))
            order_id = data.get('id')

            order = Order.objects.get(id=order_id)
            status = order.status
            if status == OrderStatus.OUT_FOR_DELIVERY:
                order.status = OrderStatus.DELIVERED
                order.save()
                return JsonResponse({'success': True, 'message': 'Order status updated to Delivered.'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid status update.'})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


def order_history(request):
    # Faqat kerakli statusdagilar
    orders = (
        Order.objects.filter(status__in=[
            OrderStatus.OUT_FOR_DELIVERY,
            OrderStatus.DELIVERED,
            OrderStatus.CANCELLED
        ])
        .annotate(date=TruncDate('created_at'))
        .order_by('-created_at', '-id')
    )

    # Sanalar bo‘yicha guruhlash
    grouped = {}
    for order in orders:
        if order.date not in grouped:
            grouped[order.date] = []
        grouped[order.date].append(order)

    # Paginatsiya (10 ta sana bir sahifada)
    all_dates = list(grouped.keys())
    paginator = Paginator(all_dates, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    paginated = {d: grouped[d] for d in page_obj.object_list}

    context = {
        'orders_by_date': paginated,
        'page_obj': page_obj,
    }
    return render(request, 'deliver/history.html', context)
@login_required(login_url='login')
def last_orders(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'not_authenticated'}, status=401)

    last_order = (
        Order.objects.filter(
            delivery_person=request.user,
            status=OrderStatus.OUT_FOR_DELIVERY
        )
        .annotate(date=TruncDate('created_at'))
        .order_by('-id')  # eng so‘nggi buyurtma birinchi bo‘ladi
        .first()          # faqat bittasini olamiz
    )

    if not last_order:
        return JsonResponse({'id': 'None'}, status=404)

    return JsonResponse({'id': last_order.id})

def order_history(request):
    # Faqat kerakli statusdagilar
    orders = (
        Order.objects.filter(status__in=[
            OrderStatus.OUT_FOR_DELIVERY,
            OrderStatus.DELIVERED,
            OrderStatus.CANCELLED
        ])
        .annotate(date=TruncDate('created_at'))
        .order_by('-created_at', '-id')
    )

    # Sanalar bo‘yicha guruhlash
    grouped = {}
    for order in orders:
        if order.date not in grouped:
            grouped[order.date] = []
        grouped[order.date].append(order)

    # Paginatsiya (10 ta sana bir sahifada)
    all_dates = list(grouped.keys())
    paginator = Paginator(all_dates, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    paginated = {d: grouped[d] for d in page_obj.object_list}

    context = {
        'orders_by_date': paginated,
        'page_obj': page_obj,
    }
    return render(request, 'deliver/history.html', context)
@csrf_exempt
@login_required
def update_order_status(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body.decode('utf-8'))
            order_id = data.get('id')

            order = Order.objects.get(id=order_id)
            status = order.status
            if status == OrderStatus.OUT_FOR_DELIVERY:
                order.status = OrderStatus.DELIVERED
                order.save()
                return JsonResponse({'success': True, 'message': 'Order status updated to Delivered.'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid status update.'})
        except Order.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Order not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

@login_required(login_url='login')  # login sahifasiga yo‘naltiradi
def profile(request):
    from .forms import EmployeeProfileForm
    employee = request.user.employee  # endi bu faqat login bo‘lgan userlarda ishlaydi
    
    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save(commit=False)
            # Agar parol kiritilgan bo‘lsa — yangilaymiz
            if form.cleaned_data.get('password'):
                request.user.set_password(form.cleaned_data['password'])
                request.user.save()
            employee.save()
            return redirect('home')
    else:
        form = EmployeeProfileForm(instance=employee)
    
    return render(request, 'deliver/profile.html', {'form': form})

def orders_view(request):
    
    active_orders = Order.objects.filter(status=OrderStatus.OUT_FOR_DELIVERY)
    delivered_orders = Order.objects.filter(status=OrderStatus.DELIVERED)
    canceled_orders = Order.objects.filter(status=OrderStatus.CANCELLED)

    return render(request, 'deliver/orders.html', {
        'active_orders': active_orders,
        'delivered_orders': delivered_orders,
        'canceled_orders': canceled_orders,
    })
