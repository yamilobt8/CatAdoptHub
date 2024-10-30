from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.
class User(AbstractUser):
    pass

class Cat(models.Model):
    owner = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    age = models.IntegerField()
    address = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    description = models.CharField(max_length=50, default='No Description')
    image = models.URLField()
    is_available = models.BooleanField(default=True)
    is_adopted = models.BooleanField(default=False)
    is_ill = models.BooleanField(default=False)
    type_of_disease = models.CharField(max_length=50, blank=True, default="")
    def __str__(self):
        return f'{self.name} by {self.owner}'

class Comment(models.Model):
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, editable=False)
    def __str__(self):
        return f'comment by {self.user} on {self.cat.name}'

class AdoptionRequests(models.Model):
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE, related_name='adoption_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_requests')
    request_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Approved', 'Approved')], default='Pending')