from django.contrib import admin
from django.urls import path

from authentication import profileController
from . import views
from . import dashboardController
from . import camera
from . import capPictureController
from . import train

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('nguoidung', views.userthem, name='nguoidung'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('cappicture/<str:student_id>/<str:name>/', views.cappicture, name='cappicture'),
    path('regisImg', views.regisImg, name='regisImg'),
    path('delete_student/<int:student_id>/', dashboardController.delete_student, name='delete_student'),
    path('diemdanh', camera.diemdanh, name='diemdanh'),
    path('classroom_list', dashboardController.classroom_list, name='classroom_list'),
    path('add_student/', dashboardController.add_student, name='add_student'),
    path('classroom/<int:class_id>/', dashboardController.classroom_detail, name='classroom_detail'),
    path('classroom/<int:class_id>/add_student/', dashboardController.add_student, name='add_student'),
    path('student/<int:student_id>/edit/', dashboardController.edit_student, name='edit_student'), 
    path('embeddings', train.embeddings, name='embeddings'), 
    path('classroom', views.classroom, name='classroom'),
    path('classroom/<int:class_id>/', dashboardController.classroom_student_list, name='classroom_student_list'),
    path('classroom/<int:class_id>/add_student/', dashboardController.add_student, name='add_student'),
    path('classroom/<int:classroom_id>/', dashboardController.classroom_student_list, name='classroom_list_attendance'),
    path('classroom_list_attendance', dashboardController.classroom_list_attendance, name='classroom_list_attendance'),
    path('student_list', dashboardController.student_list, name='student_list'),
    path('export-to-excel/', views.export_to_excel, name='export_to_excel'),
    
    path('profile', profileController.view, name='profile'),

   

]

