# -*- coding: utf-8 -*-
from shop.models.cartmodel import Cart
from django.contrib.auth.models import AnonymousUser


def get_or_create_cart(request):
    """
    Let's inspect the request for session or for user, then either find a
    matching cart and return it or create a new one bound to the user (if one
    exists), or to the session.
    """

    if not hasattr(request, '_cart'):
        session = getattr(request, 'session', None)
        session_cart = None
        if session != None:
            try:
                session_cart = Cart.objects.get(pk=session['cart_id'])
            except (Cart.DoesNotExist, KeyError):
                pass

        user = None
        user_cart = None
        if request.user and not isinstance(request.user, AnonymousUser):
            user = request.user
            try:
                user_cart = Cart.objects.get(user=user)
            except (Cart.DoesNotExist):
                pass

        cart = None
        if session_cart and user_cart and session_cart != user_cart:
            # NOTE: Overwrite user cart if session cart has items
            if len(session_cart.items.all()) >= 1:
                user_cart.delete()
                cart = session_cart
                cart.user = user
                cart.save()
            else:
                session['cart_id'] = user_cart.id
                cart = user_cart
        elif user_cart:
            cart = user_cart
        elif session_cart:
            cart = session_cart

        # NOTE: Create cart if non found
        if not cart:
            cart = Cart()
            if user != None:
                cart.user = user
            cart.save()
            if session != None:
                session['cart_id'] = cart.id

        setattr(request, '_cart', cart)

    return getattr(request, '_cart')
