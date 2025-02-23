import os
import torch
import requests
import json
import threading
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from io import BytesIO

# ComfyUI Server Configuration
COMFYUI_API_URL = "http://127.0.0.1:8188/prompt"

# GUI Setup
window = ctk.CTk()
window.geometry("600x700")
window.title("ComfyUI Stable Diffusion Generator")

ctk.CTkLabel(window, text="Enter Prompt:", font=("Arial", 14)).pack(pady=5)

prompt_entry = ctk.CTkEntry(window, width=500)
prompt_entry.pack(pady=5)

ctk.CTkLabel(window, text="Guidance Scale:").pack()
guidance_scale = ctk.CTkSlider(window, from_=1, to=20, number_of_steps=19)
guidance_scale.set(7.5)
guidance_scale.pack()

ctk.CTkLabel(window, text="Number of Inference Steps:").pack()
steps_slider = ctk.CTkSlider(window, from_=5, to=30, number_of_steps=25)
steps_slider.set(15)
steps_slider.pack()

status_label = ctk.CTkLabel(window, text="", font=("Arial", 12))
status_label.pack(pady=10)

image_label = ctk.CTkLabel(window, text="Generated Image Will Appear Here")
image_label.pack(pady=10)

def check_server():
    try:
        response = requests.get("http://127.0.0.1:8188", timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        return False

def generate_image():
    def run_generation():
        if not check_server():
            status_label.configure(text="ComfyUI server not running!", text_color="red")
            return
        
        prompt = prompt_entry.get()
        if not prompt:
            status_label.configure(text="Please enter a prompt!", text_color="red")
            return
        
        status_label.configure(text="Generating image... Please wait.", text_color="blue")
        window.update_idletasks()
        
        payload = {
            "prompt": prompt,
            "steps": int(steps_slider.get()),
            "cfg": float(guidance_scale.get())
        }
        
        try:
            response = requests.post(COMFYUI_API_URL, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            
            if "image" in result:
                image_data = BytesIO(bytes.fromhex(result["image"]))
            else:
                status_label.configure(text="Error: No image in response", text_color="red")
                return
            
            image = Image.open(image_data)
            image.save("generated_image.png")
            
            img = ImageTk.PhotoImage(image.resize((300, 300)))
            image_label.configure(image=img)
            image_label.image = img
            status_label.configure(text="Image generated successfully!", text_color="green")
        except requests.ConnectionError:
            status_label.configure(text="Connection Error: Unable to reach ComfyUI server", text_color="red")
        except requests.Timeout:
            status_label.configure(text="Error: Server took too long to respond", text_color="red")
        except requests.RequestException as e:
            status_label.configure(text=f"Request Error: {str(e)}", text_color="red")
    
    threading.Thread(target=run_generation, daemon=True).start()

generate_button = ctk.CTkButton(window, text="Generate Image", command=generate_image)
generate_button.pack(pady=10)

window.mainloop()