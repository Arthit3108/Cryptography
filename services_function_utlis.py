import numpy as np
from PIL import Image
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet


current_key_version = "2025-04-25"

load_dotenv()

def get_date(token_string):
    import base64, struct, datetime, ast

    # ใช้ ast เพื่อแปลง b'...' ให้เป็น bytes
    token_bytes = ast.literal_eval(token_string)

    # แก้ padding base64
    padding = 4 - (len(token_bytes) % 4)
    if padding != 4:
        token_bytes += b"=" * padding

    # decode และดึง timestamp
    decoded = base64.urlsafe_b64decode(token_bytes)
    timestamp = struct.unpack(">Q", decoded[1:9])[0]

    return datetime.datetime.fromtimestamp(timestamp).date()


def get_key(version):
    env_var = f"KEY_{version}"
    key = os.getenv(env_var)
    if key:
        return key.encode()
    raise ValueError("not found")


def lfsr_index_generator(seed):
    # Ensure the seed is a 256-bit value
    seed_bin = seed & ((1 << 256) - 1)

    feedback_poly = (
        (1 << 256) | (1 << 241) | (1 << 178) | (1 << 121) | 1
    )

    def lfsr_random(seed_bin):
        while True:
            # Extract the least significant bit (LSB)
            feedback_bit = seed_bin & 1

            # Compute the new state using the feedback polynomial
            if feedback_bit:
                seed_bin ^= feedback_poly

            # Shift the state right by 1 bit
            seed_bin >>= 1

            # Inject the feedback bit into the MSB position
            seed_bin |= (feedback_bit << 255)

            yield seed_bin

    # Return a generator based on the initial seed
    return lfsr_random(seed_bin)

def right_circular_shift(decimal_number, shift_amount, bit_width=8):
    # Create a mask for the given bit width
    mask = (1 << bit_width) - 1

    # Perform the right circular shift using bitwise operations
    result = ((decimal_number >> shift_amount) |
              (decimal_number << (bit_width - shift_amount))) & mask

    return result


def left_circular_shift(decimal_number, shift_amount, bit_width=8):
    # Create a mask for the given bit width
    mask = (1 << bit_width) - 1

    # Perform the left circular shift using bitwise operations
    result = ((decimal_number << shift_amount) |
              (decimal_number >> (bit_width - shift_amount))) & mask

    return result

def divide_into_grid(channel, rows, cols, div):
    # Calculate the base size of each subregion
    row_div = rows // div
    col_div = cols // div

    # Handle leftover rows and columns using the LFSR generator
    leftover_rows = rows % div
    leftover_cols = cols % div

    if leftover_rows > 0:
        row_div += 1  # Assign leftover rows to the last index
    if leftover_cols > 0:
        col_div += 1  # Assign leftover columns to the last index

    # Create the grid
    grid = []
    for i in range(div):
        for j in range(div):
            start_row = i * row_div
            end_row = min((i + 1) * row_div, rows)
            start_col = j * col_div
            end_col = min((j + 1) * col_div, cols)

            grid.append((start_row, end_row, start_col, end_col))

    return grid

def shift_bits_indices(channel, secret_key, rows, cols, channel_idx):
    # Initialize the LFSR generator
    lfsr_gen = lfsr_index_generator(secret_key + channel_idx)
    shift_gen = lfsr_index_generator(secret_key - channel_idx)

    # Divide the channel into a 3x3 grid
    div = 0
    if rows < cols:
      div = cols // 60
    else :
      div = rows // 60
    grid = divide_into_grid(channel, rows, cols, div)

    # Divide the channel into a grid
    grid = divide_into_grid(channel, rows, cols, div)

    # Randomly select indices from the grid using the LFSR generator
    use_indices = (div * div) - 1
    selected_indices = [next(lfsr_gen) % len(grid) for _ in range(use_indices)]
    selected_indices = list(set(selected_indices))  # Ensure unique indices

    # Process each selected index
    for idx in selected_indices:
        start_row, end_row, start_col, end_col = grid[idx]

        # Flatten the subregion
        subregion = channel[start_row:end_row, start_col:end_col].flatten()

        # Determine the shift amount
        shift_amount = next(shift_gen) % 8  # Limit shift amount to [0, 7] for 8-bit pixels

        # Apply the right circular shift to each pixel in the subregion
        subregion = np.array([right_circular_shift(pixel, shift_amount, bit_width=8) for pixel in subregion], dtype=np.uint8)

        # Update the channel
        channel[start_row:end_row, start_col:end_col] = subregion.reshape(end_row - start_row, end_col - start_col)

    return channel


def reverse_shift_bits_indices(channel, secret_key, rows, cols, channel_idx):
    # Initialize the LFSR generator
    lfsr_gen = lfsr_index_generator(secret_key + channel_idx)
    shift_gen = lfsr_index_generator(secret_key - channel_idx)

    # Divide the channel into a 3x3 grid
    div = 0
    if rows < cols:
      div = cols // 60
    else :
      div = rows // 60
    grid = divide_into_grid(channel, rows, cols, div)

    # Divide the channel into a 3x3 grid
    grid = divide_into_grid(channel, rows, cols, div)

    # Randomly select indices from the grid using the LFSR generator
    use_indices = (div * div) - 1
    selected_indices = [next(lfsr_gen) % len(grid) for _ in range(use_indices)]
    selected_indices = list(set(selected_indices))  # Ensure unique indices

    # Process each selected index
    for idx in selected_indices:
        start_row, end_row, start_col, end_col = grid[idx]

        # Flatten the subregion
        subregion = channel[start_row:end_row, start_col:end_col].flatten()

        # Determine the shift amount
        shift_amount = next(shift_gen) % 8

        # Apply the left circular shift to each pixel in the subregion
        subregion = np.array([left_circular_shift(pixel, shift_amount, bit_width=8) for pixel in subregion], dtype=np.uint8)

        # Update the channel
        channel[start_row:end_row, start_col:end_col] = subregion.reshape(end_row - start_row, end_col - start_col)

    return channel

def flip_all_bits(decimal_number):
    # Flip all bits using bitwise NOT
    flipped_number = ~decimal_number & 0xFF

    return flipped_number

# swap and flip in indices with pesudo random
def flip_bits_indices(channel_input, secret_key, rows, cols, channel_idx):
    channel = channel_input.copy()

    # Initialize the LFSR generator
    lfsr_gen = lfsr_index_generator(secret_key + channel_idx)

    # Divide the channel into a 3x3 grid
    div = 0
    if rows < cols:
      div = cols // 30
    else :
      div = rows // 30
    grid = divide_into_grid(channel, rows, cols, div)

    # Randomly select indices from the grid using the LFSR generator
    use_indices = (div * div) - 1
    selected_indices = [next(lfsr_gen) % len(grid) for _ in range(use_indices)]
    selected_indices = list(set(selected_indices))  # Ensure unique indices


    for idx in selected_indices:
        start_row, end_row, start_col, end_col = grid[idx]

        # Flatten the subregion
        subregion = channel[start_row:end_row, start_col:end_col].flatten()

        if len(subregion) == 0:
          continue

        # Perform random swaps
        for _ in range(channel_idx):
            # Generate two random indices within the subregion
            idx1 = next(lfsr_gen) % len(subregion)
            idx2 = next(lfsr_gen) % len(subregion)

            if idx1 % channel_idx == 0 or idx2 % channel_idx == 0:
                subregion = flip_all_bits(subregion)
                # print("after flip : ", subregion)

        # Update the channel with the modified subregion
        channel[start_row:end_row, start_col:end_col] = subregion.reshape(end_row - start_row, end_col - start_col)

    return channel


def xor_all_elements(channel, secret_key):
    rows, cols = channel.shape
    gen = lfsr_index_generator(secret_key - 64)

    # Iterate over all elements in the channel
    for row_idx in range(rows):
        for col_idx in range(cols):
            # Get the current pixel value
            value = int(channel[row_idx, col_idx])

            # Generate a pseudo-random XOR key based on position and secret_key
            gen_value = next(gen)
            xor_key = (secret_key + gen_value) % 256

            # Apply XOR operation
            new_value = value ^ xor_key

            new_value = new_value % 256
            channel[row_idx, col_idx] = np.uint8(new_value)

    return channel

# Encryption Function for Color Images
def encrypt_image(image_file, secret_key, output_image_path):
    # Load image
    image = Image.open(image_file).convert('RGB')
    image_array = np.array(image)
    # Encrypt each channel (R, G, B) separately
    en_channels = []
    shift_channels = []
    flip_channels = []

    channel_idx = 1
    for channel in range(3):  # Process each channel
        channel_data = image_array[:, :, channel]
        rows, cols = channel_data.shape

        flip_image = flip_bits_indices(channel_data, secret_key, rows, cols, channel_idx)
        flip_channels.append(flip_image)
        print("flip : ", flip_image)

        shifted_image = shift_bits_indices(flip_image, secret_key, rows, cols, channel_idx)
        shift_channels.append(shifted_image)
        print("shifted_image : ", shifted_image)

        xor_image = xor_all_elements(shifted_image, secret_key)
        print("xor : ", xor_image)

        # Append the encrypted channel and shuffled indices
        en_channels.append(xor_image)

        channel_idx += 2

    # Step 3: Combine encrypted channels into a single color image
    encrypted_image = np.stack(en_channels, axis=-1)
    encrypted_image_pil = Image.fromarray(encrypted_image)

    if output_image_path:
        encrypted_image_pil.save(output_image_path)

    print("encrypted : ", en_channels)

    return en_channels

# Decryption Function for Color Images
def decrypt_image(encrypted_image_path, secret_key, output_path):
    # Load image
    
    image = Image.open(encrypted_image_path).convert('RGB')  # Convert to RGB
    image_array = np.array(image)

    # Step 2: Decrypt each channel (R, G, B) separately
    decrypted_channels = []

    channel_idx = 1
    for i in range(3):
        channel = image_array[:, :, i]
        rows, cols = channel.shape

        # Step 2: Reverse XOR Operation
        xor_image = xor_all_elements(channel, secret_key)

        unshifted_image = reverse_shift_bits_indices(channel, secret_key, rows, cols, channel_idx)
        print("flip : ", unshifted_image)

        unfliped_image = flip_bits_indices(unshifted_image, secret_key, rows, cols, channel_idx)
        print("unfliped : ", unfliped_image)

        # Append the decrypted channel to the list
        decrypted_channels.append(unfliped_image)
        channel_idx += 2


    print("decrypted_channels : ", decrypted_channels)

    # Step 3: Combine decrypted channels into a single color image
    decrypted_image = np.stack(decrypted_channels, axis=-1)
    decrypted_image_pil = Image.fromarray(decrypted_image)
    decrypted_image_pil.save(output_path)


    return decrypted_channels