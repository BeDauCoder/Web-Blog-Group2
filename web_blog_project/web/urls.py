from django.urls import path
from . import views
from .views import add_item, edit_item, delete_item, like_item, add_comment, item_list, item_detail, about, contact, \
    draft_item_list, chatbot_view, CustomPasswordResetView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('posts/', item_list, name='post_list'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
    path('search/', views.search_items, name='search'),
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
    path('chatbot/', chatbot_view, name='chatbot'),
    path('drafts/edit/<int:pk>/', views.edit_draft, name='edit_draft'),
    # Trang yêu cầu đặt lại mật khẩu
    # path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'),
    #      name='password_reset'),
    # Trang thông báo đã gửi email đặt lại mật khẩu
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset.html'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    # Trang nhập mật khẩu mới sau khi xác thực qua email
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    # Trang thông báo thành công sau khi mật khẩu đã được thay đổi
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),

    # path('chat/', views.chat_view, name='chat_view'),
    # path('chats/<int:chat_id>/', views.chat_view, name='chat_detail'),
]
