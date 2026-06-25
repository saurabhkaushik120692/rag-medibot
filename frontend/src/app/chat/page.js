"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import styles from "./chat.module.css";

export default function ChatPage() {
    const [role, setRole] = useState(null);
    const [accessibleData, setAccessibleData] = useState([]);
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState([]);
    const router = useRouter();

    useEffect(() => {
        const storedRole = localStorage.getItem("userRole");
        if (!storedRole) {
            // Keep this as "/login" because the Next.js login page is local
            router.push("/login");
            return;
        }
        setRole(storedRole);

        // Fetch accessible collections dynamically from FastAPI
        const fetchCollections = async () => {
            try {
                const res = await fetch(`http://localhost:8000/collections/${storedRole}`);
                if (res.ok) {
                    const data = await res.json();
                    setAccessibleData(data); // e.g. ["general", "clinical", "nursing"]
                } else {
                    console.error("Failed to load collections");
                }
            } catch (err) {
                console.error("Error connecting to backend for collections:", err);
            }
        };

        fetchCollections();
    }, [router]);

    const handleSendMessage = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { sender: "user", text: input };
        setMessages(prev => [...prev, userMessage]);
        const currentInput = input;
        setInput("");

        try {
            const res = await fetch("http://localhost:8000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: currentInput, role: role })
            });
            const data = await res.json();

            setMessages(prev => [...prev, { sender: "bot", text: data.answer }]);
        } catch (err) {
            setMessages(prev => [...prev, { sender: "bot", text: "Error connecting to server. Please try again." }]);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem("userRole");
        router.push("/login");
    };

    if (!role) return <div className={styles.loading}>Loading Workspace...</div>;

    return (
        <div className={styles.chatContainer}>
            {/* Left Sidebar - Accessible data */}
            <aside className={styles.sidebar}>
                <div className={styles.sidebarHeader}>
                    <h3>MediAssist RAG</h3>
                    <span className={styles.roleBadge}>{role.replace("_", " ").toUpperCase()}</span>
                </div>
                <div className={styles.accessSection}>
                    <h4>ACCESSIBLE DATABASES</h4>
                    <ul className={styles.collectionList}>
                        {accessibleData.map((col) => (
                            <li key={col} className={styles.collectionItem}>
                                📁 {col.toUpperCase()}
                            </li>
                        ))}
                    </ul>
                </div>
                <button onClick={handleLogout} className={styles.logoutButton}>
                    Logout
                </button>
            </aside>

            {/* Right Section - Chat Screen */}
            <main className={styles.chatArea}>
                <div className={styles.messageBox}>
                    {messages.length === 0 ? (
                        <div className={styles.welcomeText}>
                            Ask a question about the {accessibleData.join(", ")} databases.
                        </div>
                    ) : (
                        messages.map((msg, i) => (
                            <div key={i} className={msg.sender === "user" ? styles.userRow : styles.botRow}>
                                <div className={styles.bubble}>{msg.text}</div>
                            </div>
                        ))
                    )}
                </div>

                {/* Input Bar */}
                <form onSubmit={handleSendMessage} className={styles.inputForm}>
                    <input
                        type="text"
                        placeholder="Type your medical query..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        className={styles.textInput}
                    />
                    <button type="submit" className={styles.sendButton}>Send</button>
                </form>
            </main>
        </div>
    );
}
