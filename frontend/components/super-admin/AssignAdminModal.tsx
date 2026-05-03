"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/Modal";

interface AssignAdminModalProps {
  open: boolean;
  onClose: () => void;
  onAssign: (email: string) => Promise<void>;
}

export function AssignAdminModal({ open, onClose, onAssign }: AssignAdminModalProps) {
  const [email, setEmail] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    await onAssign(email);
    onClose();
  };

  return (
    <Modal open={open} onClose={onClose} title="Assign Domain Admin">
      <form onSubmit={submit} className="space-y-3">
        <Input value={email} onChange={e => setEmail(e.target.value)} placeholder="admin@example.com" />
        <Button type="submit">Assign</Button>
      </form>
    </Modal>
  );
}
