from django.shortcuts import render
from .models import FoodItem, Category, SubCategory

def menu_view(request):
    items = FoodItem.objects.filter(is_available=True)

    category_slug = request.GET.get('category')
    subcategory_id = request.GET.get('subcategory')
    search = request.GET.get('search')
    price = request.GET.get('price')

    if category_slug:
        items = items.filter(category__slug=category_slug)

    if subcategory_id:
        items = items.filter(subcategory__id=subcategory_id)

    if search:
        items = items.filter(name__icontains=search)

    if price:
        if price == "low":
            items = items.filter(price__lt=10)
        elif price == "mid":
            items = items.filter(price__range=(10, 15))
        elif price == "high":
            items = items.filter(price__gt=15)

    subcategories = SubCategory.objects.all()
    if category_slug:
        subcategories = subcategories.filter(category__slug=category_slug)

    context = {
        'items': items,
        'subcategories': subcategories,
        'current_category': category_slug,
        'current_subcategory': subcategory_id,
        'current_price': price,
        'search_query': search,
    }
    return render(request, 'menu.html', context)
