'''
程序執行時，開啟攝影機
=>每隔一段時間就將照片儲存丟到azure api
假如是 empty or a_few 就給labview的 server發消息讓警示燈亮起代表測試成功
'''
from catch_photo import *
import client
import api_model
import time

fps = 30
Threshold=15
if __name__=="__main__":
    # initialize the things you need
    # height=480 width=640 for every pic
    cap=init_camera(480,640)
    # sock=client.init_socket(PORT)
    while True:
        # send status
        time.sleep(1)
        frame=read_one_pic(cap)
        io_file=encode_frame_into_file(frame)
        status,max_value=api_model.prediction_with_data(io_file)
# =============================================================
# directly send photo to cloud service
        # status,max_value=api_model.test_with_file_data('./test_new/18.jpeg')
# =============================================================
        # 先查看出來的機率是不是太小
        if(max_value<Threshold):
            print("This value is not vaild to verify your status!")
            continue
        # 查看status 檢察目前水位是否沒問題
        MSG_FROM_LABVIEW=client.send_status(status)
        if(MSG_FROM_LABVIEW=="WARNING"):
            print("need to add some water")
            time.sleep(fps)
        elif(MSG_FROM_LABVIEW=="OKAY"):
            print("no need to worry")
            time.sleep(fps)
        else:
            print("Didn't received your data")
