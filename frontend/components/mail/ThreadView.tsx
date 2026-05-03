import { MailItem } from "@/types";

interface ThreadViewProps {
  thread: MailItem[];
  onOpen: (item: MailItem) => void;
}

export function ThreadView({ thread, onOpen }: ThreadViewProps) {
  return (
    <div className="space-y-2">
      {thread.map(item => (
        <button
          key={item.uid || item.id}
          onClick={() => onOpen(item)}
          className="w-full rounded-lg border border-slate-200 p-3 text-left dark:border-slate-800"
        >
          <div className="font-medium">{item.subject}</div>
          <div className="text-sm text-slate-500">{item.from_email || item.from}</div>
        </button>
      ))}
    </div>
  );
}
