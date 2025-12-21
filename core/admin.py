from django.contrib import admin
from .models import Account, Post, Order, OrderItem, Item


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("username", "display_name", "email")
    search_fields = ("username", "display_name", "email")
    list_filter = ("username", "display_name", "email")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("author", "created_at")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "is_completed",
        "is_canceled",
        "created_at",
        "display_items",
    )
    inlines = [OrderItemInline]

    def display_items(self, obj):
        return ", ".join(
            [
                f"{oi.item.id}: {oi.item.name} (x{oi.quantity})"
                for oi in obj.orderitem_set.all()
            ]
        )

    display_items.short_description = "Items"


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price")
    search_fields = ("name",)
    list_filter = ("price",)
