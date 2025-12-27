from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from .models import Account, Post, Item, Order, OrderItem, Comment, Reaction
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
import logging, json

logger = logging.getLogger(__name__)


def user_create(request):
    if request.method == "POST":
        username = request.POST.get("username", "Anonymous")
        display_name = request.POST.get("display_name", "Anonymous")
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = Account.objects.create(
            username=username or "Anonymous",
            display_name=display_name or "Anonymous",
            email=email,
            password=password,
        )
        request.session["user_id"] = user.id  # type: ignore
        return redirect("post_list")

    return render(request, "signup/user_form.html", {"action": "create"})


def user_list(request):
    users = Account.objects.all()
    return render(request, "signup/user_list.html", {"users": users})


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = Account.objects.get(username=username, password=password)
            request.session["user_id"] = user.id  # type: ignore
            return redirect("post_list")
        except Account.DoesNotExist:
            return render(
                request,
                "login/login.html",
                {"error": "Invalid username or password."},
            )
    return render(request, "login/login.html")


def user_logout(request):
    request.session.flush()
    return redirect("user_login")


def get_current_user(request):
    user_id = request.session.get("user_id")
    if user_id:
        try:
            return Account.objects.get(id=user_id)
        except Account.DoesNotExist:
            pass
    return None


def post_create(request):
    user = get_current_user(request)
    if not user:
        return redirect("user_login")

    if request.method == "POST":
        content = request.POST.get("content", "")
        image = request.FILES.get("image")
        video = request.FILES.get("video")

        Post.objects.create(
            author=user,
            content=content,
            image=image,
            video=video,
        )
        return redirect("post_list")

    return render(request, "home/post_form.html", {"action": "create"})


def post_list(request):
    user = get_current_user(request)
    if not user:
        return redirect("user_login")

    if request.method == "POST":
        content = request.POST.get("content", "")
        image = request.FILES.get("image")
        video = request.FILES.get("video")

        Post.objects.create(
            author=user,
            content=content,
            image=image,
            video=video,
        )
        return redirect("post_list")

    posts = Post.objects.select_related("author").order_by("-created_at")
    return render(request, "home/post_list.html", {"posts": posts, "user": user})


def post_detail(request, post_id):  # type: ignore
    # Get post
    post = get_object_or_404(Post, id=post_id)  # type: ignore

    # Active comments
    comments = (
        post.comments.filter(is_active=True)  # type: ignore
        .select_related("author")
        .order_by("-created_at")
    )

    # Current logged-in user (your custom session auth)
    user = get_current_user(request)  # type: ignore

    # Aggregate reaction counts (SAFE for templates)
    reaction_counts = post.reactions.values("reaction_type").annotate(  # type: ignore
        count=Count("id")
    )

    # Current user's reaction (if any)
    user_reaction = None
    if user:
        user_reaction = (
            Reaction.objects.filter(post=post, user=user)
            .values_list("reaction_type", flat=True)
            .first()
        )

    return render(  # type: ignore
        request,  # type: ignore
        "details/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "user": user,
            "reaction_counts": list(reaction_counts),
            "user_reaction": user_reaction,
        },
    )


def post_edit(request, post_id):
    user = get_current_user(request)
    if not user:
        return redirect("user_login")

    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        post.content = request.POST.get("content", post.content)
        if "image" in request.FILES:
            post.image = request.FILES["image"]
        if "video" in request.FILES:
            post.video = request.FILES["video"]
        post.save()
        return redirect("post_list")

    return render(request, "home/post_form.html", {"post": post, "action": "edit"})


def post_delete(request, post_id):
    user = get_current_user(request)
    if not user:
        return redirect("user_login")

    post = get_object_or_404(Post, id=post_id)
    post.delete()
    return redirect("post_list")


def item_list(request):
    items = Item.objects.all()
    return render(request, "items/item_list.html", {"items": items})


def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, "items/item_detail.html", {"item": item})


def item_create(request):
    user = get_current_user(request)
    if not user:
        return redirect("user_login")

    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        image = request.FILES.get("image")

        Item.objects.create(
            name=name, description=description, price=price, image=image
        )
        return redirect("item_list")

    return render(request, "items/item_form.html", {"action": "create"})


def order_create(request, item_id):
    user = get_current_user(request)
    if not user:
        return redirect("user_login")

    if request.method == "POST":
        item_ids = request.POST.getlist("item_ids")
        quantities = request.POST.getlist("quantities")

        order = Order.objects.create(user=user)

        for item_id, quantity in zip(item_ids, quantities):
            item = get_object_or_404(Item, id=item_id)
            OrderItem.objects.create(order=order, item=item, quantity=int(quantity))

        return redirect("order_detail", order_id=order.id)  # type: ignore

    items = Item.objects.all()
    return render(request, "orders/order_form.html", {"items": items})


def order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)

    for item in order.items.all():
        item.subtotal = item.price * item.quantity
    return render(request, "orders/order_detail.html", {"order": order})


def order_list(request):
    user = get_current_user(request)
    if not user:
        return redirect("user_login")

    orders = Order.objects.filter(user=user).order_by("-created_at")
    return render(request, "orders/order_list.html", {"orders": orders})


def order_cancel(request, order_id):
    user = get_current_user(request)
    if not user:
        return redirect("user_login")

    order = get_object_or_404(Order, id=order_id, user=user)
    order.status = "canceled"  # type: ignore
    order.save()
    return redirect("order_list")


def order_complete(request, order_id):
    user = get_current_user(request)
    if not user:
        return redirect("user_login")

    order = get_object_or_404(Order, id=order_id, user=user)
    order.status = "completed"  # type: ignore
    order.save()
    return redirect("order_list")


def comment_create(request, post_id):
    user = get_current_user(request)
    if not user:
        return redirect("user_login")

    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        image = request.FILES.get("image")
        video = request.FILES.get("video")

        if content:
            Comment.objects.create(
                post=post,
                author=user,
                content=content,
                image=image,
                video=video,
                is_active=True,
            )

        return redirect("post_detail", post_id=post.id)  # type: ignore

    return redirect("post_detail", post_id=post.id)  # type: ignore


def get_profile(request, user_id):
    user = get_object_or_404(Account, id=user_id)
    posts = Post.objects.filter(author=user).order_by("-created_at")
    return render(
        request, "profile/profile_detail.html", {"user": user, "posts": posts}
    )


@csrf_exempt
def react_to_post(request, post_id):
    from django.http import JsonResponse
    import json

    user = get_current_user(request)
    if not user:
        return JsonResponse({"error": "Not logged in"}, status=401)

    post = get_object_or_404(Post, id=post_id)

    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        reaction = data.get("reaction")

        EMOJI_MAP = {
            "👍": "like",
            "❤️": "love",
            "😂": "haha",
            "😮": "wow",
            "😢": "sad",
            "😡": "angry",
        }

        reaction_key = EMOJI_MAP.get(reaction)
        if not reaction_key:
            return JsonResponse({"error": "Invalid reaction"}, status=400)

        Reaction.objects.update_or_create(
            post=post,
            user=user,
            defaults={"reaction_type": reaction_key},
        )

        counts = post.reactions.values("reaction_type").annotate(count=Count("id"))  # type: ignore

        return JsonResponse(
            {
                "success": True,
                "counts": list(counts),
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Bad JSON"}, status=400)


def add_reaction(request, post_id, reaction_type):
    user = get_current_user(request)
    if not user:
        return redirect("user_login")

    post = get_object_or_404(Post, id=post_id)

    Reaction.objects.create(post=post, user=user, reaction_type=reaction_type)

    return redirect("post_detail", post_id=post.id)  # type: ignore
