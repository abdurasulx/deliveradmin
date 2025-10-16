# auto fill this file. this file is django app's urls.py
from django.urls import path
from . import views # import views.py from main app

urlpatterns = [
    path('', views.home, name='home'),  # home page view
     path('products/', views.products_view, name='products'),
    path('products/add/', views.products_view, name='add_product'),
    path('products/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.employee_create, name='employee_add'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    path('conorders/', views.conorders_list, name='conorders_list'),
    path('conorders/<int:pk>/', views.conorder_detail, name='conorder_detail'),
    path('conorders/<int:pk>/update_status/', views.conorder_update_status, name='conorder_update_status'),
    path('conorders/add/', views.conorder_create, name='conorder_create'),
    path('conorders/<int:pk>/delete/', views.conorder_delete, name='conorder_delete'),
    path('orders/', views.orders_view, name='orders_view'),
    path('orders/data/', views.order_status_data, name='order_status_data'),
    path('orders/status/', views.order_status_data, name='order_status_data'),
    path('conorders/assign/', views.assign_order, name='assign_order'),
    path('assign_deliver/', views.assign_deliver, name='assign_deliver'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('deliver/dashboard/', views.deliver_dashboard, name='deliver_dashboard'),
    path('deliver/order/<int:order_id>/delivered/', views.order_mark_delivered, name='order_mark_delivered'),
    path('update_order_status/', views.update_order_status, name='update_order_status'),
    path('telegram/send/', views.send_telegram_message, name='send_telegram_message'),
    path('api/orders/<int:deliver_id>/', views.get_orders_api, name='get_orders_api'),
    path('api/all_orders/', views.all_orders_api, name='all_orders_api'),


] 
# add more paths as needed