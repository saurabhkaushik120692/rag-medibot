"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const router = useRouter();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError("");
        setLoading(true);

        try {
            // Call your backend login API
            const res = await fetch("http://localhost:8000/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });

            // console.log(res.json());

            const data = await res.json();

            if (res.ok && data.role) {
                // Save the returned role in localStorage
                localStorage.setItem("userRole", data.role);

                // Redirect to the chat page
                router.push("/chat");
            } else {
                setError(data.message || "Invalid username or password.");
            }
        } catch (err) {
            setError("Could not connect to the authentication server.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.container}>
            <form onSubmit={handleLogin} style={styles.card}>
                <h2 style={styles.title}>MediAssist Portal</h2>
                <p style={styles.subtitle}>Enter credentials to access your workspace</p>

                {error && <div style={styles.errorAlert}>{error}</div>}

                <div style={styles.inputGroup}>
                    <label style={styles.label}>Username</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        placeholder="Enter username"
                        required
                        style={styles.input}
                    />
                </div>

                <div style={styles.inputGroup}>
                    <label style={styles.label}>Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        placeholder="Enter password"
                        required
                        style={styles.input}
                    />
                </div>

                <button type="submit" disabled={loading} style={styles.button}>
                    {loading ? "Authenticating..." : "Enter Workspace"}
                </button>
            </form>
        </div>
    );
}

const styles = {
    container: { display: "flex", justifyContent: "center", alignItems: "center", height: "100vh", backgroundColor: "#f0f2f5" },
    card: { padding: "40px", borderRadius: "12px", backgroundColor: "#ffffff", boxShadow: "0 4px 12px rgba(0,0,0,0.1)", width: "380px" },
    title: { margin: "0 0 10px 0", color: "#1a73e8", fontSize: "24px", textAlign: "center" },
    subtitle: { margin: "0 0 24px 0", color: "#5f6368", fontSize: "14px", textAlign: "center" },
    errorAlert: { padding: "10px", backgroundColor: "#fde8e8", color: "#e53e3e", borderRadius: "6px", fontSize: "14px", marginBottom: "15px", border: "1px solid #f8b4b4", textAlign: "center" },
    inputGroup: { marginBottom: "20px" },
    label: { display: "block", textAlign: "left", marginBottom: "8px", fontWeight: "bold", fontSize: "14px", color: "#3c4043" },
    input: { width: "100%", padding: "12px", borderRadius: "6px", border: "1px solid #dadce0", fontSize: "16px", outline: "none", boxSizing: "border-box" },
    button: { width: "100%", padding: "12px", backgroundColor: "#1a73e8", color: "#fff", border: "none", borderRadius: "6px", fontSize: "16px", cursor: "pointer", fontWeight: "bold", marginTop: "10px" }
};
