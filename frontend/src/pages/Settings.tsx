import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Mail, RefreshCw, CheckCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { useToastStore } from "@/stores/toast-store";
import { API_BASE_URL } from "@/lib/api";

export default function Settings() {
  const { addToast } = useToastStore();
  const [autoSyncEnabled] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [gmailAccountId, setGmailAccountId] = useState<string | null>(null);
  const [lastSynced, setLastSynced] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const connected = params.get("gmail_connected");
    const accountId = params.get("gmail_account_id");

    if (connected === "true" && accountId) {
      localStorage.setItem("gmail_account_id", accountId);
      setGmailAccountId(accountId);

      addToast("success", "Gmail connected successfully.");

      window.history.replaceState({}, "", "/settings");
      return;
    }

    const savedAccountId = localStorage.getItem("gmail_account_id");
    const savedLastSynced = localStorage.getItem("last_gmail_sync");

    if (savedAccountId) {
      setGmailAccountId(savedAccountId);
    }

    if (savedLastSynced) {
      setLastSynced(savedLastSynced);
    }
  }, [addToast]);

  const handleConnect = () => {
    window.location.href = `${API_BASE_URL}/api/v1/auth/google/login`;
  };

  const handleSync = async () => {
    setIsSyncing(true);

    try {
      let accountId =
        gmailAccountId || localStorage.getItem("gmail_account_id");

      if (!accountId) {
        const res = await fetch(`${API_BASE_URL}/gmail-accounts/`);

        if (!res.ok) {
          addToast("error", "Unable to fetch Gmail accounts.");
          return;
        }

        const accounts = await res.json();

        if (!accounts || accounts.length === 0) {
          addToast("warning", "No connected Gmail accounts found.");
          return;
        }

        accountId = accounts[0].id;

        localStorage.setItem("gmail_account_id", accountId || "");
        setGmailAccountId(accountId);
      }

      const syncRes = await fetch(
        `${API_BASE_URL}/api/v1/gmail/sync/${accountId}`
      );

      const result = await syncRes.json();

      if (!syncRes.ok) {
        addToast("error", result.detail || "Sync failed.");
        return;
      }

      const syncTime = new Date().toLocaleTimeString();

      localStorage.setItem("last_gmail_sync", syncTime);
      setLastSynced(syncTime);

      addToast(
        "success",
        `Synced successfully. Picked up ${result.saved_count} new emails.`
      );
    } catch (error) {
      console.error("Sync error:", error);
      addToast("error", "Error connecting to server for sync.");
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8 max-w-3xl"
    >
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">
          Manage your account and integration settings
        </p>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Mail className="w-5 h-5 text-red-500" />
              Gmail Integration
            </CardTitle>
          </CardHeader>

          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Connect your Gmail account to allow Mail AI to classify incoming
              emails and manage your inbox.
            </p>

            {gmailAccountId ? (
              <div className="flex items-center gap-2 rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
                <CheckCircle className="h-4 w-4" />
                <span>Gmail connected successfully.</span>
              </div>
            ) : (
              <div className="rounded-lg border bg-muted/40 px-4 py-3 text-sm text-muted-foreground">
                Gmail is not connected yet.
              </div>
            )}

            {gmailAccountId && (
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">
                  Account ID: {gmailAccountId}
                </p>

                <p className="text-xs text-muted-foreground">
                  Last synced: {lastSynced || "Not yet"}
                </p>

                <p className="text-xs text-muted-foreground">
                  Auto Sync:{" "}
                  {autoSyncEnabled ? "Enabled — every 5 minutes" : "Disabled"}
                </p>
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-3">
              <Button onClick={handleConnect} className="gap-2">
                {gmailAccountId ? "Reconnect Gmail" : "Connect Gmail"}
              </Button>

              <Button
                variant="outline"
                onClick={handleSync}
                isLoading={isSyncing}
                className="gap-2"
                disabled={!gmailAccountId || isSyncing}
              >
                <RefreshCw className="w-4 h-4" />
                Force Sync Now
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Profile Details</CardTitle>
          </CardHeader>

          <CardContent>
            <div className="space-y-4">
              <div className="grid gap-2">
                <label className="text-sm font-medium">Name</label>
                <div className="h-10 w-full rounded-md border border-input bg-muted/50 px-3 py-2 text-sm text-muted-foreground">
                  Demo User
                </div>
              </div>

              <div className="grid gap-2">
                <label className="text-sm font-medium">Email</label>
                <div className="h-10 w-full rounded-md border border-input bg-muted/50 px-3 py-2 text-sm text-muted-foreground">
                  demo@mail-ai.app
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}