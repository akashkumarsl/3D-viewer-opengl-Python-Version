from enum import Enum

from OpenGL.GL import *

import glm


# Defines several possible options for camera movement. Used as abstraction to stay away from window-system specific input methods
class Camera_Movement:
    FORWARD = 1
    BACKWARD = 2
    LEFT = 3
    RIGHT = 4

# Default camera values
YAW         = -90.0
PITCH       =  0.0
SPEED       =  1
SENSITIVITY =  0.1
ZOOM        =  45.0

# An abstract camera class that processes input and calculates the corresponding Euler Angles, Vectors and Matrices for use in OpenGL
class Camera:

    def __init__(self, posX=0.0, posY=0.0, posZ=0.0, upX=0.0, upY=1.0, upZ=0.0, yaw=YAW, pitch=PITCH):
        self.Position = glm.vec3(posX, posY, posZ)
        self.WorldUp = glm.vec3(upX, upY, upZ)
        self.Yaw = yaw
        self.Pitch = pitch

        self.Front = glm.vec3(0.0, 0.0, -1.0)
        self.Up = glm.vec3(0.0, 1.0, 0.0)
        self.Right = glm.vec3(1.0, 0.0, 0.0)
        self.MovementSpeed = SPEED
        self.MouseSensitivity = SENSITIVITY
        self.Zoom = ZOOM

        self.updateCameraVectors()

    # returns the view matrix calculated using Euler Angles and the LookAt Matrix
    def GetViewMatrix(self):
        # The * operator is used to unpack the components of the self.Position vector into separate arguments.
        return glm.lookAt(self.Position, self.Position + self.Front, self.Up)

    # processes input received from any keyboard-like input system. Accepts input parameter in the form of camera defined ENUM (to abstract it from windowing systems)
    def ProcessKeyboard(self, direction, deltaTime):
        velocity = self.MovementSpeed * deltaTime
        if (direction == Camera_Movement.FORWARD):
            for i in range(3):
                self.Position[i] += self.Front[i] * velocity
        if (direction == Camera_Movement.BACKWARD):
            for i in range(3):
                self.Position[i] -= self.Front[i] * velocity
        if (direction == Camera_Movement.LEFT):
            for i in range(3):
                self.Position[i] -= self.Right[i] * velocity
        if (direction == Camera_Movement.RIGHT):
            for i in range(3):
                self.Position[i] += self.Right[i] * velocity

    # processes input received from a mouse input system. Expects the offset value in both the x and y direction.
    def ProcessMouseMovement(self, xoffset, yoffset, constrainPitch=True):
        xoffset *= self.MouseSensitivity
        yoffset *= self.MouseSensitivity

        self.Yaw   += xoffset
        self.Pitch += yoffset

        # make sure that when pitch is out of bounds, screen doesn't get flipped
        if (constrainPitch):
            if (self.Pitch > 89.0):
                self.Pitch = 89.0
            if (self.Pitch < -89.0):
                self.Pitch = -89.0

        # update Front, Right and Up Vectors using the updated Euler angles
        self.updateCameraVectors()

    # processes input received from a mouse scroll-wheel event. Only requires input on the vertical wheel
    def ProcessMouseScroll(self, yoffset):
        self.Zoom -= yoffset
        if (self.Zoom <= 1.0):
            self.Zoom = 1.0
        if (self.Zoom >= 45.0):
            self.Zoom = 45.0

    # calculates the front vector from the Camera's (updated) Euler Angles
    def updateCameraVectors(self) -> None:
        # calculate the new Front vector
        front = glm.vec3()
        front.x = glm.cos(glm.radians(self.Yaw)) * glm.cos(glm.radians(self.Pitch))
        front.y = glm.sin(glm.radians(self.Pitch))
        front.z = glm.sin(glm.radians(self.Yaw)) * glm.cos(glm.radians(self.Pitch))
        self.Front = glm.normalize(front)
        # also re-calculate the Right and Up vector
        self.Right = glm.normalize(glm.cross(self.Front, self.WorldUp))  
        self.Up    = glm.normalize(glm.cross(self.Right, self.Front)) 
