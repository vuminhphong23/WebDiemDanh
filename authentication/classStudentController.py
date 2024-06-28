# classStudentController.py
from django.shortcuts import redirect, render, get_object_or_404
from .models import Classroom, TblStudents

def view(request):
    student_id = request.session.get('student_id')  # Assuming the student ID is stored in the session
    if student_id:
        student = get_object_or_404(TblStudents, student_id=student_id)
        classrooms = student.classrooms.all()  # Fetch all classrooms the student is registered in
        return render(request, "student/class_students.html", {'classrooms': classrooms})
    else:
        return redirect('home')

def viewdetail(request, class_id):
    student_id = request.session.get('student_id')  # Assuming the student ID is stored in the session
    if student_id:
        classroom = get_object_or_404(Classroom, pk=class_id)
        students = classroom.students.all()
        context = {
            'classroom': classroom,
            'students': students
        }
        return render(request, 'student/class_detail.html', context)
    else:
        return redirect('home')