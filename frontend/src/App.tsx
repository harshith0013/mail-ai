import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Layout } from "@/components/layout/Layout";
import Dashboard from "@/pages/Dashboard";
import Emails from "@/pages/Emails";
import Notifications from "@/pages/Notifications";
import ReviewQueue from "@/pages/ReviewQueue";
import Settings from "@/pages/Settings";
import { AnimatePresence } from "framer-motion";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/emails" element={<Emails />} />
            <Route path="/notifications" element={<Notifications />} />
            <Route path="/review-queue" element={<ReviewQueue />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </AnimatePresence>
      </Layout>
    </BrowserRouter>
  );
}
