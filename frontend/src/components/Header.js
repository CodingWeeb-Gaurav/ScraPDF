import React from "react";
import { Navbar, Nav, Container } from "react-bootstrap";

const Header = () => {
  return (
    <Navbar bg="dark" variant="dark" expand="lg">
      <Container>
        <Navbar.Brand href="/">
            <img
            src="/ScraPDF logo.png"  // Path relative to 'public/' directory
            alt="ScraPDF Logo"
            height="40"  // Adjust as needed
            style={{ maxWidth: '150px', objectFit: 'contain' }}  // Adjust width
          />
            
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto">
            <Nav.Link href="/">Home</Nav.Link>
            <Nav.Link href="/about">About</Nav.Link>
            <Nav.Link href="/contact">Contact</Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Header;
// Compare this snippet from frontend/src/components/Footer.js: