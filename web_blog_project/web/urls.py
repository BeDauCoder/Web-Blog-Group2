from django.urls import path 
from . import views
from .views import add_item,edit_item,delete_item,like_item,add_comment,item_list,item_detail,about,contact,draft_item_list
urlpatterns = [
    path("register/", views.register, name='register'),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name='logout'),
    path('', item_list, name='item_list'),
    path('item/add/', add_item, name='add_item'),
    path('item/edit/<int:pk>/', edit_item, name='edit_item'),
    path('item/delete/<int:pk>/', delete_item, name='delete_item'),
    path('item/like/<int:pk>/', like_item, name='like_item'),
    path('item/<int:pk>/comment/', add_comment, name='add_comment'),
    path('item/<int:pk>/', item_detail, name='item_detail'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('drafts/', draft_item_list, name='draft_item_list'),
]