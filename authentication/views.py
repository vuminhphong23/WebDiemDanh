from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import TblStudents
from django.shortcuts import render
from .models import  TblStudents




def home(request):
    student_id = request.session.get('student_id')
    student_name = request.session.get('student_name')
    if student_id and student_name:
        return render(request, "authentication/index.html", {"fname": student_name, "student_id": student_id})
    
    user = request.user
    if user.is_authenticated:  
        return redirect('dashboard')
    else:
        return render(request, "authentication/index.html")


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        pass1 = request.POST.get('pass1')
        role = request.POST.get('is_superuser')

        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            if role == 'teacher':
                login(request, user)
                # messages.success(request, "Logged In Successfully as Teacher!")
                return redirect('dashboard')
            else:
                messages.error(request, "Vai trò không hợp lệ đối với người dùng này")
                return redirect('signin')
        elif role == 'student':
            try:
                student = TblStudents.objects.get(email=username)
                if student.check_password(pass1):
                    request.session['student_id'] = student.student_id
                    request.session['student_name'] = student.name
                    # messages.success(request, "Logged In Successfully as Student!")
                    return redirect('home')
                else:
                    messages.error(request, "Đăng nhập không thành công!")
            except TblStudents.DoesNotExist:
                messages.error(request, "Đăng nhập không thành công!")
            
            return redirect('signin')
    
    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Đăng xuất thành công")
    return redirect('signin')






