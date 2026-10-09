import os
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from apps.students.services import DataImportService

class DataImportWebUploadView(LoginRequiredMixin, View):
    """Admin-facing dataset upload and validation interface."""
    template_name = 'students/data_import.html'

    def get(self, request, *args, **kwargs):
        if not (request.user.is_admin_user() or request.user.is_staff):
            raise PermissionDenied("Only administrators can access the dataset import manager.")
        return render(request, self.template_name, {
            'categories': ['Student Profiles', 'Academic Records', 'Attendance Records', 'LMS Activity Summaries', 'Placement Assessments']
        })

    def post(self, request, *args, **kwargs):
        if not (request.user.is_admin_user() or request.user.is_staff):
            raise PermissionDenied("Only administrators can access the dataset import manager.")

        dataset_file = request.FILES.get('dataset_file')
        category = request.POST.get('category', 'Student Profiles')

        if not dataset_file:
            messages.error(request, "Please select a valid CSV or Excel file to upload.")
            return redirect('students:data_import')

        # Validate file extension
        ext = os.path.splitext(dataset_file.name)[1].lower()
        if ext not in ['.csv', '.xlsx', '.xls']:
            messages.error(request, f"Unsupported file format '{ext}'. Only CSV and Excel (.xlsx, .xls) files are permitted.")
            return redirect('students:data_import')

        # Save temporary file safely
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'imports'))
        filename = fs.save(dataset_file.name, dataset_file)
        file_path = fs.path(filename)

        try:
            result = DataImportService.import_from_file(file_path)
            imported_count = result['imported_count']
            errors = result['errors']

            if imported_count > 0:
                messages.success(request, f"Successfully processed and imported {imported_count} student records from '{dataset_file.name}'.")
            
            if errors:
                messages.warning(request, f"Encountered {len(errors)} validation warnings during import.")

            return render(request, self.template_name, {
                'categories': ['Student Profiles', 'Academic Records', 'Attendance Records', 'LMS Activity Summaries', 'Placement Assessments'],
                'filename': dataset_file.name,
                'category': category,
                'imported_count': imported_count,
                'errors': errors,
                'import_completed': True
            })
        except Exception as e:
            messages.error(request, f"Import Failed: {str(e)}")
            return redirect('students:data_import')
        finally:
            # Cleanup temp file
            if os.path.exists(file_path):
                os.remove(file_path)
