# import os
# import cv2
# import numpy as np
# from mtcnn.mtcnn import MTCNN
# from sklearn.model_selection import train_test_split
# from django.http import HttpResponse
# from django.shortcuts import render
# from django.shortcuts import redirect
# import firebase_admin
# from firebase_admin import credentials, storage

# # Function to enhance image by applying denoising and smoothing
# def enhance_image(image):
#     # Làm sạch nhiễu bằng Gaussian Blur
#     blurred_image = cv2.GaussianBlur(image, (5, 5), 0)
    
#     # Tăng cường độ sáng và độ tương phản
#     enhanced_image = cv2.convertScaleAbs(blurred_image, alpha=1.2, beta=10)
    
#     return enhanced_image

# # Function to flip and rotate images to increase dataset size
# def augment_images(images):
#     augmented_images = []
#     for image in images:
        
#         # Flip image vertically
#         flipped_vertical = cv2.flip(image, 1)
#         augmented_images.append(flipped_vertical)
        
#         # Rotate image by 15 degrees clockwise
#         rows, cols, _ = image.shape
#         rotation_matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), 15, 1)
#         rotated_image = cv2.warpAffine(image, rotation_matrix, (cols, rows))
#         augmented_images.append(rotated_image)
        
#         # Rotate image by -15 degrees counterclockwise
#         rotation_matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), -15, 1)
#         rotated_image = cv2.warpAffine(image, rotation_matrix, (cols, rows))
#         augmented_images.append(rotated_image)
#     return augmented_images


# def upload_to_firebase(image, folder, image_name):
#     bucket = storage.bucket()
#     blob = bucket.blob(f'{folder}/{image_name}')
#     _, img_encoded = cv2.imencode('.jpg', image)
#     blob.upload_from_string(img_encoded.tobytes(), content_type='image/jpeg')
#     print(f'Uploaded {image_name} to {folder}.')

# def capture_images(student_id, name):
#     cap = cv2.VideoCapture(0)
#     detector = MTCNN()
#     img_count = 0
#     captured_images = []

#     print("Press 'c' to capture image. Press 'q' to quit.")
#     while img_count < 10:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         frame = cv2.flip(frame, 1)
#         cv2.imshow('Capturing Images', frame)
        
#         key = cv2.waitKey(1)
#         if key & 0xFF == ord('c'):
#             results = detector.detect_faces(frame)
#             if results:
#                 x1, y1, width, height = results[0]['box']
#                 x1, y1 = abs(x1), abs(y1)
#                 x2, y2 = x1 + width, y1 + height
#                 face = frame[y1:y2, x1:x2]
#                 face = cv2.resize(face, (160, 160))
#                 face = enhance_image(face)
#                 captured_images.append(face)
#                 img_count += 1
#                 print(f"Captured image {img_count}")
#         elif key & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
    
#     augmented_images = augment_images(captured_images)
#     train_images, val_images = train_test_split(augmented_images, test_size=0.33, random_state=42)
    
#     for i, img in enumerate(train_images):
#         upload_to_firebase(img, f'train/{student_id}_{name}', f'{student_id}_{name}_{i+1}.jpg')
#     for i, img in enumerate(val_images):
#         upload_to_firebase(img, f'val/{student_id}_{name}', f'{student_id}_{name}_{i+1}.jpg')

import cv2
import face_recognition
from firebase_admin import storage
import numpy as np

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

# Function to upload images to Firebase
def upload_to_firebase(image, folder, image_name):
    bucket = storage.bucket()
    blob = bucket.blob(f'{folder}/{image_name}')
    _, img_encoded = cv2.imencode('.jpg', image)
    blob.upload_from_string(img_encoded.tobytes(), content_type='image/jpeg')
    print(f'Uploaded {image_name} to {folder}.')

# Function to capture and save images with face detection
def capture_images(student_id, name):
    cap = cv2.VideoCapture(0)
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
            face_locations = face_recognition.face_locations(frame)
            if face_locations:
                for (top, right, bottom, left) in face_locations:
                    face = frame[top:bottom, left:right]
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

    # Save training images (first 2/3) and validation images (last 1/3)
    split_point = int(len(augmented_images) * 0.67)
    train_images = augmented_images[:split_point]
    val_images = augmented_images[split_point:]
    
    for i, img in enumerate(train_images):
        upload_to_firebase(img, f'train/{student_id}_{name}', f'{student_id}_{name}_{i+1}.jpg')
    for i, img in enumerate(val_images):
        upload_to_firebase(img, f'val/{student_id}_{name}', f'{student_id}_{name}_{i+1}.jpg')

