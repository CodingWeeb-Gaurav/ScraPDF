import React, { useContext } from "react";
import { Navbar, Nav, Container, Button } from "react-bootstrap";
import { ThemeContext } from "../context/ThemeContext"; // Import ThemeContext

const Header = () => {
    const { theme, toggleTheme } = useContext(ThemeContext); // Access theme and toggleTheme

    return (
        <Navbar bg={theme === "light" ? "light" : "dark"} variant={theme === "light" ? "light" : "dark"} expand="lg">
            <Container>
                <Navbar.Brand href="/">
                    <img
                        align="Center"
                        src="/ScraPDF logo.png" // Path relative to 'public/' directory
                        alt="ScraPDF Logo"
                        height="40" // Adjust as needed
                        style={{ maxWidth: "150px", objectFit: "contain" }} // Adjust width
                    />
                </Navbar.Brand>
                {/* Toggle theme button */}
                <Nav className="ml-auto">
                    <Button
                        variant={theme === "light" ? "outline-dark" : "outline-light"}
                        onClick={toggleTheme}
                    >
                        {theme === "light" ? "🌙 Dark Mode" : "☀️ Light Mode"}
                    </Button>
                </Nav>
            </Container>
        </Navbar>
    );
};

export default Header;