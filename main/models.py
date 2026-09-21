import uuid
from django.db import models

# Create your models here.
class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    role = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None
    
class Education(models.Model):
    institution = models.CharField(max_length=255)
    program = models.CharField(max_length=255)
    start_year = models.PositiveIntegerField()
    end_year = models.PositiveIntegerField(blank=True, null=True)
    activities = models.TextField(blank=True, default="")
    
    def __str__(self): 
        return self.institution

class Message(models.Model):
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=100)
    message = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name