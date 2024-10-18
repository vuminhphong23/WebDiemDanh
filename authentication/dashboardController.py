import datetime
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
import pandas as pd
from sympy import Max
from .models import Attendance, TblStudents, Classroom, AttendanceSession
from .models import TblStudents
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q,Count
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.contrib.auth.models import User
from urllib.parse import unquote
from django.http import JsonResponse
import os
import tempfile
from firebase_admin import storage


from django.shortcuts import render, redirect
from .models import TblStudents, Classroom, User, AttendanceSession

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

        print(f'Total students: {total_students}, Total classes: {total_class}, Total teachers: {total_teachers}')

        # Lấy danh sách các lớp giáo viên đang dạy
        teacher_classes = Classroom.objects.filter(teacher=user)
        print(f'Teacher {user.username} is teaching {teacher_classes.count()} classes.')

        # Tạo dictionary để lưu dữ liệu absent_data cho từng lớp
        class_absent_data = {}

        for classroom in teacher_classes:
            total_sessions = AttendanceSession.objects.filter(classroom=classroom).count()
            attended_sessions = AttendanceSession.objects.filter(
                classroom=classroom,
                attendances__attended=True
            ).distinct().count()

            classroom.total_sessions = total_sessions
            classroom.attended_sessions = attended_sessions

            absent_data = []
            if total_sessions > 0:  
                # Lấy danh sách sinh viên theo từng lớp
                students = classroom.students.annotate(
                    attended_count=Count('attendances', filter=Q(attendances__attended=True, attendances__session__classroom=classroom)),
                )

                for student in students:
                    absent_rate = (attended_sessions - student.attended_count) / total_sessions
                    absent_data.append({
                        'student_name': student.name,
                        'absent_rate': round(absent_rate * 100, 2),
                    })

                    print(f"Student {student.name} attended {student.attended_count} out of {total_sessions} sessions in classroom {classroom.class_name}. Absent rate: {absent_rate * 100:.2f}%")

            # Gắn dữ liệu vắng mặt vào dictionary theo từng lớp
            class_absent_data[classroom.class_id] = absent_data

        print(f'Class absent data: {class_absent_data}')

        return render(request, 'admin/index.php', {
            'total_students': total_students,
            'total_class': total_class,
            'total_teachers': total_teachers,
            'teacher_classes': teacher_classes,
            'class_absent_data': class_absent_data,  # Dữ liệu vắng mặt cho các lớp
        })

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
    
    # Adding attendance data
    session_data = []
    total_students = classroom.students.count()
    
    for session in sessions:
        attended_count = Attendance.objects.filter(session=session, attended=1).count()
        attendance_percentage = (attended_count / total_students) * 100 if total_students > 0 else 0
        session_data.append((session, attended_count, total_students, attendance_percentage))
    
    return render(request, 'attendance/attendance_detail.html', {
        'classroom': classroom,
        'sessions': session_data,  # Pass session data with attendance count and percentage
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

@login_required
def manual_attendance(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        session_id = request.POST.get('session_id')
        student = get_object_or_404(TblStudents, student_id=student_id)
        session = get_object_or_404(AttendanceSession, session_id=session_id)
        
        now = datetime.datetime.now()
        attendance, created = Attendance.objects.get_or_create(
            student=student,
            session=session,
            defaults={'attended': True, 'date': now.date(), 'time': now.time()}
        )
        
        if not created:
            attendance.attended = True
            attendance.date = now.date()
            attendance.time = now.time()
            attendance.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return redirect('home')

@login_required
def delete_attendance(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        session_id = request.POST.get('session_id')
        student = get_object_or_404(TblStudents, student_id=student_id)
        session = get_object_or_404(AttendanceSession, session_id=session_id)
        
        attendance = Attendance.objects.filter(student=student, session=session).first()
        if attendance:
            attendance.delete()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return redirect('home')

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

# Hàm gọi ảnh từ Firebase Storage
def load_image(image_path):
    try:
        bucket = storage.bucket()
        blob = bucket.blob(image_path)
        filename = image_path.split('/')[-1]
        temp_image_path = os.path.join(tempfile.gettempdir(), filename)
        blob.download_to_filename(temp_image_path)
        #print(f"Đã tải thành công ảnh xuống {temp_image_path}")
        return temp_image_path
    except FileNotFoundError:
        print(f"Không tìm thấy file: {image_path}")

# Hàm xử lý logic lấy ảnh và trả về JsonResponse
def session_attendance(class_name, time, date, student_id, student_name):
    formatted_date = process_date(date)
    image_path = f'result-attendance/{class_name}_{time}_{formatted_date}_{student_id}_{student_name}.jpg'
    #print(f"Đang kiểm tra đường dẫn ảnh: {image_path}")
    
    temp_image_path = load_image(image_path)
    
    if temp_image_path:
        # Tạo URL tạm thời để truy cập ảnh từ Firebase
        bucket = storage.bucket()
        blob = bucket.blob(image_path)
        image_url = blob.generate_signed_url(expiration=datetime.timedelta(minutes=15))
        return JsonResponse({'image_url': image_url})
    else:
        return JsonResponse({'error': 'Không tìm thấy ảnh'}, status=404)

#Xử lý dữ liệu ngày khi trả về
def process_date(encoded_date):
    try:
        # Giải mã chuỗi URL
        decoded_date = unquote(encoded_date)
        # Chuyển đổi định dạng từ dd/mm/yyyy sang datetime
        date_obj = datetime.datetime.strptime(decoded_date, '%d/%m/%Y')
        # Định dạng lại thành yyyyMMdd
        formatted_date = date_obj.strftime('%Y%m%d')
        return formatted_date
    except ValueError as e:
        #print(f"Error processing date: {e}")
        return None  # Hoặc trả về một giá trị mặc định khác

# Hàm xử lý logic lấy ảnh dựa trên student_id, student_name và date
def student_attendance_detail(request):
    student_id = request.GET.get('student_id')
    student_name = request.GET.get('student_name')
    date = request.GET.get('date')
    time= request.GET.get('time')
    class_name = request.GET.get('class_name')

    # print(f"Received student_id: {student_id}, student_name: {student_name}, date: {date}")

    if not student_id or not student_name or not date:
        return JsonResponse({'error': 'Thiếu thông tin student_id, student_name hoặc date'}, status=400)

    # Tiến hành kiểm tra ảnh
    response = session_attendance(class_name, time, date, student_id, student_name)
    return response