import { MailItem } from "@/types";

interface PriorityInboxProps {
  items: MailItem[];
}

export function PriorityInbox({ items }: PriorityInboxProps) {
  const prioritized = items.slice(0, 5);
  return (
    <section className="rounded-xl border border-slate-200 p-4 dark:border-slate-800">
      <h2 className="mb-3 text-sm font-semibold">Priority Inbox</h2>
      <ul className="space-y-2 text-sm">
        {prioritized.map(item => (
          <li key={item.uid || item.id} className="truncate">
            {item.subject}
          </li>
        ))}
      </ul>
    </section>
  );
}
