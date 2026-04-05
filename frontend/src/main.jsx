import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { ClerkProvider } from "@clerk/clerk-react";
import App from "./App.jsx";
import "./index.css";

const clerkPubKey = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY;
const isClerkKeyValid = clerkPubKey && clerkPubKey.startsWith("pk_") && clerkPubKey !== "pk_test_bWlnaHXR5YWJsZS1kb2ctNTcuY2xlcmsuYWNjb3VudHMuZGV2JA";

// ── Apply saved theme BEFORE React renders to prevent flash ──
(function () {
  const saved = localStorage.getItem("intentshield_theme");
  // Only add dark class if the user explicitly chose dark (default is light)
  if (saved === "dark") {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
})();


ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    {isClerkKeyValid ? (
      <ClerkProvider publishableKey={clerkPubKey}>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </ClerkProvider>
    ) : (
      <div style={{ padding: "40px", color: "white", textAlign: "center", fontFamily: "sans-serif" }}>
        <h2>Missing Clerk Publishable Key</h2>
        <p>Your application is currently crashing because no valid Clerk authentication key was found.</p>
        <p>Please go to <strong>Clerk.com</strong>, create an active API Key, and save it in your <code>frontend/.env</code> as <strong>VITE_CLERK_PUBLISHABLE_KEY</strong>.</p>
        <p>Then refresh the page!</p>
      </div>
    )}
  </React.StrictMode>
);
