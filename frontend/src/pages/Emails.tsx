import { fetchEmails, classifyEmail } from "@/lib/api";
import { useApi } from "@/hooks/use-api";
import { DataTable, ColumnDef } from "@/components/ui/DataTable";
import { EmailMessage } from "@/types";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { motion } from "framer-motion";
import { useToastStore } from "@/stores/toast-store";
import { useState } from "react";
import { Modal } from "@/components/ui/Modal";

export default function Emails() {
  const { data: emails, isLoading, error, refetch } = useApi(fetchEmails);
  const { addToast } = useToastStore();
  const [classifyingId, setClassifyingId] = useState<string | null>(null);
  
  const [selectedEmail, setSelectedEmail] = useState<EmailMessage | null>(null);

  const handleClassify = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setClassifyingId(id);
    try {
      await classifyEmail(id);
      addToast("success", "Email classified successfully");
      refetch();
    } catch (err: any) {
      addToast("error", err.message || "Failed to classify email");
    } finally {
      setClassifyingId(null);
    }
  };

  const columns: ColumnDef<EmailMessage>[] = [
    {
      key: "subject",
      header: "Subject",
      filterMethod: (item, query) => (item.subject || "").toLowerCase().includes(query.toLowerCase()),
      cell: (item) => <span className="font-medium">{item.subject || "No Subject"}</span>,
    },
    {
      key: "sender",
      header: "Sender",
      filterMethod: (item, query) => (item.sender_email || "").toLowerCase().includes(query.toLowerCase()),
      cell: (item) => <span className="text-muted-foreground">{item.sender_email || "Unknown"}</span>,
    },
    {
      key: "date",
      header: "Date",
      cell: (item) => <span className="text-muted-foreground">{new Date(item.created_at).toLocaleDateString()}</span>,
    },
    {
      key: "actions",
      header: "Actions",
      cell: (item) => (
        <div className="flex justify-end">
          <Button 
            variant="outline" 
            size="sm"
            onClick={(e) => handleClassify(item.id, e)}
            isLoading={classifyingId === item.id}
          >
            Classify
          </Button>
        </div>
      ),
    }
  ];

  if (error) {
    return <div className="text-destructive p-4">Error: {error.message}</div>;
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Emails</h1>
        <p className="text-muted-foreground mt-1">Manage and classify your emails</p>
      </div>

      <DataTable 
        data={emails || []} 
        columns={columns} 
        isLoading={isLoading} 
        searchable 
        searchPlaceholder="Filter by subject or sender..."
        onRowClick={(email) => setSelectedEmail(email)}
      />

      <Modal 
        isOpen={!!selectedEmail} 
        onClose={() => setSelectedEmail(null)}
        title="Email Details"
      >
        {selectedEmail && (
          <div className="space-y-4">
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Subject</div>
              <div className="text-base font-medium">{selectedEmail.subject || "No Subject"}</div>
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Sender</div>
              <div className="text-base">{selectedEmail.sender_email}</div>
            </div>
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Date</div>
              <div className="text-base">{new Date(selectedEmail.created_at).toLocaleString()}</div>
            </div>
            <div className="pt-4 flex justify-end">
              <Button onClick={(e) => {
                 setSelectedEmail(null);
                 handleClassify(selectedEmail.id, e);
              }}>
                Trigger Classification
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </motion.div>
  );
}
