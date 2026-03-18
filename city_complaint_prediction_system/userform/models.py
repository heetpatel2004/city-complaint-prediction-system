from django.db import models
import random

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]

    CATEGORY_CHOICES = [
        ('Garbage', 'Garbage'),
        ('Water Supply', 'Water Supply'),
        ('Road Issues', 'Road Issues'),
        ('Street Lights', 'Street Lights'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    mobile = models.CharField(max_length=15)
    category = models.CharField(max_length=50,choices=CATEGORY_CHOICES,default='Garbage')
    complaint_title = models.CharField(max_length=200)
    description = models.TextField()

    image = models.ImageField(upload_to='complaints/', blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    complaint_id = models.CharField(max_length=20, unique=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 Generate unique complaint ID safely
    def save(self, *args, **kwargs):
        if not self.complaint_id:
            while True:
                new_id = "CMP" + str(random.randint(10000, 99999))
                if not Complaint.objects.filter(complaint_id=new_id).exists():
                    self.complaint_id = new_id
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.complaint_id} - {self.complaint_title}"