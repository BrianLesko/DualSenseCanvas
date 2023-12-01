# By Brian Lesko , 11/28/2023
# This python script implements a simple sketchpad using a dualsense touchpad, conneceted via USB C. 

import io # used for the image download
import time # used for the sleep function
import numpy as np # used for the image and array making
import streamlit as st # used for the GUI
import matplotlib.pyplot as plt # used for saving the image

import dualsense # Custom class by Brian Lesko for Wired DualSense controller communication
import customize_gui # Custom class by Brian Lesko for streamlit GUI modifications
gui = customize_gui.gui()
DualSense = dualsense.DualSense

vendorID = int("0x054C", 16)
productID = int("0x0CE6", 16)

def dualSenseCanvas():
    st.set_page_config(layout='wide')
    gui.clean_format()
    gui.about(text = "This code implements a simple sketchpad using a dualsense touchpad.")
    Title = st.empty()
    ds = DualSense(vendorID,productID)
    ds.connect()
    progress_bar = st.progress(0)
    text = st.empty()
    image_placeholder = st.empty()
    n = 1080-10 # y is 1100 - 10 
    m = 1900-30 # x is 40 - 1900
    pixels = np.ones((n,m))
    loops = 900
    pixel_size = 10
    for i in range(loops): 
        ds.receive()
        ds.updateTouchpad(n=1)
        y, x = ds.touchpad_x[0], ds.touchpad_y[0]
        y1, x1 = ds.touchpad1_x[0], ds.touchpad1_y[0]
        # first touch detection and pixel drawing
        if ds.touchpad_isActive:
            if 0 <= x < n and 0 <= y < m:  # Check that the touchpad values are within the image dimensions
                for dx in range(-pixel_size//2 + 1, pixel_size//2 + 1):
                    for dy in range(-pixel_size//2 + 1, pixel_size//2 + 1):
                        if 0 <= x + dx < n and 0 <= y + dy < m:  # Check that the coordinates are within the image dimensions
                            pixels[x + dx][y + dy] = max(0, pixels[x + dx][y + dy] - 1)  # Subtract 1 from the pixel value, but don't go below 0
        # second finger touch detection and pixel drawing
        if ds.touchpad1_isActive:
            if 0 <= x1 < n and 0 <= y1 < m:
                for dx in range(-pixel_size//2 + 1, pixel_size//2 + 1):
                    for dy in range(-pixel_size//2 + 1, pixel_size//2 + 1):
                        if 0 <= x1 + dx < n and 0 <= y1 + dy < m:
                            pixels[x1 + dx][y1 + dy] = max(0, pixels[x1 + dx][y1 + dy] - 1)
        progress_bar.progress((i + 1)/loops)
        with image_placeholder: st.image(pixels, use_column_width=True)
        time.sleep(.00005)
        progress_bar.progress((i + 1)/loops)
    with Title: st.title("Your Artwork is finished")
    st.balloons()
    # Download your image
    buffer = io.BytesIO()
    plt.imsave(buffer, pixels, cmap='gray', format='png')
    with st.sidebar: 
        st.write("")
        "---"
        st.write("")
        col1, col2, col3 = st.columns([1,1,1])
        with col2: 
            st.subheader("Download")
            st.download_button(
            label="as png",
            data=buffer.getvalue(),
            file_name='my_artwork.png',
            mime='image/png',
            )
        st.write("")
        "---"
    ds.disconnect()

dualSenseCanvas()