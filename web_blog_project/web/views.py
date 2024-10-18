from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Item,Comment,Category
from .forms import ItemForm, CommentForm,ItemStatusForm,CategoryFilterForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
import requests 
#######################################################
"""Author: VanDUng
# date:14/10/2025 filter by catogrories
"""
def get_weather_forecast(city):
    try:
        with open("API_KEY", "r") as file:
            API_KEY = file.read().strip()  # Đọc khóa API và loại bỏ khoảng trắng
    except Exception as e:
        print(f"Error reading API key: {e}")
        return []  # Trả về danh sách rỗng nếu không thể đọc khóa API

    forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric'
    
    try:
        response = requests.get(forecast_url)
        response.raise_for_status()  # Kiểm tra mã trạng thái
        return response.json().get('list', [])  # Dữ liệu dự báo trong key 'list'
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")

    return []  # Trả về danh sách rỗng nếu có lỗi



"""date:10/10/2025
feature: search item by item.Name and itemDescription"""
from django.db.models import Q

def search_items(request):
    query = request.GET.get('q')  # Get the search query from the URL
    results = []
    
    if query:
        # Filter items based on the search query
        results = Item.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )  # Modify fields as per your Item model

    return render(request, 'search_results.html', {'query': query, 'results': results})
#####################################################

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



####
def item_list(request):
    # Lấy tất cả các danh mục để hiển thị trong danh sách thả xuống
    categories = Category.objects.all()
    
    # Lấy danh mục được chọn từ yêu cầu, nếu có
    selected_category = request.GET.get('category')
    
     # Lọc các item dựa trên danh mục đã chọn (nếu có), nếu không sẽ hiển thị tất cả
    if selected_category:
        items = Item.objects.filter(category_id=selected_category, status='published').order_by('-created_at')  # Hoặc thuộc tính bạn muốn
    else:
        items = Item.objects.filter(status='published').order_by('-created_at')  # Hoặc thuộc tính bạn muốn
    
    hot_items = Item.objects.filter(status='published').order_by('-likes')[:3]
    
    # Phân trang
    paginator = Paginator(items, 6)  # Hiển thị 6 item mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    ## Danh sách các thành phố cho dự báo thời tiết
    cities = ["Hanoi", "Ho Chi Minh City", "Da Nang","Nha Trang","BangKok","Singapore","Jakara","Phuket","Phu Ly"]
    weather_forecasts = []

    # Lấy một dự báo duy nhất cho từng thành phố
    for city in cities:
        forecasts = get_weather_forecast(city)  # Hàm này trả về một danh sách dự báo cho thành phố
        if forecasts:
            # Chọn dự báo đầu tiên (hoặc một dự báo cụ thể)
            weather_forecasts.append({
                'city': city,
                'forecast': forecasts[0]  # Lấy dự báo đầu tiên
            })


    # Chuẩn bị dữ liệu ngữ cảnh cho mẫu
    context = {
        'page_obj': page_obj,
        'hot_items': hot_items,
        'categories': categories,
        'weather_forecasts': weather_forecasts,  # Đây là một danh sách phẳng chứa tất cả các dự báo
    }

    return render(request, 'item_list.html', context)

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

def edit_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('item_detail', pk=pk)
        else:
            return HttpResponse(form.errors.as_json())  # Thêm dòng này để kiểm tra lỗi trong form
    else:
        form = ItemForm(instance=item)
    return render(request, 'edit_item.html', {'form': form})

def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
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


def draft_item_list(request):
    drafts = Item.objects.filter(status='Draft')
    if request.method == 'POST':
        form = ItemStatusForm(request.POST)
        if form.is_valid():
            item_id = request.POST.get('item_id')
            item = get_object_or_404(Item, id=item_id)
            item.status = form.cleaned_data['status']
            item.save()
            messages.success(request, 'Item status updated successfully!')
            return redirect('draft_item_list')
    else:
        form = ItemStatusForm()
    return render(request, 'draft_item_list.html', {'drafts': drafts, 'form':form})