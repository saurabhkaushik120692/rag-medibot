// app/page.js
"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function RootPage() {
  const router = useRouter();

  useEffect(() => {
    // If user has already logged in, send them straight to chat, otherwise to login
    const userRole = localStorage.getItem("userRole");
    if (userRole) {
      router.push("/chat");
    } else {
      router.push("/login");
    }
  }, [router]);

  return (
    <div style={loadingContainerStyles}>
      <h3>Redirecting to portal...</h3>
    </div>
  );
}

const loadingContainerStyles = {
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  height: "100vh",
  color: "#5f6368",
};
