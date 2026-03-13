# Sugam 


## CV Tasks (Assigned to Sugam)
- [ ] **[CV]** Implement `process_cv` in `fetcher.py`
    - **Path**: `src/esp32_cam_slam/esp32_cam_slam/fetcher.py`
    - **Goal**: Decode the raw JPEG bytes into an OpenCV image.
    - **Parameter**: `image_data` (The raw bytes received from the ESP32-CAM stream).
    - **Command**: `cv_image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)`
    - **Return**: Assign the result to `cv_image` to be used for future processing (e.g., ORB, display).

## ROS & SLAM Tasks
- [ ] **[ROS]** Publish decoded images to a ROS 2 `Image` topic
- [ ] **[ROS]** Implement Camera Info publisher with calibration parameters
- [ ] **[SLAM]** Feature extraction using ORB or FAST
- [ ] **[SLAM]** Feature matching and tracking between frames
- [ ] **[SLAM]** Implement Visual Odometry (VO) pipeline
- [ ] **[SLAM]** Loop closure detection and global map optimization
