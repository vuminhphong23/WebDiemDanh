# # ===========================================================================================================
# from django.utils import timezone
# import cv2
# from django.shortcuts import get_object_or_404, redirect, render
# from numpy import expand_dims
# from mtcnn.mtcnn import MTCNN
# from keras_facenet import FaceNet
# import pickle
# import json
# from .models import AttendanceSession, TblStudents, Attendance

# # Load FaceNet model for embedding extraction
# embedder = FaceNet()
# facenet_model = embedder.model
# detector = MTCNN()

# # Extract face embeddings from a given frame
# def get_face_embeddings(frame):
#     faces = detector.detect_faces(frame)
#     embeddings = []
#     boxes = []
#     for face in faces:
#         x1, y1, width, height = face['box']
#         x1, y1 = abs(x1), abs(y1)
#         x2, y2 = x1 + width, y1 + height
#         face_pixels = frame[y1:y2, x1:x2]
#         face_pixels = cv2.resize(face_pixels, (160, 160))
#         face_pixels = face_pixels.astype('float32')
#         mean, std = face_pixels.mean(), face_pixels.std()
#         face_pixels = (face_pixels - mean) / std
#         samples = expand_dims(face_pixels, axis=0)
#         yhat = facenet_model.predict(samples)
#         embeddings.append(yhat[0])
#         boxes.append((x1, y1, x2, y2))
#     return embeddings, boxes

# def get_attendance_record(session_id):
#     """
#     Hàm này trả về một từ điển chứa trạng thái điểm danh của mỗi sinh viên trong mỗi buổi học.
#     """
#     attendance_record = {}
#     # Lấy tất cả các bản ghi điểm danh từ cơ sở dữ liệu cho session_id cụ thể
#     attendances = Attendance.objects.filter(session_id=session_id)
#     for attendance in attendances:
#         student_id = attendance.student_id
#         date_attended = attendance.date
#         # Kiểm tra xem đã tạo khóa cho sinh viên trong attendance_record chưa
#         if student_id not in attendance_record:
#             attendance_record[student_id] = set()
#         # Thêm ngày điểm danh vào tập hợp tương ứng
#         attendance_record[student_id].add(date_attended)
#     return attendance_record


# # Capture video from the webcam and make predictions
# def realtime_face_recognition(model, out_encoder, classroom_id, session_id):
#     cap = cv2.VideoCapture(0)
#     detections = []  # Danh sách để lưu thông tin nhận diện
#     confidence_threshold = 80.0  # Ngưỡng tin cậy
#     attendance_message = ""

#     # Lấy dữ liệu điểm danh từ cơ sở dữ liệu
#     attendance_record = get_attendance_record(session_id)
#     session = get_object_or_404(AttendanceSession, session_id=session_id)

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         frame = cv2.flip(frame, 1)

#         face_embeddings, boxes = get_face_embeddings(frame)

#         for i, face_emb in enumerate(face_embeddings):
#             samples = expand_dims(face_emb, axis=0)
#             yhat_class = model.predict(samples)
#             yhat_prob = model.predict_proba(samples)
#             class_index = yhat_class[0]
#             class_probability = yhat_prob[0, class_index] * 100
#             predict_name = out_encoder.inverse_transform(yhat_class)[0]

#             x1, y1, x2, y2 = boxes[i]
#             cv2.putText(frame, f'{predict_name} ({class_probability:.2f}%)', 
#                         (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
#             cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

#             # In thông báo nhận diện khuôn mặt
#             stripped_name = predict_name.split('_', 1)[-1]
#             print(f"Detected: {stripped_name} with {class_probability:.2f}% confidence")

#             if class_probability >= confidence_threshold:
#                 try:
#                     student = TblStudents.objects.get(name=stripped_name)
#                     print(f"Marking attendance for {stripped_name}")

#                     now = timezone.localtime()
#                     today = now.date()
#                     current_time = now.time()

#                     # Check if the current date matches the session date
#                     if today != session.date:
#                         attendance_message = f"{student.student_id} - {student.name} is not on the session date"
#                         print(attendance_message)
#                         continue
                    
#                     # Check if the current time is within the session time range
#                     if not (session.start_time <= current_time <= session.end_time):
#                         attendance_message = f"{student.student_id} - {student.name} is outside session time range"
#                         print(attendance_message)
#                         continue

#                     # Kiểm tra xem đã điểm danh cho sinh viên này trong ngày hôm nay chưa
#                     if student.student_id in attendance_record:
#                         if today in attendance_record[student.student_id]:
#                             print(f"Attendance for {stripped_name} already recorded for today")
#                             attendance_message = f"{student.student_id} - {student.name} already Attendance"
#                             print(attendance_message)
#                             continue  # Bỏ qua nếu đã điểm danh cho sinh viên này trong ngày hôm nay
#                     else:
#                         attendance_record[student.student_id] = set()

#                     # Ghi thông tin điểm danh vào cơ sở dữ liệu
#                     attendance_instance, created = Attendance.objects.get_or_create(
#                         student=student,
#                         session_id=session_id,
#                         date=today,
#                         time=current_time,
#                         attended=True
#                     )

#                     # Đánh dấu đã điểm danh cho sinh viên này trong ngày hôm nay
#                     attendance_record[student.student_id].add(today)
#                     attendance_message = f"{student.student_id} - {student.name} Attendance successfully"
#                     print(attendance_message)

#                 except TblStudents.DoesNotExist:
#                     print(f"Student {stripped_name} not found in database")


#         if attendance_message:
#             cv2.putText(frame, attendance_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
#         cv2.imshow('Video', frame)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()

    

# def diemdanh(request, classroom_id, session_id):
#     with open('Face/svm_model/svm_model.pkl', 'rb') as model_file:
#         model = pickle.load(model_file)
#     with open('Face/svm_model/out_encoder.pkl', 'rb') as encoder_file:
#         out_encoder = pickle.load(encoder_file)

#     realtime_face_recognition(model, out_encoder, classroom_id, session_id)
#     return redirect('session_attendance_detail', session_id=session_id)


from django.utils import timezone
import cv2
from django.shortcuts import get_object_or_404, redirect
from numpy import expand_dims
import face_recognition
from keras_facenet import FaceNet
import pickle
import threading 
from .models import AttendanceSession, TblStudents, Attendance
from .pnhLCD1602 import LCD1602
from firebase_admin import storage

# Load FaceNet model for embedding extraction
embedder = FaceNet()
facenet_model = embedder.model

redirect_flag = False

# Extract face embeddings from a given frame
def get_face_embeddings(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # face_recognition cần sử dụng ảnh RGB
    face_locations = face_recognition.face_locations(rgb_frame)  # Phát hiện vị trí khuôn mặt
    embeddings = []
    boxes = []

    for face_location in face_locations:
        top, right, bottom, left = face_location
        face_pixels = frame[top:bottom, left:right]
        face_pixels = cv2.resize(face_pixels, (160, 160))
        face_pixels = face_pixels.astype('float32')
        mean, std = face_pixels.mean(), face_pixels.std()
        face_pixels = (face_pixels - mean) / std
        samples = expand_dims(face_pixels, axis=0)
        yhat = facenet_model.predict(samples)
        embeddings.append(yhat[0])
        boxes.append((left, top, right, bottom))

    return embeddings, boxes

def get_attendance_record(session_id):
    attendance_record = {}
    attendances = Attendance.objects.filter(session_id=session_id)
    for attendance in attendances:
        student_id = attendance.student_id
        date_attended = attendance.date
        if student_id not in attendance_record:
            attendance_record[student_id] = set()
        attendance_record[student_id].add(date_attended)
    return attendance_record

def upload_to_firebase(image, folder, image_name):
    bucket = storage.bucket()
    blob = bucket.blob(f'{folder}/{image_name}')
    _, img_encoded = cv2.imencode('.jpg', image)
    blob.upload_from_string(img_encoded.tobytes(), content_type='image/jpeg')
    print(f'Uploaded {image_name} to {folder}.')
    

def realtime_face_recognition(model, out_encoder, classroom_id, session_id):    
    cap = cv2.VideoCapture(0)
    confidence_threshold = 80.0  # Ngưỡng xác suất để điểm danh
    attendance_message = ""
    attendance_record = get_attendance_record(session_id)
    session = get_object_or_404(AttendanceSession, session_id=session_id)

    frame_count = 0  # Đếm số khung hình để giảm tần suất nhận diện

    while True:
        
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)

        # Chỉ xử lý mỗi 7 khung hình để giảm tải
        frame_count += 1
        if frame_count % 7 != 0:
            continue

        face_embeddings, boxes = get_face_embeddings(frame)

        for i, face_emb in enumerate(face_embeddings):
            samples = expand_dims(face_emb, axis=0)
            yhat_class = model.predict(samples)
            yhat_prob = model.predict_proba(samples)
            class_index = yhat_class[0]
            class_probability = yhat_prob[0, class_index] * 100
            predict_name = out_encoder.inverse_transform(yhat_class)[0]

            x1, y1, x2, y2 = boxes[i]
            
            if class_probability < confidence_threshold:
                predict_name = "Unknown"  # Gán nhãn "Unknown"
                # Vẽ chữ "Unknown" với màu đỏ
                cv2.putText(frame, predict_name, 
                            (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Khung màu đỏ
            else:
                stripped_name = predict_name.split('_', 1)[-1]
                print(f"Detected: {stripped_name} with {class_probability:.2f}% confidence")
                # Vẽ tên và xác suất với màu xanh
                cv2.putText(frame, f'{stripped_name} ({class_probability:.2f}%)', 
                            (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # Chỉ thực hiện điểm danh khi xác suất đủ lớn
            if class_probability >= confidence_threshold:
                try:
                    student = TblStudents.objects.get(name=stripped_name)
                    print(f"Marking attendance for {stripped_name}")

                    now = timezone.localtime()
                    today = now.date()
                    current_time = now.time()
                    formatted_date = today.strftime('%Y%m%d')

                    if today != session.date:
                        attendance_message = f"{student.student_id} - {student.name} is not on the session date"
                        print(attendance_message)
                        continue
                    
                    if not (session.start_time <= current_time <= session.end_time):
                        attendance_message = f"{student.student_id} - {student.name} is outside session time range"
                        print(attendance_message)
                        continue

                    if student.student_id in attendance_record:
                        if today in attendance_record[student.student_id]:
                            print(f"Attendance for {stripped_name} already recorded for today")
                            attendance_message = f"{student.student_id} - {student.name} already Attendance"
                            print(attendance_message)
                            continue
                    else:
                        attendance_record[student.student_id] = set()
                        formatted_time = current_time.strftime('%H:%M')
                        upload_to_firebase(
                            frame,  # Sử dụng trực tiếp khung hình 'frame' thay vì ghi ra tệp
                            f'result-attendance', 
                            f'{ session.classroom.class_name}_{formatted_time}_{formatted_date}_{student.student_id}_{student.name}.jpg'
                        )
                        lcd = LCD1602()
                        # Hiển thị tên và xác suất lên LCD
                        lcd.clear()  # Xóa nội dung cũ
                        lcd.write_string(f"{stripped_name}")  # Hiển thị tên ở dòng 1
                        lcd.write_string(f"{class_probability:.2f}%")  # Hiển thị phần trăm ở dòng 2

                    # Ghi nhận điểm danh
                    attendance_instance, created = Attendance.objects.get_or_create(
                        student=student,
                        session=session,
                        attended=True
                    )

                    # Cập nhật thông tin cho điểm danh
                    attendance_instance.date = today
                    attendance_instance.time = current_time
                    attendance_instance.save()

                    attendance_record[student.student_id].add(today)
                    attendance_message = f"{student.student_id} - {student.name} Attendance successfully"
                    print(attendance_message)


                except TblStudents.DoesNotExist:
                    print(f"Student {stripped_name} not found in database")

        if attendance_message:
            cv2.putText(frame, attendance_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Đóng LCD khi kết thúc
    if lcd is not None:
        lcd.close()

def diemdanh(request, classroom_id, session_id):
    with open('Face/svm_model/svm_model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    with open('Face/svm_model/out_encoder.pkl', 'rb') as encoder_file:
        out_encoder = pickle.load(encoder_file)

    # Tạo một luồng mới để chạy nhận diện khuôn mặt
    recognition_thread = threading.Thread(target=realtime_face_recognition, args=(model, out_encoder, classroom_id, session_id))
    recognition_thread.start()

    return redirect('session_attendance_detail', session_id=session_id)


















