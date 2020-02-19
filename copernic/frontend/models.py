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
