import { useApi } from "@/hooks/use-api";
import { fetchDashboardSummary } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { Mail, Tag, Bell, Archive, Star, HelpCircle } from "lucide-react";
import { motion } from "framer-motion";

interface StatCardProps {
  title: string;
  value: number;
  icon: React.ElementType;
  colorClass: string;
  delay: number;
}

function StatCard({ title, value, icon: Icon, colorClass, delay }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
    >
      <Card className="full-h border shadow-sm hover:shadow-md transition-shadow">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
          <div className={`p-2 rounded-lg ${colorClass}`}>
            <Icon className="w-4 h-4" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">{value}</div>
        </CardContent>
      </Card>
    </motion.div>
  );
}

export default function Dashboard() {
  const { data: summary, isLoading, error } = useApi(fetchDashboardSummary);

  if (error) {
    return <div className="text-destructive p-4">Error loading dashboard: {error.message}</div>;
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-6"
    >
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground mt-1">Overview of your Mail AI activity</p>
      </div>

      {isLoading || !summary ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-[120px] rounded-xl" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <StatCard
            title="Total Emails"
            value={summary.total_emails}
            icon={Mail}
            colorClass="bg-blue-500/10 text-blue-500"
            delay={0.1}
          />
          <StatCard
            title="Classifications"
            value={summary.total_classifications}
            icon={Tag}
            colorClass="bg-purple-500/10 text-purple-500"
            delay={0.2}
          />
          <StatCard
            title="Notifications"
            value={summary.total_notifications}
            icon={Bell}
            colorClass="bg-orange-500/10 text-orange-500"
            delay={0.3}
          />
          <StatCard
            title="Archived Emails"
            value={summary.archived_emails}
            icon={Archive}
            colorClass="bg-gray-500/10 text-gray-500"
            delay={0.4}
          />
          <StatCard
            title="Important Emails"
            value={summary.important_count}
            icon={Star}
            colorClass="bg-red-500/10 text-red-500"
            delay={0.5}
          />
          <StatCard
            title="Uncertain Emails"
            value={summary.uncertain_count}
            icon={HelpCircle}
            colorClass="bg-yellow-500/10 text-yellow-500"
            delay={0.6}
          />
        </div>
      )}
    </motion.div>
  );
}
