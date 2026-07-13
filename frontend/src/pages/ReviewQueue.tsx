import { useEffect, useState } from "react";
import api from "../lib/api";
import { Button } from "@/components/ui/Button";
import { RefreshCw, AlertTriangle, Archive, CheckCircle } from "lucide-react";
import { useToastStore } from "@/stores/toast-store";

type ReviewItem = {
  classification_id: string;
  email_id: string;
  subject: string | null;
  sender_email: string | null;
  category: string;
  confidence: number;
  suggested_action: string;
  reason: string | null;
  created_at: string;
};

export default function ReviewQueue() {
  const { addToast } = useToastStore();
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const [items, setItems] = useState<ReviewItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [actingId, setActingId] = useState<string | null>(null);

  const fetchReviewQueue = async () => {
    setLoading(true);
    try {
      const res = await api.get<ReviewItem[]>("/review-queue/");
      setItems(res.data);
    } catch (err) {
      console.error("Review queue error:", err);
      addToast("error", "Failed to load review queue.");
    } finally {
      setLoading(false);
    }
    setLastUpdated(new Date().toLocaleTimeString());
  };

  const handleAction = async (emailId: string, action: "archive" | "keep") => {
    setActingId(emailId);

    try {
      await api.post(`/api/v1/review/${emailId}`, { action });

      addToast(
        "success",
        action === "archive"
          ? "Email archived successfully."
          : "Email kept in inbox."
      );

      await fetchReviewQueue();
    } catch (err) {
      console.error("Review action error:", err);
      addToast("error", "Failed to update review decision.");
    } finally {
      setActingId(null);
    }
  };

  useEffect(() => {
    fetchReviewQueue();
  
    const interval = setInterval(() => {
      fetchReviewQueue();
    }, 15000);
  
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Review Queue</h1>
          <p className="text-slate-500 mt-1">
            Emails that need your manual decision
          </p>
          <p className="text-xs text-slate-400 mt-2">
    Last updated: {lastUpdated || "Not yet"}
  </p>
        </div>

        <Button variant="outline" onClick={fetchReviewQueue} isLoading={loading}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {items.length === 0 ? (
        <div className="bg-white border rounded-2xl shadow-sm p-10 text-center">
          <p className="text-slate-600 font-medium">No review items 🎉</p>
          <p className="text-sm text-slate-400 mt-2">
            Emails marked as hold for review will appear here.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((item) => (
            <div
              key={item.classification_id}
              className="bg-white border rounded-2xl shadow-sm p-5"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-5 h-5 text-yellow-500" />
                    <h3 className="text-lg font-semibold text-slate-900">
                      {item.subject || "No Subject"}
                    </h3>
                  </div>

                  <p className="text-sm text-slate-500 mt-1">
                    {item.sender_email || "Unknown sender"}
                  </p>
                </div>

                <span className="px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700">
                  Needs Review
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-5">
                <div className="rounded-xl bg-slate-50 p-4">
                  <p className="text-xs text-slate-500">Category</p>
                  <p className="font-semibold text-slate-900 mt-1">
                    {item.category}
                  </p>
                </div>

                <div className="rounded-xl bg-slate-50 p-4">
                  <p className="text-xs text-slate-500">Confidence</p>
                  <p className="font-semibold text-slate-900 mt-1">
                    {(item.confidence * 100).toFixed(0)}%
                  </p>
                </div>

                <div className="rounded-xl bg-slate-50 p-4">
                  <p className="text-xs text-slate-500">Suggested Action</p>
                  <p className="font-semibold text-slate-900 mt-1">
                    {item.suggested_action}
                  </p>
                </div>
              </div>

              {item.reason && (
                <p className="text-sm text-slate-500 mt-4">{item.reason}</p>
              )}

              <div className="flex flex-col sm:flex-row gap-3 mt-5">
                <Button
                  variant="outline"
                  onClick={() => handleAction(item.email_id, "keep")}
                  isLoading={actingId === item.email_id}
                  disabled={actingId === item.email_id}
                  className="gap-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  Keep in Inbox
                </Button>

                <Button
                  onClick={() => handleAction(item.email_id, "archive")}
                  isLoading={actingId === item.email_id}
                  disabled={actingId === item.email_id}
                  className="gap-2"
                >
                  <Archive className="w-4 h-4" />
                  Archive
                </Button>
              </div>

              <p className="text-xs text-slate-400 mt-4">
                Created: {item.created_at}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}