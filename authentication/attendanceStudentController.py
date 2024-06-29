from django.shortcuts import redirect, render, get_object_or_404
from .models import Attendance, AttendanceSession, Classroom, TblStudents
from django.db.models import OuterRef, Subquery, Max
from django.utils.dateparse import parse_date

def view(request):
    student_id = request.session.get('student_id')  # Assuming the student ID is stored in the session
    if student_id:
        student = get_object_or_404(TblStudents, student_id=student_id)
        classrooms = student.classrooms.all()  # Fetch all classrooms the student is registered in
        return render(request, "student/attendance_students.html", {'classrooms': classrooms})
    else:  
        return redirect('home')
    
# def viewdetail(request, classroom_id):
#     classroom = get_object_or_404(Classroom, pk=classroom_id)

#     students = classroom.students.all()  # Get all students in the classroom

#     latest_attendance_subquery = Attendance.objects.filter(
#         student=OuterRef('pk'),
#         session__classroom=classroom  # Filter by classroom
#     ).order_by('-date').values('date')[:1]

#     students_with_latest_attendance = students.annotate(
#         latest_attendance_datetime=Subquery(latest_attendance_subquery)
#     )

#     latest_attendance_list = []

#     for student in students_with_latest_attendance:
#         if student.latest_attendance_datetime:
#             latest_attendance = Attendance.objects.filter(
#                 student=student,
#                 session__classroom=classroom,
#                 date=student.latest_attendance_datetime
#             ).first()
#             if latest_attendance:
#                 latest_attendance_list.append(latest_attendance)

#     return render(request, 'student/attendance_detail.html', {'classroom': classroom, 'students': students, 'attendance': latest_attendance_list})

def viewdetail(request, class_id):
    student_id = request.session.get('student_id')  # Assuming the student ID is stored in the session
    if student_id:
        classroom = get_object_or_404(Classroom, pk=class_id)
        date_filter = request.GET.get('date')
        if date_filter:
            sessions = classroom.attendance_sessions.filter(date=parse_date(date_filter))
        else:
            sessions = classroom.attendance_sessions.all()
        return render(request, 'student/attendance_detail.html', {
            'classroom': classroom,
            'sessions': sessions,
            'date_filter': date_filter,
        })
    else:  
        return redirect('home')

def session_attendance(request, session_id):
    student_id = request.session.get('student_id')  # Assuming the student ID is stored in the session
    if student_id:
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
        
        return render(request, 'student/session_detail.html', {
            'session': session,
            'attendance_details': attendance_details
        })
    else:  
        return redirect('home')