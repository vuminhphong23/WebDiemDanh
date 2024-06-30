from datetime import datetime, timezone
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Classroom(models.Model):
    class_id = models.AutoField(primary_key=True)
    class_name = models.CharField(max_length=100)
    teacher = models.ForeignKey(User, limit_choices_to={'is_superuser': False}, on_delete=models.CASCADE)  # Liên kết tới bảng User
    subject = models.CharField(max_length=100)

    def __str__(self):
        return self.class_name

class TblStudents(models.Model):
    student_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=100, unique=True)
    phone = models.CharField(max_length=15)
    iCap = models.BooleanField(default=False)
    date_birth = models.DateField()
    password = models.CharField(max_length=128, default=make_password('abc@123'))
    classrooms = models.ManyToManyField(Classroom, related_name='students',blank=True)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"

    def __str__(self):
        return self.name

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

class AttendanceSession(models.Model):
    session_id = models.AutoField(primary_key=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='attendance_sessions')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.classroom.class_name} - {self.date} ({self.start_time} - {self.end_time})"

class Attendance(models.Model):
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='attendances', null=True)
    student = models.ForeignKey(TblStudents, on_delete=models.CASCADE, related_name='attendances')
    attended = models.BooleanField(default=False)
    date = models.DateField(null=True, blank=True)  # Thêm cột date
    time = models.TimeField(null=True, blank=True)  # Thêm cột time

    def __str__(self):
        return f"{self.student.name} - {self.session.classroom.class_name} - {self.session.date}"

    def save(self, *args, **kwargs):
        if not self.date or not self.time:
            now = timezone.now()
            self.date = self.date or now.date()
            self.time = self.time or now.time()
        if self.session:
            if not (self.date == self.session.date and self.session.start_time <= self.time <= self.session.end_time):
                self.attended = False
            else:
                self.attended = True
        super().save(*args, **kwargs)
