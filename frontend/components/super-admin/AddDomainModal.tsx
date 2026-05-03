"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/Modal";

interface AddDomainModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (domain: string) => Promise<void>;
}

export function AddDomainModal({ open, onClose, onSubmit }: AddDomainModalProps) {
  const [domain, setDomain] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    await onSubmit(domain);
    setDomain("");
    onClose();
  };

  return (
    <Modal open={open} onClose={onClose} title="Add Domain">
      <form onSubmit={submit} className="space-y-3">
        <Input value={domain} onChange={e => setDomain(e.target.value)} placeholder="example.com" />
        <Button type="submit">Create</Button>
      </form>
    </Modal>
  );
}
