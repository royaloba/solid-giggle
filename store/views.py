from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Brand, Wishlist

def home_view(request):
    categories = Category.objects.all()
    # Fetch top 4 featured sneakers
    featured_products = Product.objects.filter(is_featured=True).prefetch_related('images')[:4]
    
    # Fetch 8 newest arrivals, excluding the featured ones
    new_arrivals = Product.objects.exclude(id__in=featured_products).order_by('-created_at').prefetch_related('images')[:8]
    
    # Fetch only brands that have at least one product associated with them
    active_brands = Brand.objects.filter(products__isnull=False).distinct()

    user_wishlist = []
    if request.user.is_authenticated:
        # WRAPPED IN list() so the template can read it perfectly
        user_wishlist = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    return render(request, 'store/home.html', {
        'categories': categories,
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
        'brands': active_brands,
        'user_wishlist': user_wishlist,
    })

def product_detail(request, slug):
    # prefetch_related prevents N+1 queries when looping through images and variants in the template
    product = get_object_or_404(
        Product.objects.prefetch_related('images', 'variants'), 
        slug=slug
    )
    
    context = {
        'product': product,
        # Optional: You can filter out variants with 0 stock here, 
        # or handle it visually in the template (shown below)
        'variants': product.variants.all(), 
        'images': product.images.all(),
    }
    
    user_wishlist = []
    if request.user.is_authenticated:
        # WRAPPED IN list()
        user_wishlist = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    
    context['user_wishlist'] = user_wishlist
    return render(request, 'store/product_detail.html', context)

def product_list(request):
    """Handles the main store page, category filtering, searching, and sorting"""
    products = Product.objects.all().prefetch_related('images')
    categories = Category.objects.all()
    brands = Brand.objects.all() # Fetch brands for the filter drawer
    
    # Category Filter
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
        
    # Search Query
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(brand__name__icontains=search_query)
        )

    # Brand Filter
    brand_slug = request.GET.get('brand')
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)

    # Price Filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(base_price__gte=min_price)
    if max_price:
        products = products.filter(base_price__lte=max_price)

    # Sort Order
    sort_by = request.GET.get('sort')
    if sort_by == 'price_asc':
        products = products.order_by('base_price')
    elif sort_by == 'price_desc':
        products = products.order_by('-base_price')
    else:
        products = products.order_by('-created_at') # Default to Newest

    user_wishlist = []
    if request.user.is_authenticated:
        # WRAPPED IN list()
        user_wishlist = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
        
    return render(request, 'store/store.html', {
        'products': products.distinct(),
        'categories': categories,
        'brands': brands,
        'current_category': category_slug,
        'user_wishlist': user_wishlist, # ADDED: This was missing!
    })

@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        user_wishlist = request.user.wishlist.values_list('id', flat=True) 
        return render(request, 'store/partials/product_card.html', {
            'product': product,
            'user_wishlist': user_wishlist
        })
        
    # Redirect back to wherever the user clicked it from
    return redirect(request.META.get('HTTP_REFERER', 'store:home'))

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})