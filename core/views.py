from django.shortcuts import render, redirect
from django.contrib import messages
from menu.models import FoodItem
from reviews.models import Review
from .models import ContactMessage

def home(request):
    best_sellers = FoodItem.objects.filter(is_best_seller=True, is_available=True)[:6]
    latest_reviews = Review.objects.all().order_by('-created_at')[:5]
    return render(request, 'home.html', {
        'best_sellers': best_sellers,
        'reviews': latest_reviews
    })

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message
        )
        messages.success(request, "Your message has been sent successfully!")
        return redirect('core:contact')
        
    return render(request, 'contact.html')
