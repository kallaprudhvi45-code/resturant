from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from menu.models import FoodItem
from .models import Order, OrderItem
import urllib.parse

def cart_add(request, item_id):
    cart = request.session.get('cart', {})
    item_id_str = str(item_id)
    
    if item_id_str in cart:
        cart[item_id_str] += 1
    else:
        cart[item_id_str] = 1
        
    request.session['cart'] = cart
    messages.success(request, "Item added! To order, go to cart.")
    return redirect('menu:menu_view')

def cart_remove(request, item_id):
    cart = request.session.get('cart', {})
    item_id_str = str(item_id)
    if item_id_str in cart:
        del cart[item_id_str]
    request.session['cart'] = cart
    return redirect('orders:cart_detail')

def cart_update(request, item_id, action):
    cart = request.session.get('cart', {})
    item_id_str = str(item_id)
    if item_id_str in cart:
        if action == 'increment':
            cart[item_id_str] += 1
        elif action == 'decrement':
            cart[item_id_str] -= 1
            if cart[item_id_str] <= 0:
                del cart[item_id_str]
    request.session['cart'] = cart
    return redirect('orders:cart_detail')

def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0
    invalid_items = []
    
    for item_id, quantity in cart.items():
        try:
            food_item = FoodItem.objects.get(id=item_id)
        except FoodItem.DoesNotExist:
            invalid_items.append(item_id)
            continue
        subtotal = food_item.price * quantity
        total_price += subtotal
        cart_items.append({
            'food_item': food_item,
            'quantity': quantity,
            'subtotal': subtotal
        })
    
    # Clean up invalid items from session
    if invalid_items:
        for item_id in invalid_items:
            del cart[item_id]
        request.session['cart'] = cart
        
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('menu:menu_view')
        
    if request.method == 'POST':
        full_name = request.POST.get('name') or ''
        phone = request.POST.get('phone') or ''
        address = request.POST.get('address') or ''
        pincode = request.POST.get('pincode') or ''
        
        # Validate missing fields
        if not full_name or not phone or not address or not pincode:
            messages.error(request, "Please fill in all required fields.")
            return redirect('orders:checkout')
            
        # Strip phone to prevent 500 DataError on PostgreSQL which enforces max_length=15
        phone = "".join(c for c in phone if c.isdigit() or c == '+')
        if len(phone) > 15:
            phone = phone[:15]
            
        if len(full_name) > 200:
            full_name = full_name[:200]
            
        if len(pincode) > 10:
            pincode = pincode[:10]
        
        # Calculate total
        total_amount = 0
        order_items_data = []
        for item_id, quantity in cart.items():
            try:
                food_item = FoodItem.objects.get(id=item_id)
            except FoodItem.DoesNotExist:
                continue  # Skip items that don't exist in DB
            total_amount += food_item.price * quantity
            order_items_data.append((food_item, quantity))
        
        if not order_items_data:
            messages.warning(request, "Could not find the items in your cart. Please try again.")
            request.session['cart'] = {}
            return redirect('menu:menu_view')
            
        # Create Order
        order = Order.objects.create(
            full_name=full_name,
            phone_number=phone,
            address=address,
            pincode=pincode,
            total_amount=total_amount
        )
        
        items_list_str = ""
        for food_item, quantity in order_items_data:
            OrderItem.objects.create(
                order=order,
                food_item=food_item,
                quantity=quantity,
                price=food_item.price
            )
            items_list_str += f"- {food_item.name} x {quantity} \n"
            
        # Review logic: Check if this is the 2nd order (or more) and NOT already reviewed
        from reviews.models import Review
        order_count = Order.objects.filter(phone_number=phone).count()
        already_reviewed = Review.objects.filter(phone_number=phone).exists()
        
        if order_count >= 2 and not already_reviewed:
            request.session['show_review_popup'] = True
        else:
            request.session['show_review_popup'] = False
            
        # Clear Cart
        request.session['cart'] = {}
        
        # WhatsApp message generation
        from django.conf import settings
        import re
        
        # Get raw number from settings
        raw_number = str(getattr(settings, 'WHATSAPP_NUMBER', '9133117272'))
        # Clean non-numeric characters e.g. +, -, spaces
        clean_number = "".join(filter(str.isdigit, raw_number))
        
        # Logic: If it's a 10-digit number and doesn't start with 91, prepend 91 for India
        if len(clean_number) == 10 and not clean_number.startswith('91'):
            clean_number = "91" + clean_number
            
        message = f"Name: {full_name}\n" \
                  f"Phone: {phone}\n" \
                  f"Address: {address} ({pincode})\n\n" \
                  f"Items:\n{items_list_str}\n" \
                  f"Total: ₹{total_amount}"
                  
        encoded_message = urllib.parse.quote(message)
        # Using https://api.whatsapp.com/ to ensure compatibility with both mobile and WhatsApp Web
        whatsapp_url = f"https://api.whatsapp.com/send?phone={clean_number}&text={encoded_message}"
        
        # Redirect logic: we want to show a success page with the review popup and then redirect to whatsapp
        return render(request, 'order_success.html', {'whatsapp_url': whatsapp_url})
        
    return render(request, 'order.html')

