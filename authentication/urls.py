from django.contrib import admin
from django.urls import path
from . import views
from . import dashboardController
from . import camera
from . import capPicture
from . import train
# urlpatterns = [
#     # views home orgri
#     path('', views.home, name='home'),

#     # path('', views.bost, name='bost'),
#     path('bostt', views.bost2, name='bostt'),
#     path('nguoidung', views.userthem, name='nguoidung'),

#     path('signup', views.signup, name='signup'),
#     path('activate/<uidb64>/<token>', views.activate, name='activate'),
#     path('signin', views.signin, name='signin'),
#     path('signout', views.signout, name='signout'),
#     # path('run_cap_picture/', views.run_cap_picture, name='run_cap_picture'),
#     # path('run_cap_picture/<str:student_id>/<str:name>/', views.run_cap_picture, name='run_cap_picture'),
#     path('aa/<str:student_id>/<str:name>/', views.aa, name='aa'),
#     # dashboardController
#     # buil ở đây
#     # path('demo', dashboardController.demo, name='demo'),

#     # path('ok', dashboardController.ok, name='ok'),
#     path('regisImg', views.regisImg, name='regisImg'),
#     # test data
#     # path('', dashboardController.data, name='students-view'),

#     # student
#     # path('test', dashboardController.data, name='students-view'),
#     # path('add_student/', dashboardController.add_student, name='add_student'),
#     # path('update_student/<int:student_id>/', dashboardController.update_student, name='update_student'),
#     path('delete_student/<int:student_id>/', dashboardController.delete_student, name='delete_student'),


#     path('diemdanh', camera.diemdanh, name='diemdanh'),



#     # class
#     # path('', dashboardController.classroom_list, name='classroom_list'),
#     # path('add_student/', dashboardController.add_student, name='add_student'),
#     # path('classroom/<int:class_id>/', dashboardController.classroom_detail, name='classroom_detail'),
#     # path('classroom/<int:class_id>/add_student/', dashboardController.add_student, name='add_student'),

#     path('classroom_list', dashboardController.classroom_list, name='classroom_list'),
#     path('add_student/', dashboardController.add_student, name='add_student'),
#     path('classroom/<int:class_id>/', dashboardController.classroom_detail, name='classroom_detail'),
#     path('classroom/<int:class_id>/add_student/', dashboardController.add_student, name='add_student'),
#     path('student/<int:student_id>/edit/', dashboardController.edit_student, name='edit_student'), 

#     path('embeddings', views.embeddings, name='embeddings'), 
#     path('classroom', views.classroom, name='classroom'),
# ]

urlpatterns = [
    path('', views.home, name='home'),
    path('bostt', views.bost2, name='bostt'),
    path('nguoidung', views.userthem, name='nguoidung'),
    path('signup', views.signup, name='signup'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('signin', views.signin, name='signin'),
    path('signout', views.signout, name='signout'),
    path('aa/<str:student_id>/<str:name>/', views.aa, name='aa'),
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
    # path('aa/<str:student_id>/<str:name>/', capPicture.aa, name='aa'),
    # path('student_list', dashboardController.student_list, name='student_list'),
    path('classroom_list_attendance', dashboardController.classroom_list_attendance, name='classroom_list_attendance'),
    path('student_list', dashboardController.student_list, name='student_list'),
    path('export-to-excel/', views.export_to_excel, name='export_to_excel'),
   

]

