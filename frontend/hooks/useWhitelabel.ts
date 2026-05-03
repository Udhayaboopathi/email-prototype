"use client";

import { useEffect, useState } from "react";

interface WhitelabelSettings {
  brandName: string;
  logoUrl: string;
  primaryColor: string;
}

export function useWhitelabel() {
  const [settings, setSettings] = useState<WhitelabelSettings>({
    brandName: "Self Hosted Mail",
    logoUrl: "/icon-192.png",
    primaryColor: "#1d4ed8"
  });

  useEffect(() => {
    const stored = localStorage.getItem("mail.whitelabel");
    if (stored) {
      const parsed = JSON.parse(stored) as WhitelabelSettings;
      setSettings(parsed);
      document.documentElement.style.setProperty("--brand-color", parsed.primaryColor);
    }
  }, []);

  return { settings, setSettings };
}
