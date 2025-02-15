import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import "./Description.css";

const Description = () => {
    return (
        <div className = "description-container p-4 my-4 shadow-sm rounded">
            <h2 className="text-center mb-4">ScraPDF</h2>
            <p className="text-center lead">
                Do you have a scanned PDF where you can't select or copy images, logos or diagrams?
                ScraPDF is a web application that extracts non-textual contents from your PDF files whether they can be selected or not. 
                The application allows users to upload PDF files or provide a URL to a PDF file. 
                The uploaded file is then processed using OCR to extract the text content. 
                The extracted text can be downloaded as a text file for further use.
            </p>
        </div>
    );
};

export default Description;