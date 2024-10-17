from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.http import HttpResponse,HttpResponseForbidden,JsonResponse
from django.db.models import Q
from .models import Item, Comment,Category,Message,Chat
from .forms import ItemForm, CommentForm, ItemStatusForm,ChatForm
from PIL import Image
import os,datetime
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
import logging
from django.urls import reverse



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

@login_required
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



def chatbot_view(request):
    form = ChatForm()
    categories = Category.objects.all()

    # Khởi tạo danh sách hội thoại để lưu trữ cuộc trò chuyện từ session
    conversation = request.session.get('conversation', [])

    # Kiểm tra nếu người dùng yêu cầu reset cuộc trò chuyện
    if request.method == 'POST':
        if 'reset' in request.POST:
            # Xóa session lưu hội thoại và reset cuộc trò chuyện
            request.session['conversation'] = []
            conversation = []  # Reset conversation về trống
        else:
            form = ChatForm(request.POST)
            if form.is_valid():
                message = form.cleaned_data['message'].lower()

                # Lưu tin nhắn của người dùng vào hội thoại
                conversation.append({'text': message, 'sender': 'user'})

                # Xử lý tin nhắn của người dùng và tạo phản hồi
                response = ""
                if 'danh mục' in message and ('bao nhiêu' in message or 'liệt kê' in message):
                    if 'bao nhiêu' in message:
                        response = f"Hiện có {categories.count()} danh mục."
                    elif 'liệt kê' in message:
                        response = "Danh sách các danh mục: " + ", ".join([category.name for category in categories])
                elif 'bài viết mới nhất' in message:
                    latest_item = Item.objects.filter(status='published').order_by('-created_at').first()
                    if latest_item:
                        item_detail_url = reverse('item_detail', args=[latest_item.pk])
                        response = (f"Bài viết mới nhất là '<a href=\"{item_detail_url}\">{latest_item.name}</a>':<br>"
                                    f"Thời gian tạo: {latest_item.created_at}")
                    else:
                        response = "Không có bài viết nào."
                elif 'bài viết của' in message:
                    try:
                        username = message.split('bài viết của ')[1].strip()
                        user = User.objects.get(username=username)
                        user_items = Item.objects.filter(created_by=user, status='published')
                        if user_items:
                            response = "Danh sách các bài viết của " + username + ":<br>"
                            for item in user_items:
                                item_detail_url = reverse('item_detail', args=[item.pk])
                                response += f'<a href="{item_detail_url}">{item.name}</a><br><br>'
                        else:
                            response = f"Không có bài viết nào của người dùng {username}."
                    except User.DoesNotExist:
                        response = f"Người dùng {username} không tồn tại."
                elif 'tài chính tôi hiện có' in message:
                    try:
                        price_str = message.split('tài chính tôi hiện có')[1].strip()
                        price = float(price_str.split(' ')[0])
                        affordable_items = Item.objects.filter(price__lte=price, status='published')
                        if affordable_items:
                            response = f"Các bài viết liên quan đến mức giá {price}:<br>"
                            for item in affordable_items:
                                item_detail_url = reverse('item_detail', args=[item.pk])
                                response += f'<a href="{item_detail_url}">{item.name}</a> - Giá: {item.price}<br>'
                        else:
                            response = "Không có bài viết nào phù hợp với mức giá đó."
                    except ValueError:
                        response = "Xin vui lòng nhập số tiền hợp lệ."
                elif 'các sự kiện vào tháng' in message:
                    try:
                        month_str = message.split('các sự kiện vào tháng ')[1].strip()
                        month = int(month_str)
                        items_in_month = Item.objects.filter(start_date__month=month, status='published')
                        if items_in_month:
                            response = f"Các bài viết trong tháng {month}:<br>"
                            for item in items_in_month:
                                item_detail_url = reverse('item_detail', args=[item.pk])
                                response += f'<a href="{item_detail_url}">{item.name}</a> - Ngày bắt đầu: {item.start_date}<br>'
                        else:
                            response = f"Không có bài viết nào trong tháng {month}."
                    except ValueError:
                        response = "Xin vui lòng nhập tháng hợp lệ."
                elif 'bài viết vào ngày' in message:
                    try:
                        day_str = message.split('bài viết vào ngày ')[1].strip()
                        date = datetime.datetime.strptime(day_str, '%Y-%m-%d').date()
                        items_on_date = Item.objects.filter(start_date=date, status='published')
                        if items_on_date:
                            response = f"Các bài viết vào ngày {date}:<br>"
                            for item in items_on_date:
                                item_detail_url = reverse('item_detail', args=[item.pk])
                                response += f'<a href="{item_detail_url}">{item.name}</a> - Ngày bắt đầu: {item.start_date}<br>'
                        else:
                            response = f"Không có bài viết nào vào ngày {date}."
                    except ValueError:
                        response = "Xin vui lòng nhập ngày hợp lệ (YYYY-MM-DD)."
                else:
                    response = "Xin lỗi, tôi không hiểu câu hỏi của bạn. Hãy hỏi lại."

                # Thêm phản hồi của bot vào hội thoại
                conversation.append({'text': response, 'sender': 'bot'})

                # Cập nhật session để lưu hội thoại
                request.session['conversation'] = conversation

    return render(request, 'chat_bot.html', {'form': form, 'conversation': conversation})


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





# @login_required
# def chat_view(request, chat_id=None):
#     chats = request.user.chats.all()
#     selected_chat = None
#
#     if chat_id:
#         selected_chat = get_object_or_404(Chat, pk=chat_id)
#         if request.user not in selected_chat.participants.all():
#             return redirect('chat_view')
#         if request.method == 'POST' and 'content' in request.POST:
#             content = request.POST.get('content')
#             if content:
#                 Message.objects.create(chat=selected_chat, sender=request.user, content=content)
#
#     if request.method == 'POST' and 'create_chat' in request.GET:
#         usernames = request.POST.getlist('users')
#         users = User.objects.filter(username__in=usernames)
#         chat = Chat.objects.create()
#         chat.participants.set(users)
#         chat.participants.add(request.user)
#         chat.save()
#         return redirect('chat_detail', chat_id=chat.id)
#
#     return render(request, 'chat_detail.html',
#                   {'chats': chats, 'selected_chat': selected_chat, 'users': User.objects.all()})





