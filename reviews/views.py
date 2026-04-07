from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Review

def submit_review(request):
    if request.method == 'POST':
        name = request.POST.get('name') or ''
        phone = request.POST.get('phone') or ''
        rating = request.POST.get('rating')
        comment = request.POST.get('comment') or ''
        
        phone = "".join(c for c in phone if c.isdigit() or c == '+')
        if len(phone) > 15:
            phone = phone[:15]
            
        if len(name) > 100:
            name = name[:100]
        
        Review.objects.create(
            name=name,
            phone_number=phone,
            rating=rating,
            comment=comment
        )
        messages.success(request, "Thank you for your review!")
        
        # Clear the flag
        if 'show_review_popup' in request.session:
            del request.session['show_review_popup']
            
        return redirect('core:home')
    return redirect('core:home')
