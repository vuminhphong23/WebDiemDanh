from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth import authenticate, login, logout

from authentication.capPictureController import capture_images
from .tokens import generate_token
import subprocess
from django.shortcuts import render
from django.http import HttpResponse
import cv2
import os
from sklearn.model_selection import train_test_split
from mtcnn.mtcnn import MTCNN
from .models import Classroom, TblStudents
from .x import get_embedding, create_embeddings
from os import listdir
from os.path import isdir
from PIL import Image
from numpy import savez_compressed, asarray
from mtcnn.mtcnn import MTCNN
import base64
import numpy as np
import firebase_admin
from firebase_admin import credentials, storage

def home(request):
    return render(request, "authentication/index.html")

def classroom(request):
    return render(request, "class/classroom_detail.html")

def regisImg(request):
    return render(request, "admin/registerImage.html")


def dashboard(request):
    # Get the total number of students
    total_students = TblStudents.objects.count()
    total_class = Classroom.objects.count()
    return render(request, 'admin/index.php', {'total_students': total_students, 'total_class': total_class})
    # return render(request, "admin/index.php")

def userthem(request):
    return render(request, "admin/nguoidung.php")



def cappicture(request, student_id, name):
    if request.method == 'GET':
        return render(request, 'admin/capture_image.html', {'student_id': student_id, 'name': name})
    elif request.method == 'POST':
        capture_images(student_id, name)
        # Lấy thông tin sinh viên từ cơ sở dữ liệu
        student = TblStudents.objects.get(student_id=student_id)
        # Lấy classroom_id từ thông tin sinh viên
        classroom_id = student.classroom.class_id
        # # Thêm thông báo đăng ký thành công
        # messages.success(request, 'Đăng ký ảnh thành công!')
        # Chuyển hướng đến trang classroom_detail với classroom_id
        return redirect(f'/classroom/{classroom_id}/')



    

    



    


# register logout login
def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        role = request.POST['role']  
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('signup')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('signup')
        
        if len(username) > 20:
            messages.error(request, "Username must be under 20 characters!!")
            return redirect('signup')
        
        if pass1 != pass2:
            messages.error(request, "Passwords didn't match!!")
            return redirect('signup')
        
        if not username.isalnum():
            messages.error(request, "Username must be Alpha-Numeric!!")
            return redirect('signup')
        
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = role  
        myuser.is_active = True  
        myuser.is_staff = True 
        myuser.save()
        messages.success(request, "Your Account has been created successfully!!")
        
        return redirect('signin')
        
    return render(request, "authentication/signup.html")


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request, 'activation_failed.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']
        role = request.POST['is_superuser']

        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            if role == 'teacher':
                login(request, user)
                fname = user.first_name
                messages.success(request, "Logged In Successfully as Teacher!")
                return render(request, "authentication/index.html",{"fname":fname})
            else:
                messages.error(request, "Invalid role for this user!")
                return redirect('signin')
        elif role == 'student':
            try:
                student = TblStudents.objects.get(email=username)
                if student.check_password(pass1):
                    request.session['student_id'] = student.student_id
                    request.session['student_name'] = student.name
                    messages.success(request, "Logged In Successfully as Student!")
                    return render(request, "authentication/index.html", {"fname": student.name, "student_id": student.student_id})
                else:
                    messages.error(request, "Bad Credentials for Student!")
            except TblStudents.DoesNotExist:
                messages.error(request, "Bad Credentials!")
            
            return redirect('signin')
    
    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully!!")
    return redirect('home')

import pandas as pd
from django.http import HttpResponse
from .models import TblStudents, Attendance

def export_to_excel(request):
    students = TblStudents.objects.all()
    attendance = Attendance.objects.all()

    data = []
    for student in students:
        student_attendance = attendance.filter(student=student)
        for att in student_attendance:
            data.append({
                'Mã sinh viên': student.student_id,
                'Họ và tên': student.name,
                'Email': student.email,
                'Số điện thoại': student.phone,
                'Ngày sinh': student.date_birth.strftime("%d-%m-%Y"),
                'Ngày điểm danh': att.datetime.strftime("%d-%m-%Y"),
                'Thời gian': att.datetime.strftime("%H:%M:%S"),
                'Điểm danh': 'Có mặt' if att.attended else 'Đã điểm danh',
            })

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=attendance.xlsx'
    df.to_excel(response, index=False)
    return response


