from django.db import models
from django.contrib.auth.models import User


def note_upload_path(instance, filename):
    return f'notes/{instance.studying_year}/{instance.department}/{instance.section}/{instance.subject}/Unit_{instance.unit_number}/{filename}'


class Note(models.Model):
    YEAR_CHOICES = [
        ("1st Year", "1st Year"),
        ("2nd Year", "2nd Year"),
        ("3rd Year", "3rd Year"),
        ("4th Year", "4th Year"),
        ("Others", "Others"),
    ]

    studying_year = models.CharField(max_length=20, choices=YEAR_CHOICES, default="Others")
    department = models.CharField(max_length=100)
    section = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    unit_number = models.PositiveIntegerField()
    file = models.FileField(upload_to=note_upload_path)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.studying_year} - {self.department} - {self.section} - {self.subject} - Unit {self.unit_number}"

# Create your models here.
