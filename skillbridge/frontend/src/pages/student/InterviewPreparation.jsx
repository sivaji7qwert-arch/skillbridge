import { useEffect, useState } from "react";
import PageHeader from "../../components/PageHeader.jsx";
import { CheckCircle2, Clock3, Mic, Pause, Play, RotateCcw, Square } from "lucide-react";

const QUESTIONS = {
  "Data Analyst": [
    ["SQL", "Find the second-highest salary without using LIMIT."],
    ["Analytics", "How would you explain a sudden drop in a dashboard metric?"],
    ["Behavioural", "Tell me about a decision you made using data."],
  ],
  "Software Engineer": [
    ["DSA", "Explain the time complexity of a hash-map lookup."],
    ["System Design", "Design a URL shortener at a high level."],
    ["Behavioural", "Describe a difficult production bug you solved."],
  ],
  "Cloud Engineer": [
    ["Cloud", "Compare horizontal and vertical scaling."],
    ["DevOps", "How would you safely deploy a breaking API change?"],
    ["Behavioural", "Tell me about an incident you handled."],
  ],
};

export default function InterviewPreparation() {
  const [role, setRole] = useState("Data Analyst");
  const [completed, setCompleted] = useState([]);
  const [roundActive, setRoundActive] = useState(false);
  const [roundPaused, setRoundPaused] = useState(false);
  const [secondsLeft, setSecondsLeft] = useState(30 * 60);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [listening, setListening] = useState(false);
  const questions = QUESTIONS[role];
  const toggle = (question) => setCompleted((items) => items.includes(question) ? items.filter((item) => item !== question) : [...items, question]);

  useEffect(() => {
    if (!roundActive || roundPaused || secondsLeft <= 0) return undefined;
    const timer = window.setInterval(() => setSecondsLeft((value) => value - 1), 1000);
    return () => window.clearInterval(timer);
  }, [roundActive, roundPaused, secondsLeft]);

  useEffect(() => {
    if (secondsLeft === 0) setRoundActive(false);
  }, [secondsLeft]);

  const startRound = () => {
    setRoundActive(true);
    setRoundPaused(false);
    setSecondsLeft(30 * 60);
    setQuestionIndex(0);
    setAnswer("");
    setFeedback(null);
  };

  const endRound = () => {
    setRoundActive(false);
    setRoundPaused(false);
    setFeedback(answer.trim() ? "Round saved in this session. Review your answer and try to make the result more specific." : "Round ended. Start again when you are ready.");
  };

  const reviewAnswer = () => {
    const wordCount = answer.trim().split(/\s+/).filter(Boolean).length;
    if (!wordCount) {
      setFeedback("Add a short answer first. The coach needs something to review.");
      return;
    }
    const hasExample = /example|project|built|improved|reduced|increased|result/i.test(answer);
    setFeedback(hasExample
      ? `Good foundation: ${wordCount} words and a concrete example detected. Add the measurable result and your personal contribution.`
      : `${wordCount} words captured. Strengthen this answer with a specific example, your action, and a measurable result.`);
    setCompleted((items) => items.includes(questions[questionIndex][1]) ? items : [...items, questions[questionIndex][1]]);
  };

  const nextQuestion = () => {
    setQuestionIndex((index) => (index + 1) % questions.length);
    setAnswer("");
    setFeedback(null);
  };

  const startSpeech = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setFeedback("Voice input is not supported in this browser. Type your answer instead.");
      return;
    }
    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.onstart = () => setListening(true);
    recognition.onresult = (event) => setAnswer((value) => `${value} ${event.results[0][0].transcript}`.trim());
    recognition.onend = () => setListening(false);
    recognition.start();
  };

  const timeLabel = `${String(Math.floor(secondsLeft / 60)).padStart(2, "0")}:${String(secondsLeft % 60).padStart(2, "0")}`;

  return (
    <div>
      <PageHeader title="Interview Preparation" subtitle="Practice role-specific questions and build confidence before applying." />
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
        <select value={role} onChange={(e) => { setRole(e.target.value); setCompleted([]); }} className="border border-slate-200 rounded-lg px-3 py-2 text-sm bg-white">
          {Object.keys(QUESTIONS).map((item) => <option key={item}>{item}</option>)}
        </select>
        <div className="text-sm text-slate-500">{completed.length} of {questions.length} practice tasks complete</div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <div className="bg-brand-900 text-white rounded-xl p-5"><Clock3 size={19} /><div className="text-xs text-brand-100/70 mt-4">AI practice session</div><div className="text-lg font-semibold mt-1">30-minute focused round</div><div className="text-xs text-brand-100/70 mt-1">Practice, answer, and receive instant coaching in this tab.</div></div>
        <div className="bg-white border border-slate-200 rounded-xl p-5"><div className="text-xs text-slate-500">Interview checklist</div><div className="space-y-2 mt-3 text-sm text-slate-700"><div>Resume stories with measurable results</div><div>Two projects you can explain deeply</div><div>Questions ready for the interviewer</div></div></div>
        <div className="bg-white border border-slate-200 rounded-xl p-5"><div className="text-xs text-slate-500">Mock interview</div><div className="text-sm text-slate-700 mt-3">Start a focused practice round for {role}.</div><button type="button" onClick={startRound} className="inline-flex items-center gap-2 mt-4 px-3 py-2 rounded-lg bg-brand-600 text-white text-xs font-medium"><Play size={14} /> Start round</button></div>
      </div>

      {roundActive && (
        <section className="bg-white border-2 border-brand-200 rounded-xl p-5 mb-6" aria-label="Interview practice round">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
            <div><div className="text-xs text-brand-600 font-medium">AI Coach · {role}</div><div className="text-lg font-semibold text-slate-900 mt-1">Live practice round</div></div>
            <div className={`text-2xl font-mono font-semibold ${secondsLeft < 60 ? "text-red-600" : "text-slate-900"}`}>{timeLabel}</div>
          </div>
          <div className="text-xs text-slate-500 mt-4">Question {questionIndex + 1} of {questions.length} · Keep your answer structured: situation, action, result.</div>
          <div className="text-base font-medium text-slate-800 mt-2">{questions[questionIndex][1]}</div>
          <textarea value={answer} onChange={(event) => setAnswer(event.target.value)} rows={5} placeholder="Type your answer here..." className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm mt-4" />
          <div className="flex flex-wrap gap-2 mt-3">
            <button type="button" onClick={reviewAnswer} className="px-3 py-2 rounded-lg bg-brand-600 text-white text-xs font-medium">Review answer</button>
            <button type="button" onClick={startSpeech} className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-200 text-slate-600 text-xs"> <Mic size={14} /> {listening ? "Listening..." : "Speak answer"}</button>
            <button type="button" onClick={() => setRoundPaused((value) => !value)} className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-200 text-slate-600 text-xs">{roundPaused ? <Play size={14} /> : <Pause size={14} />} {roundPaused ? "Resume" : "Pause"}</button>
            <button type="button" onClick={nextQuestion} className="px-3 py-2 rounded-lg border border-slate-200 text-slate-600 text-xs">Next question</button>
            <button type="button" onClick={endRound} className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-red-200 text-red-600 text-xs"><Square size={13} /> End round</button>
          </div>
          {feedback && <div className="mt-4 bg-emerald-50 border border-emerald-200 rounded-lg p-3 text-sm text-emerald-800"><strong>Coach feedback:</strong> {feedback}</div>}
        </section>
      )}

      <div className="space-y-3">
        {questions.map(([category, question]) => (
          <div key={question} className={`bg-white border rounded-xl p-4 ${completed.includes(question) ? "border-emerald-300" : "border-slate-200"}`}>
            <div className="flex items-start gap-3"><button type="button" onClick={() => toggle(question)} className="mt-0.5 text-emerald-600" title="Mark complete">{completed.includes(question) ? <CheckCircle2 size={19} /> : <div className="w-[19px] h-[19px] rounded-full border border-slate-300" />}</button><div><div className="text-xs text-brand-600 font-medium">{category}</div><div className="text-sm text-slate-800 mt-1">{question}</div><div className="text-xs text-slate-500 mt-2">Speak your answer aloud, then write one improvement.</div></div></div>
          </div>
        ))}
      </div>
      <button type="button" onClick={() => setCompleted([])} className="inline-flex items-center gap-2 text-xs text-slate-500 hover:text-brand-600 mt-5"><RotateCcw size={14} /> Reset practice</button>
    </div>
  );
}
