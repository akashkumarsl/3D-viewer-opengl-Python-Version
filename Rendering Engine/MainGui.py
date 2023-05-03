import glfw
import OpenGL.GL as gl
import numpy as np
from OpenGL.GL import *
from OpenGL.GL import shaders as shader
from OpenGL.GL.shaders import compileProgram, compileShader
from ctypes import c_void_p
from tkinter import filedialog as fd
import os    
import finalData
import imgui
from imgui.integrations.glfw import GlfwRenderer
from glfw import _GLFWwindow as GLFWwindow
from CameraClass import Camera, Camera_Movement
from glfw.GLFW import *
import glm
from TextureLoader import load_texture
import cv2
import mediapipe as mp
import math
import time
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
cap = cv2.VideoCapture(0)


albedocheck=False
metalcheck=False
speccheck=False
roughcheck=False
aocheck=False
first=0
def material_edit():
    global first
    imgui.set_next_window_size(300,400)
    imgui.set_next_window_position(0,600)
    imgui.begin("Material Edit",flags=imgui.WINDOW_MENU_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_ALWAYS_VERTICAL_SCROLLBAR)
    global albedocheck,metalcheck,speccheck,roughcheck,aocheck

    extra,albedocheck=imgui.checkbox("Albedo",albedocheck)
    extra,metalcheck=imgui.checkbox("Metallic",metalcheck)
    extra,speccheck=imgui.checkbox("Specular",speccheck)
    extra,roughcheck=imgui.checkbox("Roughness",roughcheck)
    extra,aocheck=imgui.checkbox("AO",aocheck)

    imgui.end()


# For webcam input Zoom:

def zoomreg():
    
    distance= 0
    with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
        success, image = cap.read()
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
               
                x2, y2 = int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * image.shape[1]), int(hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * image.shape[0])
                x3, y3 = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image.shape[1]), int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image.shape[0])

                distance = math.sqrt((x2 - x3)**2 + (y2 - y3)**2)

    return distance
    

# For webcam input:
def faceReg():
    with mp_face_detection.FaceDetection(
      model_selection=0, min_detection_confidence=0.5) as face_detection:
        
        success, image = cap.read()

        results = face_detection.process(image)
        try:
            if len(results.detections)==1 :
                detection=results.detections[0]
                x=1-(detection.location_data.relative_bounding_box.xmin + (detection.location_data.relative_bounding_box.width/2))
                y=1-(detection.location_data.relative_bounding_box.ymin + (detection.location_data.relative_bounding_box.height/2))
                Nx=(2 * x) -1
                Ny=(2 * y) -1
            else:
                Nx=FaceX
                Ny=FaceY
        except:
            Nx=FaceX
            Ny=FaceY

    return Nx,Ny

lightstate= True
def light_pos():    
    #Setting the size and position of the window for light position and light color and accept values for shininess in imgui
    imgui.set_next_window_size(300,500)
    imgui.set_next_window_position(1600, 600)
    imgui.begin("Light Position")
    global lightstate,lightpos,lightcolor,shininess
    _,lightstate=imgui.checkbox("Light",lightstate)
    lightstate=int(lightstate)
    imgui.text("Light Position")
    _,lightpos[0]=imgui.slider_float("X",lightpos[0],-500,500,format="%.3f",power=1.0)
    _,lightpos[1]=imgui.slider_float("Y",lightpos[1],-500,500,format="%.3f",power=1.0)
    _,lightpos[2]=imgui.slider_float("Z",lightpos[2],-500,500,format="%.3f",power=1.0)   
    imgui.text("Light Color")
    _,lightcolor[0]=imgui.slider_float("R",lightcolor[0],0,1,format="%.3f",power=1.0)
    _,lightcolor[1]=imgui.slider_float("G",lightcolor[1],0,1,format="%.3f",power=1.0)
    _,lightcolor[2]=imgui.slider_float("B",lightcolor[2],0,1,format="%.3f",power=1.0)
    imgui.text("Shininess")
    #Also make sure it is integer
    _,shininess=imgui.slider_int("Shininess",shininess,32,1000,format="%d") 
    imgui.end()

#Create a imgui menu bar and pass array of check box
def side_bar(instanceContainer):
    #Setting the size and position of the window
    # imgui.set_window_font_scale(45.0)
    imgui.set_next_window_size(width * 0.15, height * 0.5)
    imgui.set_next_window_position(width * 0.85, 0)

    #Menu bar constraints and flags for the window 
    imgui.begin("File Properties",flags=imgui.WINDOW_MENU_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_ALWAYS_VERTICAL_SCROLLBAR)
    
    #Creating a menu bar of tree nodes
    for array in instanceContainer:
        if imgui.tree_node(array.Path, imgui.TREE_NODE_DEFAULT_OPEN):

            #Creating a check box for each mesh in the scene and storing the state of the checkbox in the array of checkbox 
            for count,name in enumerate(array.Mesh):# enumerate returns the index and the value of the array
                #imgui checkbox returns the state of the checkbox and the name of the checkbox
                #parameter 1: name of the checkbox 
                #parameter 2: state of the checkbox
                changed,show_checkbox=imgui.checkbox(name[1],array.checkbox[count])
                array.checkbox[count]=show_checkbox
            #Creating a separator between the tree nodes
            imgui.separator()
            imgui.tree_pop()
    imgui.end()

def openFile():  

    # opening a file using the askopenfilename() method of the filedialog module
    # the filedialog module is imported, tkinter library is imported as fd
    #the file has path
    the_file = fd.askopenfilename(  
        title = "Select a file of any type",  
        filetypes = [("All files", "*.*"),("Text files", "*.txt"),("OBJ files", "*.obj"),("FBX files", "*.fbx"),("image files", "*.png"),("image files", "*.jpg"),("image files", "*.jpeg")]  
        )    
    # the file has path, we return the file path
    return the_file


def main():
    # Setup window
    imgui.create_context()
    #Scale all imgui windows
    imgui.get_io().font_global_scale = 1.5
    #Set the Font style and size of the imgui windows 
    imgui.get_io().fonts.add_font_from_file_ttf("C:\\Windows\\Fonts\\arial.ttf", 15.0)
   
    window_name = "Rendering Engine"
    if not glfw.init():
        print("Could not initialize OpenGL context")
        exit(1)

    # Decide GL+GLSL versions and create window with graphics context (GLF
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)

    # Get Window data from primary monitor and set it as window size
    MyMonitor =  glfw.get_primary_monitor()
    # Get the current video mode of the monitor as a GLFWvidmode class instance
    mode = glfw.get_video_mode(MyMonitor)
    # Get the resolution of the monitor   
    global width,height,lastX,lastY,flagmat
    width=mode.size.width
    height=mode.size.height

    print(width,height)
    # Set the mouse position at the center of the screen
    lastX =  width/ 2.0
    lastY = height / 2.0
    flagmat=0

    # Create a windowed mode window and its OpenGL context    
    window = glfw.create_window(
        int(width), int(height), window_name, None, None
      )
    glfw.make_context_current(window)

    # Pass the window to imgui.GLFW object to process the inputs
    impl = GlfwRenderer(window)

    #import the vs.txt and fs.txt files of 
    vertex_src = open("vs.txt", "r").read()
    fragment_src = open("fs.fs", "r").read()

    vertex_srcAABB = open("aabbvs.txt", "r").read()
    fragment_shaderAABB = open("aabbfs.txt", "r").read()

    #Compile the shaders and create a shader program 
    newShader=compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))
    AABBshader=compileProgram(compileShader(vertex_srcAABB, GL_VERTEX_SHADER), compileShader(fragment_shaderAABB, GL_FRAGMENT_SHADER))

    # Flag1 to check if the object is loaded or not 
    flag1=0
    # openGL state settings for background color and depth testing
    glClearColor(0.1, 0.1, 0.1, 1.0)  
    glEnable(GL_DEPTH_TEST)
    # initialize the frame count and the last time for fps calculation
    last_time = glfw.get_time()
    frame_count = 0
    fps = 0.0

    # Set Wireframe mode flag 
    StateWireFrame=False
    StateAABB=False
    # imgui.same_line(spacing=width * 0.1)

    global threshold,prev_distance,FaceX,FaceY,lightpos,lightcolor,shininess, instanceContainer,sensitive,enablesense,pres,textureID
    textureID= load_texture("defaultgrey.jpg")
    sensitive=3
    threshold = 0.2  # 30% 
    prev_distance = 0
    pres=1
    FaceX,FaceY = 0,0
    lightpos= [0,0,0]
    lightcolor=[1,1,1]
    shininess=32
    instanceContainer=[]
    enablesense=False
    glClearColor(0.2,0.2,0.2,1)
    #While loop to keep the window open and process the draw calls
    while not glfw.window_should_close(window):
        # process the inputs for wasd camera movement and esc to close the window
        processInput(window)

        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # font_size = 18
        # font_path = "D:\Downloads\pixelletters-font"
        # io = imgui.get_io()
        # io.fonts.add_font_from_file_ttf(font_path, size_pixels=font_size)
        # io.font_global_scale = 2.0

        # impl is the imgui.GLFW object to process the inputs
        impl.process_inputs()
        # Start the new frame
        imgui.new_frame()
        
        # Create a menu bar and pass the array of checkbox
        if imgui.begin_main_menu_bar():
       
            if imgui.begin_menu("File", True):
        
                if imgui.begin_menu("LOAD"):
                    
                    obj, selected_quit = imgui.menu_item("obj", None, True, True)
                    if obj:
                        # Open the file dialog and get the file path
                        file=openFile()
                        if len(file)!=0:# file is a string type with path
                            
                            # Create an instance of the class LoadOBJECT and pass the file path
                            instance=finalData.LoadOBJECT(file)
                            instance.Loadfile()
                            instance.LoadMesh()
                            instance.SendData()
                            instance.GenerateAABB_VAO()
                            
                            instanceContainer.append(instance)
                            # Create a camera object and pass the position of the object
                            global camera
                            camera=Camera(0,0,100)
                            flag1=1
                            
                    imgui.end_menu()
                imgui.separator()
                
                # Quit button/esc to close the window
                _,clickedquit=imgui.menu_item("Quit","esc",False,True)
                if clickedquit:
                    exit(1)
                imgui.end_menu() 
            
            imgui.same_line(spacing=25)
            if imgui.begin_menu('Views',True):
                _,StateAABB=imgui.checkbox('AABB',StateAABB)
                imgui.separator()
                _,StateWireFrame=imgui.checkbox('WireFrame',StateWireFrame)
                imgui.separator()
                imgui.end_menu()

            # Texture menu to import the image by calling the openfile function to get the file path
            imgui.same_line(spacing=25)
            if imgui.begin_menu("Texture",True):
                _,clickedTEXTURE=imgui.menu_item("Import image",None,False,True)
                if clickedTEXTURE:
                    textureID=load_texture(openFile())
                imgui.end_menu()

            # same line to keep the menu bar in one line and add a spacing between the menu bar and the next menu
            # imgui.set_next_window_size(width * 0.15, height * 0.5)
            # imgui.same_line(spacing=width * 0.6)

            imgui.same_line(spacing=25)
            if imgui.begin_menu('Spatial Reality',True):
                _,enablesense=imgui.checkbox('Enable',enablesense)
                imgui.separator()
                _,sensitive=imgui.slider_float("sensitivity to move",sensitive,1,4,format="%.1f",power=1.0)
                imgui.separator()
                _,pres=imgui.slider_float("Precision",pres,1,10,format="%0.0f",power=1.0)
                imgui.end_menu()

            imgui.same_line(spacing=25)
            if imgui.begin_menu('Help',True):
                imgui.text("Press 'esc' to quit")
                imgui.text("Press 'w' to move upward")
                imgui.text("Press 's' to move Downward")
                imgui.text("Press 'a' to move left")
                imgui.text("Press 'd' to move right")
                imgui.text("Press 'q' to move Forward")
                imgui.text("Press 'e' to move Backward")
                imgui.text("Press 'up,left,' to rotate in x,y axis")
                imgui.text("Press 'down,right' to rotate in x,y axis in reverse")
                imgui.text("Press 'u' to scale uniformly")
                imgui.text("Press 'shift+u' to scale uniformly in reverse")
                imgui.text("Press 'x,y,z' to scale in x,y,z axis")
                imgui.text("Press 'shift+x,y,z' to scale in x,y,z axis in reverse")
                imgui.text("Press 'i&k' to move the camera in +z and -z axis")
                imgui.text("Press 'j&l' to move the camera in +x and -x axis")
                imgui.text("Press 'o&p' to Zoom in and out")          
                imgui.text("Press 'alt' to activate the Pinch to Zoom feature")    
                imgui.end_menu()
            imgui.end_main_menu_bar()# end the main menu bar 
        light_pos()
        material_edit()
        # object shader program to draw the object
        if flag1==1:
            side_bar(instanceContainer)
            glUseProgram(newShader)
            #pass the light position,ligh color and the object color,view pos, to the shader
            glUniform3f(glGetUniformLocation(newShader, "lightColor"), lightcolor[0], lightcolor[1], lightcolor[2])
            glUniform3f(glGetUniformLocation(newShader, "lightPos"), lightpos[0], lightpos[1], lightpos[2])
            glUniform3f(glGetUniformLocation(newShader, "viewPos"), camera.Position.x, camera.Position.y, camera.Position.z)
            glUniform1i(glGetUniformLocation(newShader, "lightState"), lightstate)
            glUniform1i(glGetUniformLocation(newShader, "shininess"), shininess)
          
            
#-----------------------Camera controls--------------------------------------------#
            if flagmat==0:
                model = glm.mat4(1.0)
                model = glm.rotate(model, glm.radians(20.0), glm.vec3(1.0, 0.3, 0.5))
                glUniformMatrix4fv(glGetUniformLocation(newShader, "model"), 1, GL_FALSE, glm.value_ptr(model))

            # pass projection matrix to shader (note that in this case it could change every frame)
            projection = glm.perspective(glm.radians(camera.Zoom), width/ height, 0.1, 10000.0)
            glUniformMatrix4fv(glGetUniformLocation(newShader, "projection"), 1, GL_FALSE, glm.value_ptr(projection))

            # camera/view transformation
            view = camera.GetViewMatrix()
            glUniformMatrix4fv(glGetUniformLocation(newShader, "view"), 1, GL_FALSE, glm.value_ptr(view))

            #Translate the object and pass it to model matrix along the x,y,z axis upon I,J,K key press
            if imgui.get_io().keys_down[GLFW_KEY_D]:
                model = glm.translate(model, glm.vec3(0.01, 0.0, 0.0))
                flagmat=1
            if imgui.get_io().keys_down[GLFW_KEY_W]:
                model = glm.translate(model, glm.vec3(0.0, 0.01, 0.0))
                flagmat=1

            if imgui.get_io().keys_down[GLFW_KEY_S]:
                model = glm.translate(model, glm.vec3(0.0, -0.01, 0.0))
                flagmat=1
            
            if imgui.get_io().keys_down[GLFW_KEY_A]:
                model = glm.translate(model, glm.vec3(-0.01, 0.0, 0.0))
                flagmat=1

            if imgui.get_io().keys_down[GLFW_KEY_Q]:
                model = glm.translate(model, glm.vec3(0.0, 0.0, 0.01))
                flagmat=1
            
            if imgui.get_io().keys_down[GLFW_KEY_E]:
                model = glm.translate(model, glm.vec3(0.0, 0.0, -0.01))
                flagmat=1              
                           
            #Rotate the object and pass it to model matrix along the x,y,z axis upon arrow key press
            if imgui.get_io().keys_down[GLFW_KEY_UP]:
                model = glm.rotate(model, glm.radians(1.0), glm.vec3(1.0, 0.0, 0.0))
                flagmat=1

            if imgui.get_io().keys_down[GLFW_KEY_DOWN]:
                model = glm.rotate(model, glm.radians(1.0), glm.vec3(-1.0, 0.0, 0.0))
                flagmat=1

            if imgui.get_io().keys_down[GLFW_KEY_LEFT]:
                model = glm.rotate(model, glm.radians(1.0), glm.vec3(0.0, 1.0, 0.0))
                flagmat=1         

            if imgui.get_io().keys_down[GLFW_KEY_RIGHT]:
                model = glm.rotate(model, glm.radians(1.0), glm.vec3(0.0, -1.0, 0.0))
                flagmat=1

            #Rotate the object and pass it to model matrix along the Z axis
            if imgui.get_io().keys_down[GLFW_KEY_COMMA]:
                model = glm.rotate(model, glm.radians(1.0), glm.vec3(0.0, 0.0, 1.0))
                flagmat=1

            if imgui.get_io().keys_down[GLFW_KEY_PERIOD]:
                model = glm.rotate(model, glm.radians(1.0), glm.vec3(0.0, 0.0, -1.0))
                flagmat=1

            #Scale along all axis
            if not imgui.get_io().keys_down[GLFW_KEY_LEFT_SHIFT]:
                if imgui.get_io().keys_down[GLFW_KEY_U]:
                    model = glm.scale(model, glm.vec3(1.01, 1.01, 1.01))
                    flagmat=1

            #Scale along all axis in reverse upon shift key press with u
            if imgui.get_io().keys_down[GLFW_KEY_LEFT_SHIFT]:
                if imgui.get_io().keys_down[GLFW_KEY_U]:
                    model = glm.scale(model, glm.vec3(0.99, 0.99, 0.99))
                    flagmat=1

            #Scale the object and pass it to model matrix along the x,y,z axis upon key press
            if not imgui.get_io().keys_down[GLFW_KEY_LEFT_SHIFT]:
                if imgui.get_io().keys_down[GLFW_KEY_X]:
                    model = glm.scale(model, glm.vec3(1.01, 1.0, 1.0))
                    
                    flagmat=1
                if imgui.get_io().keys_down[GLFW_KEY_Y]:
                    model = glm.scale(model, glm.vec3(1.0, 1.01, 1.0))
                    
                    flagmat=1
                if imgui.get_io().keys_down[GLFW_KEY_Z]:
                    model = glm.scale(model, glm.vec3(1.0, 1.0, 1.01))
                    flagmat=1

            #Scale back the object and pass it to model matrix along the x,y,z axis upon shift key press with x,y,z
            if imgui.get_io().keys_down[GLFW_KEY_LEFT_SHIFT]:
                if imgui.get_io().keys_down[GLFW_KEY_X]:
                    model = glm.scale(model, glm.vec3(0.99, 1.0, 1.0))
                    flagmat=1

                if imgui.get_io().keys_down[GLFW_KEY_Y]:
                    model = glm.scale(model, glm.vec3(1.0, 0.99, 1.0))
                    flagmat=1
                
                if imgui.get_io().keys_down[GLFW_KEY_Z]:
                    model = glm.scale(model, glm.vec3(1.0, 1.0, 0.99))
                    flagmat=1

            glUniformMatrix4fv(glGetUniformLocation(newShader, "model"), 1, GL_FALSE, glm.value_ptr(model))

            #Activate mouse movement only when the mouse ctrl key is pressed
            if imgui.get_io().keys_down[GLFW_KEY_LEFT_CONTROL]:

                #pass the x and y position to the camera class upon mouse movement
                mouse_x, mouse_y = imgui.get_io().mouse_pos
                xoffset = mouse_x - lastX
                yoffset = lastY - mouse_y

                #update the last x and y position
                lastX = mouse_x 
                lastY = mouse_y

                #call the mouse movement function only after the mouse has moved
                if xoffset != 0 or yoffset != 0:
                    camera.ProcessMouseMovement(xoffset, yoffset)

            #call the zoom function only after the o or p key has been pressed
            if imgui.get_io().keys_down[GLFW_KEY_O]:
                camera.ProcessMouseScroll(1)
            if imgui.get_io().keys_down[GLFW_KEY_P]:
                camera.ProcessMouseScroll(-1) 

            
            if glfw.get_key(window, glfw.KEY_TAB) == glfw.PRESS or enablesense:                                                                             
                FaceX1,FaceY1=faceReg()
                # FaceX,FaceY=FaceX * sensitive,FaceY * sensitive
                deltaChangeX=FaceX-FaceX1
                deltaChangey=FaceY-FaceY1
                if abs(deltaChangeX)>(0.01/pres) or abs(deltaChangey)>(0.01/pres):
                    FaceX=FaceX1
                    FaceY=FaceY1
                    model = glm.rotate(model, glm.radians(deltaChangeX * 45*sensitive), glm.vec3(0, 1, 0))
                    model = glm.rotate(model, glm.radians(-deltaChangey * 45*sensitive), glm.vec3(1, 0, 0))
                    glUniformMatrix4fv(glGetUniformLocation(newShader, "model"), 1, GL_FALSE, glm.value_ptr(model))
                    flagmat=1

            
            if glfw.get_key(window, glfw.KEY_LEFT_ALT):
      
                curr_distance = zoomreg()
                
                #If the distance is greater than the previous distance then zoom in

                if abs(curr_distance - prev_distance) > prev_distance * threshold:
                    # If the change in distance is significant, print whether the user is zooming in or out and reset the cooldown timer
                    if curr_distance > prev_distance:
                        #perform zoom in using the camera class
                        camera.ProcessMouseScroll(50)
                       
                    else:
                        #perform zoom out using the camera class
                        camera.ProcessMouseScroll(-100)

                    prev_distance = curr_distance # Update the previous distance to the current distance

#--------------------------Camera Control Ends Here--------------------------------------------#
            #VAO has VBO and EBO and AABB and Index data
            #So we use enumerate to get the index
            #index is the index of the VAO
            #i is the VAO
            #instance.checkbox[index] is the checkbox value

            for instance in instanceContainer:                  
                for index,i in enumerate(instance.VAOs):
                    if instance.checkbox[index]:
                        glBindVertexArray(i['VAO'])
                        if StateWireFrame:
                            glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
                        else:
                            glPolygonMode( GL_FRONT_AND_BACK, GL_FILL )
                        glDrawElements(GL_TRIANGLES, len(i['Index']), GL_UNSIGNED_INT, None)
                        glBindVertexArray(0)

            if StateAABB:
                #Shader for AABB
                glUseProgram(AABBshader)
                glUniformMatrix4fv(glGetUniformLocation(AABBshader, "model"), 1, GL_FALSE, glm.value_ptr(model))
                glUniformMatrix4fv(glGetUniformLocation(AABBshader, "view"), 1, GL_FALSE, glm.value_ptr(view))
                glUniformMatrix4fv(glGetUniformLocation(AABBshader, "projection"), 1, GL_FALSE, glm.value_ptr(projection))
                #Get the AABB VAO from the instance class and draw it by getting the each VAO/mesh
                for instance in instanceContainer:
                    aabb=instance.AABB_VAO
                    for VAO in aabb:
                        glBindVertexArray(VAO)
                        glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
                        glDrawElements(GL_TRIANGLES,36, GL_UNSIGNED_INT, None)
                        glBindVertexArray(0)
        
        imgui.render()# It renders the UI only after the main loop is done

        # Fps counter code starts here    
        global delta_time # It is the time between the current frame and the last frame in seconds used in the camera class

        current_time = glfw.get_time()
        delta_time = current_time - last_time
        frame_count += 1
        if delta_time >= 1.0:
            fps = frame_count / delta_time
            frame_count = 0
            last_time = current_time
        
        # Update the window title with the frame rate
            glfw.set_window_title(window,f"Rendering Engine - FPS: {fps:.2f}")

        impl.render(imgui.get_draw_data()) # It renders the draw data of the glfw window
        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()

def processInput(window: GLFWwindow) -> None:

    if (glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS):
        glfwSetWindowShouldClose(window, True)

    if (glfwGetKey(window, GLFW_KEY_I) == GLFW_PRESS):
        camera.ProcessKeyboard(Camera_Movement.FORWARD, delta_time)
    if (glfwGetKey(window, GLFW_KEY_K) == GLFW_PRESS):
        camera.ProcessKeyboard(Camera_Movement.BACKWARD, delta_time)
    if (glfwGetKey(window, GLFW_KEY_J) == GLFW_PRESS):
        camera.ProcessKeyboard(Camera_Movement.LEFT, delta_time)
    if (glfwGetKey(window, GLFW_KEY_L) == GLFW_PRESS):
        camera.ProcessKeyboard(Camera_Movement.RIGHT, delta_time)

if __name__ == "__main__":
    main()