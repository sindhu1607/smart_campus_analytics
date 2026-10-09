import os
import random
import numpy as np
import pandas as pd
from django.utils import timezone
from datetime import date, timedelta
from django.db import transaction
from django.contrib.auth import get_user_model

from apps.students.models import Department, Program, AcademicYear, Semester, StudentProfile, FacultyAssignment
from apps.academics.models import Subject, SemesterResult, AssessmentResult
from apps.attendance.models import AttendanceRecord
from apps.lms.models import LMSActivitySummary
from apps.engagement.models import ActivityCategory, EngagementActivity, StudentEngagement
from apps.placements.models import PlacementAssessment, PlacementApplication
from apps.skills.models import Skill, StudentSkillAssessment
from apps.feedback.models import FeedbackCategory, StudentFeedback, FacultyFeedback
from apps.analytics.models import StudentSuccessSnapshot
from apps.interventions.models import InterventionRecord

User = get_user_model()

class DataImportService:
    """Service to import and validate student datasets from CSV or Excel files."""

    @staticmethod
    def import_from_file(file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Please provide a CSV or Excel file.")

        imported_count = 0
        errors = []

        # Ensure baseline department and program exist
        dept, _ = Department.objects.get_or_create(code='GENERAL', defaults={'name': 'General Engineering'})
        prog, _ = Program.objects.get_or_create(code='GEN-BTECH', defaults={'name': 'B.Tech General', 'department': dept})
        acad_yr, _ = AcademicYear.objects.get_or_create(year_label='2025-2026', defaults={'is_current': True})
        sem, _ = Semester.objects.get_or_create(number=1, academic_year=acad_yr)

        with transaction.atomic():
            for idx, row in df.iterrows():
                row_num = idx + 2  # Excel/CSV 1-indexed header offset
                student_id = str(row.get('student_id', '')).strip()
                name = str(row.get('name', '')).strip()

                if not student_id or student_id.lower() == 'nan':
                    errors.append(f"Row {row_num}: Missing student_id")
                    continue

                first_name = name.split()[0] if name and name != 'nan' else 'Student'
                last_name = ' '.join(name.split()[1:]) if len(name.split()) > 1 else str(student_id)
                email = str(row.get('email', f"{student_id.lower()}@campus.edu")).strip()

                # Get department if specified in row
                dept_code = str(row.get('department', 'GENERAL')).strip().upper()
                row_dept, _ = Department.objects.get_or_create(code=dept_code, defaults={'name': f"Department of {dept_code}"})
                row_prog, _ = Program.objects.get_or_create(code=f"{dept_code}-BTECH", defaults={'name': f"B.Tech in {dept_code}", 'department': row_dept})

                # Validate numeric ranges
                try:
                    cgpa = float(row.get('cgpa', 7.0))
                    if not (0.0 <= cgpa <= 10.0):
                        errors.append(f"Row {row_num}: Invalid CGPA {cgpa}. Must be between 0.0 and 10.0.")
                        continue
                except ValueError:
                    errors.append(f"Row {row_num}: Non-numeric CGPA.")
                    continue

                try:
                    attendance_pct = float(row.get('attendance_percentage', 80.0))
                    if not (0.0 <= attendance_pct <= 100.0):
                        errors.append(f"Row {row_num}: Invalid attendance percentage {attendance_pct}.")
                        continue
                except ValueError:
                    errors.append(f"Row {row_num}: Non-numeric attendance percentage.")
                    continue

                # Create or update student profile
                student, created = StudentProfile.objects.update_or_create(
                    student_id=student_id,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'department': row_dept,
                        'program': row_prog,
                        'current_semester': int(row.get('semester', 1)),
                        'admission_year': 2024,
                    }
                )

                # Semester Result
                SemesterResult.objects.update_or_create(
                    student=student,
                    semester=sem,
                    defaults={
                        'sgpa': cgpa,
                        'cgpa': cgpa,
                        'backlog_count': int(row.get('backlog_count', 0))
                    }
                )

                # Attendance Record
                AttendanceRecord.objects.update_or_create(
                    student=student,
                    semester=sem,
                    subject=None,
                    defaults={
                        'total_classes': 100,
                        'classes_attended': int(attendance_pct)
                    }
                )

                # LMS Summary
                LMSActivitySummary.objects.update_or_create(
                    student=student,
                    defaults={
                        'login_frequency': int(row.get('lms_login_frequency', 15)),
                        'assignment_completion_pct': float(row.get('assignment_completion_percentage', 85.0)),
                        'last_activity_date': timezone.now()
                    }
                )

                # Placement Assessment
                PlacementAssessment.objects.update_or_create(
                    student=student,
                    defaults={
                        'aptitude_score': float(row.get('aptitude_score', 65.0)),
                        'coding_score': float(row.get('coding_score', 60.0)),
                        'mock_interview_score': float(row.get('mock_interview_score', 70.0))
                    }
                )

                imported_count += 1

        return {'imported_count': imported_count, 'errors': errors}

class SyntheticDataGeneratorService:
    """Generates realistic demonstration data for Smart Campus Analytics."""

    @staticmethod
    def generate_all(student_count=40, seed=42):
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        with transaction.atomic():
            # 1. Departments & Programs
            departments_data = [
                ('CSE', 'Computer Science & Engineering', 'Dr. Alan Turing'),
                ('ECE', 'Electronics & Communication', 'Dr. Claude Shannon'),
                ('EEE', 'Electrical & Electronics', 'Dr. Nikola Tesla'),
                ('MECH', 'Mechanical Engineering', 'Dr. James Watt')
            ]
            departments = []
            for code, name, hod in departments_data:
                dept, _ = Department.objects.get_or_create(code=code, defaults={'name': name, 'head_of_department': hod})
                departments.append(dept)
                Program.objects.get_or_create(code=f"BTECH-{code}", defaults={'name': f"B.Tech in {name}", 'department': dept})

            # 2. Academic Year & Semesters
            acad_year, _ = AcademicYear.objects.get_or_create(year_label="2025-2026", defaults={'is_current': True})
            semesters = []
            for num in range(1, 9):
                s, _ = Semester.objects.get_or_create(number=num, academic_year=acad_year, defaults={'is_active': (num == 5)})
                semesters.append(s)
            current_sem = semesters[4]  # Sem 5

            # 3. Create Demo Users & Roles
            admin_user, _ = User.objects.get_or_create(
                username='admin',
                defaults={'email': 'admin@smartcampus.edu', 'role': User.Role.ADMINISTRATOR, 'is_staff': True, 'is_superuser': True}
            )
            admin_user.set_password('Admin@1234')
            admin_user.save()

            faculty_user, _ = User.objects.get_or_create(
                username='faculty_cse',
                defaults={'email': 'faculty@smartcampus.edu', 'role': User.Role.FACULTY, 'department_name': 'CSE', 'is_staff': True}
            )
            faculty_user.set_password('Faculty@1234')
            faculty_user.save()
            FacultyAssignment.objects.get_or_create(faculty_user=faculty_user, department=departments[0])

            placement_user, _ = User.objects.get_or_create(
                username='placement_officer',
                defaults={'email': 'placement@smartcampus.edu', 'role': User.Role.PLACEMENT_OFFICER, 'is_staff': True}
            )
            placement_user.set_password('Placement@1234')
            placement_user.save()

            # 4. Subjects
            subjects = []
            for dept in departments:
                sub1, _ = Subject.objects.get_or_create(code=f"{dept.code}301", defaults={'name': f"Advanced {dept.name} Concepts", 'department': dept, 'credits': 4})
                sub2, _ = Subject.objects.get_or_create(code=f"{dept.code}302", defaults={'name': f"{dept.name} Lab & Projects", 'department': dept, 'credits': 3})
                subjects.extend([sub1, sub2])

            # 5. Skills & Categories
            tech_skill1, _ = Skill.objects.get_or_create(name="Python & Machine Learning", category=Skill.SkillCategory.TECHNICAL)
            tech_skill2, _ = Skill.objects.get_or_create(name="Data Structures & Algorithms", category=Skill.SkillCategory.TECHNICAL)
            soft_skill, _ = Skill.objects.get_or_create(name="Leadership & Public Speaking", category=Skill.SkillCategory.SOFT_SKILL)

            act_cat, _ = ActivityCategory.objects.get_or_create(name="Hackathon & Innovation")
            act, _ = EngagementActivity.objects.get_or_create(title="Smart Campus AI Hackathon", defaults={'category': act_cat, 'event_date': date.today() - timedelta(days=20), 'organizer': 'AI Club'})

            fb_cat, _ = FeedbackCategory.objects.get_or_create(name="Academic Support & Infrastructure")

            # 6. Generate Synthetic Students across Groups A-F
            first_names = ['Aarav', 'Ananya', 'Rohan', 'Priya', 'Vikram', 'Sneha', 'Aditya', 'Kavya', 'Rahul', 'Divya', 'Siddharth', 'Meera']
            last_names = ['Sharma', 'Verma', 'Patel', 'Rao', 'Nair', 'Singh', 'Gupta', 'Iyer', 'Reddy', 'Joshi']

            created_students = []
            group_cycle = ['GROUP_A', 'GROUP_B', 'GROUP_C', 'GROUP_D', 'GROUP_E', 'GROUP_F']

            for i in range(1, student_count + 1):
                stu_id = f"STU2025{i:03d}"
                fn = random.choice(first_names)
                ln = random.choice(last_names)
                dept = departments[(i - 1) % len(departments)]
                prog = dept.programs.first()
                group = group_cycle[(i - 1) % len(group_cycle)]

                stu_user, _ = User.objects.get_or_create(
                    username=stu_id.lower(),
                    defaults={'email': f"{stu_id.lower()}@smartcampus.edu", 'first_name': fn, 'last_name': ln, 'role': User.Role.STUDENT}
                )
                stu_user.set_password('Student@1234')
                stu_user.save()

                student, _ = StudentProfile.objects.get_or_create(
                    student_id=stu_id,
                    defaults={
                        'user': stu_user,
                        'first_name': fn,
                        'last_name': ln,
                        'email': stu_user.email,
                        'department': dept,
                        'program': prog,
                        'current_semester': 5,
                        'admission_year': 2023,
                    }
                )
                created_students.append(student)

                # Configure metrics by group
                if group == 'GROUP_A':  # Strong Overall
                    cgpa = round(random.uniform(8.6, 9.8), 2)
                    backlogs = 0
                    att_pct = random.randint(88, 98)
                    lms_completion = random.uniform(88.0, 100.0)
                    plac_score = random.uniform(85.0, 95.0)
                elif group == 'GROUP_B':  # Academic & Attendance Risk
                    cgpa = round(random.uniform(4.5, 6.2), 2)
                    backlogs = random.choice([1, 2, 3])
                    att_pct = random.randint(52, 69)
                    lms_completion = random.uniform(40.0, 62.0)
                    plac_score = random.uniform(35.0, 55.0)
                elif group == 'GROUP_C':  # Strong Academics, Low Placement
                    cgpa = round(random.uniform(8.2, 9.5), 2)
                    backlogs = 0
                    att_pct = random.randint(85, 95)
                    lms_completion = random.uniform(80.0, 95.0)
                    plac_score = random.uniform(35.0, 52.0)  # Weak coding/aptitude
                elif group == 'GROUP_D':  # Low LMS Engagement
                    cgpa = round(random.uniform(7.0, 8.2), 2)
                    backlogs = 0
                    att_pct = random.randint(78, 88)
                    lms_completion = random.uniform(30.0, 48.0)
                    plac_score = random.uniform(65.0, 78.0)
                elif group == 'GROUP_E':  # Incomplete / Missing Records
                    cgpa = round(random.uniform(6.8, 8.0), 2)
                    backlogs = 0
                    att_pct = random.randint(75, 85)
                    lms_completion = 70.0
                    plac_score = None  # No placement record
                else:  # GROUP_F: Improving Students
                    cgpa = round(random.uniform(7.2, 8.4), 2)
                    backlogs = 0
                    att_pct = random.randint(82, 92)
                    lms_completion = random.uniform(75.0, 90.0)
                    plac_score = random.uniform(70.0, 85.0)

                SemesterResult.objects.update_or_create(
                    student=student,
                    semester=current_sem,
                    defaults={
                        'sgpa': cgpa,
                        'cgpa': cgpa,
                        'backlog_count': backlogs,
                        'passed': (backlogs == 0)
                    }
                )

                # Subject Assessments
                dept_subjects = Subject.objects.filter(department=dept)
                for sub in dept_subjects:
                    AssessmentResult.objects.update_or_create(
                        student=student,
                        subject=sub,
                        semester=current_sem,
                        assessment_name="Midterm Exam",
                        defaults={
                            'marks_obtained': round((cgpa / 10.0) * 100 * random.uniform(0.9, 1.05), 2),
                            'max_marks': 100.00
                        }
                    )

                # Attendance Record
                AttendanceRecord.objects.update_or_create(
                    student=student,
                    semester=current_sem,
                    subject=None,
                    defaults={
                        'total_classes': 120,
                        'classes_attended': int((att_pct / 100.0) * 120)
                    }
                )

                # LMS Summary
                LMSActivitySummary.objects.update_or_create(
                    student=student,
                    defaults={
                        'login_frequency': int(att_pct / 4),
                        'assignment_completion_pct': lms_completion,
                        'assignment_timeliness_pct': max(0.0, lms_completion - random.uniform(0, 10)),
                        'learning_resource_views': random.randint(20, 150),
                        'quiz_participation_pct': lms_completion,
                        'last_activity_date': timezone.now() - timedelta(days=random.randint(0, 5))
                    }
                )

                # Placement Assessment (if applicable)
                if plac_score is not None:
                    PlacementAssessment.objects.update_or_create(
                        student=student,
                        defaults={
                            'aptitude_score': round(plac_score * random.uniform(0.9, 1.1), 1),
                            'coding_score': round(plac_score * random.uniform(0.85, 1.15), 1),
                            'mock_interview_score': round(plac_score * random.uniform(0.9, 1.0), 1),
                            'resume_readiness_score': round(random.uniform(60, 95), 1),
                            'communication_score': round(random.uniform(65, 90), 1)
                        }
                    )
                    StudentSkillAssessment.objects.update_or_create(
                        student=student, skill=tech_skill1, defaults={'proficiency_score': plac_score}
                    )
                
                StudentSkillAssessment.objects.update_or_create(
                    student=student, skill=soft_skill, defaults={'proficiency_score': random.uniform(60, 90)}
                )

                # Engagement
                StudentEngagement.objects.update_or_create(
                    student=student, activity=act, defaults={'role': 'Participant', 'engagement_score': random.uniform(50, 90)}
                )

                # Feedback
                StudentFeedback.objects.update_or_create(
                    student=student, category=fb_cat, defaults={'satisfaction_score': random.randint(3, 5), 'comments': 'Great learning environment.'}
                )

                # Evaluate Explainable AI Success Snapshot & Risk Level
                from apps.analytics.services import StudentAnalyticsEngine
                StudentAnalyticsEngine.evaluate_and_save_snapshot(student)

            return len(created_students)
