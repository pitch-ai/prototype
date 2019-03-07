import cv2
import numpy as np
import dlib
import matplotlib.pyplot as pyplot
import matplotlib.patches as patches
from math import hypot


## Constants ##
# May need to edit these as needed depending on our demo
REGION_FRACTION_H = 0.4
REGION_FRACTION_V = 0.45
RIGHT_THRESH = 0.7
LEFT_THRESH = 2
TOP_THRESH = 0.05
BOTTOM_THRESH = 0.5
USER_FRAME_TEST = 200

# Takes a filename for a video file
# Will generate basic stats for where the user is looking per frame.
# Horizontal and vertical are independently calculated.
# If filename is None, this method uses the webcam/internal laptop camera
# and only records 200 frames before returning (for debugging)
def analyzeEyeMovement(filename):
    if not filename:
        filename = 0

    cap = cv2.VideoCapture(filename)
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor("../data/shape_predictor_68_face_landmarks.dat")
    stats = {'center_h': 0, 'center_v': 0, 'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
    frame_count = 0
    displayFrame = None
    while cap.isOpened() or filename == 0:
        _, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray)
        for face in faces:
            landmarks = predictor(gray, face)
            gzl_h, gzl_v = get_gaze_ratio(
                [36, 37, 38, 39, 40, 41], landmarks, frame, gray)
            gzr_h, gzr_v = get_gaze_ratio(
                [42, 43, 44, 45, 46, 47], landmarks, frame, gray)
            gz_h = (gzl_h + gzr_h) / 2
            gz_v = (gzl_v + gzr_v) / 2
            if gz_h <= RIGHT_THRESH:
                stats['right'] += 1
            elif gz_h >= LEFT_THRESH:
                stats['left'] += 1
            else:
                stats['center_h'] += 1

            if gz_v <= TOP_THRESH:
                stats['top'] += 1
            elif gz_v >= BOTTOM_THRESH:
                stats['bottom'] += 1
            else:
                stats['center_v'] += 1

        if frame_count >= USER_FRAME_TEST and filename == 0:
            print 'Exiting...'
            displayFrame = frame
            break

        frame_count += 1

        cv2.imshow("Feed", frame)
        key = cv2.waitKey(1)

    cap.release()
    stats['top'] /= (1.0 * frame_count)
    stats['bottom'] /= (1.0 * frame_count)
    stats['left'] /= (1.0 * frame_count)
    stats['right'] /= (1.0 * frame_count)
    print stats
    height, width, _ = displayFrame.shape
    fig, ax = pyplot.subplots(1)
    im2 = displayFrame.copy()
    im2[:, :, 0] = displayFrame[:, :, 2]
    im2[:, :, 2] = displayFrame[:, :, 0]
    ax.imshow(im2)
    # Right
    ax.add_patch(patches.Rectangle((0, 0), width / 6, height,
        linewidth=1, edgecolor='r', facecolor='r', alpha=stats['right']))
    # Left
    ax.add_patch(patches.Rectangle((5 * width / 6, 0), width / 6, height,
        linewidth=1, edgecolor='r', facecolor='r', alpha=stats['left']))
    # Bottom
    ax.add_patch(patches.Rectangle((width / 6, 5 * height / 6), 4 * width / 6, height / 6,
        linewidth=1, edgecolor='r', facecolor='r', alpha=stats['bottom']))
    # Top
    ax.add_patch(patches.Rectangle((width / 6, 0), 4 * width / 6, height / 6,
        linewidth=1, edgecolor='r', facecolor='r', alpha=stats['top']))
    pyplot.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    pyplot.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
    pyplot.show()

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
    top_side_threshold = threshold_eye[0: int(height * REGION_FRACTION_V), 0: width]
    bottom_side_threshold = threshold_eye[int(height * (1 - REGION_FRACTION_V)): height, 0: width]

    left_side_white = cv2.countNonZero(left_side_threshold)
    right_side_white = cv2.countNonZero(right_side_threshold)
    top_side_white = cv2.countNonZero(top_side_threshold)
    bottom_side_white = cv2.countNonZero(bottom_side_threshold)

    if left_side_white == 0:
        gaze_ratio_h = RIGHT_THRESH
    elif right_side_white == 0:
        gaze_ratio_h = LEFT_THRESH
    else:
        gaze_ratio_h = (1.0 * left_side_white) / right_side_white

    if top_side_white == 0:
        gaze_ratio_v = TOP_THRESH
    elif bottom_side_white == 0:
        gaze_ratio_v = BOTTOM_THRESH
    else:
        gaze_ratio_v = (1.0 * top_side_white) / bottom_side_white

    return gaze_ratio_h, gaze_ratio_v

if __name__ == '__main__':
    analyzeEyeMovement(None)