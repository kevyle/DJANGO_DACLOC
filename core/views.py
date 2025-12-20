from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Account, Post, Item, Order, OrderItem, Comment


def user_create(request):
    if request.method == 'POST':
        username = request.POST.get('username', 'Anonymous')
        display_name = request.POST.get('display_name', 'Anonymous')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Tạo người dùng mới
        user = Account.objects.create(
            username=username or 'Anonymous',
            display_name=display_name or 'Anonymous',
            email=email,
            password=password,  # không mã hóa để đơn giản
        )
        request.session['user_id'] = user.id
        return redirect('post_list')

    return render(request, 'signup/user_form.html', {'action': 'create'})

def user_list(request):
    users = Account.objects.all()
    return render(request, 'signup/user_list.html', {'users': users})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user = Account.objects.get(username=username, password=password)
            request.session['user_id'] = user.id
            return redirect('post_list')
        except Account.DoesNotExist:
            return render(request, 'login/login.html', {'error': 'Sai tên người dùng hoặc mật khẩu'})
    return render(request, 'login/login.html')


def user_logout(request):
    request.session.flush()
    return redirect('user_login')


def get_current_user(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return Account.objects.get(id=user_id)
        except Account.DoesNotExist:
            pass
    return None


def post_create(request):
    user = get_current_user(request)
    if not user:
        return redirect('user_login')

    if request.method == 'POST':
        content = request.POST.get('content', '')
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        Post.objects.create(
            author=user,
            content=content,
            image=image,
            video=video,
        )
        return redirect('post_list')

    return render(request, 'home/post_form.html', {'action': 'create'})


def post_list(request):
    user = get_current_user(request)
    if not user:
        return redirect('user_login')
    
    if request.method == 'POST':
        content = request.POST.get('content', '')
        image = request.FILES.get('image')
        video = request.FILES.get('video')
        
        Post.objects.create(
            author=user,
            content=content,
            image=image,
            video=video,
        )
        return redirect('post_list')  # Redirect để reload trang
    
    # GET - hiển thị posts
    posts = Post.objects.select_related('author').order_by('-created_at')
    return render(request, 'home/post_list.html', {'posts': posts, 'user': user})



def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.filter(is_active=True).order_by('-created_at')


    user = get_current_user(request)


    return render(request, 'details/post_detail.html', {
    'post': post,
    'comments': comments,
    'user': user,
})

def post_edit(request, post_id):
    user = get_current_user(request)
    if not user:
        return redirect('user_login')

    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        post.content = request.POST.get('content', post.content)
        if 'image' in request.FILES:
            post.image = request.FILES['image']
        if 'video' in request.FILES:
            post.video = request.FILES['video']
        post.save()
        return redirect('post_list')

    return render(request, 'home/post_form.html', {'post': post, 'action': 'edit'})

def post_delete(request, post_id):
    user = get_current_user(request)
    if not user:
        return redirect('user_login')

    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect('post_list')

def item_list(request):
    items = Item.objects.all()
    return render(request, 'items/item_list.html', {'items': items})

def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'items/item_detail.html', {'item': item})

def item_create(request):
    user = get_current_user(request)
    if not user:
        return redirect('user_login')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        image = request.FILES.get('image')

        Item.objects.create(
            name=name,
            description=description,
            price=price,
            image=image
        )
        return redirect('item_list')

    return render(request, 'items/item_form.html', {'action': 'create'})

def order_create(request, item_id):
    user = get_current_user(request)
    if not user:
        return redirect('user_login')

    if request.method == 'POST':
        item_ids = request.POST.getlist('item_ids')
        quantities = request.POST.getlist('quantities')

        order = Order.objects.create(user=user)

        for item_id, quantity in zip(item_ids, quantities):
            item = get_object_or_404(Item, id=item_id)
            OrderItem.objects.create(order=order, item=item, quantity=int(quantity))

        return redirect('order_detail', order_id=order.id)

    items = Item.objects.all()
    return render(request, 'orders/order_form.html', {'items': items})

def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    for item in order.items.all():
        item.subtotal = item.price * item.quantity
    return render(request, "orders/order_detail.html", {"order": order})


def order_list(request):
    user = get_current_user(request)
    if not user:
        return redirect('user_login')

    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})

def order_cancel(request, order_id):
    user = get_current_user(request)
    if not user:
        return redirect('user_login')

    order = get_object_or_404(Order, id=order_id, user=user)
    order.status = 'canceled'
    order.save()
    return redirect('order_list')

def order_complete(request, order_id):
    user = get_current_user(request)
    if not user:
        return redirect('user_login')

    order = get_object_or_404(Order, id=order_id, user=user)
    order.status = 'completed'
    order.save()
    return redirect('order_list')

def comment_create(request, post_id):
    user = get_current_user(request)
    if not user:
        return redirect('user_login')

    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        if content:
            Comment.objects.create(
                post=post,
                author=user,
                content=content,
                image=image,
                video=video,
                is_active=True
            )

        return redirect('post_detail', post_id=post.id)

    return redirect('post_detail', post_id=post.id)

def get_profile(request, user_id):
    user = get_object_or_404(Account, id=user_id)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    return render(request, 'profile/profile_detail.html', {'user': user, 'posts': posts})