from django.http import HttpResponse
from django.shortcuts import render, redirect
from sympy import Max
from .models import Attendance, TblStudents, Classroom, AttendanceSession
from django.http import JsonResponse
from .models import TblStudents
from django.db.models import Count
from .forms import TblStudentsForm
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date


def classroom_student_list(request, class_id):
    classroom = get_object_or_404(Classroom, class_id=class_id)
    search_query = request.GET.get('q', '')

    if search_query:
        students = TblStudents.objects.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(student_id__icontains=search_query)
        ).filter(classroom=classroom)
    else:
        students = TblStudents.objects.filter(classroom=classroom)
    
    total_students = students.count()

    return render(request, "class/classroom_detail.html", {
        'classroom': classroom,
        'students': students,
        'search_query': search_query,
        'total_students': total_students,
        'class_id': class_id
    })


def data(request):
    # Chuyển đổi QuerySet thành danh sách các từ điển để dễ đọc
    t3 = list(TblStudents.objects.values())

    # Lọc các bản ghi có name bắt đầu bằng "Beatles"
    t4 = list(TblStudents.objects.filter(name__startswith="Beatles").values())

    # Tìm kiếm chính xác
    t5 = list(TblStudents.objects.filter(name="Phong Vu").values())

    # Tìm kiếm một phần
    t6 = list(TblStudents.objects.filter(name__contains="N").values())


    data = {
        "all_students": t3,
        "starts_with_beatles": t4,
        "exact_name_phong_vu": t5,
        "contains_n": t6,
    }
    return JsonResponse(data)

@login_required
def classroom_list(request):
    user = request.user
    classrooms = Classroom.objects.filter(teacher=user)
    return render(request, 'class/classroom_list.html', {'classrooms': classrooms})

def classroom_list_attendance(request):
    user = request.user
    classrooms = Classroom.objects.filter(teacher=user)
    return render(request, 'attendance/classroom_list.html', {'classrooms': classrooms})

def classroom_detail(request, class_id):
    student_id = request.session.get('student_id')
    student_name = request.session.get('student_name')
    if student_id and student_name:
        return redirect('home')
    classroom = get_object_or_404(Classroom, pk=class_id)
    students = classroom.students.all()
    return render(request, 'class/classroom_detail.html', {'classroom': classroom, 'students': students})

def edit_student(request, student_id):
    student = get_object_or_404(TblStudents, pk=student_id)
    if request.method == 'POST':
        form = TblStudentsForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('classroom_detail', class_id=student.classroom.class_id)
    else:
        form = TblStudentsForm(instance=student)
    return render(request, 'class/edit_student.html', {'form': form, 'student': student})


def add_student(request, class_id):
    classroom = get_object_or_404(Classroom, pk=class_id)
    if request.method == 'POST':
        form = TblStudentsForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.classroom = classroom
            student.save()
            return redirect('classroom_detail', class_id=class_id)  # Corrected redirect URL name
    else:
        form = TblStudentsForm(initial={'classroom': classroom})
    return render(request, 'class/add_student.html', {'form': form, 'classroom': classroom})

def delete_student(request, student_id):
    student = get_object_or_404(TblStudents, student_id=student_id)
    if request.method == 'POST':
        student.delete()
        # Fetch the updated list of students
        students = TblStudents.objects.all()
        students_data = list(students.values('student_id', 'name', 'email', 'phone', 'date_birth'))
        return JsonResponse({'status': 'success', 'message': 'Student deleted successfully.', 'students': students_data})
    return render(request, 'class/delete_student.html', {'student': student})

def classroom_student_list(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)
    students = TblStudents.objects.filter(classroom=classroom)
    total_students = students.count()

    return render(request, 'class/classroom_detail.html', {
        'classroom': classroom,
        'students': students,
        'total_students': total_students
    })



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
