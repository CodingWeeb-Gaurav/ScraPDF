import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = () => {
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState("");
    const [loading, setLoading] = useState(false);
    const [processing, setProcessing] = useState(false); //useState(false) represents the initial state of the component

    const handleFileChange = (e) => { //handleFileChange is a function that takes an event as an argument and updates the file state with the selected file
        const selectedFile = e.target.files[0];
        if (selectedFile && selectedFile.type !== "application/pdf") {
            setMessage("Only PDF files are allowed.");
            setFile(null);
            return;
        }
        setFile(selectedFile);
        setMessage("");
    };

    const handleUpload = async (e) => { //handleUpload is an async function that takes an event as an argument and uploads the selected file to the server
        e.preventDefault();

        if (!file) {
            setMessage("Please select a file to upload.");
            return;
        }

        if (file.size > 12 * 1024 * 1024) { // 12 MB limit
            setMessage("File size exceeds 12 MB.");
            return;
        }

        const apiUrl = process.env.REACT_APP_API_URL;
        if (!apiUrl) {
            setMessage("API URL is not configured.");
            return;
        }

        const formData = new FormData();
        formData.append('pdf', file);

        setLoading(true);
        try {
            const res = await axios.post(`${apiUrl}/upload`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setMessage(res.data.message || "Upload successful!");
            setFile(null); // Reset file
        } catch (err) {
            if (err.response) {
                setMessage(err.response.data.msg || "An error occurred while uploading.");
            } else {
                setMessage("Network error or server is unreachable.");
            }
        } finally {
            setLoading(false);
        }
    };

    const handleProcess = async () => {
        if (!file) {
            setMessage("Please select a file to process.");
            return;
        }
        const apiUrl = process.env.REACT_APP_API_URL;
        if (!apiUrl) {
            setMessage("API URL is not configured.");
            return;
        }
        setProcessing(true);
        setMessage("Processing...");
        try {
            const res = await axios.post(`${apiUrl}/process-pdf`, {
                pdf_filename: file.name, // Pass the file name to the backend
            });
            setMessage(res.data.message || "Processing successful!");
        } catch (err) {
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
            <h1>PDF Upload</h1>
            <form onSubmit={handleUpload}>
                <div>
                    <input
                        type="file"
                        accept="application/pdf"
                        onChange={handleFileChange}
                        disabled={loading}
                    />
                </div>
                <button type="submit" disabled={loading || !file}>
                    {loading ? 'Uploading...' : 'Upload'}
                </button>
            </form>
            <button onClick={handleProcess} disabled={processing || !file||loading}
                style={{marginTop: "10px",
                padding: "10px 20px",
                backgroundColor: processing? "gray" : "blue",
                color: "white",
                border: "none",
                borderRadius: "5px",
                cursor: processing? "not-allowed" : "pointer",
                }}
            >
                {processing ? 'Processing...' : 'Process'}
            </button>
            {message && (
                <div style={{ marginTop: "10px", color: loading ? "blue" : "green" }}>
                    {message}
                </div>
            )}
        </div>
    );
};

export default FileUpload;
