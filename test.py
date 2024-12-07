import base64

def image_to_base64(image_path):
    try:
        # Open the image file in binary read mode
        with open(image_path, "rb") as image_file:
            # Encode the image file to base64
            base64_string = base64.b64encode(image_file.read()).decode('utf-8')
        return base64_string
    except Exception as e:
        return f"An error occurred: {e}"

# Example usage
image_path = "pat.jpg"  # Replace with your image path
base64_result = image_to_base64(image_path)
print(base64_result)