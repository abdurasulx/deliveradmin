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
from .forms import EmployeeProfileForm

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
def logout_view(request):
    logout(request)
    return redirect('login')
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
def deliver_dashboard(request):
    try:
        deliver = Employee.objects.get(user=request.user, role='supplier')
    except Employee.DoesNotExist:
        messages.error(request, "Sizda yetkazib beruvchi huquqi yo‘q!")
        return redirect('dashboard')

    orders = Order.objects.filter(deliver=deliver).order_by('-created_at')
    return render(request, 'deliver/dashboard.html', {'orders': orders})


@login_required(login_url='login')
def submit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if not hasattr(request.user, 'employee') or request.user.employee.role != 'supplier':
        messages.error(request, "Siz bu amalni bajara olmaysiz.")
        return redirect('dashboard')

    if order.deliver.user != request.user:
        messages.error(request, "Bu buyurtma sizga tegishli emas.")
        return redirect('deliver_dashboard')

    order.status = 'submitted'
    order.save()
    messages.success(request, "✅ Buyurtma topshirildi.")
    return redirect('deliver_dashboard')    
# Create your views here.
@login_required(login_url='login')
def products_view(request):
    products = Product.objects.all().select_related('category')
    categories = Category.objects.all()

    if request.method == "POST" and 'name' in request.POST:
        prd=Product.objects.create(
            name=request.POST['name'],
            description=request.POST.get('detail', ''),
            category_id=request.POST.get('category'),
            price=request.POST.get('price'),
            count=request.POST.get('count') or 0,
            is_active='is_active' in request.POST

        )
        pi=ProductImage.objects.create(
            product=prd,
            
            image=request.FILES.get('image')    
        )
        
        return redirect('products')

    return render(request, 'products.html', {
        'products': products,
        'categories': categories
    })

@login_required(login_url='login')
@staff_member_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    pi=ProductImage.objects.get(product=product)

    if request.method == "POST":
        product.name = request.POST['name']
        product.price = request.POST['price']
        product.count = request.POST['count']
        product.is_active = 'is_active' in request.POST
        
        if 'image' in request.FILES:
        
            pi.image=request.FILES.get('image') or pi.image
            pi.save()
        product.save()
        return redirect('products')
    return redirect('products')
@login_required(login_url='login')
@staff_member_required
def delete_product(request, pk):
    Product.objects.filter(pk=pk).delete()
    return redirect('products')


@login_required(login_url='login')
@staff_member_required
def category_list(request):
    categories = Category.objects.all().order_by('-created_at')
    return render(request, 'categories/list.html', {'categories': categories})

@login_required(login_url='login')
@staff_member_required
def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        parent_id = request.POST.get('parent')
        parent = Category.objects.get(id=parent_id) if parent_id else None
        Category.objects.create(name=name, parent=parent)
        return redirect('category_list')
    categories = Category.objects.all()
    return render(request, 'categories/form.html', {'categories': categories, 'action': 'add'})

@login_required(login_url='login')
@staff_member_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST.get('name')
        parent_id = request.POST.get('parent')
        category.parent = Category.objects.get(id=parent_id) if parent_id else None
        category.save()
        return redirect('category_list')
    categories = Category.objects.exclude(id=pk)
    return render(request, 'categories/form.html', {'category': category, 'categories': categories, 'action': 'edit'})

@login_required(login_url='login')
@staff_member_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('category_list')


@login_required(login_url='login')
@staff_member_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employees/list.html', {'employees': employees})


@login_required(login_url='login')
@staff_member_required
def employee_create(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        role = request.POST.get('role')
        is_active = True if request.POST.get('is_active') == 'on' else False

        # 🔹 1. Avval foydalanuvchini yaratamiz
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active
        )

        # 🔹 2. Keyin hodim yozuvini yaratamiz
        Employee.objects.create(
            user=user,
            phone=phone,
            role=role,
            is_activ=is_active,
            password=password
        )

        return redirect('employee_list')

    return render(request, 'employees/add.html')


@login_required(login_url='login')
@staff_member_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        user = employee.user
        # yangilash
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)

        new_username = request.POST.get('username', user.username)
        if new_username != user.username:
            # oddiy tekshiruv — unique bo'lishini tekshiring
            if User.objects.filter(username=new_username).exclude(pk=user.pk).exists():
                messages.error(request, 'Ushbu username band. Boshqa tanlang.')
                return redirect('employee_edit', pk=pk)
            user.username = new_username

        password = request.POST.get('password')
        if password:
            user.set_password(password)  # hashlaydi

        user.save()

        # employee maydonlari
        employee.phone = request.POST.get('phone', employee.phone)
        employee.role = request.POST.get('role', employee.role)
        # checkbox nomi formadagi name="is_active"
        employee.is_activ = True if request.POST.get('is_active') == 'on' else False
        employee.save()

        messages.success(request, 'Hodim ma\'lumotlari yangilandi.')
        return redirect('employee_list')

    return render(request, 'employees/edit.html', {'employee': employee})



@login_required(login_url='login')
@staff_member_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    employee.user.delete()  # birga o‘chadi
    messages.success(request, 'Hodim o‘chirildi!')
    return redirect('employee_list')

@login_required(login_url='login')
@staff_member_required
def conorders_list(request):
    """
    Get all orders and their respective statuses and delivers
    """
    pending_orders = ConOrder.objects.filter(status='pending')
    submitted_orders = ConOrder.objects.filter(status='submitted')
    accepted_orders = ConOrder.objects.filter(status='accepted')
    rejected_orders = ConOrder.objects.filter(status='rejected')
    delivers = Employee.objects.filter(role='supplier', is_activ=True)

    context = {
        # orders that are pending to be submitted
        'pending_orders': pending_orders,

        # orders that are submitted and waiting to be accepted
        'submitted_orders': submitted_orders,

        # orders that are accepted and waiting to be delivered
        'accepted_orders': accepted_orders,

        # orders that are rejected
        'rejected_orders': rejected_orders,
        'delivers': delivers

    }
    return render(request, 'orders/list.html', context)



class ConOrderForm(forms.ModelForm):
    class Meta:
        model = ConOrder
        fields = ['orderlist', 'client', 'delivery_address', 'status', 'deliver']
        widgets = {
            'delivery_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'orderlist': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'deliver': forms.Select(attrs={'class': 'form-select'}),
        }

# --- Detail view ---
@login_required(login_url='login')
@staff_member_required
def conorder_detail(request, pk):
    order = get_object_or_404(ConOrder, pk=pk)
    return render(request, 'orders/detail.html', {'order': order})

# --- Create view ---
@login_required(login_url='login')
@staff_member_required
def conorder_create(request):
    if request.method == 'POST':
        form = ConOrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Buyurtma muvaffaqiyatli qo‘shildi ✅")
            return redirect('conorders_list')
    else:
        form = ConOrderForm()
    return render(request, 'orders/add.html', {'form': form})

# --- Delete view ---
@login_required(login_url='login')
@staff_member_required
def conorder_delete(request, pk):
    order = get_object_or_404(ConOrder, pk=pk)
    order.delete()
    messages.warning(request, "Buyurtma o‘chirildi ❌")
    return redirect('conorders_list')

# --- Status update view (quick action) ---
@login_required(login_url='login')
@staff_member_required
def conorder_update_status(request, pk):
    order = get_object_or_404(ConOrder, pk=pk)
    new_status = request.GET.get('status')

    if new_status in ['pending', 'submitted', 'accepted', 'rejected']:
        order.status = new_status
        order.save()
        messages.info(request, f"Buyurtma holati {new_status} ga o‘zgartirildi ✅")

    return redirect('conorders_list')

@login_required(login_url='login')
@staff_member_required
def order_status_data(request):
    pending = list(ConOrder.objects.filter(status='pending').values())
    submitted = list(ConOrder.objects.filter(status='submitted').values())
    accepted = list(ConOrder.objects.filter(status='accepted').values())
    rejected = list(ConOrder.objects.filter(status='rejected').values())

    return JsonResponse({
        'pending': pending,
        'submitted': submitted,
        'accepted': accepted,
        'rejected': rejected
    })
@login_required(login_url='login')

def orders_view(request):
    
    active_orders = Order.objects.filter(status=OrderStatus.OUT_FOR_DELIVERY)
    delivered_orders = Order.objects.filter(status=OrderStatus.DELIVERED)
    canceled_orders = Order.objects.filter(status=OrderStatus.CANCELLED)

    return render(request, 'deliver/orders.html', {
        'active_orders': active_orders,
        'delivered_orders': delivered_orders,
        'canceled_orders': canceled_orders,
    })

@login_required(login_url='login')
@staff_member_required
def assign_order(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        deliver_id = request.POST.get("deliver_id")

        order = get_object_or_404(ConOrder, id=order_id)
        deliver = get_object_or_404(Employee, id=deliver_id)

        order.deliver = deliver
        order.status = "submitted"
        order.save()
    return redirect('orders_view')
@login_required(login_url='login')
@require_POST
def assign_deliver(request):
    order_id = request.POST.get('order_id')
    deliver_id = request.POST.get('deliver_id')

    try:
        order = ConOrder.objects.get(id=order_id)
        deliver = Employee.objects.get(id=deliver_id)
        order.deliver = deliver
        order.status = 'submitted'  # topshirildi
        order.save()
        return JsonResponse({'success': True})
    except ConOrder.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Buyurtma topilmadi!'})
    except Employee.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Yetkazib beruvchi topilmadi!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
def send_telegram_message(request):
    if request.method == "GET":
        # HTML sahifani qaytarish
        return render(request, "admin/send_telegram.html")

    elif request.method == "POST":
        bot_token = request.POST.get("bot_token")
        message = request.POST.get("message")
        image = request.FILES.get("image")

        if not bot_token or not message:
            return JsonResponse({"success": False, "error": "Token yoki xabar matni kiritilmagan!"})

        users = Customer.objects.exclude(telegram_id__isnull=True)
        sent_count = 0

        for user in users:
            chat_id = user.telegram_id
            try:
                if image:
                    files = {'photo': image.read()}
                    data = {'chat_id': chat_id, 'caption': message}
                    requests.post(f'https://api.telegram.org/bot{bot_token}/sendPhoto', data=data, files=files)
                else:
                    requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage',
                                  data={'chat_id': chat_id, 'text': message})
                sent_count += 1
            except Exception as e:
                print(f"Xabar yuborishda xatolik: {e}")

        return JsonResponse({"success": True, "count": sent_count})

    else:
        return JsonResponse({"success": False, "error": "Faqat GET yoki POST ruxsat etilgan."})
def get_orders_api(request,deliver_id):
    dlvr = get_object_or_404(Employee, id=deliver_id, role='supplier')
    orders = ConOrder.objects.filter(deliver=dlvr).values('id', 'orderlist__customer_name', 'delivery_address', 'status', 'created_at')
    
    return JsonResponse(list(orders), safe=False)
@login_required(login_url='login')
# @staff_member_required
def all_orders_api(request):
    import json
    pending = list(ConOrder.objects.filter(status='pending').values())
    submitted = list(ConOrder.objects.filter(status='submitted').values())
    accepted = list(ConOrder.objects.filter(status='accepted').values())
    rejected = list(ConOrder.objects.filter(status='rejected').values())

    data = {
        'pending': pending,
        'submitted': submitted,
        'accepted': accepted,
        'rejected': rejected
    }

    return JsonResponse(data, safe=True)
    

    # Agar POST bo‘lmasa
    return JsonResponse({'success': False, 'message': 'Faqat POST so‘rovlar qo‘llaniladi.'})

    # 🔹 3. Boshqa metodlar uchun javob
   

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

