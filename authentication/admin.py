from django.contrib import admin
from .models import TblStudents, Classroom, AttendanceSession, Attendance

class TblStudentsInline(admin.TabularInline):
    model = TblStudents.classrooms.through
    extra = 1

class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 1
    raw_id_fields = ('session', 'student')

@admin.register(TblStudents)
class TblStudentsAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'email', 'phone', 'date_birth', 'iCap', 'display_classrooms')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('date_birth', 'classrooms', 'iCap')
    exclude = ('password',)

    def display_classrooms(self, obj):
        return ", ".join([classroom.class_name for classroom in obj.classrooms.all()])

    display_classrooms.short_description = 'Classrooms'
    readonly_fields = ('student_id',)
    filter_horizontal = ('classrooms',)

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            raw_password = form.cleaned_data.get('password')
            if raw_password and not obj.pk:
                obj.set_password(raw_password)
        super().save_model(request, obj, form, change)

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('class_id', 'class_name', 'teacher', 'subject', 'display_students')
    search_fields = ('class_name', 'teacher__username', 'subject')
    inlines = [TblStudentsInline]
    list_filter = ('teacher',)

    def display_students(self, obj):
        return ", ".join([student.name for student in obj.students.all()])

    display_students.short_description = 'Students'

class AttendanceSessionInline(admin.TabularInline):
    model = AttendanceSession
    extra = 1
    show_change_link = True

@admin.register(AttendanceSession)
class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'classroom', 'date', 'start_time', 'end_time')
    search_fields = ('classroom__class_name', 'date')
    list_filter = ('classroom', 'date')
    inlines = [AttendanceInline]

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('session', 'student', 'attended', 'datetime')
    search_fields = ('session__classroom__class_name', 'student__name', 'session__date')
    list_filter = ('session__classroom', 'session__date', 'attended')
    raw_id_fields = ('session', 'student')
    fields = ('session', 'student', 'datetime', 'attended')


