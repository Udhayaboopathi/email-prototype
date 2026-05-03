"use client";


export const dynamic = 'force-dynamic';
import { CalendarView } from "@/components/calendar/CalendarView";

export default function CalendarPage() {
  return (
    <main className="p-4 md:p-6">
      <h1 className="mb-4 text-xl font-semibold text-slate-900 dark:text-slate-100">Calendar</h1>
      <CalendarView />
    </main>
  );
}