import { motion } from "framer-motion";

export function ConfidenceBar({ value }: { value: number }) {
  // Map 0-1 to percentage
  const percent = Math.min(100, Math.max(0, value * 100));

  // Determine color based on confidence
  let colorClass = "bg-green-500";
  if (percent < 50) colorClass = "bg-red-500";
  else if (percent < 75) colorClass = "bg-yellow-500";

  return (
    <div className="w-full flex items-center gap-3">
      <div className="relative h-2 flex-1 rounded-full bg-muted overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percent}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={`absolute top-0 left-0 h-full rounded-full ${colorClass}`}
        />
      </div>
      <div className="text-xs font-medium w-10 text-right text-muted-foreground">
        {percent.toFixed(0)}%
      </div>
    </div>
  );
}
