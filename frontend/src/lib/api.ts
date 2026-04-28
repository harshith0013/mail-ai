import axios from "axios";
import { 
  DashboardSummary, 
  EmailMessage, 
  Notification, 
  ReviewQueueItem, 
  ClassificationResult, 
  ClassifyResponse, 
  SyncResponse 
} from "@/types";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const fetchDashboardSummary = async (): Promise<DashboardSummary> => {
  const res = await api.get("/dashboard/summary");
  return res.data;
};

export const fetchEmails = async (): Promise<EmailMessage[]> => {
  const res = await api.get("/emails/");
  return res.data;
};

export const fetchNotifications = async (): Promise<Notification[]> => {
  const res = await api.get("/notifications/");
  return res.data;
};

export const fetchReviewQueue = async (): Promise<ReviewQueueItem[]> => {
  const res = await api.get("/review-queue/");
  return res.data;
};

export const fetchClassificationResults = async (): Promise<ClassificationResult[]> => {
  const res = await api.get("/classification-results/");
  return res.data;
};

export const classifyEmail = async (emailId: string): Promise<ClassifyResponse> => {
  const res = await api.post(`/api/v1/classify/${emailId}`);
  return res.data;
};

export const syncGmail = async (accountId: string): Promise<SyncResponse> => {
  const res = await api.get(`/api/v1/gmail/sync/${accountId}`);
  return res.data;
};

export default api;
