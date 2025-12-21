from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Account, Post, Item, Order, OrderItem, Comment, Reaction
from django.db.models import Count
from django.views.decorators.csrf import csrf_exempt
import logging

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
        request.session["user_id"] = user.id
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
            request.session["user_id"] = user.id
            return redirect("post_list")
        except Account.DoesNotExist:
            return render(
                request,
                "login/login.html",
                {"error": "Sai tên người dùng hoặc mật khẩu"},
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
        return redirect("post_list")  # Redirect để reload trang

    posts = Post.objects.select_related("author").order_by("-created_at")
    return render(request, "home/post_list.html", {"posts": posts, "user": user})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.filter(is_active=True).order_by("-created_at")

    user = get_current_user(request)

    return render(
        request,
        "details/post_detail.html",
        {
            "post": post,
            "comments": comments,
            "user": user,
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

        return redirect("order_detail", order_id=order.id)

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
    order.status = "canceled"
    order.save()
    return redirect("order_list")


def order_complete(request, order_id):
    user = get_current_user(request)
    if not user:
        return redirect("user_login")

    order = get_object_or_404(Order, id=order_id, user=user)
    order.status = "completed"
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

        return redirect("post_detail", post_id=post.id)

    return redirect("post_detail", post_id=post.id)


def get_profile(request, user_id):
    user = get_object_or_404(Account, id=user_id)
    posts = Post.objects.filter(author=user).order_by("-created_at")
    return render(
        request, "profile/profile_detail.html", {"user": user, "posts": posts}
    )


@csrf_exempt
def react_to_post(request, post_id):
    """Handle reaction to a post via AJAX POST."""
    import json
    from django.http import JsonResponse

    user = get_current_user(request)
    if not user:
        return JsonResponse({"error": "Not authenticated"}, status=401)

    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            reaction = data.get("reaction", "")

            logger.info(
                "react_to_post called",
                extra={
                    "post_id": post_id,
                    "user_id": getattr(user, "id", None),
                    "reaction": reaction,
                },
            )

            if not reaction:
                logger.warning(
                    "No reaction provided in request body", extra={"post_id": post_id}
                )
                return JsonResponse({"error": "No reaction provided"}, status=400)
            # Normalize reaction: map emoji or other labels to allowed choice keys
            EMOJI_MAP = {
                "❤️": "love",
                "😂": "haha",
                "😮": "wow",
                "😢": "sad",
                "😡": "angry",
                "👍": "like",
                "👎": "angry",
                "🔥": "like",
                "🎉": "love",
                "😍": "love",
                "👏": "love",
                "💯": "love",
            }

            reaction_key = EMOJI_MAP.get(reaction, reaction)

            try:
                # Create or update reaction (upsert)
                obj, created = Reaction.objects.update_or_create(
                    post=post, user=user, defaults={"reaction_type": reaction_key}
                )
            except Exception as e:
                logger.exception("Failed to save reaction", exc_info=e)
                return JsonResponse(
                    {"error": "Failed to save reaction", "details": str(e)}, status=500
                )

            # Return aggregated counts per reaction type for the post
            counts = list(
                post.reactions.values("reaction_type").annotate(count=Count("id"))
            )

            logger.info(
                "Reaction saved",
                extra={
                    "post_id": post_id,
                    "user_id": user.id,
                    "reaction": reaction,
                    "created": created,
                },
            )

            return JsonResponse(
                {
                    "success": True,
                    "created": created,
                    "reaction": reaction,
                    "counts": counts,
                }
            )
        except json.JSONDecodeError:
            logger.warning(
                "Invalid JSON received in react_to_post", extra={"post_id": post_id}
            )
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Method not allowed"}, status=405)


def add_reaction(request, post_id, reaction_type):
    user = get_current_user(request)
    if not user:
        return redirect("user_login")

    post = get_object_or_404(Post, id=post_id)

    Reaction.objects.create(post=post, user=user, reaction_type=reaction_type)

    return redirect("post_detail", post_id=post.id)
