import os
import sys
import json
import argparse
import glob
from pathlib import Path
import time
import google.generativeai as genai
from google.api_core import exceptions

def setup_api_key():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        sys.exit(1)
    genai.configure(api_key=api_key)

def generate_image(prompt, output_path, model_name):
    print(f"Generating: {os.path.basename(output_path)}...")
    try:
        # Use GenerativeModel for gemini-3-pro-image-preview
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        
        # Check for inline data (image)
        image_data = None
        if response.parts:
            for part in response.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    image_data = part.inline_data.data
                    break
        
        if image_data:
            with open(output_path, 'wb') as f:
                f.write(image_data)
            print("  Success")
            return True
        else:
            print("  Failed: No image data in response")
            if response.text:
                print(f"  Response text: {response.text[:100]}...")
            return False

    except Exception as e:
        print(f"  Failed: {e}")
        return False

def process_file(file_path, model_name):
    try:
        with open(file_path, 'r') as f:
            prompts = json.load(f)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return

    # Create output directory based on the filename
    # E.g. docs/images/world/drowned_ruins_images.json -> docs/images/world/drowned_ruins_images/
    filename = os.path.basename(file_path)
    stem = os.path.splitext(filename)[0]
    output_dir = os.path.join(os.path.dirname(file_path), stem)
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Processing {filename} -> {output_dir}/")

    for item in prompts:
        asset_id = item.get('asset_id')
        prompt_text = item.get('image_prompt')
        
        if not asset_id or not prompt_text:
            continue
            
        output_image_path = os.path.join(output_dir, f"{asset_id}.jpeg") # Gemini usually returns JPEG
        
        if os.path.exists(output_image_path):
            print(f"  Skipping {asset_id} (already exists)")
            continue
            
        success = generate_image(prompt_text, output_image_path, model_name)
        if success:
            # Sleep briefly to avoid hitting rate limits too hard
            time.sleep(4) 

def main():
    parser = argparse.ArgumentParser(description="Generate images from JSON prompts using Gemini API.")
    parser.add_argument("path", help="File or directory path containing prompt JSONs")
    parser.add_argument("--model", default="gemini-3-pro-image-preview", help="Model name to use")
    
    args = parser.parse_args()
    
    setup_api_key()
    
    path = Path(args.path)
    if path.is_file():
        process_file(path, args.model)
    elif path.is_dir():
        # Look for .json files
        files = glob.glob(os.path.join(args.path, "*.json"))
        print(f"Found {len(files)} JSON files in {args.path}")
        for f in files:
            process_file(f, args.model)
    else:
        print(f"Invalid path: {path}")

if __name__ == "__main__":
    main()
