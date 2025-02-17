import React, { useEffect, useContext } from "react"; // Import useContext
import "bootstrap/dist/css/bootstrap.min.css";
import Header from "./components/Header";
import Footer from "./components/Footer";
import FileUpload from "./components/FileUpload";
import Description from "./components/Description";
import { ThemeProvider, ThemeContext } from "./context/ThemeContext"; // Import ThemeProvider and ThemeContext

const AppContent = () => {
    const { theme } = useContext(ThemeContext);

    useEffect(() => {
        document.body.className = theme === "light" ? "light-theme" : "dark-theme";
    }, [theme]);

    return (
        <div>
            <Header />
            <Description />
            <main className="container my-4">
                <h2 className="text-center">Upload Your PDF</h2>
                <FileUpload />
            </main>
            <Footer />
        </div>
    );
};
const App = () => {
    return (
        <ThemeProvider>
            <AppContent />
        </ThemeProvider>
    );
};

export default App;