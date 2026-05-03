export default function OfflinePage() {
  return (
    <div className="mx-auto mt-20 max-w-xl rounded-xl border border-slate-200 p-8 text-center dark:border-slate-800">
      <h1 className="mb-2 text-2xl font-semibold">You are offline</h1>
      <p className="text-slate-500">Cached content is available. Reconnect to sync recent messages.</p>
    </div>
  );
}
