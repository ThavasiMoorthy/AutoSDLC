import { useState, useEffect, useRef } from 'react'
import {
    FileText, CheckCircle, Activity, Code, Brain, Send,
    MessageCircle, FolderTree, LayoutDashboard, Users, Cpu,
    GitBranch, Zap, Rocket, Terminal, Database,
    Layers, ChevronRight, Eye, ArrowLeft, Loader2, Globe
} from 'lucide-react'
import { ProjectBrief, ProjectState } from './types'

// In production (Railway), frontend is served from the same origin as the API
// In development, the Vite dev server runs on :5173 and API on :8000
const API = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';

interface ChatMsg { role: 'user' | 'assistant'; content: string; }

const SDLC_PHASES = [
    { icon: FileText, label: 'Requirements', color: 'from-blue-500 to-blue-600', key: 'srs' },
    { icon: LayoutDashboard, label: 'Planning', color: 'from-violet-500 to-purple-600', key: 'plan' },
    { icon: Users, label: 'Roles', color: 'from-orange-500 to-amber-600', key: 'roles' },
    { icon: Code, label: 'Code Gen', color: 'from-emerald-500 to-green-600', key: 'artifacts' },
    { icon: Rocket, label: 'Prototype', color: 'from-pink-500 to-rose-600', key: 'prototype' },
];

function App() {
    const [brief, setBrief] = useState('');
    const [project, setProject] = useState<ProjectState | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [chatOpen, setChatOpen] = useState(false);
    const [chatInput, setChatInput] = useState('');
    const [messages, setMessages] = useState<ChatMsg[]>([
        { role: 'assistant', content: '👋 Hi! I\'m your **AutoSDLC Assistant**. Submit a project brief and ask me anything about your project plan, architecture, or costs.' }
    ]);
    const [chatLoading, setChatLoading] = useState(false);
    const chatRef = useRef<HTMLDivElement>(null);
    const [codeTab, setCodeTab] = useState(0);
    const [activeSection, setActiveSection] = useState<string | null>(null);

    // Prototype state
    const [protoLoading, setProtoLoading] = useState(false);
    const [protoReady, setProtoReady] = useState(false);
    const [protoView, setProtoView] = useState(false);
    const [protoHtml, setProtoHtml] = useState('');

    const submit = async () => {
        if (!brief) return;
        setLoading(true); setError(null); setProtoReady(false);
        try {
            const res = await fetch(`${API}/projects`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: "Project", description: "Auto", brief_content: brief } as ProjectBrief)
            });
            if (!res.ok) throw new Error('Submit failed');
            setProject(await res.json());
        } catch (e) { setError(e instanceof Error ? e.message : 'Error'); }
        finally { setLoading(false); }
    };

    const generatePrototype = async () => {
        if (!project) return;
        setProtoLoading(true);
        try {
            const res = await fetch(`${API}/prototype/${project.id}`, { method: 'POST' });
            if (!res.ok) throw new Error('Failed to generate prototype');
            const data = await res.json();
            setProtoHtml(data.html);
            setProtoReady(true);
            setProtoView(true);
        } catch (e) {
            setError(e instanceof Error ? e.message : 'Prototype generation failed');
        } finally {
            setProtoLoading(false);
        }
    };

    const sendChat = async () => {
        if (!chatInput.trim()) return;
        const msg = chatInput.trim();
        setChatInput('');
        setMessages(p => [...p, { role: 'user', content: msg }]);
        setChatLoading(true);
        try {
            const res = await fetch(`${API}/chat`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: msg, project_id: project?.id })
            });
            const data = await res.json();
            setMessages(p => [...p, { role: 'assistant', content: data.reply }]);
        } catch { setMessages(p => [...p, { role: 'assistant', content: 'Connection error.' }]); }
        finally { setChatLoading(false); }
    };

    useEffect(() => {
        if (!project) return;
        const i = setInterval(async () => {
            try {
                const res = await fetch(`${API}/projects/${project.id}`);
                if (res.ok) setProject(await res.json());
            } catch { }
        }, 2000);
        return () => clearInterval(i);
    }, [project?.id]);

    useEffect(() => { chatRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages]);

    const reqs = project?.srs?.requirements || [];
    const tasks = project?.plan?.tasks || [];
    const cost = project?.plan?.estimated_cost || 0;
    const days = project?.plan?.total_estimated_days || 0;
    const codeFiles = project?.artifacts ? Object.keys(project.artifacts.code_snippets) : [];

    const getPhaseStatus = (key: string) => {
        if (!project) return 'idle';
        if (key === 'srs' && reqs.length > 0) return 'completed';
        if (key === 'plan' && tasks.length > 0) return 'completed';
        if (key === 'roles' && tasks.some(t => t.assigned_role)) return 'completed';
        if (key === 'artifacts' && codeFiles.length > 0) return 'completed';
        if (key === 'prototype' && protoReady) return 'completed';
        if (project && key === 'srs' && reqs.length === 0) return 'working';
        return 'idle';
    };

    // ============ PROTOTYPE FULLSCREEN VIEW ============
    if (protoView && protoHtml) {
        // Create blob URL for reliable iframe rendering
        const blob = new Blob([protoHtml], { type: 'text/html; charset=utf-8' });
        const blobUrl = URL.createObjectURL(blob);

        return (
            <div className="h-screen flex flex-col bg-slate-950">
                {/* Toolbar */}
                <div className="flex items-center justify-between px-5 py-3 bg-slate-900/80 border-b border-white/5 backdrop-blur-xl">
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => { URL.revokeObjectURL(blobUrl); setProtoView(false); }}
                            className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors px-3 py-1.5 rounded-lg hover:bg-white/5"
                        >
                            <ArrowLeft className="w-4 h-4" /> Back to Dashboard
                        </button>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
                            <Globe className="w-3.5 h-3.5 text-emerald-400" />
                            <span className="text-xs font-semibold text-emerald-300">Live Prototype</span>
                        </div>
                        <button
                            onClick={() => { const w = window.open(); if (w) { w.document.write(protoHtml); w.document.close(); } }}
                            className="flex items-center gap-2 px-3 py-1.5 bg-violet-500/10 rounded-lg border border-violet-500/20 hover:bg-violet-500/20 transition-colors cursor-pointer"
                        >
                            <Eye className="w-3.5 h-3.5 text-violet-400" />
                            <span className="text-xs font-semibold text-violet-300">Open in New Tab</span>
                        </button>
                    </div>
                </div>
                {/* Live Preview Iframe */}
                <iframe
                    src={blobUrl}
                    className="flex-1 w-full border-0"
                    title="Website Prototype"
                    style={{ minHeight: 0 }}
                />
            </div>
        )
    }

    // ============ MAIN DASHBOARD VIEW ============
    return (
        <div className="min-h-screen relative">
            <div className="bg-grid" />
            <div className="bg-glow" />
            <div className="floating-shape" style={{ top: '10%', left: '5%', width: 300, height: 300, background: 'rgba(59,130,246,0.06)' }} />
            <div className="floating-shape" style={{ top: '60%', right: '10%', width: 250, height: 250, background: 'rgba(139,92,246,0.05)', animationDelay: '5s' }} />

            <div className="relative z-10 p-6 max-w-[1600px] mx-auto">

                {/* HEADER */}
                <header className="card-surface rounded-2xl p-5 mb-6 flex items-center justify-between animate-slide-up">
                    <div className="flex items-center gap-4">
                        <div className="relative">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                                <Cpu className="w-6 h-6 text-white" />
                            </div>
                            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-emerald-500 rounded-full border-2 border-slate-900 animate-pulse" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-extrabold tracking-tight">
                                <span className="bg-gradient-to-r from-blue-400 via-violet-400 to-cyan-400 bg-clip-text text-transparent">AutoSDLC</span>
                            </h1>
                            <p className="text-xs text-slate-500 font-medium tracking-wide">AI-POWERED SOFTWARE ENGINEERING PLATFORM</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <div className="px-3 py-1.5 bg-emerald-500/10 rounded-lg border border-emerald-500/15 flex items-center gap-2">
                            <Zap className="w-3.5 h-3.5 text-emerald-400" />
                            <span className="text-xs font-semibold text-emerald-300">Groq LPU Active</span>
                        </div>
                        <button
                            onClick={() => setChatOpen(!chatOpen)}
                            className={`px-3 py-2 rounded-xl flex items-center gap-2 transition-all text-xs font-semibold ${chatOpen
                                ? 'bg-blue-500/15 border border-blue-500/25 text-blue-300 shadow-lg shadow-blue-500/10'
                                : 'card-surface hover:border-white/10 text-slate-400 hover:text-white'
                                }`}
                        >
                            <MessageCircle className="w-4 h-4" />
                            AI Assistant
                        </button>
                    </div>
                </header>

                {/* SDLC PIPELINE */}
                <div className="card-surface rounded-2xl p-4 mb-6 animate-slide-up delay-100">
                    <div className="flex items-center gap-2 mb-3 px-2">
                        <GitBranch className="w-4 h-4 text-violet-400" />
                        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">SDLC Pipeline</span>
                    </div>
                    <div className="pipeline-container">
                        {SDLC_PHASES.map((phase, i) => {
                            const status = getPhaseStatus(phase.key);
                            const Icon = phase.icon;
                            return (
                                <div key={phase.key} className="contents">
                                    <div className="pipeline-node">
                                        <div className={`pipeline-icon bg-gradient-to-br ${phase.color} ${status === 'idle' ? 'opacity-30 grayscale' : ''} ${status === 'working' ? 'agent-working' : ''}`}>
                                            {status === 'completed' ? <CheckCircle className="w-6 h-6" /> : <Icon className="w-6 h-6" />}
                                        </div>
                                        <span className={`text-[10px] font-semibold uppercase tracking-wider ${status === 'completed' ? 'text-white' : 'text-slate-500'}`}>{phase.label}</span>
                                    </div>
                                    {i < SDLC_PHASES.length - 1 && (
                                        <div className={`pipeline-connector ${status === 'completed' ? 'opacity-100' : 'opacity-30'}`} />
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>

                <div className="flex gap-6">
                    {/* MAIN CONTENT */}
                    <div className="flex-1 min-w-0">

                        {/* Stats */}
                        <div className="grid grid-cols-4 gap-4 mb-6 animate-slide-up delay-200">
                            <StatCard icon={<FileText className="w-5 h-5" />} label="Requirements" value={reqs.length} color="blue" />
                            <StatCard icon={<Layers className="w-5 h-5" />} label="Plan Tasks" value={tasks.length} color="violet" />
                            <StatCard icon={<Terminal className="w-5 h-5" />} label="Code Files" value={codeFiles.length} color="emerald" />
                            <StatCard icon={<Database className="w-5 h-5" />} label="Est. Cost" value={`$${cost}`} color="amber" />
                        </div>

                        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 animate-slide-up delay-300">
                            {/* INPUT PANEL */}
                            <div className="xl:col-span-1">
                                <div className="card-3d">
                                    <div className="card-surface rounded-2xl p-6 h-full">
                                        <div className="flex items-center gap-2 mb-4">
                                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                                                <Terminal className="w-4 h-4 text-white" />
                                            </div>
                                            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300">Project Brief</h2>
                                        </div>
                                        <textarea
                                            className="w-full h-36 bg-black/30 border border-white/5 rounded-xl p-4 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/30 outline-none transition-all resize-none text-sm font-mono text-slate-300 placeholder-slate-600"
                                            placeholder="// Describe your project...&#10;// e.g. 'Build a food delivery&#10;// app with GPS tracking'"
                                            value={brief}
                                            onChange={e => setBrief(e.target.value)}
                                        />
                                        <button
                                            onClick={submit}
                                            disabled={loading || !brief}
                                            className="w-full mt-3 bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 hover:from-blue-500 hover:via-blue-400 hover:to-cyan-400 disabled:opacity-30 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl font-bold transition-all flex items-center justify-center gap-2 text-sm shadow-lg shadow-blue-500/20"
                                        >
                                            {loading ? <Activity className="w-4 h-4 animate-spin" /> : <Rocket className="w-4 h-4" />}
                                            {loading ? 'Agents Working...' : 'Launch Analysis'}
                                        </button>

                                        {/* Generate Prototype Button */}
                                        {codeFiles.length > 0 && (
                                            <button
                                                onClick={generatePrototype}
                                                disabled={protoLoading}
                                                className="w-full mt-2 bg-gradient-to-r from-pink-600 via-rose-500 to-orange-500 hover:from-pink-500 hover:via-rose-400 hover:to-orange-400 disabled:opacity-50 text-white px-6 py-3 rounded-xl font-bold transition-all flex items-center justify-center gap-2 text-sm shadow-lg shadow-pink-500/20"
                                            >
                                                {protoLoading ? (
                                                    <>
                                                        <Loader2 className="w-4 h-4 animate-spin" />
                                                        Generating Website...
                                                    </>
                                                ) : protoReady ? (
                                                    <>
                                                        <Eye className="w-4 h-4" />
                                                        View Prototype
                                                    </>
                                                ) : (
                                                    <>
                                                        <Globe className="w-4 h-4" />
                                                        Generate Live Prototype
                                                    </>
                                                )}
                                            </button>
                                        )}

                                        {protoReady && (
                                            <button
                                                onClick={() => setProtoView(true)}
                                                className="w-full mt-2 border border-pink-500/20 text-pink-300 hover:bg-pink-500/10 px-4 py-2 rounded-xl text-xs font-semibold transition-all flex items-center justify-center gap-2"
                                            >
                                                <Eye className="w-3.5 h-3.5" />
                                                Open Fullscreen Preview
                                            </button>
                                        )}

                                        {error && <p className="text-red-400 text-xs mt-2 font-mono">⚠ {error}</p>}

                                        {/* Agent Status */}
                                        {project && (
                                            <div className="mt-4 space-y-1.5">
                                                <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-2">Agent Status</p>
                                                {[
                                                    { name: 'Requirement Agent', done: reqs.length > 0 },
                                                    { name: 'Planning Agent', done: tasks.length > 0 },
                                                    { name: 'Role Agent', done: tasks.some(t => t.assigned_role) },
                                                    { name: 'Coding Agent', done: codeFiles.length > 0 },
                                                    { name: 'Prototype Agent', done: protoReady },
                                                ].map(a => (
                                                    <div key={a.name} className="flex items-center gap-2">
                                                        <div className={`w-2 h-2 rounded-full ${a.done ? 'bg-emerald-400' : 'bg-slate-600 animate-pulse'}`} />
                                                        <span className={`text-xs font-mono ${a.done ? 'text-emerald-300' : 'text-slate-500'}`}>{a.name}</span>
                                                        {a.done && <CheckCircle className="w-3 h-3 text-emerald-400 ml-auto" />}
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* RESULTS */}
                            <div className="xl:col-span-2 space-y-5">
                                {/* Requirements */}
                                {reqs.length > 0 && (
                                    <ResultSection
                                        icon={<FileText className="w-5 h-5 text-white" />}
                                        gradient="from-blue-500 to-blue-600"
                                        title="Software Requirements (SRS)"
                                        subtitle={`${reqs.length} requirements identified`}
                                        isOpen={activeSection === 'reqs'}
                                        onToggle={() => setActiveSection(activeSection === 'reqs' ? null : 'reqs')}
                                    >
                                        <div className="space-y-2">
                                            {reqs.map(req => (
                                                <div key={req.id} className="flex items-start gap-3 p-3 bg-black/20 rounded-xl border border-white/[0.03]">
                                                    <span className="font-mono text-[10px] text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded-md font-bold mt-0.5">{req.id}</span>
                                                    <p className="text-sm text-slate-300 flex-1">{req.description}</p>
                                                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${req.priority === 'High' ? 'bg-red-500/15 text-red-300' : req.priority === 'Low' ? 'bg-green-500/15 text-green-300' : 'bg-amber-500/15 text-amber-300'}`}>
                                                        {req.priority}
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    </ResultSection>
                                )}

                                {/* Plan */}
                                {tasks.length > 0 && (
                                    <ResultSection
                                        icon={<LayoutDashboard className="w-5 h-5 text-white" />}
                                        gradient="from-violet-500 to-purple-600"
                                        title="Project Plan & WBS"
                                        subtitle={`${tasks.length} tasks · ${days} days · $${cost}`}
                                        isOpen={activeSection === 'plan'}
                                        onToggle={() => setActiveSection(activeSection === 'plan' ? null : 'plan')}
                                    >
                                        <div className="overflow-hidden rounded-xl border border-white/[0.03]">
                                            <table className="w-full text-sm">
                                                <thead>
                                                    <tr className="bg-white/[0.03] text-slate-400 text-xs uppercase tracking-wider">
                                                        <th className="text-left p-3">Task</th>
                                                        <th className="text-left p-3">Role</th>
                                                        <th className="text-center p-3">Days</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="divide-y divide-white/[0.03]">
                                                    {tasks.map(t => (
                                                        <tr key={t.id} className="hover:bg-white/[0.02] transition-colors">
                                                            <td className="p-3 text-white font-medium">{t.name}</td>
                                                            <td className="p-3">
                                                                <span className="text-xs bg-violet-500/10 text-violet-300 px-2 py-0.5 rounded-md font-mono">{t.assigned_role || 'TBD'}</span>
                                                            </td>
                                                            <td className="p-3 text-center font-mono text-slate-400">{t.estimated_days}</td>
                                                        </tr>
                                                    ))}
                                                </tbody>
                                            </table>
                                        </div>
                                        <div className="mt-3 flex gap-6 text-xs">
                                            <span className="text-slate-500">Total: <span className="stat-number font-bold text-base">{days}</span> days</span>
                                            <span className="text-slate-500">Cost: <span className="text-emerald-400 font-bold text-base font-mono">${cost}</span></span>
                                        </div>
                                    </ResultSection>
                                )}

                                {/* Code */}
                                {codeFiles.length > 0 && (
                                    <ResultSection
                                        icon={<Code className="w-5 h-5 text-white" />}
                                        gradient="from-emerald-500 to-green-600"
                                        title="Generated Code"
                                        subtitle={`${codeFiles.length} files generated`}
                                        isOpen={activeSection === 'code'}
                                        onToggle={() => setActiveSection(activeSection === 'code' ? null : 'code')}
                                    >
                                        <div className="bg-black/30 rounded-xl p-3 border border-white/[0.03] mb-3">
                                            <p className="text-[10px] text-slate-500 uppercase tracking-wider font-bold mb-2 flex items-center gap-1">
                                                <FolderTree className="w-3 h-3" /> Architecture
                                            </p>
                                            <div className="grid grid-cols-2 gap-x-4 gap-y-0.5 font-mono text-xs">
                                                {project!.artifacts!.file_structure.map((f, i) => (
                                                    <div key={i} className="text-blue-300/70 py-0.5">📄 {f}</div>
                                                ))}
                                            </div>
                                        </div>
                                        <div className="flex gap-1 overflow-x-auto pb-1">
                                            {codeFiles.map((f, i) => (
                                                <button key={f} onClick={() => setCodeTab(i)}
                                                    className={`px-3 py-1.5 rounded-lg text-[11px] font-mono whitespace-nowrap transition-all ${codeTab === i ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/20' : 'text-slate-600 hover:text-slate-400'}`}>
                                                    {f.split('/').pop()}
                                                </button>
                                            ))}
                                        </div>
                                        <div className="code-editor rounded-xl overflow-hidden mt-2">
                                            <div className="code-editor-header">
                                                <div className="code-dot bg-red-500/80" />
                                                <div className="code-dot bg-yellow-500/80" />
                                                <div className="code-dot bg-green-500/80" />
                                                <span className="ml-3 text-xs font-mono text-slate-500">{codeFiles[codeTab]}</span>
                                                <button onClick={() => navigator.clipboard.writeText(project!.artifacts!.code_snippets[codeFiles[codeTab]])}
                                                    className="ml-auto text-[10px] text-slate-500 hover:text-white px-2 py-0.5 rounded bg-white/5 hover:bg-white/10 font-mono transition-colors">copy</button>
                                            </div>
                                            <pre className="p-4 overflow-x-auto max-h-72 overflow-y-auto text-xs leading-relaxed">
                                                <code className="text-emerald-300/80">{project!.artifacts!.code_snippets[codeFiles[codeTab]]}</code>
                                            </pre>
                                        </div>
                                    </ResultSection>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* CHAT PANEL */}
                    {chatOpen && (
                        <div className="w-[360px] flex-shrink-0 animate-slide-up">
                            <div className="card-surface rounded-2xl flex flex-col h-[calc(100vh-120px)] sticky top-6">
                                <div className="p-4 border-b border-white/[0.04] flex items-center gap-3">
                                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center">
                                        <Brain className="w-4 h-4 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="font-bold text-sm">AI Assistant</h3>
                                        <p className="text-[10px] text-emerald-400 font-medium">Online · Context-Aware</p>
                                    </div>
                                </div>
                                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                                    {messages.map((m, i) => (
                                        <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'} chat-bubble`}>
                                            <div className={`max-w-[85%] p-3 rounded-2xl text-sm leading-relaxed ${m.role === 'user'
                                                ? 'bg-blue-600/20 border border-blue-500/15 text-blue-50 rounded-br-md'
                                                : 'bg-white/[0.04] border border-white/[0.04] text-slate-300 rounded-bl-md'}`}>
                                                <p className="whitespace-pre-wrap">{m.content}</p>
                                            </div>
                                        </div>
                                    ))}
                                    {chatLoading && (
                                        <div className="flex justify-start chat-bubble">
                                            <div className="bg-white/[0.04] border border-white/[0.04] p-3 rounded-2xl rounded-bl-md">
                                                <div className="flex gap-1.5">
                                                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                                                    <div className="w-2 h-2 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                                                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                    <div ref={chatRef} />
                                </div>
                                <div className="p-3 border-t border-white/[0.04]">
                                    <div className="flex gap-2">
                                        <input type="text" value={chatInput} onChange={e => setChatInput(e.target.value)}
                                            onKeyDown={e => e.key === 'Enter' && sendChat()}
                                            placeholder="Ask about your project..."
                                            className="flex-1 bg-black/30 border border-white/[0.05] rounded-xl px-3 py-2.5 text-sm focus:ring-2 focus:ring-blue-500/30 outline-none font-mono placeholder-slate-600" />
                                        <button onClick={sendChat} disabled={chatLoading || !chatInput.trim()}
                                            className="bg-gradient-to-r from-blue-600 to-violet-600 hover:from-blue-500 hover:to-violet-500 disabled:opacity-30 p-2.5 rounded-xl transition-all shadow-lg shadow-blue-500/15">
                                            <Send className="w-4 h-4 text-white" />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

// ===== REUSABLE COMPONENTS =====

function ResultSection({ icon, gradient, title, subtitle, isOpen, onToggle, children }: {
    icon: React.ReactNode; gradient: string; title: string; subtitle: string;
    isOpen: boolean; onToggle: () => void; children: React.ReactNode;
}) {
    return (
        <div className="card-3d">
            <div className="card-surface rounded-2xl overflow-hidden">
                <button onClick={onToggle} className="w-full flex items-center justify-between p-5 hover:bg-white/[0.02] transition-colors">
                    <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${gradient} flex items-center justify-center shadow-lg`}>{icon}</div>
                        <div className="text-left">
                            <h3 className="font-bold text-sm text-white">{title}</h3>
                            <p className="text-xs text-slate-500">{subtitle}</p>
                        </div>
                    </div>
                    <ChevronRight className={`w-5 h-5 text-slate-500 transition-transform ${isOpen ? 'rotate-90' : ''}`} />
                </button>
                {isOpen && <div className="px-5 pb-5">{children}</div>}
            </div>
        </div>
    )
}

function StatCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: string | number; color: string }) {
    const colors: Record<string, string> = {
        blue: 'from-blue-500/15 to-blue-600/5 border-blue-500/10',
        violet: 'from-violet-500/15 to-violet-600/5 border-violet-500/10',
        emerald: 'from-emerald-500/15 to-emerald-600/5 border-emerald-500/10',
        amber: 'from-amber-500/15 to-amber-600/5 border-amber-500/10',
    };
    const iconColors: Record<string, string> = {
        blue: 'from-blue-500 to-blue-600',
        violet: 'from-violet-500 to-violet-600',
        emerald: 'from-emerald-500 to-emerald-600',
        amber: 'from-amber-500 to-amber-600',
    };
    return (
        <div className="card-3d">
            <div className={`bg-gradient-to-br ${colors[color]} border rounded-2xl p-4 card-surface`}>
                <div className="flex items-center justify-between mb-3">
                    <div className={`w-9 h-9 rounded-xl bg-gradient-to-br ${iconColors[color]} flex items-center justify-center shadow-lg`}>
                        <span className="text-white">{icon}</span>
                    </div>
                    <span className="stat-number text-2xl font-extrabold">{value}</span>
                </div>
                <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">{label}</p>
            </div>
        </div>
    )
}

export default App
