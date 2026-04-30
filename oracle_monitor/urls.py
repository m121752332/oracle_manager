from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # ⭐ 加這行（admin入口）
    path('admin/', admin.site.urls),
    path('', include('locks.urls')),
]
