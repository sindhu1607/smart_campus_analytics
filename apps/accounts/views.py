from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, View
from django.urls import reverse_lazy
from django.contrib import messages

from apps.accounts.models import User
from apps.students.models import StudentProfile, Department, Program
from apps.analytics.services import StudentAnalyticsEngine

class LandingPageView(TemplateView):
    template_name = 'landing.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard_redirect')
        return super().get(request, *args, **kwargs)

class UserLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('accounts:dashboard_redirect')

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login')

class UserRegisterView(View):
    template_name = 'accounts/register.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('accounts:dashboard_redirect')
        departments = Department.objects.all()
        return render(request, self.template_name, {'departments': departments})

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        student_id_input = request.POST.get('student_id', '').strip()
        dept_id = request.POST.get('department')

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, self.template_name, {'departments': Department.objects.all()})

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken. Please choose another username.")
            return render(request, self.template_name, {'departments': Department.objects.all()})

        if email and User.objects.filter(email=email).exists():
            messages.error(request, f"Email '{email}' is already registered.")
            return render(request, self.template_name, {'departments': Department.objects.all()})

        # Security: Public self-registration is strictly restricted to STUDENT role.
        # Faculty, Placement, and Admin accounts must be created by an existing Administrator.
        role = User.Role.STUDENT

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )

        student_id = student_id_input.upper() if student_id_input else f"STU{user.id:04d}"
        dept = Department.objects.filter(id=dept_id).first() if dept_id else Department.objects.first()
        if not dept:
            dept = Department.objects.create(code='CSE', name='Computer Science & Engineering')
        prog = dept.programs.first() if dept else None
        if not prog and dept:
            prog = Program.objects.create(code=f'BTECH-{dept.code}', name=f'B.Tech in {dept.name}', department=dept)
        
        student_profile = StudentProfile.objects.create(
            user=user,
            student_id=student_id,
            first_name=first_name or username,
            last_name=last_name or 'Student',
            email=email or f"{username}@campus.edu",
            department=dept,
            program=prog,
            admission_year=2025,
            current_semester=1
        )
        StudentAnalyticsEngine.evaluate_and_save_snapshot(student_profile)

        login(request, user)
        messages.success(request, f"Account successfully created! Welcome to Smart Campus Analytics, {user.username}.")
        return redirect('accounts:dashboard_redirect')

class DashboardRedirectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_student_user():
            if hasattr(user, 'student_profile'):
                messages.info(request, f"Welcome Student, {user.first_name or user.username}!")
                return redirect('analytics:student_detail', student_id=user.student_profile.student_id)
            return redirect('accounts:profile')
        else:
            messages.info(request, f"Welcome {user.get_role_display()}, {user.username}!")
            return redirect('analytics:overview_dashboard')

class AdminDashboardStubView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboards/admin_dashboard.html'

class FacultyDashboardStubView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboards/faculty_dashboard.html'

class PlacementDashboardStubView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboards/placement_dashboard.html'

class StudentDashboardStubView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboards/student_dashboard.html'

class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

def custom_403_view(request, exception=None):
    return render(request, '403.html', status=403)

def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)
