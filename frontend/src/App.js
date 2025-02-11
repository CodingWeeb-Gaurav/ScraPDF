import React from "react";
import "bootstrap/dist/css/bootstrap.min.css";
import Header from "./components/Header";
import Footer from "./components/Footer";
import FileUpload from "./components/FileUpload";

const App = () => {
    return (
        <div>
            <Header />
            <main className="container my-4">
                <h2 className="text-center">Upload Your PDF</h2>
                <FileUpload />
            </main>
            <Footer />
        </div>

    );
};

export default App;

