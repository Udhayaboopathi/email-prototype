interface Attachment {
  name: string;
  size: number;
}

interface AttachmentViewerProps {
  attachments: Attachment[];
}

export function AttachmentViewer({ attachments }: AttachmentViewerProps) {
  if (attachments.length === 0) return null;
  return (
    <div className="rounded-lg border border-slate-200 p-3 dark:border-slate-800">
      <h3 className="mb-2 text-sm font-semibold">Attachments</h3>
      <ul className="space-y-1 text-sm">
        {attachments.map(attachment => (
          <li key={attachment.name} className="flex justify-between">
            <span>{attachment.name}</span>
            <span>{Math.round(attachment.size / 1024)} KB</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
