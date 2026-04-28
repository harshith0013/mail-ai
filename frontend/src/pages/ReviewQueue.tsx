import { useApi } from "@/hooks/use-api";
import { fetchReviewQueue } from "@/lib/api";
import { EmptyState } from "@/components/ui/EmptyState";
import { ListTodo, Check, X } from "lucide-react";
import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Skeleton } from "@/components/ui/Skeleton";
import { ConfidenceBar } from "@/components/ui/ConfidenceBar";
import { Button } from "@/components/ui/Button";
import { useToastStore } from "@/stores/toast-store";

export default function ReviewQueue() {
  const { data: queue, isLoading, error, refetch } = useApi(fetchReviewQueue);
  const { addToast } = useToastStore();

  if (error) {
    return <div className="text-destructive p-4">Error: {error.message}</div>;
  }

  const handleAction = (id: string, action: 'approve' | 'reject') => {
    // Optimistic UI or API call here. The current API doesn't have an endpoint for this yet, so just simulating
    addToast("success", `Classification ${action}d successfully`);
    refetch(); 
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Review Queue</h1>
        <p className="text-muted-foreground mt-1">Review uncertain classifications or items requiring confirmation</p>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2].map((i) => <Skeleton key={i} className="w-full h-40 rounded-xl" />)}
        </div>
      ) : !queue || queue.length === 0 ? (
        <EmptyState
          icon={<ListTodo className="w-10 h-10" />}
          title="Inbox Zero!"
          description="There are no emails waiting for your review. The AI is confident about everything else."
        />
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
          {queue.map((item, i) => (
             <motion.div
               key={item.classification_id}
               initial={{ opacity: 0, y: 10 }}
               animate={{ opacity: 1, y: 0 }}
               transition={{ delay: i * 0.05 }}
             >
              <Card className="hover:shadow-md transition-shadow h-full flex flex-col">
                <CardContent className="p-6 flex-1 flex flex-col gap-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <h3 className="font-semibold">{item.subject || "No Subject"}</h3>
                      <p className="text-sm text-muted-foreground">{item.sender_email}</p>
                    </div>
                    <Badge variant="outline">{item.category}</Badge>
                  </div>
                  
                  <div className="bg-muted/50 rounded-lg p-3 space-y-2 text-sm">
                    <div className="flex justify-between text-muted-foreground">
                      <span>Suggested Action:</span>
                      <span className="font-medium text-foreground">{item.suggested_action.replace('_', ' ')}</span>
                    </div>
                    <div className="flex justify-between items-center text-muted-foreground">
                      <span className="w-24">Confidence:</span>
                      <ConfidenceBar value={item.confidence} />
                    </div>
                  </div>

                  <p className="text-sm text-muted-foreground italic line-clamp-2">
                    "...{item.reason}..."
                  </p>

                  <div className="mt-auto pt-4 flex gap-2">
                    <Button 
                      variant="outline" 
                      className="flex-1"
                      onClick={() => handleAction(item.classification_id, 'reject')}
                    >
                      <X className="w-4 h-4 mr-2" />
                      Reject
                    </Button>
                    <Button 
                      className="flex-1"
                      onClick={() => handleAction(item.classification_id, 'approve')}
                    >
                      <Check className="w-4 h-4 mr-2" />
                      Approve
                    </Button>
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
