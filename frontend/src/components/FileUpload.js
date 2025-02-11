import React, { useState } from 'react';
import axios from 'axios';
console.log("API URL:", process.env.REACT_APP_API_URL);

const FileUpload = () => {
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);//handles the loading state of the file upload
    const [processing, setProcessing] = useState(false);// handles the loading state of the file pending processing

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile && selectedFile.type === "application/pdf") {
            setFile(selectedFile);
            setMessage("");
        } else {
            setMessage("Please select a valid PDF file.");
            setFile(null);
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setMessage("No file selected.");
            return;
        }

        const formData = new FormData();
        formData.append('pdf', file);

        setLoading(true);
        try {
            const apiUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';
            const res = await axios.post(`${apiUrl}/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setMessage(res.data.message || "Upload successful!");
        } catch (err) {
            if (err.response) {
                setMessage(err.response.data.error || "An error occurred while uploading.");
            } else {
                setMessage("Network error or server is unreachable.");
            }
        } finally {
            setLoading(false);
        }
    };
    const handleProcess = async () => {
        if (!file) {
            setMessage("No file selected.");
            return;
        }

        setProcessing(true);
        try {
            const apiUrl = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';
            const res = await axios.post(`${apiUrl}/process-pdf`, { pdf_filename: file.name });
            console.log("sending payload to the backend", file.name);
            setMessage(res.data.message || "Processing successful!");}
            catch (err) {
                if (err.response) {
                    setMessage(err.response.data.error || "An error occurred while processing.");
                } else {
                    setMessage("Network error or server is unreachable.");
                }
            } finally {
                setProcessing(false);
            }
        };

    return (
        <div style={{ padding: "20px" }}>
            <h1>Frontend PDF Upload</h1>
            <input
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}//handles the file change event
                disabled={loading || processing}//disables the file input while the file is being uploaded or processed
            />
            <button 
                onClick={handleUpload} 
                disabled={!file || loading || processing}//disables the upload button if no file is selected, or if the file is being uploaded or processed
                style={{ marginTop: "10px", marginRight: "10px" }}
                >
                {loading? 'Uploading' : 'Upload'}
            </button>
            <button
                onClick={handleProcess}
                disabled={!file || loading || processing}
                style={{ marginTop: "10px" }}
            >
                {processing? 'Processing' : 'Process'}
                </button>
            {message && (
                <p style={{ marginTop: "10px", color: message.includes("success") ? "green" : "red" }}>
                    {message}
                </p>
            )}
        </div>
    );
};

export default FileUpload;