import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Create the static folder if it doesn't exist
if not os.path.exists('static'):
    os.makedirs('static')

# Load the TensorFlow model (Update the path to your model)
model = tf.saved_model.load('./model/saved_model')
infer = model.signatures['serving_default']

# Label map for sign language gestures
label_map = {
    1: 'Hello',
    2: 'Yes',
    3: 'No',
    4: 'Thank You',
    5: 'I Love You'
}

# Function to run detection
def detectFun(image):
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis, ...]
    output_dict = infer(input_tensor)
    num_detections = int(output_dict['num_detections'][0])
    detection_classes = output_dict['detection_classes'][0][:num_detections].numpy().astype(np.int64)
    detection_boxes = output_dict['detection_boxes'][0][:num_detections].numpy()
    detection_scores = output_dict['detection_scores'][0][:num_detections].numpy()
    return detection_classes, detection_boxes, detection_scores


# Draw bounding boxes and save the image with labels
def draw_boxes(image, boxes, classes, scores, threshold=0.4):
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # Dynamically adjust the font size based on the image size
    font_size = max(60, int(width / 15))
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    for i in range(len(boxes)):
        if scores[i] >= threshold:
            ymin, xmin, ymax, xmax = boxes[i]
            (left, right, top, bottom) = (xmin * width, xmax * width, ymin * height, ymax * height)

            # Draw the bounding box with thicker lines
            draw.rectangle(((left, top), (right, bottom)), outline="green", width=6)

            # Get the label from the label_map
            class_name = label_map.get(classes[i], 'Unknown')

            # Create the label text
            label = f'{class_name}: {scores[i]:.2f}'

            # Compute text size using textbbox()
            text_bbox = draw.textbbox((left, top), label, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]

            # Position the text just above the bounding box
            text_location = (left, top - text_height if top - text_height > 0 else top)

            # Draw a larger rectangle behind the text for better visibility
            draw.rectangle(
                [text_location, (left + text_width, top)],
                fill="green"
            )

            # Add the label text in white on top of the rectangle
            draw.text(text_location, label, fill="white", font=font)

    return image

# Route to handle image upload and run inference
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    # Load the image
    image = Image.open(io.BytesIO(file.read()))

    if image.mode != 'RGB':
        image = image.convert('RGB')

    image_np = np.array(image)

    # Run inference on the image
    detection_classes, detection_boxes, detection_scores = detectFun(image_np)

    # Filter detected labels with confidence score >= 0.5
    confidence_threshold = 0.4
    filtered_labels = [label_map.get(detection_classes[i], 'Unknown')
                       for i in range(len(detection_scores))
                       if detection_scores[i] >= confidence_threshold]

    # Remove duplicates by converting to a set, then back to a list
    filtered_labels = list(set(filtered_labels))

    # Draw bounding boxes on the image
    image_with_boxes = draw_boxes(image, detection_boxes, detection_classes, detection_scores)

    # Save the processed image to the static folder
    processed_image_path = os.path.join('static', 'processed_image.jpg')
    image_with_boxes.save(processed_image_path)

    # Return the processed image URL and filtered labels
    return jsonify({
        "processed_image_url": f'http://localhost:5000/{processed_image_path}',
        "detected_labels": filtered_labels  # Return only filtered labels
    })

if __name__ == '__main__':
    app.run(debug=True)
