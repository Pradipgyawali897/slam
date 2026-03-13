import rclpy
from rclpy.node import Node
import requests
import urllib3

# Suppress insecure request warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class StreamDebugNode(Node):
    def __init__(self):
        super().__init__('stream_debug_node')
        self.declare_parameter('url', 'https://192.168.1.5:8080/')
        self.url = self.get_parameter('url').get_parameter_value().string_value
        
        self.get_logger().info(f"Target URL: {self.url}")
        self.timer = self.create_timer(2.0, self.check_stream)

    def check_stream(self):
        self.get_logger().info(f"Attempting to fetch {self.url}...")
        try:
            # We use a short timeout for the initial connection
            response = requests.get(self.url, stream=True, timeout=5, verify=False)
            
            self.get_logger().info(f"Status Code: {response.status_code}")
            self.get_logger().info(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                self.get_logger().info("Connected! Reading first 1024 bytes...")
                # Read a small bit to see the content
                chunk = next(response.iter_content(chunk_size=1024))
                self.get_logger().info(f"First chunk size: {len(chunk)} bytes")
                self.get_logger().info(f"First 16 bytes (hex): {chunk[:16].hex()}")
                
                # Check for JPEG markers
                if b'\xff\xd8' in chunk:
                    self.get_logger().info("JPEG start marker (FF D8) found in first chunk.")
                else:
                    self.get_logger().warn("JPEG start marker NOT found in first chunk.")
            
            # Close the stream after check to avoid blocking
            response.close()
            
        except Exception as e:
            self.get_logger().error(f"Connection failed: {str(e)}")

def main(args=None):
    rclpy.init(args=args)
    node = StreamDebugNode()
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
