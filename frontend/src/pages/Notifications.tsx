import { useCallback, useEffect, useRef, useState } from "react";
import api from "../lib/api";
import { Button } from "@/components/ui/Button";
import { Bell, CheckCircle, XCircle, RefreshCw } from "lucide-react";
import { useToastStore } from "@/stores/toast-store";

type Notification = {
  id: string;
  user_id: string;
  email_message_id: string;
  type: string;
  title: string;
  message: string;
  status: string;
  created_at: string;
};

export default function Notifications() {
  const { addToast } = useToastStore();

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);
  const [actingId, setActingId] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const fetchNotifications = useCallback(async () => {
    setLoading(true);

    try {
      const res = await api.get<Notification[]>("/notifications/");
      setNotifications(res.data);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (error) {
      console.error("Notifications load error:", error);
      addToast("error", "Failed to load notifications.");
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  const fetchNotificationsRef = useRef(fetchNotifications);
  fetchNotificationsRef.current = fetchNotifications;

  const addToastRef = useRef(addToast);
  addToastRef.current = addToast;

  const markRead = async (id: string) => {
    setActingId(id);

    try {
      await api.post(`/notifications/${id}/read`);
      addToast("success", "Notification marked as read.");
      await fetchNotifications();
    } catch (error) {
      console.error("Mark read error:", error);
      addToast("error", "Failed to mark notification as read.");
    } finally {
      setActingId(null);
    }
  };

  const dismiss = async (id: string) => {
    setActingId(id);

    try {
      await api.post(`/notifications/${id}/dismiss`);
      addToast("success", "Notification dismissed.");
      await fetchNotifications();
    } catch (error) {
      console.error("Dismiss notification error:", error);
      addToast("error", "Failed to dismiss notification.");
    } finally {
      setActingId(null);
    }
  };

  useEffect(() => {
    let socket: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
    let closedByUs = false;

    const connect = () => {
      socket = new WebSocket("ws://127.0.0.1:8000/ws/notifications");

      socket.onopen = () => {
        console.log("Connected to Notification WebSocket");
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === "new_notification") {
            addToastRef.current(
              "success",
              data.message || "New notification received."
            );
            fetchNotificationsRef.current();
          }
        } catch (error) {
          console.error("WebSocket message parse error:", error);
        }
      };

      socket.onerror = () => {
        if (!closedByUs) {
          console.warn("WebSocket connection error");
        }
      };

      socket.onclose = () => {
        if (closedByUs) {
          return;
        }

        reconnectTimer = setTimeout(connect, 3000);
      };
    };

    fetchNotificationsRef.current();
    connect();

    return () => {
      closedByUs = true;

      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
      }

      if (socket) {
        socket.onopen = null;
        socket.onmessage = null;
        socket.onerror = null;
        socket.onclose = null;

        if (
          socket.readyState === WebSocket.OPEN ||
          socket.readyState === WebSocket.CONNECTING
        ) {
          socket.close();
        }
      }
    };
  }, []);

  const visibleNotifications = notifications.filter(
    (n) => n.status !== "dismissed"
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Notifications</h1>

          <p className="text-slate-500 mt-1">
            Action-required messages from your AI assistant
          </p>

          <p className="text-xs text-slate-400 mt-2">
            Last updated: {lastUpdated || "Not yet"}
          </p>
        </div>

        <Button
          variant="outline"
          onClick={fetchNotifications}
          isLoading={loading}
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Refresh
        </Button>
      </div>

      {visibleNotifications.length === 0 ? (
        <div className="bg-white border rounded-2xl shadow-sm p-10 text-center">
          <p className="text-slate-600 font-medium">No active notifications 🎉</p>
          <p className="text-sm text-slate-400 mt-2">
            Important emails and confirmation-needed items will appear here.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {visibleNotifications.map((n) => (
            <div
              key={n.id}
              className={`bg-white border rounded-2xl shadow-sm p-5 ${
                n.status === "read" ? "opacity-70" : ""
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <Bell className="w-5 h-5 text-blue-500" />
                    <h3 className="text-lg font-semibold text-slate-900">
                      {n.title}
                    </h3>
                  </div>

                  <p className="text-sm text-slate-500 mt-2">{n.message}</p>

                  <p className="text-xs text-slate-400 mt-3">
                    Created: {n.created_at}
                  </p>
                </div>

                <span
                  className={`px-3 py-1 rounded-full text-xs font-medium ${
                    n.status === "read"
                      ? "bg-slate-100 text-slate-600"
                      : "bg-blue-100 text-blue-700"
                  }`}
                >
                  {n.status}
                </span>
              </div>

              <div className="flex flex-col sm:flex-row gap-3 mt-5">
                <Button
                  variant="outline"
                  onClick={() => markRead(n.id)}
                  isLoading={actingId === n.id}
                  disabled={actingId === n.id || n.status === "read"}
                  className="gap-2"
                >
                  <CheckCircle className="w-4 h-4" />
                  Mark as Read
                </Button>

                <Button
                  onClick={() => dismiss(n.id)}
                  isLoading={actingId === n.id}
                  disabled={actingId === n.id}
                  className="gap-2"
                >
                  <XCircle className="w-4 h-4" />
                  Dismiss
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
} 