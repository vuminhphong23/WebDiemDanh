from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth import authenticate, login, logout
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

def bost(request):
    return render(request, "admin/index.php")

def bost2(request):
    # Get the total number of students
    total_students = TblStudents.objects.count()
    total_class = Classroom.objects.count()
    return render(request, 'admin/index.php', {'total_students': total_students, 'total_class': total_class})
    # return render(request, "admin/index.php")

def userthem(request):
    return render(request, "admin/nguoidung.php")

# Function to enhance image by applying denoising and smoothing
def enhance_image(image):
    # Làm sạch nhiễu bằng Gaussian Blur
    blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
    
    # Tăng cường độ sáng và độ tương phản
    enhanced_image = cv2.convertScaleAbs(blurred_image, alpha=1.2, beta=10)
    
    return enhanced_image

# Function to flip and rotate images to increase dataset size
def augment_images(images):
    augmented_images = []
    for image in images:
        
        # Flip image vertically
        flipped_vertical = cv2.flip(image, 1)
        augmented_images.append(flipped_vertical)
        
        # Rotate image by 15 degrees clockwise
        rows, cols, _ = image.shape
        rotation_matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), 15, 1)
        rotated_image = cv2.warpAffine(image, rotation_matrix, (cols, rows))
        augmented_images.append(rotated_image)
        
        # Rotate image by -15 degrees counterclockwise
        rotation_matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), -15, 1)
        rotated_image = cv2.warpAffine(image, rotation_matrix, (cols, rows))
        augmented_images.append(rotated_image)
    return augmented_images


def upload_to_firebase(image, folder, image_name):
    bucket = storage.bucket()
    blob = bucket.blob(f'{folder}/{image_name}')
    _, img_encoded = cv2.imencode('.jpg', image)
    blob.upload_from_string(img_encoded.tobytes(), content_type='image/jpeg')
    print(f'Uploaded {image_name} to {folder}.')

def capture_images(student_id, name):
    cap = cv2.VideoCapture(0)
    detector = MTCNN()
    img_count = 0
    captured_images = []

    print("Press 'c' to capture image. Press 'q' to quit.")
    while img_count < 10:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        cv2.imshow('Capturing Images', frame)
        
        key = cv2.waitKey(1)
        if key & 0xFF == ord('c'):
            results = detector.detect_faces(frame)
            if results:
                x1, y1, width, height = results[0]['box']
                x1, y1 = abs(x1), abs(y1)
                x2, y2 = x1 + width, y1 + height
                face = frame[y1:y2, x1:x2]
                face = cv2.resize(face, (160, 160))
                face = enhance_image(face)
                captured_images.append(face)
                img_count += 1
                print(f"Captured image {img_count}")
        elif key & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    
    augmented_images = augment_images(captured_images)
    train_images, val_images = train_test_split(augmented_images, test_size=0.33, random_state=42)
    
    for i, img in enumerate(train_images):
        upload_to_firebase(img, f'train/{student_id}_{name}', f'{student_id}_{name}_{i+1}.jpg')
    for i, img in enumerate(val_images):
        upload_to_firebase(img, f'val/{student_id}_{name}', f'{student_id}_{name}_{i+1}.jpg')

def aa(request, student_id, name):
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
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            messages.success(request, "Logged In Sucessfully!!")
            # return render(request, "authentication/index.html",{"fname":fname})
            return render(request, "authentication/index.html",{"fname":fname})
        else:
            messages.error(request, "Bad Credentials!!")
            return redirect('home')
    
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


