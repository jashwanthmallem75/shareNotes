from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("studying_year", "department", "section", "subject", "unit_number", "uploaded_by", "uploaded_at")
    search_fields = ("department", "section", "subject")
    list_filter = ("studying_year", "department", "section", "subject")

# Register your models here.
