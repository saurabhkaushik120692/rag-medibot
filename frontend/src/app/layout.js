// app/layout.js
export const metadata = {
  title: "MediAssist RAG Portal",
  description: "Secure role-based medical database access",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body style={globalStyles}>
        {children}
      </body>
    </html>
  );
}

// Basic reset styles to ensure components layout correctly
const globalStyles = {
  margin: 0,
  padding: 0,
  boxSizing: "border-box",
  fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  backgroundColor: "#f8f9fa",
  minHeight: "100vh",
};
