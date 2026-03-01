import { History, Trash2 } from "lucide-react";
import { Session } from "@/types";

interface SidebarHistoryProps {
  sessions: Session[];
  selectedSessionId: number | null;
  onLoadSession: (id: number) => void;
  onDeleteSession: (id: number) => void;
}

export default function SidebarHistory({ 
  sessions, 
  selectedSessionId, 
  onLoadSession, 
  onDeleteSession 
}: SidebarHistoryProps) {
  
  const handleDelete = (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    if (window.confirm("Are you sure you want to delete this session? This cannot be undone.")) {
      onDeleteSession(id);
    }
  };

  return (
    <div className="w-80 bg-white border-r h-full flex flex-col shrink-0">
      
      <div className="flex items-center gap-2 p-6 border-b text-slate-800">
        <History className="w-5 h-5" />
        <h2 className="font-semibold text-lg">Session History</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-4 [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
        <div className="space-y-2">
          {sessions.length === 0 && (
            <p className="text-sm text-slate-500 italic">No past sessions found.</p>
          )}
          {sessions.map((session) => (
            <div
              key={session.session_id}
              onClick={() => onLoadSession(session.session_id)}
              className={`group relative w-full text-left p-4 rounded-lg border transition-all cursor-pointer ${
                selectedSessionId === session.session_id
                  ? "bg-blue-50 border-blue-200 shadow-sm"
                  : "bg-white border-slate-100 hover:border-slate-300 hover:bg-slate-50"
              }`}
            >
              <div className="font-medium text-sm text-slate-800 truncate pr-8">
                {session.session_name}
              </div>
              <div className="text-xs text-slate-400 mt-1">
                {new Date(session.created_at).toLocaleString()}
              </div>

              <button
                onClick={(e) => handleDelete(e, session.session_id)}
                className="absolute right-3 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity p-2 text-red-500 hover:bg-red-100 rounded-md"
                title="Delete session"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}