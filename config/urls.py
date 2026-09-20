
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Stylinsole Administration"
admin.site.site_title = "Stylinsole Admin Portal"
admin.site.index_title = "Welcome to the Store, Manager "

urlpatterns = [
    path('', include('store.urls', namespace='store')),  # Include the store app's URLs
    path('admin/', admin.site.urls),
    path('payments/', include('payments.urls', namespace='payments')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)