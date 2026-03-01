"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import API from "../../lib/api";
import { GeneratedAnswer, Session } from "@/types";

import SidebarHistory from "@/components/SidebarHistory";
import ControlPanel from "@/components/ControlPanel";
import AnswerCard from "@/components/AnswerCard";

import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Download, AlertCircle, FileText, LogOut } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

type ExportFormat = "docx" | "pdf" | "txt";

export default function Dashboard() {
  const router = useRouter();

  const [questionFile, setQuestionFile] = useState<File | null>(null);
  const [referenceFile, setReferenceFile] = useState<File | null>(null);
  const [questionnaireId, setQuestionnaireId] = useState<number | null>(null);
  const [answers, setAnswers] = useState<GeneratedAnswer[]>([]);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(null);
  const [totalQuestions, setTotalQuestions] = useState<number | null>(null);
  const [totalChunks, setTotalChunks] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const initializeDashboard = async () => {
      const token = localStorage.getItem("token");

      if (!token) {
        router.push("/");
        return;
      }

      try {
        await API.get("/auth/me");

        const qRes = await API.get("/questionnaires/my");
        const questionnaires = qRes.data.questionnaires || [];

        if (questionnaires.length > 0) {
          const latest = questionnaires[0];
          setQuestionnaireId(latest.id);
          setTotalQuestions(latest.total_questions);
        }

        const sRes = await API.get("/answers/sessions");
        setSessions(sRes.data.sessions || []);

        setAnswers([]);
        setSelectedSessionId(null);

      } catch {
        localStorage.removeItem("token");
        router.push("/login");
      }
    };

    initializeDashboard();
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/");
  };

  // session management
  const refreshSessions = async () => {
    try {
      const res = await API.get("/answers/sessions");
      setSessions(res.data.sessions || []);
    } catch {
      console.error("Failed to fetch sessions");
    }
  };

  const loadSession = async (sessionId: number) => {
    try {
      const res = await API.get(`/answers/session/${sessionId}`);
      setAnswers(res.data.results || []);
      setSelectedSessionId(sessionId);
    } catch {
      console.error("Failed to load session");
    }
  };

  // upload handlers
  const handleQuestionnaireUpload = async () => {
    if (!questionFile) {
      setError("Please select a questionnaire file.");
      return;
    }
    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append("file", questionFile);

    try {
      const res = await API.post("/questionnaires/upload", formData);
      setQuestionnaireId(res.data.questionnaire_id);
      setTotalQuestions(res.data.total_questions);
      setAnswers([]);
      setSelectedSessionId(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  const handleReferenceUpload = async () => {
    if (!referenceFile) {
      setError("Please select a reference file.");
      return;
    }
    setLoading(true);
    setError("");
    const formData = new FormData();
    formData.append("file", referenceFile);

    try {
      const res = await API.post("/references/upload", formData);
      setTotalChunks(res.data.total_chunks);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Upload failed.");
    } finally {
      setLoading(false);
    }
  };

  // generation handlers
  const handleGenerateAnswers = async () => {
    if (!questionnaireId) {
      setError("Upload questionnaire first.");
      return;
    }
    setLoading(true);
    setError("");

    try {
      const res = await API.post(`/answers/generate/${questionnaireId}`);
      setAnswers(res.data.results || []);
      setSelectedSessionId(res.data.generation_session_id || null);
      await refreshSessions();
    } catch (err: any) {
      setError(err.response?.data?.detail || "Generation failed.");
    } finally {
      setLoading(false);
    }
  };

  const saveAnswer = async (questionId: number, answerText: string) => {
    if (!selectedSessionId) return;
    try {
      await API.put(
        `/answers/session/${selectedSessionId}/answer/${questionId}`,
        { answer: answerText }
      );
      alert("Saved successfully.");
    } catch {
      alert("Failed to save.");
    }
  };

  const regenerateAnswer = async (questionId: number, index: number) => {
    if (!selectedSessionId) return;
    try {
      const res = await API.post(
        `/answers/session/${selectedSessionId}/regenerate/${questionId}`
      );
      const updated = [...answers];
      updated[index].answer = res.data.answer;
      updated[index].confidence_score = res.data.confidence_score;
      updated[index].citations = res.data.citations || [];
      setAnswers(updated);
    } catch {
      alert("Regeneration failed.");
    }
  };

  const handleAnswerTextChange = (questionId: number, newText: string) => {
    setAnswers(prev => prev.map(ans => 
      ans.question_id === questionId ? { ...ans, answer: newText } : ans
    ));
  };

  // export handlers
  const exportSession = async (format: ExportFormat) => {
    if (!selectedSessionId) return;

    try {
      const response = await API.get(
        `/answers/export/${selectedSessionId}/${format}`,
        { responseType: "blob" }
      );

      // preserve backend MIME type
      const blob = new Blob([response.data], {
        type: response.headers["content-type"],
      });

      const contentDisposition = response.headers["content-disposition"];
      let filename = `questionnaire_session.${format}`;

      if (contentDisposition) {
        const match = contentDisposition.match(/filename="?(.+?)"?$/);
        if (match?.[1]) {
          filename = match[1];
        }
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;

      document.body.appendChild(a);
      a.click();
      a.remove();

      window.URL.revokeObjectURL(url);

    } catch (err) {
      console.error(err);
      alert("Export failed.");
    }
  };

  const handleDeleteSession = async (sessionId: number) => {
    try {
      await API.delete(`/answers/session/${sessionId}`);

      if (selectedSessionId === sessionId) {
        setSelectedSessionId(null);
        setAnswers([]);
      }
      
      // Refresh the sidebar list
      refreshSessions();
    } catch (err) {
      alert("Failed to delete session.");
    }
  };

  return (
    <div className="h-screen w-full bg-slate-50 flex overflow-hidden font-sans">
      
      {/* History Sidebar */}
      <SidebarHistory 
        sessions={sessions}
        selectedSessionId={selectedSessionId}
        onLoadSession={loadSession} onDeleteSession={handleDeleteSession}
      />

      <main className="flex-1 h-full overflow-y-auto p-8 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
        
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
              Structured Questionnaire Automation
            </h1>
            <p className="text-slate-500 mt-1">
              Upload files, generate AI responses, and export the completed document.
            </p>
          </div>
          {selectedSessionId && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  size="lg"
                  className="bg-blue-600 hover:bg-blue-700 text-white shadow-md"
                >
                  <Download className="w-5 h-5 mr-2" />
                  Export Document
                </Button>
              </DropdownMenuTrigger>

              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => exportSession("docx")}>
                  Download as DOCX
                </DropdownMenuItem>

                <DropdownMenuItem onClick={() => exportSession("pdf")}>
                  Download as PDF
                </DropdownMenuItem>

                <DropdownMenuItem onClick={() => exportSession("txt")}>
                  Download as TXT
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}

          <Button 
              onClick={handleLogout} 
              variant="outline" 
              size="lg" 
              className="border-slate-200 text-slate-600 hover:bg-slate-100 shadow-sm"
          >
            <LogOut className="w-5 h-5 mr-2" /> Logout
          </Button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-md flex items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        )}

        {/* Upload & Generate Controls */}
        <ControlPanel 
          setQuestionFile={setQuestionFile}
          handleQuestionnaireUpload={handleQuestionnaireUpload}
          setReferenceFile={setReferenceFile}
          handleReferenceUpload={handleReferenceUpload}
          handleGenerateAnswers={handleGenerateAnswers}
          loading={loading}
          questionnaireId={questionnaireId}
          totalQuestions={totalQuestions}
          totalChunks={totalChunks}
        />

        <Separator className="my-8" />

        {/* Answers Workspace */}
        <div className="max-w-5xl mx-auto">
          {answers.length === 0 ? (
            <div className="text-center py-20 bg-white border border-dashed border-slate-300 rounded-xl">
              <FileText className="w-12 h-12 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-900">No Answers Generated Yet</h3>
              <p className="text-slate-500 mt-2 max-w-sm mx-auto">
                Select a past session from the sidebar or upload files and run the pipeline to start reviewing answers.
              </p>
            </div>
          ) : (
            <div>
              <div className="mb-6 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-slate-800">Review & Edit Answers</h2>
                <Badge variant="outline" className="text-slate-500">
                  {answers.length} Questions
                </Badge>
              </div>
              
              <div className="space-y-6">
                {answers.map((item, index) => (
                  <AnswerCard
                    key={item.question_id}
                    item={item}
                    index={index}
                    selectedSessionId={selectedSessionId}
                    onAnswerChange={handleAnswerTextChange}
                    onSave={saveAnswer}
                    onRegenerate={regenerateAnswer}
                  />
                ))}
              </div>
            </div>
          )}
        </div>

      </main>
    </div>
  );
}