import { MailItem } from "@/types";
import { formatDate } from "@/lib/utils";

interface EmailListItemProps {
  item: MailItem;
  onSelect: (item: MailItem) => void;
}

export function EmailListItem({ item, onSelect }: EmailListItemProps) {
  return (
    <button
      onClick={() => onSelect(item)}
      className="w-full border-b border-slate-200 px-4 py-3 text-left hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-900"
    >
      <div className="flex items-center justify-between">
        <span className="font-medium">{item.subject || "(no subject)"}</span>
        <span className="text-xs text-slate-500">{formatDate(item.date)}</span>
      </div>
      <p className="text-sm text-slate-500">{item.from_email}</p>
      <p className="truncate text-sm">{item.snippet}</p>
    </button>
  );
}
