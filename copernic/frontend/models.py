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
from django.db import models


class ChangeRequest(models.Model):
    STATUS_WIP = 1
    STATUS_APPLIED = 2
    STATUS_CHOICES = (
        (STATUS_WIP, 'work-in-progres'),
        (STATUS_APPLIED, 'applied'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    changeid = models.UUIDField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_WIP)


class Comment(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    body = models.TextField()
    change_request = models.ForeignKey(ChangeRequest, on_delete=models.CASCADE)
