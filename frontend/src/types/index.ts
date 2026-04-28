export interface DashboardSummary {
  total_emails: number;
  total_classifications: number;
  total_notifications: number;
  archived_emails: number;
  important_count: number;
  uncertain_count: number;
}

export interface EmailMessage {
  id: string;
  user_id: string;
  subject: string | null;
  sender_email: string | null;
  created_at: string;
}

export interface ClassificationResult {
  id: string;
  email_message_id: string;
  category: string;
  importance: string;
  suggested_action: string;
  confidence: number;
  needs_confirmation: boolean;
  deadline_at: string | null;
  reason: string | null;
  created_at: string;
}

export interface Notification {
  id: string;
  user_id: string;
  email_message_id: string;
  type: string;
  title: string;
  message: string;
  status: string;
  created_at: string;
}

export interface ReviewQueueItem {
  classification_id: string;
  email_id: string;
  subject: string | null;
  sender_email: string | null;
  category: string;
  confidence: number;
  suggested_action: string;
  reason: string | null;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  name: string | null;
  google_sub: string | null;
  created_at: string;
  updated_at: string;
}

export interface GmailAccount {
  id: string;
  user_id: string;
  gmail_email: string;
  created_at: string;
}

export interface ClassifyResponse {
  message: string;
  classification_id: string;
  final_action: string;
  notification_id: string | null;
  result: any;
}

export interface SyncResponse {
  message: string;
  saved_count: number;
  fetched_count: number;
}
