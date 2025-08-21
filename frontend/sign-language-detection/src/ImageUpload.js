import React, { useState } from 'react';
import axios from 'axios';

function ImageUpload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [imageUrl, setImageUrl] = useState(null);
  const [processedImageUrl, setProcessedImageUrl] = useState(null);
  const [detectedLabels, setDetectedLabels] = useState([]);  // State to store detected labels
  const [loading, setLoading] = useState(false);

  // Handle file selection

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setImageUrl(URL.createObjectURL(e.target.files[0]));
    setProcessedImageUrl(null);
    setDetectedLabels([]); // Clear the previous detection results
  };

  // Handle image upload
  
  const handleUpload = async () => {
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append('file', selectedFile);
    try {
      setLoading(true);
      // Send the image to the backend
      const response = await axios.post('http://localhost:5000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      // Set the processed image URL and detected labels from the backend response
      setProcessedImageUrl(response.data.processed_image_url);
      setDetectedLabels(response.data.detected_labels);  // Set the detected labels
    } catch (error) {
      console.error("Error uploading image:", error);
    } finally {
      setLoading(false);
    }
  };

  // Clear the selected file and image states
  
  const handleClear = () => {
    setSelectedFile(null);
    setImageUrl(null);
    setProcessedImageUrl(null);
    setDetectedLabels([]);
  };

  return (
    <div>
      <h1>Upload an Image for Sign Language Detection</h1>
      <input
        type="file"
        onChange={handleFileChange}
        key={selectedFile ? selectedFile.name : ''} // Reset input key to allow same file upload
      />
      <br />
      {imageUrl && <img src={imageUrl} alt="Selected" width="400px" />}
      <br />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Processing..." : "Upload Image"}
      </button>
      <button onClick={handleClear} style={{ marginLeft: '10px' }} disabled={loading}>
        Clear
      </button>
      {processedImageUrl && (
        <div>
          <h2>Processed Image:</h2>
          <img src={processedImageUrl} alt="Processed" width="400px" />
          <p style={{ color: 'green', fontSize: '18px', fontWeight: 'bold' }}>
            Detected Labels: {detectedLabels.join(', ')}
          </p>
        </div>
      )}
    </div>
  );
}

export default ImageUpload;
