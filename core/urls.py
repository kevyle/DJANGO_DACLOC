from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.user_create, name='user_create'),
    path('users/', views.user_list, name='user_list'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('create/', views.post_create, name='post_create'),
    path('home/', views.post_list, name='post_list'),
    path('post/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    # path('post/<int:post_id>/delete/', views.post_delete, name='post_delete'),
    path('items/', views.item_list, name='item_list'),
    path('items/create/', views.item_create, name='item_create'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('order/create/<int:item_id>/', views.order_create, name='order_create'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/', views.order_list, name='order_list'),
    path('order/<int:order_id>/cancel/', views.order_cancel, name='order_cancel'),
    path('order/<int:order_id>/complete/', views.order_complete, name='order_complete'),
    path('comments/create/<int:post_id>/', views.comment_create, name='comment_create'),
]
