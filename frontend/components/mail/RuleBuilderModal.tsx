"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/Modal";

interface RuleBuilderModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (rule: { subject_contains: string; move_to: string }) => void;
}

export function RuleBuilderModal({ open, onClose, onSave }: RuleBuilderModalProps) {
  const [subjectContains, setSubjectContains] = useState("");
  const [moveTo, setMoveTo] = useState("INBOX");

  const submit = (event: FormEvent) => {
    event.preventDefault();
    onSave({ subject_contains: subjectContains, move_to: moveTo });
    onClose();
  };

  return (
    <Modal open={open} title="Create Rule" onClose={onClose}>
      <form onSubmit={submit} className="space-y-3">
        <Input value={subjectContains} onChange={e => setSubjectContains(e.target.value)} placeholder="Subject contains..." />
        <Input value={moveTo} onChange={e => setMoveTo(e.target.value)} placeholder="Move to folder" />
        <Button type="submit">Save Rule</Button>
      </form>
    </Modal>
  );
}
