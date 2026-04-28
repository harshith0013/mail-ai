import { motion } from "framer-motion";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Mail, RefreshCw } from "lucide-react";
import { api } from "@/lib/api"; // oops, need axios directly for a specific call, wait, I can add a function or just do it inline
import { useState } from "react";
import { useToastStore } from "@/stores/toast-store";

export default function Settings() {
  const { addToast } = useToastStore();
  const [isSyncing, setIsSyncing] = useState(false);

  const handleConnect = () => {
    window.location.href = "http://127.0.0.1:8000/api/v1/auth/google/login";
  };

  const handleSync = async () => {
    // Hardcoded account id for demo purposes. Real app would fetch user accounts.
    setIsSyncing(true);
    try {
      /* In a complete app, we'd GET accounts, but to simplify the UI flow here: */
      const res = await fetch("http://127.0.0.1:8000/gmail-accounts/");
      const accounts = await res.json();
      if (accounts && accounts.length > 0) {
        const acc = accounts[0];
        const syncRes = await fetch(`http://127.0.0.1:8000/api/v1/gmail/sync/${acc.id}`);
        const result = await syncRes.json();
        if (syncRes.ok) {
           addToast("success", `Synced successfully. Picked up ${result.saved_count} new emails.`);
        } else {
           addToast("error", result.detail || "Sync failed");
        }
      } else {
        addToast("warning", "No connected Gmail accounts found.");
      }
    } catch (e: any) {
      addToast("error", "Error connecting to server for sync.");
    } finally {
      setIsSyncing(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-8 max-w-3xl">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground mt-1">Manage your account and integration settings</p>
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
              Connect your Gmail account to allow Mail AI to automatically classify your incoming emails and manage your inbox.
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              <Button onClick={handleConnect} className="gap-2">
                Connect Gmail
              </Button>
              <Button variant="outline" onClick={handleSync} isLoading={isSyncing} className="gap-2">
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
                 <div className="h-10 w-full rounded-md border border-input bg-muted/50 px-3 py-2 text-sm text-muted-foreground">Demo User</div>
               </div>
               <div className="grid gap-2">
                 <label className="text-sm font-medium">Email</label>
                 <div className="h-10 w-full rounded-md border border-input bg-muted/50 px-3 py-2 text-sm text-muted-foreground">demo@mail-ai.app</div>
               </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </motion.div>
  );
}
