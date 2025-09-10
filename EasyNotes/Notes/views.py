# Step 5: Show notes for a selected year, section, subject, and unit
def note_unit_notes(request, year, section, subject, unit):
    notes = Note.objects.filter(studying_year=year, section=section, subject=subject, unit_number=unit)
    return render(request, 'note_unit_notes.html', {'year': year, 'section': section, 'subject': subject, 'unit': unit, 'notes': notes})
# Step 4: Show available units for a selected year, section, and subject
def note_units(request, year, section, subject):
    units = Note.objects.filter(studying_year=year, section=section, subject=subject).values_list('unit_number', flat=True).distinct().order_by('unit_number')
    return render(request, 'note_units.html', {'year': year, 'section': section, 'subject': subject, 'units': units})
# Step 3: Show available subjects for a selected year and section
def note_subjects(request, year, section):
    subjects = Note.objects.filter(studying_year=year, section=section).values_list('subject', flat=True).distinct().order_by('subject')
    return render(request, 'note_subjects.html', {'year': year, 'section': section, 'subjects': subjects})
# Step 2: Show available sections for a selected year
def note_sections(request, year):
    sections = Note.objects.filter(studying_year=year).values_list('section', flat=True).distinct().order_by('section')
    return render(request, 'note_sections.html', {'year': year, 'sections': sections})
from django.urls import reverse
# Step 1: Show available years
def note_years(request):
    years = Note.objects.values_list('studying_year', flat=True).distinct().order_by('studying_year')
    return render(request, 'note_years.html', {'years': years}) # Step 5: Show notes for a selected year, section, subject, and unit
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from collections import defaultdict
from django.http import FileResponse, Http404
import mimetypes
import os
import subprocess
from pathlib import Path

from .forms import NoteForm
from .models import Note


def home(request):
    return render(request, 'index.html')


@login_required(login_url='login')
def upload_note(request):
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            studying_year = form.cleaned_data['studying_year']
            department = form.cleaned_data['department'].upper().strip()
            section = form.cleaned_data['section'].upper().strip()
            subject = form.cleaned_data['subject'].title().strip()
            unit_number = form.cleaned_data['unit_number']
            files = request.FILES.getlist('files')
            if not files:
                messages.error(request, 'Please select at least one file to upload.')
                return render(request, 'upload.html', {'form': form})
            for f in files:
                Note.objects.create(
                    studying_year=studying_year,
                    department=department,
                    section=section,
                    subject=subject,
                    unit_number=unit_number,
                    file=f,
                    uploaded_by=request.user,
                )
            messages.success(request, 'Notes uploaded successfully!')
            
        else:
            messages.error(request, 'Please fix the errors below and resubmit.')
            return render(request, 'upload.html', {'form': form})
    else:
        form = NoteForm()
    return render(request, 'upload.html', {'form': form})


@login_required(login_url='login')
def note_list(request):
    notes = Note.objects.all().order_by(
        "studying_year", "department", "section", "subject", "unit_number"
    )
    structure = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))
    for note in notes:
        structure[note.studying_year][note.department][note.section][note.subject].append(note)

    def dictify(d):
        if isinstance(d, defaultdict):
            return {k: dictify(v) for k, v in d.items()}
        elif isinstance(d, dict):
            return {k: dictify(v) for k, v in d.items()}
        else:
            return d

    structure = dictify(structure)
    return render(request, 'note_list.html', {'structure': structure})


def view_note_inline(request, note_id):
    try:
        note = Note.objects.get(pk=note_id)
    except Note.DoesNotExist:
        raise Http404("File not found")
    content_type, _ = mimetypes.guess_type(note.file.path)
    # Redirect to the file's URL. The browser will handle opening or downloading it.
    # This is more robust for production environments and mobile devices.
    return redirect(note.file.url)


def view_note_web(request, note_id):
    try:
        note = Note.objects.get(pk=note_id)
    except Note.DoesNotExist:
        raise Http404("File not found")
    # The `view_note_web` logic is complex and relies on local file conversion,
    # which is not suitable for a standard production server.
    # We will simplify it to redirect to the file's URL, just like `view_note_inline`.
    # This ensures consistent and reliable behavior.
    return redirect(note.file.url)

# Create your views here.
