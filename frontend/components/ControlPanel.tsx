import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload, FileText, Play, Database, RefreshCw } from "lucide-react";

interface ControlPanelProps {
  setQuestionFile: (file: File | null) => void;
  handleQuestionnaireUpload: () => void;
  setReferenceFile: (file: File | null) => void;
  handleReferenceUpload: () => void;
  handleGenerateAnswers: () => void;
  loading: boolean;
  questionnaireId: number | null;
  totalQuestions: number | null;
  totalChunks: number | null;
}

export default function ControlPanel({
  setQuestionFile, handleQuestionnaireUpload,
  setReferenceFile, handleReferenceUpload,
  handleGenerateAnswers, loading, questionnaireId,
  totalQuestions, totalChunks
}: ControlPanelProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      {/* Questionnaire Upload */}
      <Card className="shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold flex items-center gap-2 text-slate-700">
            <FileText className="w-4 h-4 text-blue-500" /> 1. Questionnaire
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Input type="file" accept=".pdf,.txt,.docx" className="mb-3 cursor-pointer" onChange={(e) => setQuestionFile(e.target.files?.[0] || null)} />
          <Button onClick={handleQuestionnaireUpload} disabled={loading} variant="secondary" size="sm" className="w-full">
            <Upload className="w-4 h-4 mr-2" /> Upload
          </Button>
          {totalQuestions !== null && <p className="text-xs text-slate-500 mt-3 text-center">Parsed {totalQuestions} questions.</p>}
        </CardContent>
      </Card>

      {/* References Upload */}
      <Card className="shadow-sm">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold flex items-center gap-2 text-slate-700">
            <Database className="w-4 h-4 text-green-500" /> 2. References
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Input type="file" accept=".pdf,.txt,.docx" className="mb-3 cursor-pointer" onChange={(e) => setReferenceFile(e.target.files?.[0] || null)} />
          <Button onClick={handleReferenceUpload} disabled={loading} variant="secondary" size="sm" className="w-full">
            <Upload className="w-4 h-4 mr-2" /> Store Knowledge
          </Button>
          {totalChunks !== null && <p className="text-xs text-slate-500 mt-3 text-center">Stored {totalChunks} chunks.</p>}
        </CardContent>
      </Card>

      {/* Generate Action */}
      <Card className="shadow-sm border-blue-100 bg-blue-50/30">
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold flex items-center gap-2 text-slate-700">
            <Play className="w-4 h-4 text-purple-500" /> 3. Run Pipeline
          </CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col justify-center h-[calc(100%-3rem)]">
          <Button onClick={handleGenerateAnswers} disabled={loading || !questionnaireId} className="w-full h-12 text-md shadow-sm">
            {loading ? <><RefreshCw className="w-5 h-5 mr-2 animate-spin" /> Processing...</> : <><Play className="w-5 h-5 mr-2" /> Generate Answers</>}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}