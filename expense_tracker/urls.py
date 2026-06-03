from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('accounts.urls')),
    path('groups/', include('groups.urls')),
    path('expenses/', include('expenses.urls')),
    path('payments/', include('payments.urls')),
    path('notifications/', include('notifications.urls')),
    path('reports/', include('reports.urls')),
    path('agents/', include('agents.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
