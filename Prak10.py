import streamlit as st
import cv2
import numpy as np

def binarize_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    return binary

def get_contours(binary):
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def get_freeman_chaincode(contour):
    epsilon = 0.01 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    rect = cv2.minAreaRect(approx)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    chain_code = []
    for i in range(len(box)):
        if i == 0:
            prev_point = box[-1]
        else:
            prev_point = box[i-1]
        curr_point = box[i]
        dx = curr_point[0] - prev_point[0]
        dy = curr_point[1] - prev_point[1]
        if dx == 0:
            if dy > 0:
                chain_code.append(2)
            else:
                chain_code.append(6)
        elif dy == 0:
            if dx > 0:
                chain_code.append(0)
            else:
                chain_code.append(4)
        elif dx > 0:
            if dy > 0:
                chain_code.append(1)
            else:
                chain_code.append(7)
        elif dx < 0:
            if dy > 0:
                chain_code.append(3)
            else:
                chain_code.append(5)
    return chain_code

def get_digit(chain_code):
    digit_codes = {
        '0': [0, 2, 4, 4, 4, 6, 2],
        '1': [4, 4, 4, 6],
        '2': [0, 2, 6, 6, 6, 2],
        '3': [0, 2, 6, 6, 2, 6],
        '4': [0, 4, 6, 4, 4, 6],
        '5': [2, 0, 6, 6, 2, 6],
        '6': [2, 0, 4, 4, 2, 6, 6],
        '7': [0, 2, 6, 4],
        '8': [0, 2, 4, 6, 2, 6, 4],
        '9': [4, 2, 0, 2, 6, 4, 4]
    }
    for digit, code in digit_codes.items():
        if chain_code == code:
            return digit
    return None

def main():
    st.set_page_config(page_title='Digit Recognition', page_icon=':pencil2:')
    st.title('Digit Recognition')

    uploaded_file = st.file_uploader('Upload an image', type=['jpg', 'jpeg', 'png'])

    if uploaded_file is not None:
        image = cv2.imdecode(np.fromstring(uploaded_file.read(), cv2.IMREAD_COLOR))

        binary = binarize_image(image)

        contours = get_contours(binary)

        if len(contours) > 0:
            digit_found = False
            for contour in contours:
                chain_code = get_freeman_chaincode(contour)
                digit = get_digit(chain_code)
                if digit is not None:
                    st.success(f'Digit Found: {digit}')
                    digit_found = True
                    break
            if not digit_found:
                st.warning('No digit found in the image.')
        else:
            st.warning('No contour found in the image.')

if __name__ == '__main__':
    main()
