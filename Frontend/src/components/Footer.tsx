export function Footer() {
  return (
    <footer className="border-t border-border py-12">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-6 px-6 md:flex-row">
        <div className="flex items-center gap-6 text-xs text-muted-foreground">
          <span>© {new Date().getFullYear()} Signal Analysis</span>
          <a href="#" className="transition-colors hover:text-foreground">
            Terms
          </a>
          <a href="#" className="transition-colors hover:text-foreground">
            Privacy
          </a>
        </div>
        <div className="flex items-center gap-2">
          <span className="size-2 rounded-full bg-success" />
          <span className="font-mono-tabular text-xs text-muted-foreground">
            All systems operational
          </span>
        </div>
      </div>
    </footer>
  );
}
