"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/Modal";

interface CreateMailboxModalProps {
  open: boolean;
  onClose: () => void;
  onCreate: (address: string) => Promise<void>;
}

export function CreateMailboxModal({ open, onClose, onCreate }: CreateMailboxModalProps) {
  const [address, setAddress] = useState("");
  const submit = async (event: FormEvent) => {
    event.preventDefault();
    await onCreate(address);
    onClose();
  };

  return (
    <Modal open={open} onClose={onClose} title="Create Mailbox">
      <form onSubmit={submit} className="space-y-3">
        <Input value={address} onChange={e => setAddress(e.target.value)} placeholder="user@example.com" />
        <Button type="submit">Create</Button>
      </form>
    </Modal>
  );
}
