import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import "./globals.css";
import { Providers } from "@/components/layout/Providers";
import { cn } from "@/lib/utils";

export const metadata: Metadata = {
  title: "MailOS — Self-Hosted Email Platform",
  description: "Self-hosted email platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={cn(GeistSans.variable, "antialiased")}
    >
      <body className={GeistSans.className}>
        <Providers attribute="class" defaultTheme="system" enableSystem>
          {children}
        </Providers>
      </body>
    </html>
  );
}
