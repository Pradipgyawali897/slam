import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class Processor(Node):
    def __init__(self):
        super().__init__('processor')
        
        # Subscriptions
        self.image_sub = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )
        
        # Bridge
        self.bridge = CvBridge()
        
        self.get_logger().info("Processor node initialized. Listening to /camera/image_raw")

    def image_callback(self, msg):
        """Callback for receiving raw images"""
        try:
            # Convert ROS Image to OpenCV Image
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            
            # --- SUGAM: YOUR CV WORK STARTS HERE ---
            # You can now use cv_image for feature extraction, SLAM, etc.
            self.process_cv(cv_image)
            # ---------------------------------------
            
        except Exception as e:
            self.get_logger().error(f"Error processing image: {str(e)}")

    def process_cv(self, cv_image):
        """
        SUGAM: implement your Computer Vision and SLAM logic here.
        This function receives the decoded OpenCV image.
        """
        # Placeholder: Display the image to verify it's working
        # Note: In a headless environment, you might want to skip cv2.imshow
        self.get_logger().info(f"Received image: {cv_image.shape}")
        
        # Example: show the image (requires a display)
        # cv2.imshow("Camera Stream", cv_image)
        # cv2.waitKey(1)

def main(args=None):
    rclpy.init(args=args)
    node = Processor()
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
