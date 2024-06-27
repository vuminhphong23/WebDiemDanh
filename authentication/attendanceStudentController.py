from django.shortcuts import render, get_object_or_404
from .models import Attendance, Classroom, TblStudents
from django.db.models import OuterRef, Subquery, Max

def view(request):
    student_id = request.session.get('student_id')  # Assuming the student ID is stored in the session
    if student_id:
        student = get_object_or_404(TblStudents, student_id=student_id)
        classrooms = student.classrooms.all()  # Fetch all classrooms the student is registered in
        return render(request, "student/attendance_students.html", {'classrooms': classrooms})
    else:  
        return render(request, "student/attendance_students.html", {'classrooms': []})
    
def viewdetail(request, classroom_id):
    classroom = get_object_or_404(Classroom, pk=classroom_id)

    students = classroom.students.all()  # Get all students in the classroom

    latest_attendance_subquery = Attendance.objects.filter(
        student=OuterRef('pk'),
        session__classroom=classroom  # Filter by classroom
    ).order_by('-datetime').values('datetime')[:1]

    students_with_latest_attendance = students.annotate(
        latest_attendance_datetime=Subquery(latest_attendance_subquery)
    )

    latest_attendance_list = []

    for student in students_with_latest_attendance:
        if student.latest_attendance_datetime:
            latest_attendance = Attendance.objects.filter(
                student=student,
                session__classroom=classroom,
                datetime=student.latest_attendance_datetime
            ).first()
            if latest_attendance:
                latest_attendance_list.append(latest_attendance)

    return render(request, 'student/attendance_detail.html', {'classroom': classroom, 'students': students, 'attendance': latest_attendance_list})