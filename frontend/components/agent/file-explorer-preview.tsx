import { Folder, FileCode } from "lucide-react";

export function FileExplorerPreview() {
  return (
    <div className="surface rounded-lg p-3 text-sm">
      <div className="mb-3 font-medium">Workspace preview</div>
      <div className="space-y-2">
        <div className="flex gap-2"><Folder className="size-4 text-primary" /> modelo-ia-carrera</div>
        <div className="ml-4 flex gap-2 text-muted-foreground"><Folder className="size-4" /> backend</div>
        <div className="ml-8 flex gap-2 text-muted-foreground"><FileCode className="size-4" /> app/presentation/main.py</div>
        <div className="ml-4 flex gap-2 text-muted-foreground"><Folder className="size-4" /> frontend</div>
        <div className="ml-8 flex gap-2 text-muted-foreground"><FileCode className="size-4" /> app/page.tsx</div>
        <div className="ml-8 flex gap-2 text-muted-foreground"><FileCode className="size-4" /> components/chat/chat-view.tsx</div>
      </div>
    </div>
  );
}
