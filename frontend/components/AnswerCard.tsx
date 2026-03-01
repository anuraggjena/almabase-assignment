import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { RefreshCw, Save, BookOpen, ChevronDown, ChevronUp } from "lucide-react";
import { GeneratedAnswer } from "@/types";

interface AnswerCardProps {
  item: GeneratedAnswer;
  index: number;
  selectedSessionId: number | null;
  onAnswerChange: (id: number, val: string) => void;
  onSave: (id: number, text: string) => void;
  onRegenerate: (id: number, idx: number) => void;
}

export default function AnswerCard({ 
  item, 
  index, 
  selectedSessionId, 
  onAnswerChange, 
  onSave, 
  onRegenerate 
}: AnswerCardProps) {
  const [showEvidence, setShowEvidence] = useState(false);
  const hasCitations = Array.isArray(item.citations) && item.citations.length > 0;

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5 mb-5 transition-all hover:border-slate-300">
      <div className="flex justify-between items-start gap-4 mb-4">
        <div>
          <div className="text-sm font-semibold text-blue-600 mb-1">
            Question {index + 1}
          </div>
          <h3 className="text-base font-medium text-slate-800 leading-snug">
            {item.question}
          </h3>
        </div>
        {item.confidence_score !== undefined && (
          <Badge variant={item.confidence_score > 80 ? "default" : "secondary"} className="shrink-0">
            Score: {item.confidence_score}%
          </Badge>
        )}
      </div>

      <Textarea
        value={item.answer}
        onChange={(e) => onAnswerChange(item.question_id, e.target.value)}
        className="min-h-20 text-sm resize-y mb-4 border-slate-200 focus-visible:ring-blue-400 shadow-sm"
        placeholder="Generated answer will appear here..."
      />

      <div className="flex items-center justify-between">
        
        {hasCitations ? (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowEvidence(!showEvidence)}
            className={`text-slate-500 hover:text-blue-600 h-8 px-2 -ml-2 transition-colors ${showEvidence ? "bg-blue-50 text-blue-600" : ""}`}
          >
            <BookOpen className="w-4 h-4 mr-2" />
            Supporting Evidence ({item.citations?.length})
            {showEvidence ? <ChevronUp className="w-4 h-4 ml-1" /> : <ChevronDown className="w-4 h-4 ml-1" />}
          </Button>
        ) : (
          <div />
        )}

        {selectedSessionId && (
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              size="sm" 
              className="h-8 border-slate-200 text-slate-600" 
              onClick={() => onRegenerate(item.question_id, index)}
            >
              <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Regenerate
            </Button>
            
            <Button 
              size="sm" 
              className="h-8 bg-slate-800 hover:bg-slate-900 text-white shadow-sm" 
              onClick={() => onSave(item.question_id, item.answer)}
            >
              <Save className="w-3.5 h-3.5 mr-1.5" /> Save
            </Button>
          </div>
        )}
      </div>

      {showEvidence && hasCitations && (
        <div className="mt-4 p-4 bg-slate-50 rounded-lg border border-slate-100 text-sm animate-in fade-in slide-in-from-top-2 duration-200">
          <ul className="space-y-4">
            {item.citations!.map((c, idx) => (
              <li key={idx} className="border-l-2 border-blue-400 pl-3">
                <span className="font-semibold text-slate-700 block mb-1">
                  {c.document_name} <span className="text-slate-400 font-normal text-xs ml-1">(Chunk {c.chunk_index})</span>
                </span>
                <span className="italic text-slate-600 block leading-relaxed">
                  "{c.snippet}"
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
      
    </div>
  );
}