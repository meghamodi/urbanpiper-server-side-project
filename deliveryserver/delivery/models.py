from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):

    USER_TYPE_CHOICES = (
      (1, 'store_manager'),
      (2, 'delivery_person'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="user_profile"
    )
    user_type = models.IntegerField(
        choices=USER_TYPE_CHOICES,
        default=1
    )
    created_on = models.DateTimeField(
        auto_now_add=True
    )
    modified_on = models.DateTimeField(
        auto_now=True
    )

class DeliveryTask(models.Model):
    PRIORITY_CHOICES = (
        (1, 'high'),
        (2, 'medium'),
        (3, 'low'),
    )
    STATE_CHOICES = (
        (1, 'new'),
        (2, 'accepted'),
        (3, 'completed'),
        (4, 'declined'),
        (5, 'cancelled'),
    )
    title = models.CharField(
        max_length=255
    )


    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=1
    )
    created_by = models.ForeignKey(
        User,
        related_name='delivery_tasks',
        on_delete=models.CASCADE
    )
    state = models.IntegerField(
        choices=STATE_CHOICES,
        default=1
    )
    created_on = models.DateTimeField(
        auto_now_add=True
    )
