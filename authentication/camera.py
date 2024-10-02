# ===========================================================================================================
from django.utils import timezone
import cv2
from django.shortcuts import get_object_or_404, redirect, render
from numpy import expand_dims
from mtcnn.mtcnn import MTCNN
from keras_facenet import FaceNet
import pickle
import json
from .models import AttendanceSession, TblStudents, Attendance

# Load FaceNet model for embedding extraction
embedder = FaceNet()
facenet_model = embedder.model
detector = MTCNN()

# Extract face embeddings from a given frame
def get_face_embeddings(frame):
    faces = detector.detect_faces(frame)
    embeddings = []
    boxes = []
    for face in faces:
        x1, y1, width, height = face['box']
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height
        face_pixels = frame[y1:y2, x1:x2]
        face_pixels = cv2.resize(face_pixels, (160, 160))
        face_pixels = face_pixels.astype('float32')
        mean, std = face_pixels.mean(), face_pixels.std()
        face_pixels = (face_pixels - mean) / std
        samples = expand_dims(face_pixels, axis=0)
        yhat = facenet_model.predict(samples)
        embeddings.append(yhat[0])
        boxes.append((x1, y1, x2, y2))
    return embeddings, boxes

def get_attendance_record(session_id):
    """
    Hàm này trả về một từ điển chứa trạng thái điểm danh của mỗi sinh viên trong mỗi buổi học.
    """
    attendance_record = {}
    # Lấy tất cả các bản ghi điểm danh từ cơ sở dữ liệu cho session_id cụ thể
    attendances = Attendance.objects.filter(session_id=session_id)
    for attendance in attendances:
        student_id = attendance.student_id
        date_attended = attendance.date
        # Kiểm tra xem đã tạo khóa cho sinh viên trong attendance_record chưa
        if student_id not in attendance_record:
            attendance_record[student_id] = set()
        # Thêm ngày điểm danh vào tập hợp tương ứng
        attendance_record[student_id].add(date_attended)
    return attendance_record


# Capture video from the webcam and make predictions
def realtime_face_recognition(model, out_encoder, classroom_id, session_id):
    cap = cv2.VideoCapture(0)
    detections = []  # Danh sách để lưu thông tin nhận diện
    confidence_threshold = 90.0  # Ngưỡng tin cậy
    attendance_message = ""

    # Lấy dữ liệu điểm danh từ cơ sở dữ liệu
    attendance_record = get_attendance_record(session_id)
    session = get_object_or_404(AttendanceSession, session_id=session_id)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        face_embeddings, boxes = get_face_embeddings(frame)

        for i, face_emb in enumerate(face_embeddings):
            samples = expand_dims(face_emb, axis=0)
            yhat_class = model.predict(samples)
            yhat_prob = model.predict_proba(samples)
            class_index = yhat_class[0]
            class_probability = yhat_prob[0, class_index] * 100
            predict_name = out_encoder.inverse_transform(yhat_class)[0]

            # Use "unknown" if confidence is below the threshold
            if class_probability < confidence_threshold:
                predict_name = "Unknown"
            else:
                predict_name = out_encoder.inverse_transform(yhat_class)[0]

            x1, y1, x2, y2 = boxes[i]
            
            if predict_name == "Unknown":
                cv2.putText(frame, f'{predict_name}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            else:
                cv2.putText(frame, f'{predict_name} ({class_probability:.2f}%)', 
                            (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # In thông báo nhận diện khuôn mặt
            stripped_name = predict_name.split('_', 1)[-1]
            print(f"Detected: {stripped_name} with {class_probability:.2f}% confidence")

            if class_probability >= confidence_threshold:
                try:
                    student = TblStudents.objects.get(name=stripped_name)
                    print(f"Marking attendance for {stripped_name}")

                    now = timezone.localtime()
                    today = now.date()
                    current_time = now.time()

                    # Check if the current date matches the session date
                    if today != session.date:
                        attendance_message = f"{student.student_id} - {student.name} is not on the session date"
                        print(attendance_message)
                        continue
                    
                    # Check if the current time is within the session time range
                    if not (session.start_time <= current_time <= session.end_time):
                        attendance_message = f"{student.student_id} - {student.name} is outside session time range"
                        print(attendance_message)
                        continue

                    # Kiểm tra xem đã điểm danh cho sinh viên này trong ngày hôm nay chưa
                    if student.student_id in attendance_record:
                        if today in attendance_record[student.student_id]:
                            print(f"Attendance for {stripped_name} already recorded for today")
                            attendance_message = f"{student.student_id} - {student.name} already Attendance"
                            print(attendance_message)
                            continue  # Bỏ qua nếu đã điểm danh cho sinh viên này trong ngày hôm nay
                    else:
                        attendance_record[student.student_id] = set()

                    # Ghi thông tin điểm danh vào cơ sở dữ liệu
                    attendance_instance, created = Attendance.objects.get_or_create(
                        student=student,
                        session_id=session_id,
                        date=today,
                        time=current_time,
                        attended=True
                    )

                    # Đánh dấu đã điểm danh cho sinh viên này trong ngày hôm nay
                    attendance_record[student.student_id].add(today)
                    attendance_message = f"{student.student_id} - {student.name} Attendance successfully"
                    print(attendance_message)

                except TblStudents.DoesNotExist:
                    print(f"Student {stripped_name} not found in database")

            # Lưu thông tin nhận diện vào danh sách
            detection_info = {
                'name': stripped_name,
                'confidence': class_probability,
                'box': {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
            }
            detections.append(detection_info)
        if attendance_message:
            cv2.putText(frame, attendance_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    # Ghi thông tin nhận diện ra file JSON
    with open('detections.json', 'w') as json_file:
        json.dump(detections, json_file, indent=4)

def diemdanh(request, classroom_id, session_id):
    with open('Face/svm_model/svm_model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    with open('Face/svm_model/out_encoder.pkl', 'rb') as encoder_file:
        out_encoder = pickle.load(encoder_file)

    realtime_face_recognition(model, out_encoder, classroom_id, session_id)
    return redirect('session_attendance_detail', session_id=session_id)




# import cv2
# from django.shortcuts import render
# from numpy import expand_dims
# from mtcnn.mtcnn import MTCNN
# from keras_facenet import FaceNet
# import pickle
# import json
# from datetime import datetime
# from .models import TblStudents, Attendance

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

# # Capture video from the webcam and make predictions
# def realtime_face_recognition(model, out_encoder):
#     cap = cv2.VideoCapture(0)
#     detections = []  # List to store detection information
#     confidence_threshold = 80.0  # Confidence threshold
#     attendance_message = ""  # Variable to store attendance message
    
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
            
#             if class_probability >= confidence_threshold:
#                 cv2.putText(frame, f'{predict_name} ({class_probability:.2f}%)', 
#                             (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
#                 cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

#                 # In thông báo nhận diện khuôn mặt
#                 stripped_name = predict_name.split('_', 1)[-1]
#                 print(f"Detected: {stripped_name} with {class_probability:.2f}% confidence")
                
#                 try:
#                     student = TblStudents.objects.get(name=stripped_name)
#                     print(f"Marking attendance for {stripped_name}")
#                     Attendance.objects.update_or_create(
#                         student=student,
#                         datetime=datetime.now(),
#                         defaults={'attended': True}
#                     )
#                     attendance_message = f"{student.student_id} - {student.name} Attendance successfully"
#                     print(attendance_message)
#                 except TblStudents.DoesNotExist:
#                     print(f"Student {stripped_name} not found in database")

#                 # Lưu thông tin nhận diện vào danh sách
#                 detection_info = {
#                     'name': stripped_name,
#                     'confidence': class_probability,
#                     'box': {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2}
#                 }
#                 detections.append(detection_info)
        
#         if attendance_message:
#             cv2.putText(frame, attendance_message, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
#         cv2.imshow('Video', frame)
        
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
    
#     cap.release()
#     cv2.destroyAllWindows()
    
#     # Ghi thông tin nhận diện ra file JSON
#     with open('detections.json', 'w') as json_file:
#         json.dump(detections, json_file, indent=4)

# def diemdanh(request):
#     with open('Face/svm_model/svm_model.pkl', 'rb') as model_file:
#         model = pickle.load(model_file)
#     with open('Face/svm_model/out_encoder.pkl', 'rb') as encoder_file:
#         out_encoder = pickle.load(encoder_file)

#     realtime_face_recognition(model, out_encoder)
#     return render(request, 'admin/your_template.html', {'success_message': "Điểm danh thành công."})






