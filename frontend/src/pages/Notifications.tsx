import { useApi } from "@/hooks/use-api";
import { fetchNotifications } from "@/lib/api";
import { EmptyState } from "@/components/ui/EmptyState";
import { Bell, Info, AlertTriangle, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";

export default function Notifications() {
  const { data: notifications, isLoading, error } = useApi(fetchNotifications);

  if (error) {
    return <div className="text-destructive p-4">Error: {error.message}</div>;
  }

  const getIcon = (type: string) => {
    switch (type) {
      case "action_required": return <AlertCircle className="w-5 h-5 text-red-500" />;
      case "warning": return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      default: return <Info className="w-5 h-5 text-blue-500" />;
    }
  };

  const getBadgeType = (type: string) => {
    if (type === "action_required") return "destructive";
    if (type === "warning") return "warning";
    return "default";
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Notifications</h1>
        <p className="text-muted-foreground mt-1">Alerts and updates requiring your attention</p>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="w-full h-24 rounded-xl" />)}
        </div>
      ) : !notifications || notifications.length === 0 ? (
        <EmptyState
          icon={<Bell className="w-10 h-10" />}
          title="All caught up!"
          description="You don't have any new notifications at the moment."
        />
      ) : (
        <div className="space-y-4">
          {notifications.map((notif, i) => (
             <motion.div
               key={notif.id}
               initial={{ opacity: 0, y: 10 }}
               animate={{ opacity: 1, y: 0 }}
               transition={{ delay: i * 0.05 }}
             >
              <Card className="hover:shadow-md transition-shadow">
                <CardContent className="p-4 sm:p-6 flex gap-4">
                  <div className="shrink-0 mt-1">{getIcon(notif.type)}</div>
                  <div className="flex-1 space-y-1">
                    <div className="flex items-start justify-between gap-4">
                      <h3 className="font-medium leading-none">{notif.title}</h3>
                      <Badge variant={getBadgeType(notif.type) as any}>{notif.type.replace('_', ' ')}</Badge>
                    </div>
                    <p className="text-sm text-muted-foreground">{notif.message}</p>
                    <p className="text-xs text-muted-foreground pt-2">
                       {new Date(notif.created_at).toLocaleString()}
                    </p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </motion.div>
  );
}
