import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
from catch_photo import *
import tkinter.messagebox
class App:
    def __init__(self, window, window_title, video_source=0):
        # self.graph_def = tf.GraphDef()
        self.labels = []
        self.filename='./model/model.pb'
        self.labels_filename='./model/labels.txt'
        self.window = window
        self.window.title(window_title)
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
        # ====================================================
        self.save_path=tkinter.Entry(window)
        self.save_path.pack()
        # ====================================================
        # Button that lets the user take a snapshot
        self.btn_snapshot=tkinter.Button(window, text="Snapshot", width=50, command=self.snapshot)
        self.btn_snapshot.pack(anchor=tkinter.CENTER, expand=True)
        # self.model_setup()
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 5
        self.update()

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
        # tStart = time.time()#計時開始
        ret, frame = self.vid.get_frame()
        if ret:
            # status,possibility=self.predict_from_load(frame)
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
            # if possibility*100>18:
            #     self.possibility.set('Possibility: '+str(possibility*100)+'%')
            #     self.status.set('Status: '+status)
            # else:
            #     self.possibility.set('Possibility: '+'0'+'%')
            #     self.status.set('Status: '+'not valid!!!!!')
            # tEnd = time.time()#計時結束
            # # print (1/(tEnd - tStart))#原型長這樣
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
        with tf.Session() as sess:
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
App(tkinter.Tk(), "Tkinter and OpenCV")