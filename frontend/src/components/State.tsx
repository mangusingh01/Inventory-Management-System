import { AlertCircle, Loader2 } from "lucide-react";

type StateProps = {
  message: string;
};

export function LoadingState({ message }: StateProps) {
  return (
    <div className="state state-muted">
      <Loader2 aria-hidden="true" className="spin" size={18} />
      <span>{message}</span>
    </div>
  );
}

export function ErrorState({ message }: StateProps) {
  return (
    <div className="state state-error" role="alert">
      <AlertCircle aria-hidden="true" size={18} />
      <span>{message}</span>
    </div>
  );
}

export function EmptyState({ message }: StateProps) {
  return <div className="state state-muted">{message}</div>;
}
