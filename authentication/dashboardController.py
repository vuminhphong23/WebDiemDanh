from django.http import HttpResponse
from django.shortcuts import render, redirect
import pandas as pd
from sympy import Max
from .models import Attendance, TblStudents, Classroom, AttendanceSession
from .models import TblStudents
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.contrib.auth.models import User


def dashboard(request):
    student_id = request.session.get('student_id')
    student_name = request.session.get('student_name')
    if student_id and student_name:
        return redirect('home')
    
    user = request.user
    if user.is_authenticated:  
        total_students = TblStudents.objects.count()
        total_class = Classroom.objects.count()
        total_teachers = User.objects.filter(is_superuser=False).count()
        return render(request, 'admin/index.php', {'total_students': total_students, 'total_class': total_class, 'total_teachers': total_teachers})
    
    return redirect('home')

@login_required
def classroom_list(request):
    user = request.user
    classrooms = Classroom.objects.filter(teacher=user)
    return render(request, 'class/classroom_list.html', {'classrooms': classrooms})



def classroom_detail(request, classroom_id):
    # Check if user is logged in as a student
    student_id = request.session.get('student_id')
    student_name = request.session.get('student_name')
    if student_id and student_name:
        return redirect('home')  # Redirect to home if logged in as student
    
    # Fetch classroom details
    classroom = get_object_or_404(Classroom, class_id=classroom_id)
    
    # Filter students belonging to the selected classroom
    students = TblStudents.objects.filter(classrooms=classroom)

    # Handling search
    search_query = request.GET.get('q', '')
    if search_query:
        students = students.filter(name__icontains=search_query)

    total_students = students.count()

    return render(request, 'class/classroom_detail.html', {
        'classroom': classroom,
        'students': students,
        'total_students': total_students,
        'search_query': search_query  # Pass search_query to template to maintain state
    })


def classroom_list_attendance(request):
    user = request.user
    classrooms = Classroom.objects.filter(teacher=user)
    return render(request, 'attendance/classroom_list.html', {'classrooms': classrooms})



def classroom_attendance_detail(request, class_id):
    classroom = get_object_or_404(Classroom, pk=class_id)
    date_filter = request.GET.get('date')
    if date_filter:
        sessions = classroom.attendance_sessions.filter(date=parse_date(date_filter))
    else:
        sessions = classroom.attendance_sessions.all()
    return render(request, 'attendance/attendance_detail.html', {
        'classroom': classroom,
        'sessions': sessions,
        'date_filter': date_filter,
    })

def session_attendance_detail(request, session_id):
    session = get_object_or_404(AttendanceSession, pk=session_id)
    classroom = session.classroom
    students = classroom.students.all()

    # Create a dictionary to store attendance records keyed by student id
    attendance_dict = {attendance.student_id: attendance for attendance in session.attendances.all()}

    attendance_details = []
    for student in students:
        attendance = attendance_dict.get(student.student_id)
        if attendance:
            attendance_details.append(attendance)
        else:
            # If the student has no attendance record, create a dummy one with attended=False
            attendance_details.append(Attendance(student=student, session=session, attended=False))
    
    return render(request, 'attendance/session_detail.html', {
        'session': session,
        'attendance_details': attendance_details
    })


# chưa dung
def export_to_excel(request, session_id):
    session = get_object_or_404(AttendanceSession, session_id=session_id)
    classroom = session.classroom
    all_students = TblStudents.objects.filter(classrooms=classroom)

    data = []
    for student in all_students:
        attendance = Attendance.objects.filter(session=session, student=student).first()
        if attendance:
            attendance_status = 'Có mặt' if attendance.attended else 'Vắng'
            data.append({
                'MSSV': student.student_id,
                'Họ và tên': student.name,
                'Email': student.email,
                'Điểm danh': attendance_status,
                'Ngày': attendance.date,
                'Giờ': attendance.time,
            })
        else:
            data.append({
                'MSSV': student.student_id,
                'Họ và tên': student.name,
                'Email': student.email,
                'Điểm danh': 'Vắng',
                'Ngày': '',
                'Giờ': '',
            })

    df = pd.DataFrame(data)

    # Create an HttpResponse object with Excel file content
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename={classroom.class_name}_{session.date}_{session.start_time}_{session.end_time}.xlsx'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')

    return response