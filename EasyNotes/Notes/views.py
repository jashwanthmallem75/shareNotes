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
    return render(request, 'note_years.html', {'years': years})
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
    response = FileResponse(open(note.file.path, 'rb'), content_type=content_type or 'application/octet-stream')
    # Force inline display instead of download for browser-viewable types (e.g., PDFs, images)
    response['Content-Disposition'] = f"inline; filename=\"{note.file.name.split('/')[-1]}\""
    return response


def view_note_web(request, note_id):
    try:
        note = Note.objects.get(pk=note_id)
    except Note.DoesNotExist:
        raise Http404("File not found")
    url = note.file.url
    ext = note.file.name.split('.')[-1].lower()
    # For office formats, attempt local conversion to PDF via LibreOffice (soffice)
    office_exts = {"doc", "docx", "ppt", "pptx", "xls", "xlsx"}
    if ext in office_exts:
        src_path = Path(note.file.path)
        pdf_path = src_path.with_suffix('.pdf')
        # Convert only if PDF missing or source is newer
        try:
            if not pdf_path.exists() or src_path.stat().st_mtime > pdf_path.stat().st_mtime:
                # Try calling LibreOffice headless to convert
                from django.conf import settings
                soffice_binary = getattr(settings, 'SOFFICE_PATH', None) or 'soffice'
                soffice_cmd = [
                    soffice_binary, '--headless', '--nologo', '--nodefault', '--nolockcheck',
                    '--convert-to', 'pdf', '--outdir', str(src_path.parent), str(src_path)
                ]
                subprocess.run(soffice_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            # If conversion fails, show error message and fallback download link
            error_msg = f"Document conversion failed: {str(e)}. You can download the file instead."
            return render(request, 'web_viewer.html', {"viewer_url": None, "download_url": url, "error_msg": error_msg})

        if pdf_path.exists():
            # Build MEDIA URL for the generated PDF
            from django.conf import settings
            rel = os.path.relpath(str(pdf_path), str(settings.MEDIA_ROOT))
            viewer_url = request.build_absolute_uri(settings.MEDIA_URL + rel.replace('\\', '/'))
            return render(request, 'web_viewer.html', {"viewer_url": viewer_url, "download_url": url, "error_msg": None})

    # Non-office types or conversion not needed
    viewer_url = request.build_absolute_uri(url)
    return render(request, 'web_viewer.html', {"viewer_url": viewer_url, "download_url": url, "error_msg": None})

# Create your views here.
