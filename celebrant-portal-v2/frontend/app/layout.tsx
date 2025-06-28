import type { Metadata, Viewport } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "../src/contexts/AuthContext";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: 'swap',
});

const playfairDisplay = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
  display: 'swap',
});

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  title: "Melbourne Celebrant Portal - Professional Marriage Celebrant Management",
  description: "Complete business management platform for Australian marriage celebrants. Manage couples, ceremonies, legal forms, invoices, and compliance in one beautiful application.",
  keywords: "marriage celebrant, wedding celebrant, NOIM, ceremony planning, invoice management, legal compliance, Australian weddings",
  authors: [{ name: "Melbourne Celebrant Portal" }],
  robots: "index, follow",
  openGraph: {
    title: "Melbourne Celebrant Portal",
    description: "Professional Marriage Celebrant Management Platform",
    type: "website",
    locale: "en_AU",
    siteName: "Melbourne Celebrant Portal",
  },
  twitter: {
    card: "summary_large_image",
    title: "Melbourne Celebrant Portal",
    description: "Professional Marriage Celebrant Management Platform",
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  themeColor: '#D4A373',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${playfairDisplay.variable}`}>
      <head>
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className="font-sans antialiased bg-background text-foreground">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
