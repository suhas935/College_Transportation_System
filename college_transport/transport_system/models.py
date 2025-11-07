from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    usn = models.CharField(max_length=20, unique=True)
    sem = models.CharField(max_length=10)
    branch = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    emergency_phone = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='student_photos/')

    def __str__(self):
        return f"{self.user.username} - {self.usn}"

class BusRoute(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100)
    route = models.CharField(max_length=100)
    registered_at = models.DateTimeField(auto_now_add=True)







class Notification(models.Model):
    NOTIF_TYPES = [
        ('arrival', 'Arrival'),
        ('delay', 'Delay'),
        ('route', 'Route Change'),
    ]

    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.notif_type})"


class Payment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    route_name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=8, decimal_places=2,default=15000)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Paid")

    def __str__(self):
        return f"{self.student.username} - {self.route_name} - {self.amount}"