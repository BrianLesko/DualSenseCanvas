# By Brian Lesko , 11/28/2023
# These examples demonstrate how to use my DualSense class in a streamlit app. 
# Run one of these examples by downloading this file, calling the example function you want to test out by adding a line at the end, and running it with streamlit run examples.py
# Also make sure to plug in your controller and find its vendor and productID.

import dualsense
import streamlit as st
import time
import numpy as np
import customize_gui
gui = customize_gui.gui()
DualSense = dualsense.DualSense

vendorID = int("0x054C", 16)
productID = int("0x0CE6", 16)

def streamlit_IMU_Example():
    gui.clean_format()
    gui.about(text = "Hey it's Brian. This code implements a Dualsense USB connection and updates the gyrometer and accelerometer values. Make sure to plug in a dualsense and find its vendor and productID")
    # run the streamlit app 
    # This app's downfall is that it is not interactive, it just updates the display based on the controller input
    my_dualsense = DualSense(vendorID,productID)
    my_dualsense.connect()
    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        Title = st.empty()
        placeholder = st.empty()
        placeholder2 = st.empty()
    progress_bar = st.progress(0)
    for i in range(1000):  # Adjust the range as needed
        my_dualsense.receive()
        my_dualsense.updateGyrometer(n=100)
        round = -1
        placeholder.write(f"The Gyrometer Readings: {np.round(np.mean(my_dualsense.Pitch), round)}, {np.round(np.mean(my_dualsense.Yaw), round)}, {np.round(np.mean(my_dualsense.Roll), round)}")
        my_dualsense.updateAccelerometer(n=100)
        placeholder2.write(f"The Accelerometer Readings: {np.round(np.mean(my_dualsense.X), round)}, {np.round(np.mean(my_dualsense.Y), round)}, {np.round(np.mean(my_dualsense.Z), round)}")
        time.sleep(.03)  # Adjust the sleep time as needed
        progress_bar.progress((i + 1)/1000)
    with Title: st.header("The Controller loop is finished")
    my_dualsense.disconnect()

def streamlit_trigger_Example():
    # run the streamlit app 
    # This app's downfall is that it is not interactive, it just updates the display based on the controller input
    my_dualsense = DualSense(vendorID,productID)
    my_dualsense.connect()
    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        Title = st.empty()
        placeholder = st.empty()
    progress_bar = st.progress(0)
    for i in range(1000):  # Adjust the range as needed
        my_dualsense.receive()
        my_dualsense.updateTriggers()
        placeholder.write(f"The Trigger Readings: {my_dualsense.L1}, {my_dualsense.L2}, {my_dualsense.R1}, {my_dualsense.R2}")
        fast = 0.02
        slow = 1
        time.sleep(fast)  # Adjust the sleep time as needed
        progress_bar.progress((i + 1)/1000)
    with Title: st.header("The Controller loop is finished")
    my_dualsense.disconnect()

import pandas as pd

def streamlit_Update_All_Example():
    gui.clean_format()
    gui.about(text = "Hey it's Brian. This code implements a Dualsense USB connection and updates all the controller values. Make sure to plug in a dualsense and find its vendor and productID")
    # receive data, and put all the data into a dataframe
    ds = DualSense(vendorID,productID)
    ds.connect()
    col1,col2,col3 = st.columns([1,2,1])
    with col2:
        Title = st.empty()
        placeholder = st.empty()
    progress_bar = st.progress(0)

    # Initialize the previous DataFrame
    df_prev = pd.DataFrame()

    for i in range(1000):  # Adjust the range as needed
        ds.receive()
        ds.updateAll()
        df = pd.DataFrame({
            'Dpad': [str([ds.DpadUp, ds.DpadRight, ds.DpadDown, ds.DpadLeft])],
            'Thumbsticks': [str([ds.LX, ds.LY, ds.RX, ds.RY])],
            'Touchpad': [str([ds.touchpad_x, ds.touchpad_y, ds.touchpad1_x, ds.touchpad1_y])],
            'Buttons': [str([ds.triangle, ds.circle, ds.cross, ds.square])],
            'Triggers': [str([ds.L1, ds.L2, ds.L2btn, ds.R1, ds.R2, ds.R2btn])],
            'Accelerometer': [str([ds.X, ds.Y, ds.Z])],
            'Gyrometer': [str([ds.Roll, ds.Pitch, ds.Yaw])]
        }) #, index=[i])
        # Highlight the cells where the value has changed
        def highlight_changes(data):
            attr = 'background-color: {}'.format('#90ee90')  # Light green
            other = '' 
            condition = data.ne(df_prev.T)  # Compare with the transposed previous DataFrame
            # Adjust the condition for the 'Accelerometer' and 'Gyrometer' rows
            if 'Accelerometer' in data.index and 'Accelerometer' in df_prev.T.index:
                current_values = np.array(eval(data.loc['Accelerometer'][0]))
                prev_values = np.array(eval(df_prev.T.loc['Accelerometer'][0]))
                condition.loc['Accelerometer'] = np.linalg.norm(current_values - prev_values) > 600
            if 'Gyrometer' in data.index and 'Gyrometer' in df_prev.T.index:
                current_values = np.array(eval(data.loc['Gyrometer'][0]))
                prev_values = np.array(eval(df_prev.T.loc['Gyrometer'][0]))
                condition.loc['Gyrometer'] = np.linalg.norm(current_values - prev_values) > 800
            if 'Thumbsticks' in data.index and 'Thumbsticks' in df_prev.T.index:
                current_values = np.array(eval(data.loc['Thumbsticks'][0]))
                prev_values = np.array(eval(df_prev.T.loc['Thumbsticks'][0]))
                condition.loc['Thumbsticks'] = np.linalg.norm(current_values - prev_values) > 5

            df1 = pd.DataFrame(np.where(condition, attr, other), index=data.index, columns=data.columns)
            return df1

        styled = df.T.style.apply(highlight_changes, axis=None)  # Transpose the DataFrame before applying the style

        with placeholder: st.dataframe(styled)
        time.sleep(.1)  # Adjust the sleep time as needed
        progress_bar.progress((i + 1)/1000)

        # Update the previous DataFrame
        df_prev = df.copy()

    with Title: st.header("The Controller loop is finished")
    ds.disconnect()

import numpy 
import io
import matplotlib.pyplot as plt

def streamlit_draw_example():
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
    loops = 1000
    pixel_size = 30 
    for i in range(loops): 
        ds.receive()
        ds.updateTouchpad(n=1)
        y, x = ds.touchpad_x[0], ds.touchpad_y[0]
        y1, x1 = ds.touchpad1_x[0], ds.touchpad1_y[0]
        if ds.touchpad_isActive:
            if 0 <= x < n and 0 <= y < m:  # Check that the touchpad values are within the image dimensions
                for dx in range(-pixel_size//2 + 1, pixel_size//2 + 1):
                    for dy in range(-pixel_size//2 + 1, pixel_size//2 + 1):
                        if 0 <= x + dx < n and 0 <= y + dy < m:  # Check that the coordinates are within the image dimensions
                            pixels[x + dx][y + dy] = max(0, pixels[x + dx][y + dy] - 1)  # Subtract 1 from the pixel value, but don't go below 0
        if ds.touchpad1_isActive:
            if 0 <= x1 < n and 0 <= y1 < m:
                for dx in range(-pixel_size//2 + 1, pixel_size//2 + 1):
                    for dy in range(-pixel_size//2 + 1, pixel_size//2 + 1):
                        if 0 <= x1 + dx < n and 0 <= y1 + dy < m:
                            pixels[x1 + dx][y1 + dy] = max(0, pixels[x1 + dx][y1 + dy] - 1)
        progress_bar.progress((i + 1)/loops)
        with image_placeholder: st.image(pixels, use_column_width=True)
        time.sleep(.0001)
        progress_bar.progress((i + 1)/loops)
    with Title: st.title("Your Artwork is finished")
    
    # Download your image
    buffer = io.BytesIO()
    plt.imsave(buffer, pixels, cmap='gray', format='png')
    with st.sidebar: 
        st.write("")
        "---"
        st.write("")
        st.subheader("Download your art")
        st.write("")
        col1, col2, col3 = st.columns([1,3,1])
        with col2: st.download_button(
            label="download as png",
            data=buffer.getvalue(),
            file_name='my_artwork.png',
            mime='image/png',
        )
        st.write("")
        st.write("")  
        "---"
        
    ds.disconnect()

streamlit_draw_example()