from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
<<<<<<< HEAD
from .models import Item,Comment,Category
from .forms import ItemForm, CommentForm,ItemStatusForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
#######################################################
"""Author: VanDUng
# date:14/10/2025 filter by catogrories
"""
from .models import Item
from .forms import CategoryFilterForm

def post_list(request):
    form = CategoryFilterForm(request.GET or None)
    items = Item.objects.all()

    if form.is_valid() and form.cleaned_data['category']:
        items = items.filter(category=form.cleaned_data['category'])

    return render(request, 'item_list.html', {'items': items, 'form': form})


"""date:10/10/2025
feature: search item by item.Name and itemDescription"""
=======
from django.core.paginator import Paginator
from django.http import HttpResponse,HttpResponseForbidden
>>>>>>> SangNguyen
from django.db.models import Q
from .models import Item, Comment
from .forms import ItemForm, CommentForm, ItemStatusForm


# Hàm kiểm tra xem người dùng có phải là superuser hay không
def superuser_required(user):
    return user.is_superuser


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
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tài Khoản đã tồn tại')
        else:
            user = User.objects.create_user(username=username, password=password)
            user.save()
            messages.success(request, 'Tạo Tài Khoản Thành Công')
            return redirect('login')
    return render(request, 'register.html')


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


<<<<<<< HEAD

####
=======
>>>>>>> SangNguyen
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
#####
# def item_list(request):
    
   ###
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
    paginator = Paginator(items, 6)
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


@login_required
def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk)

    if item.created_by != request.user:
        return HttpResponseForbidden(
            '<script>alert("Bạn không có quyền xóa bài viết này."); window.location.href = "/";</script>')

    if request.method == "POST":
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
