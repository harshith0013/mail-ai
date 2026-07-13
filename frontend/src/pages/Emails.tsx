import { useEffect, useMemo, useState } from "react";
import api from "../lib/api";
import { Button } from "@/components/ui/Button";
import {
  Sparkles,
  RefreshCw,
  Archive,
  MailOpen,
  Mail,
  Trash2,
  Search,
} from "lucide-react";
import { useToastStore } from "@/stores/toast-store";
import EmailDetailModal from "@/components/ui/EmailDetailModal";

type Email = {
  id: string;
  subject: string | null;
  sender_email: string | null;
  snippet: string | null;
  created_at: string;
  is_read: boolean;
  is_archived: boolean;
};

type FilterType = "all" | "inbox" | "archived" | "read" | "unread";

export default function Emails() {
  const { addToast } = useToastStore();
  const [isSemanticMode, setIsSemanticMode] = useState(false);
  const [emails, setEmails] = useState<Email[]>([]);
  const [loading, setLoading] = useState(false);
  const [classifyingId, setClassifyingId] = useState<string | null>(null);
  const [actingId, setActingId] = useState<string | null>(null);
  const [selectedEmail, setSelectedEmail] = useState<any>(null);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<FilterType>("all");
  const openEmailDetails = async (id: string) => {
    try {
    const res = await api.get(`/email-details/${id}`);
    setSelectedEmail(res.data);
    } catch (error) {
    console.error("Email details error:", error);
    addToast("error", "Failed to load email details.");
    }
    };

    const semanticSearch = async () => {
      if (!search.trim()) {
        fetchEmails();
        return;
      }
    
      setLoading(true);
    
      try {
        const res = await api.post<Email[]>("/semantic-search/", {
          query: search,
          limit: 10,
        });
    
        setEmails(res.data);
        addToast("success", "Semantic search completed.");
      } catch (error) {
        console.error("Semantic search error:", error);
        addToast("error", "Semantic search failed.");
      } finally {
        setLoading(false);
      }
    };
    

  const fetchEmails = async () => {
    setLoading(true);

    try {
      const res = await api.get<Email[]>("/emails/");
      setEmails(res.data);
    } catch {
      addToast("error", "Failed to load emails.");
    } finally {
      setLoading(false);
    }
  };

  const classifyEmail = async (emailId: string) => {
    setClassifyingId(emailId);

    try {
      const res = await api.post(`/api/v1/classify/${emailId}`);
      addToast("success", `Classified: ${res.data.final_action}`);
      await fetchEmails();
    } catch {
      addToast("error", "Failed to classify email.");
    } finally {
      setClassifyingId(null);
    }
  };

  const archiveEmail = async (id: string) => {
    setActingId(id);

    try {
      await api.post(`/email-actions/${id}/archive`);
      addToast("success", "Email archived successfully.");
      await fetchEmails();
    } catch {
      addToast("error", "Failed to archive email.");
    } finally {
      setActingId(null);
    }
  };

  const markRead = async (id: string) => {
    setActingId(id);

    try {
      await api.post(`/email-actions/${id}/mark-read`);
      addToast("success", "Email marked as read.");
      await fetchEmails();
    } catch {
      addToast("error", "Failed to mark email as read.");
    } finally {
      setActingId(null);
    }
  };

  const markUnread = async (id: string) => {
    setActingId(id);

    try {
      await api.post(`/email-actions/${id}/mark-unread`);
      addToast("success", "Email marked as unread.");
      await fetchEmails();
    } catch {
      addToast("error", "Failed to mark email as unread.");
    } finally {
      setActingId(null);
    }
  };

  const deleteEmail = async (id: string) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this email from the app?"
    );

    if (!confirmed) return;

    setActingId(id);

    try {
      await api.delete(`/email-actions/${id}`);
      addToast("success", "Email deleted successfully.");
      await fetchEmails();
    } catch {
      addToast("error", "Failed to delete email.");
    } finally {
      setActingId(null);
    }
  };

  const filteredEmails = useMemo(() => {
    const q = search.toLowerCase().trim();

    return emails.filter((email) => {
      const matchesSearch =
        !q ||
        (email.subject || "").toLowerCase().includes(q) ||
        (email.sender_email || "").toLowerCase().includes(q) ||
        (email.snippet || "").toLowerCase().includes(q);

      const matchesFilter =
        filter === "all" ||
        (filter === "inbox" && !email.is_archived) ||
        (filter === "archived" && email.is_archived) ||
        (filter === "read" && email.is_read) ||
        (filter === "unread" && !email.is_read);

      return matchesSearch && matchesFilter;
    });
  }, [emails, search, filter]);

  useEffect(() => {
    fetchEmails();

    const interval = setInterval(() => {
      fetchEmails();
    }, 15000);

    return () => clearInterval(interval);
  }, []);

  const filterButtonClass = (value: FilterType) =>
    filter === value
      ? "bg-blue-600 text-white"
      : "bg-white text-slate-700 border hover:bg-slate-50";

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Emails</h1>
          <p className="text-slate-500 mt-1">Synced emails from Gmail</p>
        </div>

        <Button variant="outline" onClick={fetchEmails} isLoading={loading}>
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="bg-white border rounded-2xl shadow-sm p-4 space-y-4">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by subject, sender, or snippet..."
            className="w-full h-10 pl-10 pr-4 rounded-xl border text-sm outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setFilter("all")}
            className={`px-4 py-2 rounded-xl text-sm ${filterButtonClass("all")}`}
          >
            All
          </button>

          <button
            onClick={() => setFilter("inbox")}
            className={`px-4 py-2 rounded-xl text-sm ${filterButtonClass("inbox")}`}
          >
            Inbox
          </button>

          <button
            onClick={() => setFilter("archived")}
            className={`px-4 py-2 rounded-xl text-sm ${filterButtonClass("archived")}`}
          >
            Archived
          </button>

          <button
            onClick={() => setFilter("read")}
            className={`px-4 py-2 rounded-xl text-sm ${filterButtonClass("read")}`}
          >
            Read
          </button>
          <Button onClick={semanticSearch} isLoading={loading}>
  AI Search
</Button>
<div className="flex gap-3">
  <div className="relative flex-1">
    <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
    <input
      value={search}
      onChange={(e) => setSearch(e.target.value)}
      placeholder="Search by subject, sender, snippet, or meaning..."
      className="w-full h-10 pl-10 pr-4 rounded-xl border text-sm outline-none focus:ring-2 focus:ring-blue-500"
    />
  </div>

  <Button onClick={semanticSearch} isLoading={loading}>
    AI Search
  </Button>
</div>

          <button
            onClick={() => setFilter("unread")}
            className={`px-4 py-2 rounded-xl text-sm ${filterButtonClass("unread")}`}
          >
            Unread
          </button>
        </div>

        <p className="text-sm text-slate-500">
          Showing {filteredEmails.length} of {emails.length} emails
        </p>
      </div>

      <div className="bg-white border rounded-2xl shadow-sm overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-100">
            <tr>
              <th className="p-4 text-sm text-slate-600">Subject</th>
              <th className="p-4 text-sm text-slate-600">Sender</th>
              <th className="p-4 text-sm text-slate-600">Status</th>
              <th className="p-4 text-sm text-slate-600">Created</th>
              <th className="p-4 text-sm text-slate-600">Actions</th>
            </tr>
          </thead>

          <tbody>
            {filteredEmails.map((email) => (
              <tr key={email.id} className="border-t align-top">
                <td className="p-4">
                  <p className="font-medium text-slate-800">
                  <button
  className="font-medium text-blue-600 hover:underline"
  onClick={() => openEmailDetails(email.id)}
>
  {email.subject || "No Subject"}
</button>
</p>


                  {email.snippet && (
                    <p className="text-sm text-slate-400 mt-1 line-clamp-2">
                      {email.snippet}
                    </p>
                  )}
                </td>

                <td className="p-4 text-slate-500">
                  {email.sender_email || "Unknown"}
                </td>

                <td className="p-4">
                  <div className="flex flex-col gap-2">
                    <span className="w-fit rounded-full px-3 py-1 text-xs bg-slate-100 text-slate-700">
                      {email.is_read ? "Read" : "Unread"}
                    </span>

                    <span className="w-fit rounded-full px-3 py-1 text-xs bg-slate-100 text-slate-700">
                      {email.is_archived ? "Archived" : "Inbox"}
                    </span>
                  </div>
                </td>

                <td className="p-4 text-slate-400 text-sm">
                  {email.created_at}
                </td>

                <td className="p-4">
                  <div className="flex flex-wrap gap-2">
                    <Button
                      size="sm"
                      onClick={() => classifyEmail(email.id)}
                      isLoading={classifyingId === email.id}
                      disabled={
                        classifyingId === email.id || actingId === email.id
                      }
                    >
                      <Sparkles className="w-4 h-4 mr-2" />
                      Classify
                    </Button>

                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => archiveEmail(email.id)}
                      isLoading={actingId === email.id}
                      disabled={actingId === email.id || email.is_archived}
                    >
                      <Archive className="w-4 h-4 mr-2" />
                      Archive
                    </Button>

                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => markRead(email.id)}
                      isLoading={actingId === email.id}
                      disabled={actingId === email.id || email.is_read}
                    >
                      <MailOpen className="w-4 h-4 mr-2" />
                      Read
                    </Button>

                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => markUnread(email.id)}
                      isLoading={actingId === email.id}
                      disabled={actingId === email.id || !email.is_read}
                    >
                      <Mail className="w-4 h-4 mr-2" />
                      Unread
                    </Button>

                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => deleteEmail(email.id)}
                      isLoading={actingId === email.id}
                      disabled={actingId === email.id}
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      Delete
                    </Button>
                  </div>
                </td>
              </tr>
            ))}

            {filteredEmails.length === 0 && (
              <tr>
                <td className="p-6 text-slate-500" colSpan={5}>
                  No emails matched your search or filter.
                </td>
              </tr>
            )}
            {selectedEmail && (
  <EmailDetailModal
    email={selectedEmail}
    onClose={() => setSelectedEmail(null)}
  />
)}
          </tbody>
        </table>
      </div>
    </div>
  );
}
