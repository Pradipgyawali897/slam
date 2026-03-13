import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2
import numpy as np
import requests
import time

class MJPEGCamNode(Node):
    def __init__(self):
        super().__init__('mjpeg_cam_node')
        
        # Parameters
        self.declare_parameter('url', 'http://192.168.1.100:81/stream')
        self.declare_parameter('frame_id', 'camera_link')
        
        self.full_url = self.get_parameter('url').get_parameter_value().string_value
        self.frame_id = self.get_parameter('frame_id').get_parameter_value().string_value
        
        # Publishers
        self.image_pub = self.create_publisher(Image, 'camera/image_raw', 10)
        self.info_pub = self.create_publisher(CameraInfo, 'camera/camera_info', 10)
        
        self.bridge = CvBridge()
        self.camera_info_msg = self.get_default_camera_info()
        
        self.get_logger().info(f"Connecting to MJPEG stream at {self.full_url}")
        
        # Timer for reconnection or start streaming
        self.timer = self.create_timer(1.0, self.start_streaming)
        self.streaming = False

    def get_default_camera_info(self):
        """Returns a generic CameraInfo message (uncalibrated)"""
        info = CameraInfo()
        info.header.frame_id = self.frame_id
        # Example VGA resolution
        info.width = 640
        info.height = 480
        # Identity calibration
        info.k = [1.0, 0.0, 320.0, 0.0, 1.0, 240.0, 0.0, 0.0, 1.0]
        info.p = [1.0, 0.0, 320.0, 0.0, 0.0, 1.0, 240.0, 0.0, 0.0, 0.0, 1.0, 0.0]
        return info

    def start_streaming(self):
        if self.streaming:
            return
        
        try:
            # verify=False in case of self-signed certs common on ESP32
            response = requests.get(self.full_url, stream=True, timeout=5, verify=False)
            if response.status_code == 200:
                self.streaming = True
                self.get_logger().info("Stream connected!")
                self.process_stream(response)
            else:
                self.get_logger().error(f"Failed to connect: {response.status_code}")
        except Exception as e:
            self.get_logger().error(f"Stream error: {str(e)}")

    def process_stream(self, response):
        bytes_data = b''
        try:
            for chunk in response.iter_content(chunk_size=1024):
                bytes_data += chunk
                a = bytes_data.find(b'\xff\xd8') # JPEG start
                b = bytes_data.find(b'\xff\xd9') # JPEG end
                
                if a != -1 and b != -1:
                    jpg = bytes_data[a:b+2]
                    bytes_data = bytes_data[b+2:]
                    
                    try:
                        img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        if img is not None:
                            # Update camera info resolution if needed
                            if self.camera_info_msg.width != img.shape[1] or self.camera_info_msg.height != img.shape[0]:
                                self.camera_info_msg.width = img.shape[1]
                                self.camera_info_msg.height = img.shape[0]

                            # Publish Image
                            msg = self.bridge.cv2_to_imgmsg(img, encoding="bgr8")
                            msg.header.stamp = self.get_clock().now().to_msg()
                            msg.header.frame_id = self.frame_id
                            self.image_pub.publish(msg)
                            
                            # Publish CameraInfo
                            self.camera_info_msg.header.stamp = msg.header.stamp
                            self.info_pub.publish(self.camera_info_msg)
                            
                    except Exception as e:
                        self.get_logger().warn(f"Decoding error: {str(e)}")
                
                # Prevent memory bloat if markers are missing
                if len(bytes_data) > 1000000:
                    bytes_data = b''
                    
        except Exception as e:
            self.get_logger().error(f"Stream processing interrupted: {str(e)}")
            self.streaming = False

def main(args=None):
    rclpy.init(args=args)
    node = MJPEGCamNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
