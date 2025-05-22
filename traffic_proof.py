# from PIL import Image
# import io
# import binascii
# import json

# def compress_block_to_jpeg_hex(block_img, quality=75, chunk_size_bytes=31):
#     """Compress a 16x16 block using JPEG and return hex representation."""
#     buffer = io.BytesIO()
#     block_img.save(buffer, format='JPEG', quality=quality)
#     jpeg_bytes = buffer.getvalue()
#     hex_data = binascii.hexlify(jpeg_bytes).decode('utf-8')

#     chunk_size = chunk_size_bytes * 2  # 2 hex chars per byte
#     hex_chunks = [hex_data[i:i + chunk_size] for i in range(0, len(hex_data), chunk_size)]
#     return hex_chunks


# def image_to_blockwise_jpeg_hex(image_path, block_size=16, jpeg_quality=75):
#     image = Image.open(image_path).convert("RGB")
#     width, height = image.size

#     # Ensure image dimensions are divisible by block size
#     width -= width % block_size
#     height -= height % block_size
#     image = image.crop((0, 0, width, height))

#     all_blocks_chunks = []

#     for y in range(0, height, block_size):
#         for x in range(0, width, block_size):
#             box = (x, y, x + block_size, y + block_size)
#             block = image.crop(box)
#             hex_data = compress_block_to_jpeg_hex(block, quality=jpeg_quality)
#             all_blocks_chunks.append(hex_data)

#     return all_blocks_chunks

# # Main usage
# if __name__ == "__main__":
#     image_path = "/Users/parisa/Desktop/vimz/marketplace/image-data/img1.png"
#     output_json_path = "jpeg_block_chunks.json"

#     hex_blocks = image_to_blockwise_jpeg_hex(image_path)

#     # Save the list of hex strings to a JSON file
#     with open(output_json_path, "w") as json_file:
#         json.dump(hex_blocks, json_file, indent=2)

#     print(f"Saved {len(hex_blocks)} blocks to {output_json_path}")

from PIL import Image
import io
import binascii
import json

CHUNK_SIZE_BYTES = 31  # 248 bits
CHUNK_SIZE_HEX = CHUNK_SIZE_BYTES * 2  # 62 hex characters
PADDING_CHUNK = "00" * CHUNK_SIZE_BYTES

def compress_block_to_jpeg_hex_chunks(block_img, quality=75):
    """Compress block to JPEG, return list of 62-character hex chunks."""
    buffer = io.BytesIO()
    block_img.save(buffer, format='JPEG', quality=quality)
    jpeg_bytes = buffer.getvalue()
    hex_data = binascii.hexlify(jpeg_bytes).decode('utf-8')

    chunks = [hex_data[i:i + CHUNK_SIZE_HEX] for i in range(0, len(hex_data), CHUNK_SIZE_HEX)]
    
    # Pad the last chunk if it's shorter than expected (optional, can skip if not desired)
    if len(chunks[-1]) < CHUNK_SIZE_HEX:
        chunks[-1] = chunks[-1].ljust(CHUNK_SIZE_HEX, '0')
    
    return chunks

def image_to_uniform_jpeg_hex_chunks(image_path, block_size=16, jpeg_quality=75):
    image = Image.open(image_path).convert("RGB")
    width, height = image.size

    # Crop image to nearest multiple of block size
    width -= width % block_size
    height -= height % block_size
    image = image.crop((0, 0, width, height))

    block_chunks = []

    # Step 1: Collect chunks from all blocks
    for y in range(0, height, block_size):
        for x in range(0, width, block_size):
            box = (x, y, x + block_size, y + block_size)
            block = image.crop(box)
            chunks = compress_block_to_jpeg_hex_chunks(block, quality=jpeg_quality)
            block_chunks.append(chunks)

    # Step 2: Find max chunk length
    max_len = max(len(chunks) for chunks in block_chunks)

    # Step 3: Pad all to equal length
    padded_blocks = [
        chunks + [PADDING_CHUNK] * (max_len - len(chunks))
        for chunks in block_chunks
    ]

    return padded_blocks

# Main usage
if __name__ == "__main__":
    image_path = "/Users/parisa/Desktop/vimz/marketplace/image-data/img1.png"
    output_json_path = "jpeg_block_chunks_padded.json"

    padded_chunked_blocks = image_to_uniform_jpeg_hex_chunks(image_path)

    with open(output_json_path, "w") as f:
        json.dump(padded_chunked_blocks, f, indent=2)

    print(f"Saved {len(padded_chunked_blocks)} blocks to {output_json_path}")

