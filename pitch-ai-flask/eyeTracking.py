import cv2
import numpy as np
import dlib
import matplotlib
import matplotlib.pyplot as pyplot
import time
import os
import sys
from math import hypot


## Constants ##
REGION_FRACTION_H = 0.4
RIGHT_THRESH = 0.7
LEFT_THRESH = 2
FILE_NAME = 'eyemovement.png'

## Oliver: EDIT this if too slow, frame rate is the increment per second
## For example, a frame rate will evaluate 5 frames per second. (0.5 is 2 fps)
FRAME_RATE = 0.5

# Takes a filename for a video file
# Will generate basic stats for where the user is looking per frame.
# Horizontal and vertical are independently calculated.
# If filename is None, this method uses the webcam/internal laptop camera
# and only records 200 frames before returning (for debugging)
def analyzeEyeMovement(filename):
    cap = cv2.VideoCapture(filename)
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("../data/shape_predictor_68_face_landmarks.dat")
    stats = {'center': [], 'left': [], 'right': []}
    frame_count = 0
    cur_label = ('center', 0.0)
    sec = 0
    cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
    exists, frame = cap.read()
    while exists:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
        for face in faces:
            landmarks = predictor(gray, face)
            left_eye_ratio = get_gaze_ratio(
                [36, 37, 38, 39, 40, 41], landmarks, frame, gray)
            right_eye_ratio = get_gaze_ratio(
                [42, 43, 44, 45, 46, 47], landmarks, frame, gray)
            eye_ratio = (left_eye_ratio + right_eye_ratio) / 2
            next_label = None

            if eye_ratio <= RIGHT_THRESH:
                next_label = 'right'
            elif eye_ratio >= LEFT_THRESH:
                next_label = 'left'
            else:
                next_label = 'center'

            if next_label != cur_label[0]:
                stats[cur_label[0]].append((cur_label[1], timestamp - cur_label[1]))
                cur_label = (next_label, timestamp)

        sec += FRAME_RATE
        cap.set(cv2.CAP_PROP_POS_MSEC, sec * 1000)
        exists, frame = cap.read()

    cap.release()
    save_movement(stats)
    return '/static/images/' + FILE_NAME

def midpoint(p1 ,p2):
    return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)

# Gets a gaze ratio for a particular eye
def get_gaze_ratio(eye_points, facial_landmarks, frame, gray):
    eye_region = np.array([(facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y),
                           (facial_landmarks.part(eye_points[1]).x, facial_landmarks.part(eye_points[1]).y),
                           (facial_landmarks.part(eye_points[2]).x, facial_landmarks.part(eye_points[2]).y),
                           (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y),
                           (facial_landmarks.part(eye_points[4]).x, facial_landmarks.part(eye_points[4]).y),
                           (facial_landmarks.part(eye_points[5]).x, facial_landmarks.part(eye_points[5]).y)], np.int32)

    height, width, _ = frame.shape
    mask = np.zeros((height, width), np.uint8)
    cv2.polylines(mask, [eye_region], True, 255, 2)
    cv2.fillPoly(mask, [eye_region], 255)
    eye = cv2.bitwise_and(gray, gray, mask=mask)

    min_x = np.min(eye_region[:, 0])
    max_x = np.max(eye_region[:, 0])
    min_y = np.min(eye_region[:, 1])
    max_y = np.max(eye_region[:, 1])

    gray_eye = eye[min_y: max_y, min_x: max_x]
    _, threshold_eye = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY)
    height, width = threshold_eye.shape
    left_side_threshold = threshold_eye[0: height, 0: int(width * REGION_FRACTION_H)]
    right_side_threshold = threshold_eye[0: height, int(width * (1 - REGION_FRACTION_H)): width]

    left_side_white = cv2.countNonZero(left_side_threshold)
    right_side_white = cv2.countNonZero(right_side_threshold)

    if left_side_white == 0:
        gaze_ratio = RIGHT_THRESH
    elif right_side_white == 0:
        gaze_ratio = LEFT_THRESH
    else:
        gaze_ratio = (1.0 * left_side_white) / right_side_white

    return gaze_ratio

def save_movement(stats, file_folder='static/images/'):
    font = { 'family': 'Avenir LT Std' }
    label_size = { 'size': 16 }
    xlabel_size = { 'size' : 12 }

    matplotlib.rc('font', **font)
    fig, ax = pyplot.subplots()
    ax.broken_barh(stats['right'], (3, 3), facecolors='#3f47f5')
    ax.broken_barh(stats['center'], (7, 3), facecolors='#b2b5fb')
    ax.broken_barh(stats['left'], (11, 3), facecolors='#3f47f5')

    ax.set_ylim(0, 16)
    ax.set_xlim(0, 30)
    ax.set_xlabel('Seconds since start', **label_size)
    ax.set_xticks([0, 5, 10, 15, 20, 25, 30])
    ax.set_yticks([4.5, 8.5, 12.5])
    ax.set_xticklabels(['0s', '', '', '15s', '', '', '30s'], **xlabel_size)
    ax.set_yticklabels(['Right', 'Center', 'Left'], **label_size)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    ax.spines['bottom'].set_color('#e0e1e2')
    ax.spines['left'].set_color('#e0e1e2')
    ax.tick_params(axis=u'y', which=u'both',length=0)
    ax.xaxis.grid(linestyle='--', color='#e0e1e2')
    pyplot.savefig(file_folder + FILE_NAME)

if __name__ == "__main__":
    EYEMOVEMENT = analyzeEyeMovement(sys.argv[1])