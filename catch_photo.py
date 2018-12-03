import cv2
import os,sys
import time
import io
from PIL import Image
import numpy as np
# import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# os.environ["CUDA_VISIBLE_DEVICES"] = "2"
# ============================
def init_camera(size_height,size_width):
    cap = cv2.VideoCapture(0)  # 默认的摄像头
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, size_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size_height)
    print("already setting up")
    return cap
# ================================
def read_one_pic(cap):
    ret, frame = cap.read()
    try:
        if(ret):
            # cv2.imwrite('./photo_to_cloud/'+str(int(time.time()))+'.jpeg',frame)
            return frame
            camera_close(cap)
        else:
            camera_close(cap)
            raise Exception('can\'t catch any photo')
    except Exception as msg:
        print(msg)
# ===============================
def camera_close(cap):
    print("close your camera")
    cap.release()
    cv2.destroyAllWindows()
# =============================
def write_photo(file_path,frame):
    cv2.imwrite(file_path, frame)
# =============================
def encode_frame_into_file(frame):
    '''
    Reference:
    https://www.smwenku.com/a/5b7fad6d2b717767c6b0f1dc/
    '''
    img_encode = cv2.imencode('.jpg', frame)
    str_encode = img_encode[1].tostring()
    file_io = io.BytesIO(str_encode)
    return file_io
# ================================
def make_photo(file_dir,size_height,size_width,num_of_pic):
    """使用opencv拍照"""
    cap = cv2.VideoCapture(0)  # 默认的摄像头
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, size_width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size_height)
    current_pic_num=0
    if os.path.isdir(file_dir):
        print("目錄存在。")
        print("為您儲存資料")
    else:
        print("目錄不存在。")
        print("創立目錄")
        os.makedirs(file_dir)
    while True:
        ret, frame = cap.read()
        if ret:
            cv2.imshow("capture", frame)  # 弹窗口
            if (cv2.waitKey(1) & 0xFF == ord('q')):
                if(current_pic_num>=num_of_pic):
                    break
                cv2.imwrite(file_dir+str(current_pic_num)+".jpeg", frame)
                current_pic_num=current_pic_num+1
                print(current_pic_num)
            elif (cv2.waitKey(1) & 0xFF == ord('k')):
                print("Leave taking-photo mode")
                break
        else:
            break
    cap.release()
    cv2.destroyAllWindows()
def convert_to_opencv(image):
    # RGB -> BGR conversion is performed as well.
    r,g,b = np.array(image).T
    opencv_image = np.array([b,g,r]).transpose()
    return opencv_image

def crop_center(img,cropx,cropy):
    h, w = img.shape[:2]
    startx = w//2-(cropx//2)
    starty = h//2-(cropy//2)
    return img[starty:starty+cropy, startx:startx+cropx]

def resize_down_to_1600_max_dim(image):
    h, w = image.shape[:2]
    if (h < 1600 and w < 1600):
        return image

    new_size = (1600 * w // h, 1600) if (h > w) else (1600, 1600 * h // w)
    return cv2.resize(image, new_size, interpolation = cv2.INTER_LINEAR)

def resize_to_256_square(image):
    h, w = image.shape[:2]
    return cv2.resize(image, (256, 256), interpolation = cv2.INTER_LINEAR)

def update_orientation(image):
    exif_orientation_tag = 0x0112
    if hasattr(image, '_getexif'):
        exif = image._getexif()
        if (exif != None and exif_orientation_tag in exif):
            orientation = exif.get(exif_orientation_tag, 1)
            # orientation is 1 based, shift to zero based and flip/transpose based on 0-based values
            orientation -= 1
            if orientation >= 4:
                image = image.transpose(Image.TRANSPOSE)
            if orientation == 2 or orientation == 3 or orientation == 6 or orientation == 7:
                image = image.transpose(Image.FLIP_TOP_BOTTOM)
            if orientation == 1 or orientation == 2 or orientation == 5 or orientation == 6:
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
    return image
def predict_from_load(image):
    # We next get the largest center square
    h, w = image.shape[:2]
    min_dim = min(w,h)
    max_square_image = crop_center(image, min_dim, min_dim)
    # Resize that square down to 256x256
    augmented_image = resize_to_256_square(max_square_image)

    # The compact models have a network size of 227x227, the model requires this size.
    network_input_size = 227

    # Crop the center for the specified network_input_Size
    augmented_image = crop_center(augmented_image, network_input_size, network_input_size)

    # These names are part of the model and cannot be changed.
    output_layer = 'loss:0'
    input_node = 'Placeholder:0'
    with tf.Session() as sess:
        prob_tensor = sess.graph.get_tensor_by_name(output_layer)
        predictions, = sess.run(prob_tensor, {input_node: [augmented_image] })
        # print(predictions)
        # Print the highest probability label
        highest_probability_index = np.argmax(predictions)
        print('Classified as: ' + labels[highest_probability_index])

        # Or you can print out all of the results mapping self.labels to probabilities.
        # label_index = 0
        # for p in predictions:
        #     truncated_probablity = np.float64(np.round(p,8))
        #     print (self.labels[label_index], truncated_probablity)
        #     label_index += 1
if __name__=='__main__':
    '''
    file_dir 放入類別名稱
    num_of_pic=儲存照片張數
    '''
    
    # file_dir="./test_new_1028/"
    # size_height=480
    # size_width=640
    # num_of_pic=20
    # make_photo(file_dir,size_height,size_width,num_of_pic)
    graph_def = tf.GraphDef()
    labels = []
    filename='./model/model.pb'
    labels_filename='./model/labels.txt'
    # Import the TF graph
    with tf.gfile.FastGFile(filename, 'rb') as f:
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def, name='')

    # Create a list of labels.
    with open(labels_filename, 'rt') as lf:
        for l in lf:
            labels.append(l.strip())
    cap=init_camera(480,640)
    while 1:
        tStart = time.time()#計時開始
        if (cv2.waitKey(1) & 0xFF == ord('q')):
            break
        image=read_one_pic(cap)
        predict_from_load(image)
        tEnd = time.time()#計時結束
        print (1/(tEnd - tStart))#原型長這樣