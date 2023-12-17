from PIL import Image
import numpy as np

message_binary = ""
message_length_binary_char = []
secret_message_binary = []

def message_binary_format(message):
    global message_binary
    # message is converted to 8-bit binary
    message_binary = ''.join(format(ord(c), '016b') for c in message)

    # to maintain error from pass length, we have to add (extra 0 or 00)
    if len(message_binary) % 3 == 2:
        message_binary += "0"
    elif len(message_binary) % 3 == 1:
        message_binary += "00"

    return list(message_binary)

def message_length_binary_format(number):
    binary = format(number, '030b')
    return list(binary)

def hide_message(message, stego_file_name, cover_file_name):
    global message_length_binary_char, secret_message_binary
    message_length_binary_char = message_length_binary_format(len(message))
    secret_message_binary = message_binary_format(message)

    # we have to hide the length to the 1st 10 pixels
    bit_no = 0
    bit_no_s = 0
    cover_image = np.array(Image.open(cover_file_name))

    for x in range(cover_image.shape[0]):
        for y in range(cover_image.shape[1]):
            pixel = cover_image[x, y]

            red = format(pixel[0], '08b')
            green = format(pixel[1], '08b')
            blue = format(pixel[2], '08b')

            if x == 0 and y < 10:
                new_red = int(red[:-1] + message_length_binary_char[bit_no], 2)
                new_green = int(green[:-1] + message_length_binary_char[bit_no + 1], 2)
                new_blue = int(blue[:-1] + message_length_binary_char[bit_no + 2], 2)

                bit_no += 3

                cover_image[x, y] = [new_red, new_green, new_blue]
            else:
                if bit_no_s < len(secret_message_binary):
                    new_red = int(red[:-1] + secret_message_binary[bit_no_s], 2)
                    new_green = int(green[:-1] + secret_message_binary[bit_no_s + 1], 2)
                    new_blue = int(blue[:-1] + secret_message_binary[bit_no_s + 2], 2)

                    bit_no_s += 3

                    cover_image[x, y] = [new_red, new_green, new_blue]

    Image.fromarray(cover_image.astype(np.uint8)).save(stego_file_name)

    return "Success"

def secret_bit_meta_data(img, x, y):
    pixel = img[x, y]
    red = format(pixel[0], '08b')
    green = format(pixel[1], '08b')
    blue = format(pixel[2], '08b')
    return red[-1] + green[-1] + blue[-1]

def extract_secret_message(stego_file_name):
    global secret_real_message
    frame_no_binary = ""
    secret_message = []

    cover_image = np.array(Image.open(stego_file_name))
    frame_n, length_of_msg_bit = 0, 0
    only_one = 0

    for x in range(cover_image.shape[0]):
        for y in range(cover_image.shape[1]):
            if x == 0 and y < 10:
                s = secret_bit_meta_data(cover_image, x, y)
                frame_no_binary += s
            else:
                if only_one == 0:
                    frame_n = int(frame_no_binary, 2)
                    length_of_msg_bit = 0

                    if (frame_n * 16) % 3 == 2:
                        length_of_msg_bit += 1
                    elif (frame_n * 16) % 3 == 1:
                        length_of_msg_bit += 2

                    length_of_msg_bit += frame_n * 16
                    only_one = 1

                if len(secret_message) <= length_of_msg_bit:
                    s = secret_bit_meta_data(cover_image, x, y)
                    secret_message.append(s)
                else:
                    break

    secret_message_binary = ''.join(secret_message)[:-4]
    bit_8 = ""
    aa = 0
    secret_real_message = ""

    for i in range(len(secret_message_binary)):
        if aa != 16:
            bit_8 += secret_message_binary[i]
            aa += 1
        if aa == 16:
            acii = int(bit_8, 2)
            secret_real_message += chr(acii) if 32 <= acii <= 126 else ' '
            bit_8 = ""
            aa = 0

    return secret_real_message

def check_validation(cover_file, stego_file):
    try:
        mse_gray = 0.0
        mse = 0.0
        psnr = 0.0

        cover_image = np.array(Image.open(cover_file))
        stego_image = np.array(Image.open(stego_file))

        for i in range(cover_image.shape[0]):
            for j in range(cover_image.shape[1]):
                gray1 = cover_image[i, j][0]
                gray2 = stego_image[i, j][0]

                # gray1 is numpy array of bytes
                gray1 = gray1.astype(np.int16)
                gray2 = gray2.astype(np.int16)

                # calculate the MSE
                mse_gray += (gray1 - gray2) ** 2

        mse = mse_gray / (cover_image.shape[0] * cover_image.shape[1]) * 3
        psnr = 10 * np.log10((255 ** 2) / mse)

        validation = f"MSE: {mse}\nPSNR: {psnr}\n"

        return validation
    except Exception as ex:
        return f"Error: {str(ex)}"