# from os import listdir
# from os.path import isdir, exists
# from PIL import Image
# from django.http import HttpResponse
# import numpy as np
# from mtcnn.mtcnn import MTCNN
# from keras_facenet import FaceNet
# from sklearn.preprocessing import LabelEncoder, Normalizer
# from sklearn.svm import SVC
# from sklearn.metrics import classification_report, confusion_matrix
# import pickle
# import os

# # Function to detect new directories
# def detect_new_dirs(dataset_dir, pickle_file):
#     def load_existing_dirs(pickle_file):
#         if exists(pickle_file):
#             with open(pickle_file, 'rb') as file:
#                 return pickle.load(file)
#         else:
#             return set()

#     def save_existing_dirs(pickle_file, directories):
#         with open(pickle_file, 'wb') as file:
#             pickle.dump(directories, file)

#     # Load existing directories
#     existing_dirs = load_existing_dirs(pickle_file)

#     # Load dataset and detect new directories
#     new_dirs = set(listdir(dataset_dir)) - existing_dirs
#     if new_dirs:
#         print(f"New directories found in {dataset_dir}: {new_dirs}")
#         # Update the existing directories with the new ones
#         updated_dirs = existing_dirs.union(new_dirs)
#         save_existing_dirs(pickle_file, updated_dirs)
#         return new_dirs
#     else:
#         print(f"No new data found in {dataset_dir}.")
#         return None

# # Extract a single face from a given photograph
# def extract_face(filename, required_size=(160, 160)):
#     image = Image.open(filename)
#     image = image.convert('RGB')
#     pixels = np.asarray(image)
#     detector = MTCNN()
#     results = detector.detect_faces(pixels)
#     if len(results) == 0:
#         return None
#     x1, y1, width, height = results[0]['box']
#     x1, y1 = abs(x1), abs(y1)
#     x2, y2 = x1 + width, y1 + height
#     face = pixels[y1:y2, x1:x2]
#     image = Image.fromarray(face)
#     image = image.resize(required_size)
#     face_array = np.asarray(image)
#     return face_array

# # Load images and extract faces for all images in a directory
# def load_faces(directory):
#     faces = list()
#     for filename in listdir(directory):
#         path = directory + '/' + filename
#         face = extract_face(path)
#         if face is None:
#             continue
#         faces.append(face)
#     return faces

# # Load a dataset that contains one subdir for each class that in turn contains images
# def load_dataset(directory, new_dirs=None):
#     X, y = list(), list()
#     subdirs = new_dirs if new_dirs else listdir(directory)
#     for subdir in subdirs:
#         path = directory + '/' + subdir + '/'
#         if not isdir(path):
#             continue
#         faces = load_faces(path)
#         labels = [subdir for _ in range(len(faces))]
#         print('>loaded %d examples for class: %s' % (len(faces), subdir))
#         X.extend(faces)
#         y.extend(labels)
#     return X, y

# # Get embedding for a face
# def get_embedding(model, face_pixels):
#     face_pixels = face_pixels.astype('float32')
#     mean, std = face_pixels.mean(), face_pixels.std()
#     face_pixels = (face_pixels - mean) / std
#     samples = np.expand_dims(face_pixels, axis=0)
#     yhat = model.predict(samples)
#     return yhat[0]

# # Main function to load data, process it, and train the model
# def main():
#     dataset_train_dir = 'Face/dataset_split/train/'
#     dataset_val_dir = 'Face/dataset_split/val/'
#     pickle_train_file = 'Face/check_data/train_existing_dirs.pkl'
#     pickle_val_file = 'Face/check_data/val_existing_dirs.pkl'

#     # Detect new directories
#     new_train_dirs = detect_new_dirs(dataset_train_dir, pickle_train_file)
#     new_val_dirs = detect_new_dirs(dataset_val_dir, pickle_val_file)
    
#     # Load new data
#     new_trainX, new_trainy = load_dataset(dataset_train_dir, new_train_dirs) if new_train_dirs else ([], [])
#     new_valX, new_valy = load_dataset(dataset_val_dir, new_val_dirs) if new_val_dirs else ([], [])

#     # Create FaceNet embedder
#     embedder = FaceNet()
#     model = embedder.model

#     # Convert faces in train and test set to embeddings
#     new_embeddings_trainX = [get_embedding(model, face) for face in new_trainX]
#     new_embeddings_valX = [get_embedding(model, face) for face in new_valX]

#     # Load previous data if available
#     old_embeddings_trainX, old_trainy = [], []
#     old_embeddings_valX, old_valy = [], []

#     if os.path.exists('Face/train_emb_lab/train_embeddings.pkl') and os.path.exists('Face/train_emb_lab/train_labels.pkl'):
#         with open('Face/train_emb_lab/train_embeddings.pkl', 'rb') as file:
#             old_embeddings_trainX = pickle.load(file)
#         with open('Face/train_emb_lab/train_labels.pkl', 'rb') as file:
#             old_trainy = pickle.load(file)
        
#         # Combine old and new embeddings
#         combined_embeddings_trainX_list = old_embeddings_trainX.tolist()
#         combined_embeddings_trainX_list.extend(new_embeddings_trainX)
#         combined_embeddings_trainX = np.asarray(combined_embeddings_trainX_list)

#         combined_trainy = old_trainy + new_trainy

#         # Save combined data
#         with open('Face/train_emb_lab/train_embeddings.pkl', 'wb') as file:
#             pickle.dump(combined_embeddings_trainX, file)
#         with open('Face/train_emb_lab/train_labels.pkl', 'wb') as file:
#             pickle.dump(combined_trainy, file)
#     else:
#         combined_embeddings_trainX = np.asarray(new_embeddings_trainX)
#         combined_trainy = new_trainy
#         with open('Face/train_emb_lab/train_embeddings.pkl', 'wb') as file:
#             pickle.dump(combined_embeddings_trainX, file)
#         with open('Face/train_emb_lab/train_labels.pkl', 'wb') as file:
#             pickle.dump(combined_trainy, file)

#     if os.path.exists('Face/val_emb_lab/val_embeddings.pkl') and os.path.exists('Face/val_emb_lab/val_labels.pkl'):
#         with open('Face/val_emb_lab/val_embeddings.pkl', 'rb') as file:
#             old_embeddings_valX = pickle.load(file)
#         with open('Face/val_emb_lab/val_labels.pkl', 'rb') as file:
#             old_valy = pickle.load(file)
        
#         # Combine old and new embeddings
#         combined_embeddings_valX_list = old_embeddings_valX.tolist()
#         combined_embeddings_valX_list.extend(new_embeddings_valX)
#         combined_embeddings_valX = np.asarray(combined_embeddings_valX_list)

#         combined_valy = old_valy + new_valy

#         # Save combined data
#         with open('Face/val_emb_lab/val_embeddings.pkl', 'wb') as file:
#             pickle.dump(combined_embeddings_valX, file)
#         with open('Face/val_emb_lab/val_labels.pkl', 'wb') as file:
#             pickle.dump(combined_valy, file)
#     else:
#         combined_embeddings_valX = np.asarray(new_embeddings_valX)
#         combined_valy = new_valy
#         with open('Face/val_emb_lab/val_embeddings.pkl', 'wb') as file:
#             pickle.dump(combined_embeddings_valX, file)
#         with open('Face/val_emb_lab/val_labels.pkl', 'wb') as file:
#             pickle.dump(combined_valy, file)
    
#     # Normalize input vectors
#     in_encoder = Normalizer(norm='l2')
#     combined_embeddings_trainX = in_encoder.transform(np.asarray(combined_embeddings_trainX))
#     combined_embeddings_valX = in_encoder.transform(np.asarray(combined_embeddings_valX))

#     # Label encode targets
#     out_encoder = LabelEncoder()
#     out_encoder.fit(combined_trainy)
#     combined_trainy = out_encoder.transform(combined_trainy)
#     combined_valy = out_encoder.transform(combined_valy)

#     # Train SVM model
#     svm_model = SVC(kernel='linear', probability=True)
#     svm_model.fit(combined_embeddings_trainX, combined_trainy)

#     # Save the trained model and out_encoder for use in realtime_face_recognition
#     with open('Face/svm_model/svm_model.pkl', 'wb') as model_file:
#         pickle.dump(svm_model, model_file)
#     with open('Face/svm_model/out_encoder.pkl', 'wb') as encoder_file:
#         pickle.dump(out_encoder, encoder_file)

#     # Evaluate model on test set
#     y_pred = svm_model.predict(combined_embeddings_valX)
#     print("\nConfusion Matrix:")
#     print(confusion_matrix(combined_valy, y_pred))
#     print("\nClassification Report:")
#     print(classification_report(combined_valy, y_pred))

# if __name__ == "__main__":
#     main()


# def embeddings(request):
#     main()
#     return HttpResponse("Images captured, saved, and embeddings created successfully.")




# from os import listdir
# from os.path import isdir, join, exists
# from PIL import Image
# import cv2
# from django.http import HttpResponse
# import numpy as np
# from mtcnn import MTCNN
# from keras_facenet import FaceNet
# from sklearn.preprocessing import LabelEncoder, Normalizer
# from sklearn.svm import SVC
# from sklearn.metrics import classification_report, confusion_matrix
# import pickle
# import os
# import firebase_admin
# from firebase_admin import credentials, storage



# # Function to detect new directories
# def detect_new_dirs(dataset_dir, pickle_file):
#     def load_existing_dirs(pickle_file):
#         if os.path.exists(pickle_file):
#             with open(pickle_file, 'rb') as file:
#                 return pickle.load(file)
#         else:
#             return set()

#     def save_existing_dirs(pickle_file, directories):
#         with open(pickle_file, 'wb') as file:
#             pickle.dump(directories, file)

#     # Check if pickle file exists
#     if os.path.exists(pickle_file):
#         existing_dirs = load_existing_dirs(pickle_file)
#     else:
#         existing_dirs = set()

#     # Load dataset and detect new directories
#     if existing_dirs:
#         new_dirs = set(storage.bucket().list_blobs(prefix=dataset_dir)) - existing_dirs
#     else:
#         new_dirs = set(storage.bucket().list_blobs(prefix=dataset_dir))

#     if new_dirs:
#         print(f"New directories found in {dataset_dir}: {new_dirs}")
#         # Update the existing directories with the new ones
#         updated_dirs = existing_dirs.union(new_dirs)
#         save_existing_dirs(pickle_file, updated_dirs)
#         return new_dirs
#     else:
#         print(f"No new data found in {dataset_dir}.")
#         return None

# # Extract a single face from a given photograph
# def extract_face_from_storage(image_path, required_size=(160, 160)):
#     bucket = storage.bucket()
#     blob = bucket.blob(image_path)
#     img_bytes = blob.download_as_bytes()
#     nparr = np.frombuffer(img_bytes, np.uint8)
#     image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     detector = MTCNN()
#     results = detector.detect_faces(image)
#     if len(results) == 0:
#         return None
#     x1, y1, width, height = results[0]['box']
#     x1, y1 = abs(x1), abs(y1)
#     x2, y2 = x1 + width, y1 + height
#     face = image[y1:y2, x1:x2]
#     image = Image.fromarray(face)
#     image = image.resize(required_size)
#     face_array = np.asarray(image)
#     return face_array

# # Load images and extract faces for all images in a directory from Firebase Storage
# def load_faces_from_storage(directory):
#     faces = list()
#     for filename in listdir(directory):
#         path = join(directory, filename)
#         face = extract_face_from_storage(path)
#         if face is None:
#             continue
#         faces.append(face)
#     return faces

# # Load a dataset that contains one subdir for each class that in turn contains images
# def load_dataset_from_storage(directory, new_dirs=None):
#     X, y = list(), list()
#     subdirs = new_dirs if new_dirs else listdir(directory)
#     for subdir in subdirs:
#         subdir_path = join(directory, subdir)
#         if not isdir(subdir_path):
#             continue
#         faces = load_faces_from_storage(subdir_path)
#         labels = [subdir for _ in range(len(faces))]
#         print(f'>loaded {len(faces)} examples for class: {subdir}')
#         X.extend(faces)
#         y.extend(labels)
#     return X, y

# # Get embedding for a face
# def get_embedding(model, face_pixels):
#     face_pixels = face_pixels.astype('float32')
#     mean, std = face_pixels.mean(), face_pixels.std()
#     face_pixels = (face_pixels - mean) / std
#     samples = np.expand_dims(face_pixels, axis=0)
#     yhat = model.predict(samples)
#     return yhat[0]

# # Main function to load data, process it, and train the model
# def main():
#     dataset_train_dir = 'train'  # Thay đổi tên thư mục dataset trên Firebase
#     dataset_val_dir = 'val'      # Thay đổi tên thư mục dataset trên Firebase
#     pickle_train_file = 'Face/check_data/train_existing_dirs.pkl'
#     pickle_val_file = 'Face/check_data/val_existing_dirs.pkl'

#     # Detect new directories
#     new_train_dirs = detect_new_dirs(dataset_train_dir, pickle_train_file)
#     new_val_dirs = detect_new_dirs(dataset_val_dir, pickle_val_file)
    
#     # Load new data from Firebase Storage
#     new_trainX, new_trainy = load_dataset_from_storage(dataset_train_dir, new_train_dirs) if new_train_dirs else ([], [])
#     new_valX, new_valy = load_dataset_from_storage(dataset_val_dir, new_val_dirs) if new_val_dirs else ([], [])

#     # Create FaceNet embedder
#     embedder = FaceNet()
#     model = embedder.model

#     # Convert faces in train and test set to embeddings
#     new_embeddings_trainX = [get_embedding(model, face) for face in new_trainX]
#     new_embeddings_valX = [get_embedding(model, face) for face in new_valX]

#     # Load previous data if available
#     old_embeddings_trainX, old_trainy = [], []
#     old_embeddings_valX, old_valy = [], []

#     if os.path.exists('Face/train_emb_lab/train_embeddings.pkl') and os.path.exists('Face/train_emb_lab/train_labels.pkl'):
#         with open('Face/train_emb_lab/train_embeddings.pkl', 'rb') as file:
#             old_embeddings_trainX = pickle.load(file)
#         with open('Face/train_emb_lab/train_labels.pkl', 'rb') as file:
#             old_trainy = pickle.load(file)
        
#         # Combine old and new embeddings
#         combined_embeddings_trainX_list = old_embeddings_trainX.tolist()
#         combined_embeddings_trainX_list.extend(new_embeddings_trainX)
#         combined_embeddings_trainX = np.asarray(combined_embeddings_trainX_list)

#         combined_trainy = old_trainy + new_trainy

#         # Save combined data
#         with open('Face/train_emb_lab/train_embeddings.pkl', 'wb') as file:
#             pickle.dump(combined_embeddings_trainX, file)
#         with open('Face/train_emb_lab/train_labels.pkl', 'wb') as file:
#             pickle.dump(combined_trainy, file)
#     else:
#         combined_embeddings_trainX = np.asarray(new_embeddings_trainX)
#         combined_trainy = new_trainy
#         with open('Face/train_emb_lab/train_embeddings.pkl', 'wb') as file:
#             pickle.dump(combined_embeddings_trainX, file)
#         with open('Face/train_emb_lab/train_labels.pkl', 'wb') as file:
#             pickle.dump(combined_trainy, file)

#     if os.path.exists('Face/val_emb_lab/val_embeddings.pkl') and os.path.exists('Face/val_emb_lab/val_labels.pkl'):
#         with open('Face/val_emb_lab/val_embeddings.pkl', 'rb') as file:
#             old_embeddings_valX = pickle.load(file)
#         with open('Face/val_emb_lab/val_labels.pkl', 'rb') as file:
#             old_valy = pickle.load(file)
        
#         # Combine old and new embeddings
#         combined_embeddings_valX_list = old_embeddings_valX.tolist()
#         combined_embeddings_valX_list.extend(new_embeddings_valX)
#         combined_embeddings_valX = np.asarray(combined_embeddings_valX_list)

#         combined_valy = old_valy + new_valy

#         # Save combined data
#         with open('Face/val_emb_lab/val_embeddings.pkl', 'wb') as file:
#             pickle.dump(combined_embeddings_valX, file)
#         with open('Face/val_emb_lab/val_labels.pkl', 'wb') as file:
#             pickle.dump(combined_valy, file)
#     else:
#         combined_embeddings_valX = np.asarray(new_embeddings_valX)
#         combined_valy = new_valy
#         with open('Face/val_emb_lab/val_embeddings.pkl', 'wb') as file:
#             pickle.dump(combined_embeddings_valX, file)
#         with open('Face/val_emb_lab/val_labels.pkl', 'wb') as file:
#             pickle.dump(combined_valy, file)
    
#     # Normalize input vectors
#     in_encoder = Normalizer(norm='l2')
#     combined_embeddings_trainX = in_encoder.transform(np.asarray(combined_embeddings_trainX))
#     combined_embeddings_valX = in_encoder.transform(np.asarray(combined_embeddings_valX))

#     # Label encode targets
#     out_encoder = LabelEncoder()
#     out_encoder.fit(combined_trainy)
#     combined_trainy = out_encoder.transform(combined_trainy)
#     combined_valy = out_encoder.transform(combined_valy)

#     # Train SVM model
#     svm_model = SVC(kernel='linear', probability=True)
#     svm_model.fit(combined_embeddings_trainX, combined_trainy)

#     # Save the trained model and out_encoder for use in realtime_face_recognition
#     with open('Face/svm_model/svm_model.pkl', 'wb') as model_file:
#         pickle.dump(svm_model, model_file)
#     with open('Face/svm_model/out_encoder.pkl', 'wb') as encoder_file:
#         pickle.dump(out_encoder, encoder_file)

#     # Evaluate model on test set
#     y_pred = svm_model.predict(combined_embeddings_valX)
#     print("\nConfusion Matrix:")
#     print(confusion_matrix(combined_valy, y_pred))
#     print("\nClassification Report:")
#     print(classification_report(combined_valy, y_pred))

# def embeddings(request):
#     main()
#     return HttpResponse("Images captured, saved, and embeddings created successfully.")






from os import listdir
import os
from os.path import isdir, join
import tempfile
import numpy as np
import cv2
from django.http import HttpResponse
from PIL import Image
import pickle
import firebase_admin
from firebase_admin import storage
from mtcnn import MTCNN
from keras_facenet import FaceNet
from sklearn.preprocessing import LabelEncoder, Normalizer
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix

# Function to detect new directories
def detect_new_dirs(dataset_dir, pickle_file):
    # Function to load existing directories from pickle file
    def load_existing_dirs(pickle_file):
        if os.path.exists(pickle_file):
            with open(pickle_file, 'rb') as file:
                return pickle.load(file)
        else:
            return set()  # Return an empty set if pickle file doesn't exist

    # Function to save updated directories to pickle file
    def save_existing_dirs(pickle_file, directories):
        with open(pickle_file, 'wb') as file:
            pickle.dump(directories, file)

    # Load existing directories
    existing_dirs = load_existing_dirs(pickle_file)

    # Initialize Firebase Storage client
    bucket = storage.bucket()
    blobs = bucket.list_blobs(prefix=dataset_dir + '/')

    # Extract directory names from the blob names
    new_dirs = {blob.name.split('/')[1] for blob in blobs if blob.name.split('/')[1]}

    # Detect new directories
    new_dirs = new_dirs - existing_dirs
    if new_dirs:
        print(f"New directories found in {dataset_dir}: {new_dirs}")
        # Update the existing directories with the new ones
        updated_dirs = existing_dirs.union(new_dirs)
        save_existing_dirs(pickle_file, updated_dirs)
        return new_dirs
    else:
        print(f"No new data found in {dataset_dir}.")
        return None

# Extract a single face from a given photograph
def extract_face(filename, required_size=(160, 160)):
    image = Image.open(filename)
    image = image.convert('RGB')
    pixels = np.asarray(image)
    detector = MTCNN()
    results = detector.detect_faces(pixels)
    if len(results) == 0:
        return None
    x1, y1, width, height = results[0]['box']
    x1, y1 = abs(x1), abs(y1)
    x2, y2 = x1 + width, y1 + height
    face = pixels[y1:y2, x1:x2]
    image = Image.fromarray(face)
    image = image.resize(required_size)
    face_array = np.asarray(image)
    return face_array

# Load images and extract faces for all images in a directory from Firebase Storage
def load_faces(directory):
    faces = []
    try:
        bucket = storage.bucket()
        blobs = bucket.list_blobs(prefix=directory + '/')

        for blob in blobs:
            filename = blob.name.split('/')[-1]
            temp_image_path = os.path.join(tempfile.gettempdir(), filename)  # Tạo đường dẫn tạm thời

            # Tải ảnh từ Firebase Storage xuống đường dẫn tạm thời
            blob.download_to_filename(temp_image_path)

            # Trích xuất khuôn mặt từ ảnh
            face = extract_face(temp_image_path)
            if face is not None:
                faces.append(face)

            # Xóa tệp ảnh tạm thời
            os.remove(temp_image_path)

    except Exception as e:
        print(f"Error loading faces from directory '{directory}' in Firebase Storage: {str(e)}")

    return faces

# Load a dataset that contains one subdir for each class that in turn contains images
def load_dataset_from_storage(directory, new_dirs=None):
    X, y = [], []
    bucket = storage.bucket()
    
    # Use new_dirs if provided, otherwise list all subdirectories in directory
    blobs = bucket.list_blobs(prefix=directory + '/')
    subdirs = new_dirs if new_dirs else [os.path.normpath(blob.name.split('/')[1]) for blob in blobs if '/' in blob.name]
    
    for subdir in subdirs:
        subdir_path = directory + '/' + subdir
        
        # Load faces from Firebase Storage
        faces = load_faces(subdir_path)
        
        # Append faces and labels to X and y
        X.extend(faces)
        y.extend([subdir] * len(faces))
        
        print(f'Loaded {len(faces)} examples for class: {subdir}')
    
    return X, y

# Get embedding for a face
def get_embedding(model, face_pixels):
    face_pixels = face_pixels.astype('float32')
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels - mean) / std
    samples = np.expand_dims(face_pixels, axis=0)
    yhat = model.predict(samples)
    return yhat[0]

# Main function to load data, process it, and train the model
def main():
    dataset_train_dir = 'train'  # Thay đổi tên thư mục dataset trên Firebase
    dataset_val_dir = 'val'      # Thay đổi tên thư mục dataset trên Firebase
    pickle_train_file = 'Face/check_data/train_existing_dirs.pkl'
    pickle_val_file = 'Face/check_data/val_existing_dirs.pkl'

    # Detect new directories
    new_train_dirs = detect_new_dirs(dataset_train_dir, pickle_train_file)
    new_val_dirs = detect_new_dirs(dataset_val_dir, pickle_val_file)
    
    # Load new data from Firebase Storage
    new_trainX, new_trainy = load_dataset_from_storage(dataset_train_dir, new_train_dirs) if new_train_dirs else ([], [])
    new_valX, new_valy = load_dataset_from_storage(dataset_val_dir, new_val_dirs) if new_val_dirs else ([], [])

    # Check if there are new embeddings to process
    if not new_trainX:
        print("No new data found for training.")
        return
    if not new_valX:
        print("No new data found for validation.")
        return

    # Create FaceNet embedder
    embedder = FaceNet()
    model = embedder.model

    # Convert faces in train and test set to embeddings
    new_embeddings_trainX = [get_embedding(model, face) for face in new_trainX]
    new_embeddings_valX = [get_embedding(model, face) for face in new_valX]

    # Load previous data if available
    old_embeddings_trainX, old_trainy = [], []
    old_embeddings_valX, old_valy = [], []

    if os.path.exists('Face/train_emb_lab/train_embeddings.pkl') and os.path.exists('Face/train_emb_lab/train_labels.pkl'):
        with open('Face/train_emb_lab/train_embeddings.pkl', 'rb') as file:
            old_embeddings_trainX = pickle.load(file)
        with open('Face/train_emb_lab/train_labels.pkl', 'rb') as file:
            old_trainy = pickle.load(file)
        
        # Combine old and new embeddings
        combined_embeddings_trainX_list = old_embeddings_trainX.tolist()
        combined_embeddings_trainX_list.extend(new_embeddings_trainX)
        combined_embeddings_trainX = np.asarray(combined_embeddings_trainX_list)

        combined_trainy = old_trainy + new_trainy

        # Save combined data
        with open('Face/train_emb_lab/train_embeddings.pkl', 'wb') as file:
            pickle.dump(combined_embeddings_trainX, file)
        with open('Face/train_emb_lab/train_labels.pkl', 'wb') as file:
            pickle.dump(combined_trainy, file)
    else:
        combined_embeddings_trainX = np.asarray(new_embeddings_trainX)
        combined_trainy = new_trainy
        with open('Face/train_emb_lab/train_embeddings.pkl', 'wb') as file:
            pickle.dump(combined_embeddings_trainX, file)
        with open('Face/train_emb_lab/train_labels.pkl', 'wb') as file:
            pickle.dump(combined_trainy, file)

    if os.path.exists('Face/val_emb_lab/val_embeddings.pkl') and os.path.exists('Face/val_emb_lab/val_labels.pkl'):
        with open('Face/val_emb_lab/val_embeddings.pkl', 'rb') as file:
            old_embeddings_valX = pickle.load(file)
        with open('Face/val_emb_lab/val_labels.pkl', 'rb') as file:
            old_valy = pickle.load(file)
        
        # Combine old and new embeddings
        combined_embeddings_valX_list = old_embeddings_valX.tolist()
        combined_embeddings_valX_list.extend(new_embeddings_valX)
        combined_embeddings_valX = np.asarray(combined_embeddings_valX_list)

        combined_valy = old_valy + new_valy

        # Save combined data
        with open('Face/val_emb_lab/val_embeddings.pkl', 'wb') as file:
            pickle.dump(combined_embeddings_valX, file)
        with open('Face/val_emb_lab/val_labels.pkl', 'wb') as file:
            pickle.dump(combined_valy, file)
    else:
        combined_embeddings_valX = np.asarray(new_embeddings_valX)
        combined_valy = new_valy
        with open('Face/val_emb_lab/val_embeddings.pkl', 'wb') as file:
            pickle.dump(combined_embeddings_valX, file)
        with open('Face/val_emb_lab/val_labels.pkl', 'wb') as file:
            pickle.dump(combined_valy, file)
    
    # Normalize input vectors
    in_encoder = Normalizer(norm='l2')
    combined_embeddings_trainX = in_encoder.transform(np.asarray(combined_embeddings_trainX))
    combined_embeddings_valX = in_encoder.transform(np.asarray(combined_embeddings_valX))

    # Label encode targets
    out_encoder = LabelEncoder()
    out_encoder.fit(combined_trainy)
    combined_trainy = out_encoder.transform(combined_trainy)
    combined_valy = out_encoder.transform(combined_valy)

    # Train SVM model
    svm_model = SVC(kernel='linear', probability=True)
    svm_model.fit(combined_embeddings_trainX, combined_trainy)

    # Save the trained model and out_encoder for use in realtime_face_recognition
    with open('Face/svm_model/svm_model.pkl', 'wb') as model_file:
        pickle.dump(svm_model, model_file)
    with open('Face/svm_model/out_encoder.pkl', 'wb') as encoder_file:
        pickle.dump(out_encoder, encoder_file)

    # Evaluate model on test set
    y_pred = svm_model.predict(combined_embeddings_valX)
    print("\nConfusion Matrix:")
    print(confusion_matrix(combined_valy, y_pred))
    print("\nClassification Report:")
    print(classification_report(combined_valy, y_pred))

if __name__ == "__main__":
    main()

def embeddings(request):
    main()
    return HttpResponse("Images captured, saved, and embeddings created successfully.")
