# Sugam 

## CV Tasks (Assigned to Sugam)
- [ ] **[CV]** Implement `process_cv` in `processor.py`
    - **Path**: `src/esp32_cam_slam/esp32_cam_slam/processor.py`
    - **Goal**: Implement SLAM core (Feature extraction, tracking, VO estimation).
    - **Note**: The `fetcher` node now handles the HTTP stream and image publishing. Your node subscribes to `/camera/image_raw`.
    - **Input**: The `process_cv` function receives an OpenCV `cv_image`.

## System Tasks (General)
- [x] Refactor SLAM into Modular Architecture (Fetcher, Processor, Mapper)
- [ ] **[ROS]** Connect `processor` output to `mapper` input
- [ ] **[ROS]** Add `launch` file to start all nodes (Fetcher, Processor, Mapper)
- [ ] **[Rviz]** Setup Rviz2 visualization for Features and Map

## SLAM Pipeline
- [ ] Feature extraction using ORB or FAST
- [ ] Feature matching and tracking between frames
- [ ] Implement Visual Odometry (VO) pipeline
- [ ] Loop closure detection and global map optimization
