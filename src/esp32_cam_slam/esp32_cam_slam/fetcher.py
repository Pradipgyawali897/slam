import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from cv_bridge import CvBridge
import cv2
import numpy as np
import requests
import urllib3
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Fetcher(Node):
    def __init__(self):
        super().__init__('fetcher')
        
        # Parameters
        self.declare_parameter('url', 'https://192.168.1.5:8080/video')
        self.url = self.get_parameter('url').get_parameter_value().string_value
        
        self.get_logger().info(f"Fetcher node initialized. Target URL: {self.url}")
        
        # Connection state
        self.streaming = False
        self.timer = self.create_timer(1.0, self.connection_manager)

    def connection_manager(self):
        if self.streaming:
            return
        
        try:
            self.get_logger().info(f"Connecting to {self.url}...")
            # verify=False for self-signed certs
            response = requests.get(self.url, stream=True, timeout=5, verify=False)
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                self.get_logger().info(f"Connected! Content-Type: {content_type}")
                
                if 'text/html' in content_type:
                    self.get_logger().error("URL returned HTML. Please check the stream path.")
                    response.close()
                    return

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
                        # Call the placeholder function for image handling
                        self.process_cv(jpg_data)
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

    def process_cv(self, image_data):
        """
        TODO: Implement the CV part to decode JPEG and publish to ROS.
        This function is called every time a full JPEG is scanned from the stream.
        """
        self.get_logger().info(f"CAPTURED IMAGE DATA: {len(image_data)} bytes. TODO: Process with CV.")
        pass

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
