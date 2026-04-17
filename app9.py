#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 25 22:52:39 2024

@author: mac
"""

import json
import os
import random
import re
import tempfile
from dotenv import load_dotenv,find_dotenv,load_dotenv
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image, ImageColor, ImageDraw, ImageFont
from fpdf import FPDF
import base64




def call_llm(img:Image, prompt: str)->str:
    system_prompt="""
    
    """
    dotenv_path=find_dotenv()
    load_dotenv(dotenv_path)
    my_google_key=os.getenv("GOOGLE_API_KEY")

    client=genai.Client(api_key=my_google_key)
    response=client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[prompt, img],
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.5,
            safety_settings=[
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_ONLY_HIGH",
                    ),
                ],
            
            ),
        
    )
    print("Response from LLM",response)
    return response.text

def parse_json(json_input: str)->str:
    match=re.search(r"```json\n(.*?)```",json_input, re.DOTALL)
    json_input=match.group(1) if match else ""
    return json_input
def plot_bounding_boxes(img: Image, bounding_boxes: str) -> Image:
    width, height = img.size
    colors = [colorname for colorname in ImageColor.colormap.keys()]
    draw = ImageDraw.Draw(img)

    bounding_boxes = parse_json(bounding_boxes)

    for bounding_box in json.loads(bounding_boxes):
        color = random.choice(colors)

        # Convert normalized coordinates to absolute coordinates
        abs_y1 = int(bounding_box["box_2d"][0] / 1000 * height)
        abs_x1 = int(bounding_box["box_2d"][1] / 1000 * width)
        abs_y2 = int(bounding_box["box_2d"][2] / 1000 * height)
        abs_x2 = int(bounding_box["box_2d"][3] / 1000 * width)

        if abs_x1 > abs_x2:
            abs_x1, abs_x2 = abs_x2, abs_x1

        if abs_y1 > abs_y2:
            abs_y1, abs_y2 = abs_y2, abs_y1

        print(
            f"Absolute Co-ordinates: {bounding_box['label']}, {abs_y1}, {abs_x1},{abs_y2}, {abs_x2}",
        )

        draw.rectangle(((abs_x1, abs_y1), (abs_x2, abs_y2)), outline=color, width=4)

        # Draw label
        draw.text(
            (abs_x1 + 8, abs_y1 + 6),
            bounding_box["label"],
            fill=color,
            font=ImageFont.truetype(
                "Arial.ttf",
                # "path/to/your/font.ttf",
                size=14,
            ),
        )

    return img
def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'




if __name__ == "__main__":
    st.set_page_config(page_title="DeepGaze an insight into your Image")
    st.header("DeepGaze an insight into your Image")
    prompt = st.text_input("Ask what is your Query        ")
    run = st.button("Run!")

    with st.sidebar:
        uploaded_image = st.file_uploader(
            accept_multiple_files=False,
            label="Upload your photo here:",
            type=["jpg", "jpeg", "png"],
        )

        if uploaded_image:
            with st.expander("View the image"):
                st.image(uploaded_image)

    if uploaded_image and run and prompt:
        temp_file = tempfile.NamedTemporaryFile(
            "wb", suffix=f".{uploaded_image.type.split('/')[1]}", delete=False
        )
        temp_file.write(uploaded_image.getbuffer())
        image_path = temp_file.name

        img = Image.open(image_path)
        width, height = img.size
        resized_image = img.resize(
            (1024, int(1024 * height / width)), Image.Resampling.LANCZOS
        )
        os.unlink(image_path)
        print(
            f"Image Original Size: {img.size} | Resized Image size: {resized_image.size}"
        )

        with st.spinner("Running..."):
            response = call_llm(resized_image, prompt)
            #plotted_image = plot_bounding_boxes(resized_image, response)
            st.write(response) 
        

            #report_text = response
           
            #if report_text:
            #    pdf = FPDF()
            #    pdf.add_page()
            #    pdf.set_font('Arial', 'B', 12)
                #pdf.cell(40, 10, report_text)
                
                #pdf.cell(600, 200*2, border=1,align='L', link=pdf.image(resized_image, x=50, y=100, w=300, h=200))
            #    pdf.multi_cell(0, 5, report_text, 0, 1)



            
            

    
            #html = create_download_link(pdf.output(dest="S").encode("latin-1"), "test")

            #st.markdown(html, unsafe_allow_html=True)