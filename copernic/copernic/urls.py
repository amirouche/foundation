# copernic (https://github.com/amirouche/copernic)

# Copyright (C) 2020 Amirouche Boubekki

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
    path('plot/', frontend.plot),
    path('map/', frontend.map),
    path('admin/', admin.site.urls),
    # uid
    path('uid/<uid>/', frontend.uid),
    # change
    path('changes/', frontend.changes),
    path('change/new/', frontend.change_new),
    path('change/<changeid>/', frontend.change),
    # change comment
    path('change/<changeid>/comment/add/', frontend.comment_add),
    path('change/<changeid>/add/', frontend.change_add),
    path('change/<changeid>/delete/', frontend.change_delete),
    path('change/<changeid>/import/', frontend.change_import),
    path('change/<changeid>/apply/', frontend.change_apply),
]
