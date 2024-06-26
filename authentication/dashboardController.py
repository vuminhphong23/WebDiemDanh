from django.http import HttpResponse
from django.shortcuts import render, redirect
from sympy import Max
from .models import Attendance, TblStudents, Classroom
from django.http import JsonResponse
from .models import TblStudents
from django.db.models import Count
from .forms import TblStudentsForm
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required

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
    classrooms = Classroom.objects.all()
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

from django.shortcuts import render
from django.db.models import OuterRef, Subquery, Max

def student_list(request):
    # Lấy tất cả sinh viên
    students = TblStudents.objects.all()

    # Tạo subquery để lấy datetime mới nhất cho mỗi sinh viên
    latest_attendance_subquery = Attendance.objects.filter(
        student=OuterRef('pk')
    ).order_by('-datetime').values('datetime')[:1]

    # Annotate mỗi sinh viên với datetime điểm danh mới nhất
    students_with_latest_attendance = students.annotate(
        latest_attendance_datetime=Subquery(latest_attendance_subquery)
    )

    # Tạo danh sách để lưu các bản ghi điểm danh mới nhất
    latest_attendance_list = []

    # Lấy bản ghi điểm danh mới nhất cho mỗi sinh viên
    for student in students_with_latest_attendance:
        if student.latest_attendance_datetime:
            latest_attendance = Attendance.objects.filter(
                student=student,
                datetime=student.latest_attendance_datetime
            ).first()
            if latest_attendance:
                latest_attendance_list.append(latest_attendance)

    return render(request, 'attendance/attendance.html', {'students': students, 'attendance': latest_attendance_list})
