from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse,HttpResponseForbidden
from django.db.models import Q
from .models import Item, Comment,Category,Message,Chat
from .forms import ItemForm, CommentForm, ItemStatusForm
from PIL import Image
import os
from django.contrib.auth.views import PasswordResetDoneView


# Hàm kiểm tra xem người dùng có phải là superuser hay không
def superuser_required(user):
    return user.is_superuser

class CustomPasswordResetDoneView(PasswordResetDoneView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_nav_sidebar_enabled'] = False  # hoặc True, tùy thuộc vào yêu cầu
        return context

@login_required
def search_items(request):
    query = request.GET.get('q')  # Lấy thông tin tìm kiếm từ URL
    results = []
    if query:
        results = Item.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'search_results.html', {'query': query, 'results': results})


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tài Khoản đã tồn tại')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email đã được sử dụng')
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            messages.success(request, 'Tạo Tài Khoản Thành Công')
            return redirect('login')
    return render(request,'register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('item_list')
        else:
            messages.error(request, 'Thông tin đăng nhập không hợp lệ')
    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


def item_list(request):
    # Lấy tất cả các danh mục để hiển thị trong danh sách thả xuống
    categories = Category.objects.all()

    # Lấy danh mục được chọn từ yêu cầu, nếu có
    selected_category = request.GET.get('category')

    # Lọc các item dựa trên danh mục đã chọn (nếu có), nếu không sẽ hiển thị tất cả
    if selected_category:
        items = Item.objects.filter(category_id=selected_category, status='published')
    else:
        items = Item.objects.filter(status='published')

    hot_items = Item.objects.filter(status='published').order_by('-likes')[:3]

    # Phân trang
    paginator = Paginator(items, 6)  # Hiển thị 6 item mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Truyền categories vào ngữ cảnh
    return render(request, 'item_list.html', {
        'page_obj': page_obj,
        'hot_items': hot_items,
        'categories': categories,  # Truyền categories để hiển thị trong mẫu
    })
    # Lấy tất cả các danh mục để hiển thị trong danh sách thả xuống
    categories = Category.objects.all()

    # Lấy danh mục được chọn từ yêu cầu, nếu có
    selected_category = request.GET.get('category')

    # Lọc các item dựa trên danh mục đã chọn (nếu có), nếu không sẽ hiển thị tất cả
    if selected_category:
        items = Item.objects.filter(category_id=selected_category, status='published')
    else:
        items = Item.objects.filter(status='published')

    hot_items = Item.objects.filter(status='published').order_by('-likes')[:3]

    ###
    items = Item.objects.filter(status='published')
    hot_items = Item.objects.filter(status='published').order_by('-likes')[:3]
    paginator = Paginator(items, 6)  # Hiển thị 10 item mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'item_list.html', {'page_obj': page_obj, 'items': items, 'hot_items': hot_items})




@login_required
def add_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.status = 'Draft'
            item.created_by = request.user

            if 'image' in request.FILES:
                image = Image.open(request.FILES['image'])
                # Resize the image to a fixed size (e.g., 800x800 pixels)
                image = image.resize((800, 800), Image.ANTIALIAS)
                # Save the resized image to the same file
                image.save(item.image.path)

            item.save()
            return redirect('item_list')
    else:
        form = ItemForm()
    return render(request, 'add_item.html', {'form': form})


@login_required
def edit_item(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if item.created_by != request.user:
        return HttpResponseForbidden(
            '<script>alert("Bạn không có quyền chỉnh sửa bài viết này."); window.location.href = "/";</script>')

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item_detail', pk=pk)
        else:
            return HttpResponse(form.errors.as_json())
    else:
        form = ItemForm(instance=item)

    return render(request, 'edit_item.html', {'form': form})


login_required


def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if item.created_by != request.user:
        return HttpResponseForbidden(
            '<script>alert("Bạn không có quyền xóa bài viết này."); window.location.href = "/";</script>')

    if request.method == "POST":
        # Xóa tệp hình ảnh nếu có
        if item.image:
            if os.path.isfile(item.image.path):
                os.remove(item.image.path)
        item.delete()
        return redirect('item_list')

    return render(request, 'delete_item.html', {'item': item})


@login_required
def like_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if item.likes.filter(id=request.user.id).exists():
        item.likes.remove(request.user)
    else:
        item.likes.add(request.user)
    return redirect('item_detail', pk=pk)


@login_required
def add_comment(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.item = item
            comment.user = request.user
            comment.save()
            return redirect('item_detail', pk=pk)
    else:
        form = CommentForm()
    return render(request, 'add_comment.html', {'form': form})


def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    comments = Comment.objects.filter(item=item)
    return render(request, 'item_detail.html', {'item': item, 'comments': comments})


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from .models import Item
from .forms import ItemStatusForm


def superuser_required(user):
    return user.is_superuser


@login_required
@user_passes_test(superuser_required)
def draft_item_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden('<script>alert("Bạn không phải admin"); window.location.href = "/";</script>')

    drafts = Item.objects.filter(status='Draft')
    if request.method == 'POST':
        form = ItemStatusForm(request.POST)
        if form.is_valid():
            item_id = request.POST.get('item_id')
            item = get_object_or_404(Item, id=item_id)
            item.status = form.cleaned_data['status']
            item.save()
            messages.success(request, 'Trạng thái của mục đã được cập nhật thành công!')
            return redirect('draft_item_list')
    else:
        form = ItemStatusForm()

    return render(request, 'draft_item_list.html', {'drafts': drafts, 'form': form})


# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Chat, Message
from django.contrib.auth.models import User


@login_required
def chat_view(request, chat_id=None):
    chats = request.user.chats.all()
    selected_chat = None

    if chat_id:
        selected_chat = get_object_or_404(Chat, pk=chat_id)
        if request.user not in selected_chat.participants.all():
            return redirect('chat_view')
        if request.method == 'POST' and 'content' in request.POST:
            content = request.POST.get('content')
            if content:
                Message.objects.create(chat=selected_chat, sender=request.user, content=content)

    if request.method == 'POST' and 'create_chat' in request.GET:
        usernames = request.POST.getlist('users')
        users = User.objects.filter(username__in=usernames)
        chat = Chat.objects.create()
        chat.participants.set(users)
        chat.participants.add(request.user)
        chat.save()
        return redirect('chat_detail', chat_id=chat.id)

    return render(request, 'chat_detail.html',
                  {'chats': chats, 'selected_chat': selected_chat, 'users': User.objects.all()})





