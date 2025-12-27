from django.db import models


class Account(models.Model):
    username = models.CharField(
        max_length=28, default="Anonymous", blank=True, unique=True
    )
    display_name = models.CharField(
        max_length=28, default="Anonymous", blank=True, unique=False
    )
    email = models.EmailField(unique=False)
    password = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.username} ({self.display_name})" or "Anonymous"


class Post(models.Model):
    author = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to="posts/images/", null=True, blank=True)
    video = models.FileField(upload_to="posts/videos/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"

    @property
    def reaction_summary(self):
        """
        Returns a dict of reaction emoji and counts, plus user's own reaction
        """
        from django.db.models import Count

        reactions = self.reactions.values("reaction_type").annotate(count=Count("id"))  # type: ignore
        return {r["reaction_type"]: r["count"] for r in reactions}

    def user_reaction(self, user):
        if not user.is_authenticated:
            return None
        try:
            return self.reactions.get(user=user).reaction_type  # type: ignore
        except Reaction.DoesNotExist:
            return None


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="items/", blank=True, null=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="orders")
    items = models.ManyToManyField(Item, through="OrderItem")
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"  # type: ignore


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.item.name} in Order {self.order.id}"  # type: ignore


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="comments"
    )
    image = models.ImageField(upload_to="comments/images/", null=True, blank=True)
    video = models.FileField(upload_to="comments/videos/", null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return (
            f"Comment by {self.author.username} on Post {self.post.id}" or "No Content"  # type: ignore
        )


class Reaction(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(
        "Account", on_delete=models.CASCADE, related_name="reactions"
    )
    reaction_type = models.CharField(max_length=10)  # e.g., 👍, ❤️
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")  # One reaction per user per post

    def __str__(self):
        return f"{self.reaction_type} by {self.user.username} on Post {self.post.id}"
