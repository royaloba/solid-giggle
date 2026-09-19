from django.contrib import messages
#from django.core.checks import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from orders.models import Order
from .models import Product, Category, Brand, ProductImage, ProductVariant, Wishlist
from django.contrib.admin.views.decorators import staff_member_required
from .forms import ProductForm, BrandForm, CategoryForm
from django.db.models import Sum

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
        'user_wishlist': user_wishlist,
    })

@login_required
def toggle_wishlist(request, product_id):
    """Safely adds or removes a product from the wishlist."""
    product = get_object_or_404(Product, id=product_id)
    
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product).first()
    
    if wishlist_item:
        wishlist_item.delete() # Remove if exists
        in_wishlist = False
    else:
        Wishlist.objects.create(user=request.user, product=product) # Add if it doesn't
        in_wishlist = True
        
    if request.headers.get('HX-Request'):
        # Get the new total count of items in the wishlist
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        
        return render(request, 'store/partials/wishlist_heart.html', {
            'product': product,
            'in_wishlist': in_wishlist, # Pass the new state explicitly
            'wishlist_count': wishlist_count # Pass the count for the OOB swap
        })
        
    return redirect(request.META.get('HTTP_REFERER', 'store:list'))

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})



@staff_member_required(login_url='accounts:login')
def dashboard_add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            
            # Save the image to Cloudinary
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                ProductImage.objects.create(product=product, image=image_file, is_primary=True)
            
            # AUTOMATIC VARIANT & SKU GENERATION
            selected_sizes = form.cleaned_data.get('available_sizes')
            brand_prefix = product.brand.name[:3].upper()
            prod_prefix = product.name[:3].upper().replace(" ", "")
            
            for size in selected_sizes:
                # Format: NIK-AIR-15-42 (Brand - Product - Unique DB ID - Size)
                generated_sku = f"{brand_prefix}-{prod_prefix}-{product.id}-{size}"
                ProductVariant.objects.create(
                    product=product,
                    size=size,
                    sku=generated_sku
                )
            
            messages.success(request, f"{product.name} was added successfully with {len(selected_sizes)} sizes!")
            return redirect('store:dashboard_products') # Redirect to the products list
    else:
        form = ProductForm()

    return render(request, 'dashboard/add_product.html', {'form': form})

@staff_member_required(login_url='accounts:login')
def custom_dashboard(request):
    """Main Admin Dashboard Analytics and Overview"""
    
    # 1. Inventory Stats
    total_products = Product.objects.count()
    total_brands = Brand.objects.count()
    total_categories = Category.objects.count()
    
    # 2. Revenue & Order Stats
    total_orders = Order.objects.count()
    
    # Calculate Total Revenue instantly using database aggregation
    # If your Order model uses a status (like is_paid=True), you can change this to:
    # Order.objects.filter(is_paid=True).aggregate(sum=Sum('total_amount'))
    revenue_calc = Order.objects.aggregate(sum=Sum('total_amount'))
    total_revenue = revenue_calc['sum'] or 0.00  # Default to 0 if there are no orders yet
    
    # 3. Recent Activity for the tables (Latest 4 products, Latest 5 orders)
    latest_products = Product.objects.prefetch_related('images').order_by('-created_at')[:4]
    recent_orders = Order.objects.order_by('-created_at')[:5]

    context = {
        'total_products': total_products,
        'total_brands': total_brands,
        'total_categories': total_categories,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'latest_products': latest_products,
        'recent_orders': recent_orders,
    }
    return render(request, 'dashboard/index.html', context)

@staff_member_required(login_url='accounts:login')
def dashboard_add_brand(request):
    if request.method == 'POST':
        form = BrandForm(request.POST)
        if form.is_valid():
            brand = form.save()
            messages.success(request, f"Brand '{brand.name}' added successfully!")
            return redirect('store:dashboard')
    else:
        form = BrandForm()
    return render(request, 'dashboard/add_attribute.html', {'form': form, 'title': 'Add New Brand'})

@staff_member_required(login_url='accounts:login')
def dashboard_add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"Category '{category.name}' added successfully!")
            return redirect('store:dashboard')
    else:
        form = CategoryForm()
    return render(request, 'dashboard/add_attribute.html', {'form': form, 'title': 'Add New Category'})

@staff_member_required(login_url='accounts:login')
def dashboard_edit_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            
            # SYNC SIZES (Add new ones, remove unchecked ones)
            selected_sizes = form.cleaned_data.get('available_sizes')
            brand_prefix = product.brand.name[:3].upper()
            prod_prefix = product.name[:3].upper().replace(" ", "")
            
            # 1. Delete sizes that were unchecked
            product.variants.exclude(size__in=selected_sizes).delete()
            
            # 2. Add newly checked sizes
            existing_sizes = product.variants.values_list('size', flat=True)
            for size in selected_sizes:
                if size not in existing_sizes:
                    generated_sku = f"{brand_prefix}-{prod_prefix}-{product.id}-{size}"
                    ProductVariant.objects.create(
                        product=product,
                        size=size,
                        sku=generated_sku
                    )
            
            messages.success(request, f"{product.name} was updated successfully!")
            return redirect('store:dashboard_products')
    else:
        # Get existing sizes: ['40', '41', '42']
        existing_sizes = product.variants.values_list('size', flat=True)
        
        # Glue them together with commas: "40, 41, 42"
        sizes_string = ", ".join(existing_sizes)
        
        # Pass the string to the form
        form = ProductForm(instance=product, initial={'available_sizes': sizes_string})
        
    return render(request, 'dashboard/edit_product.html', {'form': form, 'product': product})

@staff_member_required(login_url='accounts:login')
def dashboard_delete_product(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f"{product_name} was deleted permanently.")
        return redirect('store:dashboard')
        
    return render(request, 'dashboard/confirm_delete.html', {'product': product})

@staff_member_required(login_url='accounts:login')
def dashboard_products(request):
    # Fetch all products, ordered by newest first
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'dashboard/products.html', {'products': products})

@staff_member_required(login_url='accounts:login')
def dashboard_orders(request):
    """List all orders for the admin."""
    # Ensure you imported Order from orders.models
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'dashboard/orders.html', {'orders': orders})

@staff_member_required(login_url='accounts:login')
def dashboard_order_detail(request, order_id):
    """View specific order details."""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'dashboard/order_detail.html', {'order': order})