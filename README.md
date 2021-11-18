# Yolov3_pytorch

Yolov3 (+tiny) object detection - object oriented pythonic pytorch implementation.

Tested with pytorch 0.4.0 and python>3.5. Some basic tests are included in [tests](https://github.com/holli/yolov3_pytorch/tree/master/test) folder.

This repo has a goal to have simple pythonic object oriented implementation that can be easily used as it is and also easy to train or modify the model.

See https://pjreddie.com/darknet/yolo/ for better explanation of how yolov3 object detection system differs from others.

# Pretrained Weights

Pretrained weights are available at: **http://www.ollihuotari.com/data/yolov3_pytorch/** . They are converted from https://pjreddie.com/darknet/yolo/. Check out the notebooks for examples how to use them.


# README for YOLOv3 Pytorch Object Detection for ROS

Thank you to ![Olli Huotari](http://www.ollihuotari.com/) for the inital implementation. 

This repo includes a ROS node for subscribing to an image, running YOLOv3, and then sending the inferences to the robot if, like in my case, you could not run infrence on the robot due to the operating system not having a supported PyTorch wheel. In the case of running this on an actual robot, delete the scp portion and simply use the `angle_publisher_node.py`. 

For any question, feel free to reach out to me via ![email](ari.chadda@gmail.com).  


