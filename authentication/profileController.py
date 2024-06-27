from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse

from authentication.capPictureController import capture_images
from .models import TblStudents
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

@csrf_exempt
def view(request):
    student_id = request.session.get('student_id')
    student_name = request.session.get('student_name')

    if not student_id:
        return redirect('home')

    student = TblStudents.objects.get(pk=student_id)

    if request.method == 'POST':
        student.name = request.POST.get('name')
        student.email = request.POST.get('email')
        student.phone = request.POST.get('phone')
        student.iCap = request.POST.get('iCap') == 'on'
        date_birth_str = request.POST.get('date_birth')
        # Chuyển đổi date_birth_str thành đối tượng datetime.date
        try:
            student.date_birth = datetime.strptime(date_birth_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            student.date_birth = None
        student.save()
        # Cập nhật context sau khi lưu thông tin
        context = {
            "fname": student_name,
            "student_id": student.student_id,
            "name": student.name,
            "email": student.email,
            "phone": student.phone,
            "iCap": "Đã đăng ký ảnh" if student.iCap else "Chưa đăng ký ảnh",
            "date_birth": student.date_birth.strftime('%Y-%m-%d') if student.date_birth else '',
        }
        return render(request, "student/profile.html", context)

    context = {
        "fname": student_name,
        "student_id": student.student_id,
        "name": student.name,
        "email": student.email,
        "phone": student.phone,
        "iCap": "Đã đăng ký ảnh" if student.iCap else "Chưa đăng ký ảnh",
        "date_birth": student.date_birth.strftime('%Y-%m-%d') if student.date_birth else '',
    }
    return render(request, "student/profile.html", context)




def cappicture(request, student_id, name):
    if request.method == 'POST':
        try:
            # Capture images (assuming you have a function named capture_images)
            capture_images(student_id, name)
            
            # Update the student's iCap status
            student = get_object_or_404(TblStudents, student_id=student_id)
            student.iCap = True
            student.save()
            
            return JsonResponse({'status': 'success', 'message': 'Images captured and uploaded successfully!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})