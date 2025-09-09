from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_note, name='upload_note'),
    path('notes/', views.note_list, name='note_list'),
    path('notes/years/', views.note_years, name='note_years'),
    path('notes/<str:year>/sections/', views.note_sections, name='note_sections'),
    path('notes/<str:year>/<str:section>/subjects/', views.note_subjects, name='note_subjects'),
    path('notes/<str:year>/<str:section>/<str:subject>/units/', views.note_units, name='note_units'),
    path('notes/<str:year>/<str:section>/<str:subject>/<int:unit>/notes/', views.note_unit_notes, name='note_unit_notes'),
    path('view/<int:note_id>/', views.view_note_inline, name='view_note_inline'),
    path('webview/<int:note_id>/', views.view_note_web, name='view_note_web'),
]

