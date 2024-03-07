#!/usr/bin/env python3

import lzma
import os
import concurrent.futures

def decompress_xz_file(xz_path):
    try:
        print(f"Decompressing {xz_path}...")
        decompressed_path = xz_path[:-3]
        with lzma.open(xz_path, "rb") as f_in, open(decompressed_path, "wb") as f_out:
            file_content = f_in.read()
            f_out.write(file_content)
        return f"Decompressed: {xz_path} -> {decompressed_path}"
    except Exception as e:
        return f"Error decompressing {xz_path}: {e}"

def decompress_xz_files_concurrently(root_dir, max_workers=4):
    xz_files = []
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".xz"):
                xz_files.append(os.path.join(subdir, file))
    
    # Use ThreadPoolExecutor to decompress files concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_xz = {executor.submit(decompress_xz_file, xz_path): xz_path for xz_path in xz_files}
        for future in concurrent.futures.as_completed(future_to_xz):
            xz_path = future_to_xz[future]
            try:
                result = future.result()
                print(result)
            except Exception as e:
                print(f"Exception for {xz_path}: {e}")

root_directory = "./test/classes"
max_workers = 2*os.cpu_count();

print(f"Decompressing files in {root_directory} using {max_workers} workers...")
decompress_xz_files_concurrently(root_directory, max_workers=max_workers) 
