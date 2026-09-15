import { useState } from "react";
import { X, Copy, Sparkles, FileText } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { API_BASE_URL } from "@/lib/api";

export default function EmailDetailModal({
  email,
  onClose,
}: {
  email: any;
  onClose: () => void;
}) {
  const [reply, setReply] = useState<string | null>(null);
  const [isGeneratingReply, setIsGeneratingReply] = useState(false);

  const [summary, setSummary] = useState<any>(null);
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);

  if (!email) return null;

  const generateSummary = async () => {
    setIsGeneratingSummary(true);

    try {
      const res = await fetch(
        `${API_BASE_URL}/email-summary/${email.email_id}`,
        { method: "POST" }
      );

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Failed to generate summary");
      }

      setSummary(data);
    } catch (error) {
      console.error("Summary generation error:", error);
    } finally {
      setIsGeneratingSummary(false);
    }
  };

  const generateReply = async () => {
    setIsGeneratingReply(true);

    try {
      const res = await fetch(
        `${API_BASE_URL}/email-reply/${email.email_id}`,
        { method: "POST" }
      );

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Failed to generate reply");
      }

      setReply(data.reply);
    } catch (error) {
      console.error("Reply generation error:", error);
    } finally {
      setIsGeneratingReply(false);
    }
  };

  const copyReply = async () => {
    if (!reply) return;
    await navigator.clipboard.writeText(reply);
  };

  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex justify-end">
      <div className="w-full max-w-2xl h-full bg-white shadow-xl overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-xl font-bold">Email Analysis</h2>

          <Button variant="outline" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        <div className="p-6 space-y-6">
          <div>
            <p className="text-sm text-slate-500">Subject</p>
            <h3 className="text-lg font-semibold">
              {email.subject || "No Subject"}
            </h3>
          </div>

          <div>
            <p className="text-sm text-slate-500">Sender</p>
            <p>{email.sender_email || "Unknown sender"}</p>
          </div>

          <div>
            <p className="text-sm text-slate-500">Snippet</p>
            <p>{email.snippet || "No snippet available"}</p>
          </div>

          <div className="border rounded-2xl p-5 bg-blue-50">
            <h3 className="font-bold mb-4">AI Analysis</h3>

            <div className="space-y-3">
              <p>
                <strong>Category:</strong>{" "}
                {email.classification || "Not Classified"}
              </p>

              <p>
                <strong>Confidence:</strong>{" "}
                {email.confidence !== null && email.confidence !== undefined
                  ? `${(email.confidence * 100).toFixed(0)}%`
                  : "N/A"}
              </p>

              <p>
                <strong>Suggested Action:</strong>{" "}
                {email.suggested_action || "N/A"}
              </p>

              <p>
                <strong>Reasoning:</strong>{" "}
                {email.reason || "No explanation available"}
              </p>
            </div>
          </div>

          <div className="border rounded-2xl p-5 bg-violet-50">
            <div className="flex items-center justify-between gap-3">
              <h3 className="font-bold text-slate-900">AI Summary</h3>

              <Button
                onClick={generateSummary}
                isLoading={isGeneratingSummary}
              >
                <FileText className="w-4 h-4 mr-2" />
                Generate Summary
              </Button>
            </div>

            {summary ? (
              <div className="mt-4 space-y-4">
                <p className="text-sm text-slate-700">{summary.summary}</p>

                <div className="grid grid-cols-2 gap-3">
                  <div className="rounded-xl bg-white border p-3">
                    <p className="text-xs text-slate-500">Priority</p>
                    <p className="font-semibold">
                      {summary.priority || "N/A"}
                    </p>
                  </div>

                  <div className="rounded-xl bg-white border p-3">
                    <p className="text-xs text-slate-500">Needs Reply</p>
                    <p className="font-semibold">
                      {summary.needs_reply ? "Yes" : "No"}
                    </p>
                  </div>
                </div>

                <div>
                  <p className="font-semibold text-sm">Action Items</p>
                  <ul className="list-disc ml-5 mt-2 text-sm text-slate-700">
                    {summary.action_items?.map((item: string) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <p className="text-sm text-slate-500 mt-4">
                Generate a Gemini-powered summary and action items for this
                email.
              </p>
            )}
          </div>

          <div className="border rounded-2xl p-5 bg-slate-50">
            <div className="flex items-center justify-between gap-3">
              <h3 className="font-bold text-slate-900">
                AI Suggested Reply
              </h3>

              <Button
                onClick={generateReply}
                isLoading={isGeneratingReply}
              >
                <Sparkles className="w-4 h-4 mr-2" />
                Generate Reply
              </Button>
            </div>

            {reply ? (
              <div className="mt-4 rounded-xl bg-white border p-4">
                <pre className="whitespace-pre-wrap text-sm text-slate-700 font-sans">
                  {reply}
                </pre>

                <Button
                  className="mt-4"
                  variant="outline"
                  onClick={copyReply}
                >
                  <Copy className="w-4 h-4 mr-2" />
                  Copy Reply
                </Button>
              </div>
            ) : (
              <p className="text-sm text-slate-500 mt-4">
                Generate a professional response based on this email.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}