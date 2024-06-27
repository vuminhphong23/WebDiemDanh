from django.contrib import admin
from django.urls import path

from authentication import attendanceStudentController, classStudentController, profileController
from . import views
from . import dashboardController
from . import camera
from . import capPictureController
from . import train

urlpatterns = [
    path('', views.home, name='home'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    
    path('embeddings', train.embeddings, name='embeddings'), 

    path('dashboard', dashboardController.dashboard, name='dashboard'),
    path('classroom/<int:classroom_id>/', dashboardController.classroom_detail, name='classroom_detail'),
    path('classroom_list', dashboardController.classroom_list, name='classroom_list'),

    path('classroom_list_attendance', dashboardController.classroom_list_attendance, name='classroom_list_attendance'),
    path('classroom/<int:class_id>/attendance/', dashboardController.classroom_attendance_detail, name='classroom_attendance_detail'),
    path('session/<int:session_id>/attendance/', dashboardController.session_attendance_detail, name='session_attendance_detail'),
    path('diemdanh/<int:classroom_id>/<int:session_id>/', camera.diemdanh, name='diemdanh'),
    
    # path('export-to-excel/', dashboardController.export_to_excel, name='export_to_excel'),
    
    path('profile', profileController.view, name='profile'),
    path('cappicture/<str:student_id>/<str:name>/', profileController.cappicture, name='cappicture'),
    path('class_students', classStudentController.view, name='class_students'),
    path('class_detail/<int:class_id>/', classStudentController.viewdetail, name='class_detail'),
    path('attendance_students', attendanceStudentController.view, name='attendance_students'),
    path('attendance_detail/<int:classroom_id>/', attendanceStudentController.viewdetail, name='attendance_detail'),
]

