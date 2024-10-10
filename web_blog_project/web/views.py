from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Item,Comment
from .forms import ItemForm, CommentForm,ItemStatusForm
from django.contrib.auth.decorators import login_required
#######################################################
"""Author: VanDUng
date:10/10/2025
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


def item_list(request):
    items = Item.objects.filter(status='published')
    return render(request, 'item_list.html', {'items': items})


def add_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()
            messages.success(request, 'Item added successfully!')
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
    drafts = Item.objects.filter(status='draft')
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