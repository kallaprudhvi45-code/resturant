from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:item_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('update/<int:item_id>/<str:action>/', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),
]
