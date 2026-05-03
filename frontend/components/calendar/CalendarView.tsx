import { formatDate } from "@/lib/utils";

interface CalendarEvent {
  id: string;
  title: string;
  start_at: string;
  end_at: string;
  location: string;
}

interface CalendarViewProps {
  events?: CalendarEvent[];
}

export function CalendarView({ events = [] }: CalendarViewProps) {
  return (
    <div className="space-y-3">
      {events.map(event => (
        <article key={event.id} className="rounded-lg border border-slate-200 p-3 dark:border-slate-800">
          <h3 className="font-medium">{event.title}</h3>
          <p className="text-sm text-slate-500">
            {formatDate(event.start_at)} → {formatDate(event.end_at)}
          </p>
          <p className="text-sm">{event.location}</p>
        </article>
      ))}
    </div>
  );
}
