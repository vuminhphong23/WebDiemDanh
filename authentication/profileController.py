from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.hashers import make_password
from authentication.capPictureController import capture_images
from .models import TblStudents
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.contrib.auth import update_session_auth_hash
from django.utils.dateparse import parse_date
@csrf_exempt
def profile(request):
    student_id = request.session.get('student_id')
    if student_id:
        student = get_object_or_404(TblStudents, student_id=student_id)
        context = {
            'student_id': student.student_id,
            'name': student.name,
            'email': student.email,
            'phone': student.phone,
            'date_birth': student.date_birth,
            'edit_mode': False,  # Disable editing initially
            'pw_edit_mode': False,  # Disable password editing initially
            'iCap':student.iCap,
        }
        return render(request, 'student/profile.html', context)
    return redirect('home')

@csrf_exempt
def update_profile(request):
    student_id = request.session.get('student_id')
    if student_id:
        if request.method == 'POST':
            student_id = request.POST.get('student_id')
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            date_birth_str = request.POST.get('date_birth')
            
            # Parse date of birth string to datetime.date object
            date_birth = parse_date(date_birth_str)
            
            try:
                student = TblStudents.objects.get(student_id=student_id)
                student.name = name
                student.email = email
                student.phone = phone
                student.date_birth = date_birth  # Assign parsed date of birth
                student.save()
                
                return JsonResponse({'status': 'success', 'message': 'Thông tin đã được cập nhật thành công!'})
            except TblStudents.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Sinh viên không tồn tại.'})
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
    return redirect('home')

@csrf_exempt
def change_password(request):
    student_id = request.session.get('student_id')
    if student_id:
        if request.method == 'POST':
            password = request.POST.get('password')
            password_confirm = request.POST.get('password_confirm')
            
            if password == password_confirm:
                try:
                    student = TblStudents.objects.get(student_id=student_id)
                    student.set_password(password)
                    student.save()
                    
                    return JsonResponse({'status': 'success', 'message': 'Mật khẩu đã được thay đổi thành công!'})
                except TblStudents.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Sinh viên không tồn tại.'})
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': f'Lỗi: {str(e)}'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Mật khẩu xác nhận không khớp.'})
        
        return JsonResponse({'status': 'error', 'message': 'Phương thức yêu cầu không hợp lệ.'})
    return redirect('home')


@csrf_exempt
def cappicture(request, student_id, name):
    if request.session.get('student_id'):
        if request.method == 'POST':
            try:
                # Capture images (assuming you have a function named capture_images)
                capture_images(student_id, name)
                
                # Update the student's iCap status
                student = get_object_or_404(TblStudents, student_id=student_id)
                student.iCap = True
                student.save()
                
                return JsonResponse({'status': 'success', 'message': 'Hình ảnh đã được chụp thành công !'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        return JsonResponse({'status': 'error', 'message': 'Đã có lỗi xảy ra, hãy chụp lại !'})
    return redirect('home')