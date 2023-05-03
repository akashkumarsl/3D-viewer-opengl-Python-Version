# 3D-viewer-opengl-Python-Version

This is a 3D viewer application that uses OpenGL and Python to render 3D models and textures. 
Additionally, lighting effects can be added to the model to enhance the viewing experience.
It also supports hand and face recognition to control the camera and zoom.


## Dependencies

To run this application, you need to install the following Python packages:

- glfw
- PyOpenGL
- PyAssimp
- numpy
- tkinter
- finalData
- imgui
- glm
- cv2
- mediapipe

## Usage

To start the application, run the MainGui.py file.
A window will open where you can select a 3D model file and a texture file. 
If no texture file is specified, a default texture will be loaded.

You can use the mouse and keyboard to move the camera around the scene.
You can also use your face and hand gestures to control the camera and zoom. 
The application uses mediapipe to detect your face and hand landmarks and map them to the camera parameters.

To move the camera forward or backward, tilt your head up or down. To move the camera left or right, turn your head left or right. 
To zoom in or out, pinch your thumb and index finger together or apart.


## Debug View

You can enable the wireframe debug and AABB view by using checkbox.
This will display the wireframe of the 3D model  
The AABB helps to visualize the boundaries of the model and can be useful for debugging purposes.
