# auto fill this file. this file is django app's urls.py
from django.urls import path
from . import views # import views.py from main app

urlpatterns = [
    path('', views.home, name='home'),  # home page view
    path('order/', views.orders_view, name='orders_view'),
    # path('orders/data/', views.order_status_data, name='order_status_data'),
    # path('orders/status/', views.order_status_data, name='order_status_data'),
    # path('conorders/assign/', views.assign_order, name='assign_order'),
   
    path('login/', views.login_view, name='login'),
  
  
    path('deliver/order/<int:order_id>/delivered/', views.order_mark_delivered, name='order_mark_delivered'),
    path('update_order_status/', views.update_order_status, name='update_order_status'),
    path('api/orders/<int:deliver_id>/', views.get_orders_api, name='get_orders_api'),
    # path('api/all_orders/', views.all_orders_api, name='all_orders_api'),
    path('profile',views.profile,name='profile'),
    path('order/<int:pk>/detail/', views.order_detail_json, name='order_detail_json'),
    path('order/history',views.order_history,name='order_history'),
    path('api/orders/last/',views.last_orders,name='last_order'),

] 
# add more paths as needed