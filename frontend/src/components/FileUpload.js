import React, { useState, useCallback } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import { Form, Button, Spinner, Container, Alert } from 'react-bootstrap';
import ExtractedImages from './ExtractedImages';
const FileUpload = () => {
    const [file, setFile] = useState(null); // Stores the selected or dropped file
    const [fileUrl, setFileUrl] = useState(""); // Stores the PDF URL entered by the user
    const [message, setMessage] = useState(""); // Stores messages about success/errors
    const [loading, setLoading] = useState(false); // Uploading state
    const [processing, setProcessing] = useState(false); // Processing state
    const [extractedImages, setExtractedImages] = useState([]); // Extracted images from the PDF
    const apiUrl = process.env.REACT_APP_API_URL";
    // Handle file drop
    const onDrop = useCallback((acceptedFiles) => {
        const selectedFile = acceptedFiles[0];
        if (selectedFile && selectedFile.type === "application/pdf") {
            setFile(selectedFile);
            setMessage("");
        } else {
            setMessage("Please select a valid PDF file.");
        }
    }, []);

    // React Dropzone setup
    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: "application/pdf",
        multiple: false,
    });

    // Handle file selection manually via input field
    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile && selectedFile.type === "application/pdf") {
            setFile(selectedFile);
            setMessage("");
        } else {
            setMessage("Please select a valid PDF file.");
        }
    };

    // Handle file upload to backend
    const handleUpload = async () => {
        if (!file && !fileUrl) {
            setMessage("No file selected or URL provided.");
            return;
        }

        setLoading(true);
        try {
            const apiUrl = process.env.REACT_APP_API_URL || "http://127.0.0.1:5000";

            if (file) {
                // Upload file
                const formData = new FormData();
                formData.append("pdf", file);

                const res = await axios.post(`${apiUrl}/upload`, formData, {
                    headers: { "Content-Type": "multipart/form-data" },
                });
                setMessage(res.data.message || "Upload successful!");
            } else if (fileUrl) {
                // Upload from URL
                const res = await axios.post(`${apiUrl}/upload-from-url`, { url: fileUrl });
                setMessage(res.data.message || "PDF fetched successfully!");
            }
        } catch (err) {
            setMessage(err.response?.data?.error || "An error occurred while uploading.");
        } finally {
            setLoading(false);
        }
    };

    // Handle file processing request to backend
    const handleProcess = async () => {
        if (!file) {
            setMessage("No file selected.");
            return;
        }

        setProcessing(true);
        try {
            const sanitizedFileName = file.name.replace(/\s+/g, "_");
            const res = await axios.post(`${apiUrl}/process-pdf`, { pdf_filename: sanitizedFileName });
            if(res.data.images) {
                setExtractedImages(res.data.images); //backend returns a list of image URLs
            }
            setMessage(res.data.message || "Processing successful!");
        } catch (err) {
            setMessage(err.response?.data?.error || "An error occurred while processing.");
        } finally {
            setProcessing(false);
        }
    };

    return (
        <Container className="mt-4">
            <h2 className="text-center"></h2>

            {/* Drag & Drop Section including file selection */}
            <div
                {...getRootProps()}
                className={`dropzone p-4 mb-3 text-center border ${isDragActive ? "border-primary" : "border-secondary"}`}
                style={{ cursor: "pointer", borderRadius: "10px", position: "relative" }}
            >
                <input {...getInputProps()} />
                {isDragActive ? (
                    <p className="text-primary">Drop the PDF here...</p>
                ) : file ? (
                    <p className="text-success"><strong>{file.name}</strong></p>
                ) : (
                    <p>Drag & drop a PDF file here, or click to select one.</p>
                )}

                {/* File Selection inside the dropbox */}
                {/* <Form.Group controlId="formFile" className="mb-3">
                    <Form.Control type="file" accept="application/pdf" onChange={handleFileChange} disabled={loading || processing} />
                </Form.Group> */}
            </div>

            {/* URL Upload Section */}
            <Form.Group controlId="formUrlUpload" className="mb-3">
                <Form.Control
                    type="text"
                    placeholder="Enter PDF URL"
                    value={fileUrl}
                    onChange={(e) => setFileUrl(e.target.value)}
                />
                <Button variant="info" className="mt-2" onClick={handleUpload} disabled={loading || processing}>
                    {loading ? <Spinner animation="border" size="sm" /> : "Fetch from URL"}
                </Button>
            </Form.Group>

            {/* Unified Upload Button (Handles both files & URL) */}
            <Button
                variant="primary"
                onClick={handleUpload}
                disabled={loading || processing || (!file && !fileUrl)}
                className="mt-3"
            >
                {loading ? <Spinner animation="border" size="sm" /> : "Upload"}
            </Button>

            {/* Process Button */}
            <Button
                variant="success"
                onClick={handleProcess}
                disabled={!file || loading || processing}
                className="mt-3"
            >
                {processing ? <Spinner animation="border" size="sm" /> : "Process"}
            </Button>

            {/* Message */}
            {message && <Alert className="mt-3" variant={message.includes("success") ? "success" : "danger"}>{message}</Alert>}

            <ExtractedImages images={extractedImages} />
        </Container>
    );
};

export default FileUpload;
