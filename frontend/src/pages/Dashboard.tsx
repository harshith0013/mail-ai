import { useEffect, useState } from "react";
import api from "../lib/api";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
} from "recharts";
import {
  Mail,
  Bell,
  Archive,
  AlertTriangle,
  Sparkles,
  Inbox,
} from "lucide-react";

type Summary = {
  total_emails: number;
  total_classifications: number;
  total_notifications: number;
  archived_emails: number;
  important_count: number;
  uncertain_count: number;
  review_count: number;
  unread_notifications: number;
};

type CategoryDistribution = {
  category: string;
  count: number;
};

function StatCard({
  title,
  value,
  icon: Icon,
}: {
  title: string;
  value: number;
  icon: any;
}) {
  return (
    <div className="bg-white rounded-2xl border shadow-sm p-5">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">{title}</p>
        <Icon className="w-5 h-5 text-slate-400" />
      </div>
      <h3 className="text-3xl font-bold mt-3 text-slate-900">{value}</h3>
    </div>
  );
}

export default function Dashboard() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [distribution, setDistribution] = useState<CategoryDistribution[]>([]);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const fetchDashboard = async () => {
    const summaryRes = await api.get<Summary>("/dashboard/summary");
    
    const distributionRes = await api.get<CategoryDistribution[]>(
      "/dashboard/category-distribution"
      
    );

    setSummary(summaryRes.data);
    setDistribution(distributionRes.data);
    setLastUpdated(new Date().toLocaleTimeString());
  };

  useEffect(() => {
    fetchDashboard().catch(console.error);
  
    const interval = setInterval(() => {
      fetchDashboard().catch(console.error);
    }, 15000);
  
    return () => clearInterval(interval);
  }, []);

  if (!summary) {
    return <div className="text-slate-600">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-slate-500 mt-1">
          Analytics overview of your AI-powered inbox
        </p>
        <p className="text-xs text-slate-400 mt-2">
    Last updated: {lastUpdated || "Not yet"}
  </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard title="Total Emails" value={summary.total_emails} icon={Mail} />
        <StatCard
          title="Classifications"
          value={summary.total_classifications}
          icon={Sparkles}
        />
        <StatCard
          title="Notifications"
          value={summary.unread_notifications}
          icon={Bell}
        />
        <StatCard
          title="Review Queue"
          value={summary.review_count}
          icon={AlertTriangle}
        />
        <StatCard
          title="Archived"
          value={summary.archived_emails}
          icon={Archive}
        />
        <StatCard
          title="Important"
          value={summary.important_count}
          icon={Inbox}
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl border shadow-sm p-6">
          <h2 className="text-lg font-semibold text-slate-900">
            Classification Distribution
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Emails grouped by AI category
          </p>

          <div className="h-80 mt-6">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distribution}>
                <XAxis dataKey="category" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-2xl border shadow-sm p-6">
          <h2 className="text-lg font-semibold text-slate-900">
            Category Share
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Percentage split of classifications
          </p>

          <div className="h-80 mt-6">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={distribution}
                  dataKey="count"
                  nameKey="category"
                  outerRadius={110}
                  label
                >
                  {distribution.map((_, index) => (
                    <Cell key={index} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
} 