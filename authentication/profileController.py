from django.shortcuts import redirect, render


def view(request):
    student_id = request.session.get('student_id')
    student_name = request.session.get('student_name')

    if student_id and student_name:
        # Nếu tồn tại thông tin sinh viên trong session, tiếp tục xử lý
        # Ví dụ: Hiển thị thông tin sinh viên
        return render(request, "student/profile.html", {"fname": student_name, "student_id": student_id})
    else:
        # Nếu không tồn tại, chuyển hướng về trang đăng nhập
        return redirect('signin')