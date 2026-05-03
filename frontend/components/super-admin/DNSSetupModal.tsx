"use client";

import { Modal } from "@/components/ui/Modal";

interface DNSSetupModalProps {
  open: boolean;
  onClose: () => void;
  records: Array<{ type: string; name: string; value: string }>;
}

export function DNSSetupModal({ open, onClose, records }: DNSSetupModalProps) {
  return (
    <Modal open={open} onClose={onClose} title="DNS Setup Guide">
      <div className="space-y-2 text-sm">
        {records.map(record => (
          <div key={`${record.type}-${record.name}`} className="rounded-lg border border-slate-200 p-2 dark:border-slate-800">
            <div className="font-semibold">{record.type}</div>
            <div>{record.name}</div>
            <div className="font-mono text-xs">{record.value}</div>
          </div>
        ))}
      </div>
    </Modal>
  );
}
