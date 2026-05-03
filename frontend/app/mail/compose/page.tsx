"use client";


export const dynamic = 'force-dynamic';
import { useState } from "react";
import { ComposeModal } from "@/components/mail/ComposeModal";

export default function ComposePage() {
  const [open, setOpen] = useState(true);
  return (
    <main className="p-4 md:p-6">
      <ComposeModal open={open} onClose={() => setOpen(false)} />
    </main>
  );
}