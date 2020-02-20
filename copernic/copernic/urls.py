"""copernic URL Configuration

The `urlpatterns` list routes URLs to views. For more information
    please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/ Examples:
    Function views 1. Add an import: from my_app import views 2. Add a
    URL to urlpatterns: path('', views.home, name='home') Class-based
    views 1. Add an import: from other_app.views import Home 2. Add a
    URL to urlpatterns: path('', Home.as_view(), name='home')
    Including another URLconf 1. Import the include() function: from
    django.urls import include, path 2. Add a URL to urlpatterns:
    path('blog/', include('blog.urls'))

"""
from django.contrib import admin
from django.urls import path
import frontend.views as frontend

urlpatterns = [
    path('', frontend.index),
    path('about/', frontend.about),
    path('query/', frontend.query),
    path('admin/', admin.site.urls),
    # uid
    path('uid/<uid>/', frontend.uid),
    # change
    path('changes/', frontend.changes),
    path('change/new/', frontend.change_new),
    path('change/<changeid>/', frontend.change),
    # path('change/<changeid>/add/', frontend.change_add),
    # path('change/<changeid>/delete/', frontend.change_delete),
    # path('change/<changeid>/apply/', frontend.change_apply),
    # change comment
    path('change/<changeid>/comment/add/', frontend.comment_add),
    path('change/<changeid>/add/', frontend.change_add),
    path('change/<changeid>/delete/', frontend.change_delete),
    path('change/<changeid>/import/', frontend.change_import),
    path('change/<changeid>/apply/', frontend.change_apply),
]
