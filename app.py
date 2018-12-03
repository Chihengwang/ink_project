import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
from catch_photo import *
import tkinter.messagebox
import client
import tensorflow as tf

PORT=8888
fps = 30
Threshold=15
class App:
    def __init__(self, window, window_title, video_source=0):
        self.graph_def = tf.GraphDef()
        self.labels = []
        self.filename='./model/model.pb'
        self.labels_filename='./model/labels.txt'
        self.window = window
        self.window.title(window_title)
        self.client=client
        self.video_source = video_source
        self.status = tkinter.StringVar()
        self.possibility = tkinter.StringVar()
        # open video source (by default this will try to open the computer webcam)
        self.vid = MyVideoCapture(self.video_source)
        # Create a canvas that can fit the above video source size
        self.canvas = tkinter.Canvas(window, width = self.vid.width, height = self.vid.height)
        self.canvas.pack()
        # ----------------------------------------
        # Create a status label.
        self.label_status = tkinter.Label(window, 
            textvariable=self.status,    # 标签的文字
            bg='green',     # 背景颜色
            font=('Arial', 12),     # 字体和字体大小
            width=30, height=2  # 标签长宽
            )
        self.possibility_label = tkinter.Label(window, 
            textvariable=self.possibility,    # 标签的文字
            bg='red',     # 背景颜色
            font=('Arial', 12),     # 字体和字体大小
            width=30, height=2  # 标签长宽
            )
        self.label_status.pack(anchor=tkinter.CENTER)
        self.possibility_label.pack(anchor=tkinter.CENTER)
        self.save_path=tkinter.Entry(window)
        self.save_path.pack()
        # ====================================================
        # 做一個frame來儲存路徑
        # https://hk.saowen.com/a/e849c05a62a70020f4bdb9f9f19c6ea03cce59468efbbc584101fcce4c81c978
        # self.path_frame = tkinter.Frame(window)
        # self.path_frame.pack()
        # self.frame_l = tkinter.Frame(self.path_frame)# 第二層frame，左frame，長在主frame上
        # self.frame_r = tkinter.Frame(self.path_frame)# 第二層frame，右frame，長在主frame上
        # self.frame_l.pack(side='left')
        # self.frame_r.pack(side='right')
        # self.path_label=tkinter.Label(self.frame_l, text='Save Path:').pack()
        # self.save_path=tkinter.Entry(self.frame_r)
        # self.save_path.pack()
        # ====================================================
        # change carema's frame
        # self.change_width_label=tkinter.Label(self.frame_l, text='Cam_width:').pack()
        # self.cam_width=tkinter.Entry(self.frame_r)
        # self.cam_width.pack()
        # self.change_height_label=tkinter.Label(self.frame_l, text='Cam_height:').pack()
        # self.cam_height=tkinter.Entry(self.frame_r)
        # self.cam_height.pack()
        # ====================================================
        # Button that lets the user take a snapshot
        self.btn_snapshot=tkinter.Button(window, text="Snapshot", width=50, command=self.snapshot)
        self.change_width_btn=tkinter.Button(window, text="cam_width_setting", width=50, command=self.change_width)
        self.change_height_btn=tkinter.Button(window, text="cam_height_setting", width=50, command=self.change_height)
        self.btn_snapshot.pack(anchor=tkinter.CENTER)
        self.change_width_btn.pack(anchor=tkinter.CENTER)
        self.change_height_btn.pack(anchor=tkinter.CENTER)
        # , expand=True 可以讓按鈕放到最底部。
        self.model_setup()
        # self.sock=client.init_socket(PORT)
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 1
        self.update()
        self.window.geometry("600x650")
        self.window.mainloop()

    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        folder_path=''
        if self.save_path.get()=='':
            tkinter.messagebox.showwarning('警告','請輸入下載路徑!!')
        else:
            folder_path=self.save_path.get()
            if ret:
                if os.path.isdir(folder_path):
                    print("save the data for you")
                else:
                    os.makedirs(folder_path)
                cv2.imwrite(folder_path+"/"+"frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpeg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    def update(self):
        # Get a frame from the video source
        tStart = time.time()#計時開始
        ret, frame = self.vid.get_frame()
        if ret:
            status,possibility=self.predict_from_load(frame)
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
            # 這裡面包含要把資料傳給labview client.send_status function就是要做這件事情。
            if possibility*100>Threshold:
                # If possibility over than eighteen,Send the msg to Labview
                self.possibility.set('Possibility: '+str(possibility*100)+'%')
                self.status.set('Status: '+status)
                # MSG_FROM_LABVIEW=self.client.send_status(status)
            else:
                self.possibility.set('Possibility: '+'0'+'%')
                self.status.set('Status: '+'not valid!!!!!')
            # tEnd = time.time()#計時結束
            # print (1/(tEnd - tStart))#原型長這樣
        self.window.after(self.delay, self.update)
    def model_setup(self):
        # Import the TF graph
        with tf.gfile.FastGFile(self.filename, 'rb') as f:
            self.graph_def.ParseFromString(f.read())
            tf.import_graph_def(self.graph_def, name='')

        # Create a list of labels.
        with open(self.labels_filename, 'rt') as lf:
            for l in lf:
                self.labels.append(l.strip())
    def predict_from_load(self,image):
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
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.3)
        with tf.Session(config=tf.ConfigProto(gpu_options=gpu_options)) as sess:
        # with tf.device('/device:GPU:0'):
            prob_tensor = sess.graph.get_tensor_by_name(output_layer)
            predictions, = sess.run(prob_tensor, {input_node: [augmented_image] })
            # print(predictions)
            # Print the highest probability label
            highest_probability_index = np.argmax(predictions)
            # print('Classified as: ' + self.labels[highest_probability_index])

            # Or you can print out all of the results mapping self.labels to probabilities.
            # label_index = 0
            # for p in predictions:
            #     truncated_probablity = np.float64(np.round(p,8))
            #     print (self.labels[label_index], truncated_probablity)
            #     label_index += 1
            return self.labels[highest_probability_index],max(predictions)
    def change_width(self):
        if self.cam_width.get()!='':
            # self.vid.set_frame_width(float(self.cam_width.get()))
            print(float(self.cam_width.get()))
            print(self.vid)
    def change_height(self):
        if self.cam_height.get()!='':
            self.vid.set_frame_height(float(self.cam_height.get()))
               
class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
        # initialize the cam's width and height
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 640)
        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)
    def set_frame_width(self,width):
        if self.vid.isOpened():
            self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
    def set_frame_height(self,height):
        if self.vid.isOpened():
            self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
    def get_frame_width(self,width):
        if self.vid.isOpened():
            return self.width
    def get_frame_height(self,height):
        if self.vid.isOpened():
            return self.height
    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()

# Create a window and pass it to the Application object
# intialize the window in the first parameter.
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
App(tkinter.Tk(), "Tkinter and OpenCV")