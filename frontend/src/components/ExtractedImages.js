import React from "react";
import { Card, Container } from "react-bootstrap";

const ExtractedImages = ({ images }) => {
    if(images.length === 0) {
        return null;
    } //image hai hi nahi to kuch nahi dikhana
    return (
        <Container className="my-4">
            <h4>Extracted Images</h4>
            <div className="Image-Container">
                {images.map((imgURL, index) => (  
                    <Card className="image-card" key={index}> 
                        <Card.Img variant="top" src={imgURL} /> 
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
                }
                .image-card img {
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                `}            
            </style>   
        </Container>

    );
};
export default ExtractedImages;