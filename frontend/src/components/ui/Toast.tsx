import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, AlertCircle, Info, AlertTriangle, X } from "lucide-react";
import { useToastStore, Toast } from "@/stores/toast-store";
import { cn } from "@/lib/utils";

const toastIcons = {
  success: <CheckCircle2 className="text-green-500 w-5 h-5" />,
  error: <AlertCircle className="text-red-500 w-5 h-5" />,
  info: <Info className="text-blue-500 w-5 h-5" />,
  warning: <AlertTriangle className="text-yellow-500 w-5 h-5" />
};

const toastBg = {
  success: "bg-green-500/10 border-green-500/20",
  error: "bg-red-500/10 border-red-500/20",
  info: "bg-blue-500/10 border-blue-500/20",
  warning: "bg-yellow-500/10 border-yellow-500/20"
};

export function ToastContainer() {
  const { toasts, removeToast } = useToastStore();

  return (
    <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2 w-full max-w-sm pointer-events-none">
      <AnimatePresence>
        {toasts.map((toast: Toast) => (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9, transition: { duration: 0.2 } }}
            className={cn(
              "pointer-events-auto flex items-start gap-3 rounded-lg border p-4 shadow-lg backdrop-blur-md bg-card",
            )}
          >
            <div className="mt-0.5 flex-shrink-0">{toastIcons[toast.type]}</div>
            <div className="flex-1 text-sm font-medium pt-0.5">{toast.message}</div>
            <button
              onClick={() => removeToast(toast.id)}
              className="flex-shrink-0 text-muted-foreground hover:text-foreground transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
