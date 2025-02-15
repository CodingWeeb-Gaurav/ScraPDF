import React, { useState } from "react";
import { Card, Container, Button } from "react-bootstrap";
import JSZip from "jszip";
import { saveAs } from "file-saver";

const ExtractedImages = ({ images, onDownload }) => {
    const [selectedImages, setSelectedImages] = useState([]); // To store selected images
    const [selectAll, setSelectAll] = useState(false); // To handle "Select All" functionality

    
    if (images.length === 0) {
        return null;
    } // If there are no images, don't render anything

    
    // Handle checkbox selection for individual images
    const handleCheckboxChange = (e, imgURL) => {
        if (selectedImages.includes(imgURL)) {
            setSelectedImages(selectedImages.filter((img) => img !== imgURL));
        } else {
            setSelectedImages([...selectedImages, imgURL]);
        }
    };

    // Handle "Select All" functionality
    const handleSelectAll = (e) => {
        setSelectAll(e.target.checked);
        if (e.target.checked) {
            setSelectedImages(images); // Select all images
        } else {
            setSelectedImages([]); // Deselect all images
        }
    };

    // Handle download of selected images
    const handleDownload = async () => {
        if (selectedImages.length === 0) {
            alert("Please select images to download.");
            return;
        }

        // Create a ZIP file
        const zip = new JSZip();
        const imgFolder = zip.folder("extracted_images");

        // Fetch each selected image and add it to the ZIP
        for (const imgURL of selectedImages) {
            try {
                const response = await fetch(imgURL);
                const blob = await response.blob();
                const filename = imgURL.split("/").pop(); // Extract filename from URL
                imgFolder.file(filename, blob);
            } catch (error) {
                console.error("Error fetching image:", error);
            }
        }

        // Generate the ZIP file and trigger download
        zip.generateAsync({ type: "blob" }).then((content) => {
            saveAs(content, "extracted_images.zip");
        });
    };

    return (
        <Container className="my-4">
            <h4>Extracted Images</h4>
            <div className="d-flex justify-content-between align-items-center mb-3">
                <div>
                    <input
                        type="checkbox"
                        checked={selectAll}
                        onChange={handleSelectAll}
                    />
                    <span className="ms-2">Select All</span>
                </div>
                <Button
                    variant="primary"
                    onClick={handleDownload}
                    disabled={selectedImages.length === 0}
                >
                    Download Selected Images
                </Button>
            </div>
            <div className="Image-Container">
                {images.map((imgURL, index) => (
                    <Card className="image-card" key={index}>
                        <Card.Img variant="top" src={imgURL} />
                        <div className="checkbox-container">
                            <input
                                type="checkbox"
                                checked={selectAll || selectedImages.includes(imgURL)}
                                onChange={(e) => handleCheckboxChange(e, imgURL)}
                            />
                        </div>
                    </Card>
                ))}
            </div>
            <style>
                {`
                .Image-Container {
                    max-height: 500px;
                    overflow-y: auto;
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    border: 1px solid #ccc;
                    border-radius: 10px;
                    padding: 10px;
                }
                .image-card {
                    width: 120px;
                    height: 120px;
                    overflow: hidden;
                    border-radius: 5px;
                    position: relative;
                }
                .image-card img {
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                }
                .checkbox-container {
                    position: absolute;
                    top: 5px;
                    left: 5px;
                    background: rgba(255, 255, 255, 0.8);
                    padding: 2px;
                    border-radius: 3px;
                }
                `}
            </style>
        </Container>
    );
};

export default ExtractedImages;