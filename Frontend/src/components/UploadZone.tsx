import { useCallback, useRef, useState } from "react";
import { Upload, FileText, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  onFile: (file: File) => void;
  disabled?: boolean;
}

const MAX_BYTES = 5 * 1024 * 1024;

export function UploadZone({ onFile, disabled }: Props) {
  const [drag, setDrag] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [staged, setStaged] = useState<File | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const validate = (f: File) => {
    if (f.type !== "application/pdf" && !f.name.toLowerCase().endsWith(".pdf")) {
      return "Only PDF resumes are supported.";
    }
    if (f.size > MAX_BYTES) return "File is larger than 5MB.";
    return null;
  };

  const handle = useCallback(
    (f: File) => {
      const err = validate(f);
      if (err) {
        setError(err);
        return;
      }
      setError(null);
      setStaged(f);
      onFile(f);
    },
    [onFile],
  );

  return (
    <div className="w-full">
      <label
        htmlFor="resume-file"
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          if (disabled) return;
          const f = e.dataTransfer.files?.[0];
          if (f) handle(f);
        }}
        className={cn(
          "group relative flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-border bg-background px-6 py-12 text-center transition-all",
          "hover:border-foreground/30 hover:bg-surface",
          drag && "border-foreground/40 bg-surface",
          disabled && "pointer-events-none opacity-60",
        )}
      >
        <input
          ref={inputRef}
          id="resume-file"
          type="file"
          accept="application/pdf,.pdf"
          className="sr-only"
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) handle(f);
          }}
        />

        {!staged ? (
          <>
            <div className="mb-4 flex size-12 items-center justify-center rounded-full border border-border bg-surface transition-transform group-hover:scale-105">
              <Upload className="size-4 text-foreground" strokeWidth={2} />
            </div>
            <p className="text-sm font-medium">Drop your resume (PDF only)</p>
            <p className="mt-1 text-xs text-muted-foreground">or click to browse · max 5MB</p>
          </>
        ) : (
          <div className="flex w-full max-w-md items-center justify-between gap-4 rounded-xl border border-border bg-surface px-4 py-3 text-left">
            <div className="flex min-w-0 items-center gap-3">
              <FileText className="size-5 shrink-0 text-foreground" />
              <div className="min-w-0">
                <p className="truncate text-sm font-medium">{staged.name}</p>
                <p className="font-mono-tabular text-xs text-muted-foreground">
                  {(staged.size / 1024).toFixed(0)} KB · PDF
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                setStaged(null);
                if (inputRef.current) inputRef.current.value = "";
              }}
              aria-label="Remove file"
              className="rounded-md p-1 text-muted-foreground hover:bg-background hover:text-foreground"
            >
              <X className="size-4" />
            </button>
          </div>
        )}
      </label>

      {error && (
        <p role="alert" className="mt-3 text-center text-xs font-medium text-destructive">
          {error}
        </p>
      )}
    </div>
  );
}
