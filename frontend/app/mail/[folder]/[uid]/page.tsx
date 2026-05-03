"use client";

import { useParams } from "next/navigation";
import { EmailReader } from "@/components/mail/EmailReader";

export default function EmailReaderPage() {
  const params = useParams<{ folder: string; uid: string }>();
  return <EmailReader folder={params.folder} uid={params.uid} />;
}