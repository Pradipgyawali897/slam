import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid, MapMetaData
from geometry_msgs.msg import Pose, Point, Quaternion
from std_msgs.msg import Header
import numpy as np

class Mapper(Node):
    def __init__(self):
        super().__init__('mapper')
        
        # Publishers
        self.map_pub = self.create_publisher(OccupancyGrid, '/map', 10)
        
        # Subscriptions (Future: subscribe to pose/features from processor)
        # self.pose_sub = self.create_subscription(PoseStamped, '/slam/pose', self.pose_callback, 10)
        
        # Map parameters
        self.resolution = 0.05  # 5cm per cell
        self.width = 100        # cells
        self.height = 100       # cells
        self.origin_x = - (self.width * self.resolution) / 2.0
        self.origin_y = - (self.height * self.resolution) / 2.0
        
        # Initialize map data (-1 is unknown)
        self.map_data = np.full((self.height, self.width), -1, dtype=np.int8)
        
        # Timer for map publishing
        self.timer = self.create_timer(1.0, self.publish_map)
        self.get_logger().info("Mapper node initialized. Publishing to /map")

    def publish_map(self):
        msg = OccupancyGrid()
        
        # Header
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'map'
        
        # Info
        msg.info = MapMetaData()
        msg.info.map_load_time = msg.header.stamp
        msg.info.resolution = self.resolution
        msg.info.width = self.width
        msg.info.height = self.height
        
        msg.info.origin = Pose()
        msg.info.origin.position = Point(x=self.origin_x, y=self.origin_y, z=0.0)
        msg.info.origin.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
        
        # Data
        msg.data = self.map_data.flatten().tolist()
        
        self.map_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = Mapper()
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
