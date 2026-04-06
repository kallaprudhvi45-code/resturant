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
    
    for item_id, quantity in cart.items():
        food_item = get_object_or_404(FoodItem, id=item_id)
        subtotal = food_item.price * quantity
        total_price += subtotal
        cart_items.append({
            'food_item': food_item,
            'quantity': quantity,
            'subtotal': subtotal
        })
        
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect('menu:menu_view')
        
    if request.method == 'POST':
        full_name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        
        # Calculate total
        total_amount = 0
        order_items_data = []
        for item_id, quantity in cart.items():
            food_item = FoodItem.objects.get(id=item_id)
            total_amount += food_item.price * quantity
            order_items_data.append((food_item, quantity))
            
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
        # Using whatsapp:// to ensure it tries to open the mobile app directly
        whatsapp_url = f"whatsapp://send?phone={clean_number}&text={encoded_message}"
        
        # Redirect logic: we want to show a success page with the review popup and then redirect to whatsapp
        return render(request, 'order_success.html', {'whatsapp_url': whatsapp_url})
        
    return render(request, 'order.html')
