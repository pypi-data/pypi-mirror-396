from spirems import Subscriber, sms2cvimg, tensor2sms, sms2tensor
import cv2
import time


global img_cnt, dt_tot, print_dt
img_cnt = 0
dt_tot = 0.0
print_dt = False


def callback_f(msg):
    global img_cnt, dt_tot, print_dt
    cvimg = sms2tensor(msg)
    dt_tot += time.time() - msg['timestamp']
    img_cnt += 1
    if img_cnt > 600 and not print_dt:
        print("dt: {}".format(dt_tot / img_cnt))
        print_dt = True
    cv2.imshow('img', cvimg)
    cv2.waitKey(5)

sub = Subscriber('/tensor_mem', 'memory_msgs::Tensor', callback_f)
