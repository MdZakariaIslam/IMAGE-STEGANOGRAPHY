import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from dotenv import load_dotenv
import os
from encryptionDecryption import encrypt_text, decrypt_text
from proposedAlgorithm import hide_message, extract_secret_message, check_validation

load_dotenv()

def create_image(left, top, im, box, image_path):
    # create a new image that has the size of the each part
    new_image = Image.new('RGB', (int(left), int(top)))
    # save the 4 parts into the each corner of the new image
    new_image.paste(im, box)
    # save the new image
    new_image.save(image_path)


def image_to_4_parts(image_path):
    # devide the image into 4 parts
    imagedata = Image.open(image_path)
    width, height = imagedata.size

    # calculate the coordinates of the 4 parts
    left = width / 2
    top = height / 2

    # crop the image into 4 parts
    top_left = imagedata.crop((0, 0, left, top))
    top_right = imagedata.crop((left, 0, width, top))
    bottom_left = imagedata.crop((0, top, left, height))
    bottom_right = imagedata.crop((left, top, width, height))

    # save the 4 parts into 4 images
    create_image(left, top, top_left, (0, 0), "new_image_top_left.png")
    create_image(left, top, top_right, (0, 0), "new_image_top_right.png")
    create_image(left, top, bottom_left, (0, 0), "new_image_bottom_left.png")
    create_image(left, top, bottom_right, (0, 0), "new_image_bottom_right.png")

    # return the size of the each part
    return left, top, width, height


def encrypt():
    validation.configure(text="")
    # get the text from the text input
    text_input = text.get("1.0", tk.END)
    # get the image path from the entry input
    image_path = entry.get()

    # check if the text input is empty
    if text_input == "\n":
        # show error message box
        tk.messagebox.showerror(title="Error", message="Please enter a text")
        return
    elif image_path == "":
        # show error message box
        tk.messagebox.showerror(
            title="Error", message="Please select an image")
        return

    # remove the new line character from the text
    text_input = text_input.replace("\n", "")
    # remove the last character if it is a space
    if text_input[-1] == " ":
        text_input = text_input[:-1]

    # get the encryption key from the .env file
    encryption_key = os.getenv("DES_KEY")
    # Encrypt the text
    encrypted_text = encrypt_text(text_input, encryption_key)
    if encrypted_text == "Invalid":
        tk.messagebox.showerror(title="Error", message="Invalid key")
        return ""
    # encode the image
    encode_image(image_path, encrypted_text)


def decrypt():
    validation.configure(text="")
    # get the image path from the entry input
    image_path = entry.get()

    # check if the image path is empty
    if image_path == "":
        # show error message box
        tk.messagebox.showerror(
            title="Error", message="Please select an image")
        return

    # get the encryption key from the .env file
    encryption_key = os.getenv("DES_KEY")
    # encode the image
    message = decode_image(image_path, encryption_key)
    # show the message in the text input
    text.delete("1.0", tk.END)
    text.insert("1.0", message)


def decode_image(image_path, encryption_key):
    # devide the image into 4 parts
    left, top, width, height = image_to_4_parts(image_path)

    # decode the message in the top left image
    message_top_left = extract_secret_message("new_image_top_left.png")
    # decode the message in the top right image
    message_top_right = extract_secret_message("new_image_top_right.png")
    # decode the message in the bottom left image
    message_bottom_left = extract_secret_message("new_image_bottom_left.png")
    # decode the message in the bottom right image
    message_bottom_right = extract_secret_message("new_image_bottom_right.png")

    # encripted message
    encrypted_text = message_top_left + message_top_right + \
        message_bottom_left + message_bottom_right

    message = decrypt_text(encrypted_text, encryption_key)

    # show the message in the message box
    if (message == "Invalid"):
        tk.messagebox.showerror(title="Error", message="Invalid key")
        return ""

    # delete the 4 images
    os.remove("new_image_top_left.png")
    os.remove("new_image_top_right.png")
    os.remove("new_image_bottom_left.png")
    os.remove("new_image_bottom_right.png")

    # return the message
    return message


def encode_image(image_path, encrypted_text):
    # calculate the size of the text
    encrypted_text_size = len(encrypted_text)
    # devide the text into 4 parts
    encrypted_text_part_size = encrypted_text_size / 4
    # convert the size to integer
    encrypted_text_part_size = int(encrypted_text_part_size)
    # now we have 4 parts of the text
    encrypted_text_part_one = encrypted_text[:encrypted_text_part_size]
    encrypted_text_part_two = encrypted_text[encrypted_text_part_size:encrypted_text_part_size * 2]
    encrypted_text_part_three = encrypted_text[encrypted_text_part_size *
                                               2:encrypted_text_part_size * 3]
    encrypted_text_part_four = encrypted_text[encrypted_text_part_size * 3:]

    # devide the image into 4 parts
    left, top, width, height = image_to_4_parts(image_path)

    # hide the message in the top left image
    hide_message(encrypted_text_part_one,
                 "stego_new_image_top_left.png", "new_image_top_left.png")
    # hide the message in the top right image
    hide_message(encrypted_text_part_two,
                 "stego_new_image_top_right.png", "new_image_top_right.png")
    # hide the message in the bottom left image
    hide_message(encrypted_text_part_three,
                 "stego_new_image_bottom_left.png", "new_image_bottom_left.png")
    # hide the message in the bottom right image
    hide_message(encrypted_text_part_four,
                 "stego_new_image_bottom_right.png", "new_image_bottom_right.png")

    # combine the 4 images into one
    # create a new image that has the size of the each part
    new_image = Image.new('RGB', (int(width), int(height)))
    # save the 4 parts into the each corner of the new image
    new_image.paste(im=Image.open("stego_new_image_top_left.png"), box=(0, 0))
    new_image.paste(im=Image.open(
        "stego_new_image_top_right.png"), box=(int(left), 0))
    new_image.paste(im=Image.open(
        "stego_new_image_bottom_left.png"), box=(0, int(top)))
    new_image.paste(im=Image.open(
        "stego_new_image_bottom_right.png"), box=(int(left), int(top)))
    # save the new image
    new_image.save("new_image.png")

    # show the new image
    load_image("new_image.png")

    # delete the 8 images
    os.remove("stego_new_image_top_left.png")
    os.remove("stego_new_image_top_right.png")
    os.remove("stego_new_image_bottom_left.png")
    os.remove("stego_new_image_bottom_right.png")

    os.remove("new_image_top_left.png")
    os.remove("new_image_top_right.png")
    os.remove("new_image_bottom_left.png")
    os.remove("new_image_bottom_right.png")

    valid = check_validation(image_path, "new_image.png")
    validation.configure(text="" + str(valid))

def image_input():
    # open file dialog
    file_path = filedialog.askopenfilename(
        title="Browse PNG File", filetypes=[("Image file", "*.png")])
    if file_path:
        # show path in entry
        entry.delete(0, tk.END)
        entry.insert(0, file_path)
        load_image(file_path)


def load_image(file_path):
    if file_path:
        img = Image.open(file_path)
        # get the image size
        width, height = img.size
        # resize the image to fit in the window
        retio = width / height
        if width > 300:
            width = 300
            height = int(width / retio)
            if height > 300:
                height = 300
                width = int(height * retio)

        if height > 300:
            height = 300
            width = int(height * retio)

        img = img.resize((width, height))
        photo = ImageTk.PhotoImage(img)

        image_label.configure(image=photo)
        image_label.image = photo  # keep a reference


# Create the main window
root = tk.Tk()
root.title("Image Steganography")
# Set the window size
root.geometry("400x450")


frame = tk.Frame(root)
# frame.grid(row=0, column=0)
frame.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X, expand=tk.YES, anchor=tk.N)

# image input entry
entry = tk.Entry(frame)
entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=tk.YES, anchor=tk.N)

# Button to browse for an image
btn_browse = tk.Button(frame, text="Browse", command=image_input)
btn_browse.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, anchor=tk.N)

image_label = tk.Label(root)
image_label.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.N)
# image_label add a image
load_image("demo.png")
# fix the size of the image label
# image_label.configure(width=300, height=300)

frame2 = tk.Frame(root)
# frame2.grid(row=1, column=0)
frame2.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X, expand=tk.YES, anchor=tk.N)

# input text
text = tk.Text(frame2, height=5)
text.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=tk.YES, anchor=tk.N)

# validation
validation = tk.Label(root, text=" ")
validation.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=tk.YES, anchor=tk.N)

# Button to encode the image
btn_encode = tk.Button(root, text="Encode", command=encrypt)
btn_encode.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, anchor=tk.N)

btn_decode = tk.Button(root, text="Decode", command=decrypt)
btn_decode.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, anchor=tk.N)


# Start the Tkinter event loop
root.mainloop()
