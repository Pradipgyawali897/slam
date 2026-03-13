import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np
import requests
import urllib3

# Disable insecure request warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Fetcher(Node):
    def __init__(self):
        super().__init__('fetcher')
        
        # Parameters
        self.declare_parameter('url', 'https://192.168.1.5:8080/video')
        self.url = self.get_parameter('url').get_parameter_value().string_value
        
        # Publishers
        self.image_pub = self.create_publisher(Image, '/camera/image_raw', 10)
        self.bridge = CvBridge()
        
        self.get_logger().info(f"Fetcher node initialized. Publishing to /camera/image_raw. Source: {self.url}")
        
        # Connection state
        self.streaming = False
        self.timer = self.create_timer(1.0, self.connection_manager)

    def connection_manager(self):
        if self.streaming:
            return
        
        try:
            self.get_logger().info(f"Connecting to {self.url}...")
            response = requests.get(self.url, stream=True, timeout=5, verify=False)
            
            if response.status_code == 200:
                self.get_logger().info("Connected to stream!")
                self.streaming = True
                self.process_stream(response)
            else:
                self.get_logger().error(f"Failed to connect: {response.status_code}")
        except Exception as e:
            self.get_logger().error(f"Connection error: {str(e)}")

    def process_stream(self, response):
        """Streams content and scans for JPEG delimiters"""
        bytes_data = b''
        try:
            for chunk in response.iter_content(chunk_size=4096):
                bytes_data += chunk
                while True:
                    a = bytes_data.find(b'\xff\xd8') # JPEG Start
                    b = bytes_data.find(b'\xff\xd9') # JPEG End marker
                    
                    if a != -1 and b != -1 and a < b:
                        jpg_data = bytes_data[a:b+2]
                        bytes_data = bytes_data[b+2:]
                        self.publish_image(jpg_data)
                    else:
                        break
                
                # Prevent memory overflow
                if len(bytes_data) > 2000000:
                    bytes_data = b''
                    
        except Exception as e:
            self.get_logger().error(f"Stream interrupted: {str(e)}")
        finally:
            self.streaming = False
            response.close()

    def publish_image(self, jpg_data):
        """Decodes JPEG and publishes to ROS topic"""
        try:
            # Decode JPEG
            np_arr = np.frombuffer(jpg_data, np.uint8)
            cv_image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            
            if cv_image is not None:
                # Convert to ROS Image message
                img_msg = self.bridge.cv2_to_imgmsg(cv_image, encoding="bgr8")
                img_msg.header.stamp = self.get_clock().now().to_msg()
                img_msg.header.frame_id = "camera_link"
                
                # Publish
                self.image_pub.publish(img_msg)
            else:
                self.get_logger().warning("Failed to decode image frame")
        except Exception as e:
            self.get_logger().error(f"Error publishing image: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = Fetcher()
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
