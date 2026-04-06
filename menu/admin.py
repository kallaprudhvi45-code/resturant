from django.contrib import admin
from .models import Category, SubCategory, FoodItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'subcategory', 'price', 'is_best_seller', 'is_available')
    list_filter = ('category', 'subcategory', 'is_best_seller', 'is_available')
    search_fields = ('name', 'description')
