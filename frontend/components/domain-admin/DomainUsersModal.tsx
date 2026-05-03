"use client";

import { Modal } from "@/components/ui/Modal";

interface DomainUser {
  id: string;
  email: string;
  role: string;
}

interface DomainUsersModalProps {
  open: boolean;
  onClose: () => void;
  users: DomainUser[];
}

export function DomainUsersModal({ open, onClose, users }: DomainUsersModalProps) {
  return (
    <Modal open={open} onClose={onClose} title="Domain Users">
      <ul className="space-y-2 text-sm">
        {users.map(user => (
          <li key={user.id} className="flex justify-between rounded-lg border border-slate-200 p-2 dark:border-slate-800">
            <span>{user.email}</span>
            <span>{user.role}</span>
          </li>
        ))}
      </ul>
    </Modal>
  );
}
