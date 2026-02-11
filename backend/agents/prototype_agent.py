from .base import BaseAgent
from ..models import ProjectState
from ..llm import generate_completion, GROQ_API_KEY
import re
import html as html_module


class PrototypeAgent(BaseAgent):
    """
    Generates a self-contained HTML+CSS prototype website.
    No external CDN dependencies — everything is inline for reliable iframe rendering.
    """
    def __init__(self):
        super().__init__(name="Prototype Agent")
    
    async def process(self, project_state: ProjectState) -> dict:
        self.update_status("working", "Generating website prototype...")
        
        brief = project_state.brief.brief_content
        project_name = project_state.brief.name or "AppName"
        
        req_text = ""
        if project_state.srs:
            req_text = "\n".join([f"- {r.description}" for r in project_state.srs.requirements[:6]])
        
        # Try LLM to generate custom feature descriptions
        features = None
        if GROQ_API_KEY:
            try:
                self.update_status("working", "AI designing your website...")
                features = await self._get_features_from_llm(brief, req_text)
            except Exception as e:
                print(f"Prototype LLM error: {e}")
        
        if not features:
            features = {
                "tagline": "Build Something Extraordinary",
                "subtitle": brief[:150] if brief else "Next-generation platform powered by AI",
                "features": [
                    {"icon": "⚡", "title": "Lightning Fast", "desc": "Sub-second response times with optimized architecture."},
                    {"icon": "🛡️", "title": "Enterprise Security", "desc": "End-to-end encryption and SOC2 compliance built-in."},
                    {"icon": "🚀", "title": "Auto Scaling", "desc": "Scales from zero to millions of users automatically."},
                ],
                "steps": [
                    {"title": "Create Account", "desc": "Sign up in seconds, no credit card needed."},
                    {"title": "Configure", "desc": "Set up your workspace and customize to your needs."},
                    {"title": "Go Live", "desc": "Deploy and see results immediately."},
                ]
            }
        
        page_html = self._build_page(project_name, features)
        self.update_status("completed", "Prototype generated!")
        
        return {"html": page_html}
    
    async def _get_features_from_llm(self, brief: str, req_text: str) -> dict:
        prompt = f"""For this project, generate marketing website content in EXACTLY this JSON format. Return ONLY valid JSON, nothing else.

PROJECT: {brief}
REQUIREMENTS: {req_text or 'General website'}

Return this exact JSON structure:
{{
  "tagline": "A short catchy headline (4-6 words)",
  "subtitle": "One sentence describing the product value (under 120 chars)",
  "features": [
    {{"icon": "emoji", "title": "Feature Name", "desc": "One sentence description"}},
    {{"icon": "emoji", "title": "Feature Name", "desc": "One sentence description"}},
    {{"icon": "emoji", "title": "Feature Name", "desc": "One sentence description"}}
  ],
  "steps": [
    {{"title": "Step Name", "desc": "One sentence"}},
    {{"title": "Step Name", "desc": "One sentence"}},
    {{"title": "Step Name", "desc": "One sentence"}}
  ]
}}

ONLY return JSON. No markdown, no backticks, no explanation."""

        raw = await generate_completion(
            "You are a JSON generator. Return ONLY valid JSON. No markdown, no backticks.",
            prompt
        )
        
        raw = raw.strip()
        # Remove markdown fences
        if raw.startswith("```"):
            lines = raw.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            raw = "\n".join(lines).strip()
        
        import json
        data = json.loads(raw)
        
        # Validate structure
        if "tagline" in data and "features" in data and "steps" in data:
            if len(data["features"]) >= 3 and len(data["steps"]) >= 3:
                return data
        
        return None

    def _esc(self, text: str) -> str:
        """Escape text for safe HTML embedding."""
        return html_module.escape(str(text))

    def _build_page(self, project_name: str, features: dict) -> str:
        safe_name = self._esc(project_name)
        tagline = self._esc(features.get("tagline", "Build Something Extraordinary"))
        subtitle = self._esc(features.get("subtitle", "Next-generation platform"))
        
        feat_list = features.get("features", [])
        step_list = features.get("steps", [])
        
        # Build feature cards HTML
        feature_colors = [
            ("59, 130, 246", "#3b82f6"),  # blue
            ("139, 92, 246", "#8b5cf6"),  # purple
            ("16, 185, 129", "#10b981"),  # emerald
        ]
        
        features_html = ""
        for i, f in enumerate(feat_list[:3]):
            rgb, hex_c = feature_colors[i % 3]
            features_html += f'''
            <div class="card feature-card" style="--accent-rgb: {rgb}; --accent: {hex_c};">
                <div class="feature-icon">{self._esc(f.get("icon", "⚡"))}</div>
                <h3 class="feature-title">{self._esc(f.get("title", "Feature"))}</h3>
                <p class="feature-desc">{self._esc(f.get("desc", "Description"))}</p>
            </div>'''
        
        # Build steps HTML
        steps_html = ""
        step_colors = ["#3b82f6", "#8b5cf6", "#06b6d4"]
        for i, s in enumerate(step_list[:3]):
            steps_html += f'''
            <div class="step">
                <div class="step-number" style="background: linear-gradient(135deg, {step_colors[i % 3]}, {step_colors[(i+1) % 3]});">{i+1}</div>
                <h3 class="step-title">{self._esc(s.get("title", "Step"))}</h3>
                <p class="step-desc">{self._esc(s.get("desc", "Description"))}</p>
            </div>'''

        return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{safe_name}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html {{ scroll-behavior: smooth; }}

body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    background: #030712;
    color: #f1f5f9;
    line-height: 1.6;
    overflow-x: hidden;
}}

/* === BACKGROUND EFFECTS === */
.bg-effects {{
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
}}
.bg-orb {{
    position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.4;
    animation: float 8s ease-in-out infinite;
}}
.bg-orb-1 {{ width: 400px; height: 400px; background: #3b82f6; top: -100px; right: -100px; }}
.bg-orb-2 {{ width: 350px; height: 350px; background: #8b5cf6; top: 50%; left: -120px; animation-delay: -3s; }}
.bg-orb-3 {{ width: 300px; height: 300px; background: #06b6d4; bottom: -80px; right: 30%; animation-delay: -5s; }}

@keyframes float {{
    0%, 100% {{ transform: translateY(0px) scale(1); }}
    50% {{ transform: translateY(-30px) scale(1.05); }}
}}

/* === NAV === */
nav {{
    position: sticky; top: 0; z-index: 100;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    background: rgba(3,7,18,0.8);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
}}
.nav-inner {{
    max-width: 1200px; margin: 0 auto; padding: 16px 24px;
    display: flex; align-items: center; justify-content: space-between;
}}
.nav-brand {{
    display: flex; align-items: center; gap: 12px; text-decoration: none; color: inherit;
}}
.nav-logo {{
    width: 40px; height: 40px; border-radius: 12px;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 18px;
    box-shadow: 0 4px 15px rgba(59,130,246,0.3);
}}
.nav-name {{ font-weight: 700; font-size: 20px; }}
.nav-links {{ display: flex; align-items: center; gap: 32px; list-style: none; }}
.nav-links a {{
    color: #94a3b8; text-decoration: none; font-size: 14px; font-weight: 500;
    transition: color 0.2s;
}}
.nav-links a:hover {{ color: white; }}
.nav-cta {{
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    color: white; border: none; padding: 10px 20px;
    border-radius: 12px; font-weight: 600; font-size: 14px;
    cursor: pointer; transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(59,130,246,0.25);
}}
.nav-cta:hover {{
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(59,130,246,0.4);
}}

/* === HERO === */
.hero {{
    position: relative; z-index: 10;
    text-align: center; padding: 100px 24px 80px;
    max-width: 900px; margin: 0 auto;
}}
.hero-badge {{
    display: inline-flex; align-items: center; gap: 8px;
    padding: 8px 16px; border-radius: 100px;
    background: rgba(59,130,246,0.1);
    border: 1px solid rgba(59,130,246,0.2);
    margin-bottom: 32px; font-size: 14px; color: #93c5fd; font-weight: 500;
}}
.hero-dot {{
    width: 8px; height: 8px; border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 8px rgba(74,222,128,0.5);
    animation: pulse 2s ease-in-out infinite;
}}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
}}
.hero h1 {{
    font-size: clamp(40px, 7vw, 72px);
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 24px;
    letter-spacing: -1px;
}}
.hero-gradient {{
    background: linear-gradient(135deg, #60a5fa, #a78bfa, #22d3ee);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.hero p {{
    font-size: 20px; color: #94a3b8; max-width: 640px;
    margin: 0 auto 40px; line-height: 1.7;
}}
.hero-buttons {{
    display: flex; gap: 16px; justify-content: center; flex-wrap: wrap;
}}
.btn-primary {{
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    color: white; border: none; padding: 16px 32px;
    border-radius: 16px; font-weight: 700; font-size: 18px;
    cursor: pointer; transition: all 0.3s;
    box-shadow: 0 8px 30px rgba(59,130,246,0.3);
}}
.btn-primary:hover {{
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(59,130,246,0.4);
}}
.btn-secondary {{
    background: rgba(255,255,255,0.05);
    color: white; border: 1px solid rgba(255,255,255,0.1);
    padding: 16px 32px; border-radius: 16px;
    font-weight: 700; font-size: 18px;
    cursor: pointer; transition: all 0.3s;
    backdrop-filter: blur(10px);
}}
.btn-secondary:hover {{
    background: rgba(255,255,255,0.1);
    border-color: rgba(255,255,255,0.2);
}}

/* === STATS === */
.stats {{
    position: relative; z-index: 10;
    max-width: 1000px; margin: 0 auto; padding: 40px 24px;
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px;
}}
.stat {{
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px; padding: 24px; text-align: center;
    transition: all 0.3s;
}}
.stat:hover {{
    background: rgba(255,255,255,0.06);
    transform: translateY(-4px);
}}
.stat-value {{
    font-size: 32px; font-weight: 800;
    background: linear-gradient(135deg, var(--stat-c1, #60a5fa), var(--stat-c2, #22d3ee));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.stat-label {{ font-size: 14px; color: #64748b; margin-top: 4px; }}

/* === SECTIONS === */
.section {{
    position: relative; z-index: 10;
    max-width: 1100px; margin: 0 auto; padding: 80px 24px;
}}
.section-label {{
    font-size: 13px; text-transform: uppercase; letter-spacing: 2px;
    font-weight: 600; text-align: center; margin-bottom: 12px;
}}
.section-title {{
    font-size: 36px; font-weight: 800; text-align: center;
    margin-bottom: 12px; letter-spacing: -0.5px;
}}
.section-desc {{
    font-size: 16px; color: #94a3b8; text-align: center;
    max-width: 560px; margin: 0 auto 48px;
}}

/* === CARDS === */
.card {{
    background: rgba(255,255,255,0.03);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px; padding: 36px;
    transition: all 0.4s cubic-bezier(0.4,0,0.2,1);
}}
.card:hover {{
    background: rgba(255,255,255,0.06);
    transform: translateY(-8px);
    border-color: rgba(var(--accent-rgb, 59,130,246), 0.2);
    box-shadow: 0 20px 50px rgba(var(--accent-rgb, 59,130,246), 0.1);
}}
.features-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }}
.feature-icon {{
    width: 56px; height: 56px; border-radius: 16px;
    background: linear-gradient(135deg, rgba(var(--accent-rgb),0.2), rgba(var(--accent-rgb),0.1));
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(var(--accent-rgb), 0.15);
    transition: transform 0.3s;
}}
.card:hover .feature-icon {{ transform: scale(1.1); }}
.feature-title {{ font-size: 20px; font-weight: 700; margin-bottom: 12px; }}
.feature-desc {{ font-size: 14px; color: #94a3b8; line-height: 1.7; }}

/* === STEPS === */
.steps-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px; }}
.step {{ text-align: center; }}
.step-number {{
    width: 64px; height: 64px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; font-weight: 800; color: white;
    margin: 0 auto 20px;
    box-shadow: 0 8px 25px rgba(59,130,246,0.3);
    transition: transform 0.3s;
}}
.step:hover .step-number {{ transform: scale(1.1); }}
.step-title {{ font-size: 18px; font-weight: 700; margin-bottom: 8px; }}
.step-desc {{ font-size: 14px; color: #94a3b8; }}

/* === PRICING === */
.pricing-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; align-items: start; }}
.price-card {{
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px; padding: 36px;
    transition: all 0.3s;
}}
.price-card:hover {{ background: rgba(255,255,255,0.06); }}
.price-card.featured {{
    background: linear-gradient(180deg, rgba(59,130,246,0.1), rgba(139,92,246,0.05));
    border-color: rgba(59,130,246,0.2);
    transform: scale(1.05);
    box-shadow: 0 20px 50px rgba(59,130,246,0.1);
}}
.price-badge {{
    display: inline-block;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    padding: 4px 16px; border-radius: 100px;
    font-size: 12px; font-weight: 700; margin-bottom: 16px;
}}
.price-name {{ font-size: 18px; font-weight: 700; margin-bottom: 8px; }}
.price-amount {{ font-size: 40px; font-weight: 800; margin-bottom: 4px; }}
.price-period {{ font-size: 16px; color: #64748b; font-weight: 400; }}
.price-desc {{ font-size: 14px; color: #64748b; margin-bottom: 24px; }}
.price-btn {{
    width: 100%; padding: 12px; border-radius: 12px;
    font-weight: 600; font-size: 14px; cursor: pointer;
    transition: all 0.3s; border: none; margin-bottom: 24px;
}}
.price-btn-outline {{
    background: transparent; color: white;
    border: 1px solid rgba(255,255,255,0.1);
}}
.price-btn-outline:hover {{ background: rgba(255,255,255,0.05); }}
.price-btn-gradient {{
    background: linear-gradient(135deg, #3b82f6, #8b5cf6); color: white;
    box-shadow: 0 4px 15px rgba(59,130,246,0.3);
}}
.price-btn-gradient:hover {{ transform: translateY(-2px); box-shadow: 0 6px 20px rgba(59,130,246,0.4); }}
.price-list {{ list-style: none; }}
.price-list li {{
    padding: 8px 0; font-size: 14px; color: #94a3b8;
    display: flex; align-items: center; gap: 8px;
}}
.check {{ color: #4ade80; font-weight: 700; }}

/* === CTA === */
.cta-box {{
    background: linear-gradient(135deg, rgba(59,130,246,0.15), rgba(139,92,246,0.1));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px; padding: 64px 48px;
    text-align: center;
    backdrop-filter: blur(10px);
}}
.cta-box h2 {{ font-size: 36px; font-weight: 800; margin-bottom: 16px; }}
.cta-box p {{ font-size: 16px; color: #94a3b8; max-width: 480px; margin: 0 auto 32px; }}

/* === FOOTER === */
footer {{
    position: relative; z-index: 10;
    border-top: 1px solid rgba(255,255,255,0.05);
    margin-top: 48px;
}}
.footer-inner {{
    max-width: 1100px; margin: 0 auto; padding: 48px 24px;
}}
.footer-grid {{
    display: grid; grid-template-columns: 2fr 1fr 1fr 1fr;
    gap: 32px; margin-bottom: 32px;
}}
.footer-brand-desc {{ font-size: 14px; color: #64748b; margin-top: 12px; }}
.footer-col h4 {{ font-size: 14px; font-weight: 600; margin-bottom: 16px; }}
.footer-col ul {{ list-style: none; }}
.footer-col li {{
    font-size: 14px; color: #64748b; padding: 4px 0;
    cursor: pointer; transition: color 0.2s;
}}
.footer-col li:hover {{ color: #cbd5e1; }}
.footer-bottom {{
    border-top: 1px solid rgba(255,255,255,0.05);
    padding-top: 32px; text-align: center;
    font-size: 13px; color: #475569;
}}

/* === RESPONSIVE === */
@media (max-width: 768px) {{
    .nav-links {{ display: none; }}
    .stats {{ grid-template-columns: repeat(2, 1fr); }}
    .features-grid, .steps-grid, .pricing-grid {{ grid-template-columns: 1fr; }}
    .footer-grid {{ grid-template-columns: 1fr 1fr; }}
    .price-card.featured {{ transform: scale(1); }}
    .hero h1 {{ font-size: 36px; }}
}}
</style>
</head>
<body>

<div class="bg-effects">
    <div class="bg-orb bg-orb-1"></div>
    <div class="bg-orb bg-orb-2"></div>
    <div class="bg-orb bg-orb-3"></div>
</div>

<nav>
    <div class="nav-inner">
        <a href="#" class="nav-brand">
            <div class="nav-logo">⚡</div>
            <span class="nav-name">{safe_name}</span>
        </a>
        <ul class="nav-links">
            <li><a href="#features">Features</a></li>
            <li><a href="#how">How It Works</a></li>
            <li><a href="#pricing">Pricing</a></li>
        </ul>
        <button class="nav-cta">Get Started</button>
    </div>
</nav>

<section class="hero">
    <div class="hero-badge">
        <span class="hero-dot"></span>
        AI-Powered Platform
    </div>
    <h1>
        {tagline.split()[0] if " " in tagline else tagline}<br/>
        <span class="hero-gradient">{" ".join(tagline.split()[1:]) if " " in tagline else "Extraordinary"}</span>
    </h1>
    <p>{subtitle}</p>
    <div class="hero-buttons">
        <button class="btn-primary">Start Free Trial →</button>
        <button class="btn-secondary">Watch Demo ▶</button>
    </div>
</section>

<section class="stats">
    <div class="stat" style="--stat-c1: #60a5fa; --stat-c2: #22d3ee;">
        <div class="stat-value">10K+</div>
        <div class="stat-label">Active Users</div>
    </div>
    <div class="stat" style="--stat-c1: #a78bfa; --stat-c2: #f472b6;">
        <div class="stat-value">99.9%</div>
        <div class="stat-label">Uptime SLA</div>
    </div>
    <div class="stat" style="--stat-c1: #34d399; --stat-c2: #4ade80;">
        <div class="stat-value">50+</div>
        <div class="stat-label">Integrations</div>
    </div>
    <div class="stat" style="--stat-c1: #fbbf24; --stat-c2: #f97316;">
        <div class="stat-value">4.9★</div>
        <div class="stat-label">User Rating</div>
    </div>
</section>

<section class="section" id="features">
    <div class="section-label" style="color: #60a5fa;">Features</div>
    <h2 class="section-title">Everything You Need</h2>
    <p class="section-desc">Powerful tools designed to help you build, deploy, and scale with confidence.</p>
    <div class="features-grid">
        {features_html}
    </div>
</section>

<section class="section" id="how">
    <div class="section-label" style="color: #a78bfa;">Process</div>
    <h2 class="section-title">Simple 3-Step Process</h2>
    <div class="steps-grid" style="margin-top: 48px;">
        {steps_html}
    </div>
</section>

<section class="section" id="pricing">
    <div class="section-label" style="color: #22d3ee;">Pricing</div>
    <h2 class="section-title">Plans for Every Scale</h2>
    <p class="section-desc">Start free, scale when you are ready. No hidden fees.</p>
    <div class="pricing-grid">
        <div class="price-card">
            <div class="price-name">Starter</div>
            <div class="price-amount">Free</div>
            <p class="price-desc">Perfect for trying out</p>
            <button class="price-btn price-btn-outline">Get Started</button>
            <ul class="price-list">
                <li><span class="check">✓</span> 5 Projects</li>
                <li><span class="check">✓</span> Basic Analytics</li>
                <li><span class="check">✓</span> Community Support</li>
            </ul>
        </div>
        <div class="price-card featured">
            <div class="price-badge">MOST POPULAR</div>
            <div class="price-name">Pro</div>
            <div class="price-amount">$29<span class="price-period">/mo</span></div>
            <p class="price-desc">Best for growing teams</p>
            <button class="price-btn price-btn-gradient">Start Trial</button>
            <ul class="price-list">
                <li><span class="check">✓</span> Unlimited Projects</li>
                <li><span class="check">✓</span> Advanced Analytics</li>
                <li><span class="check">✓</span> Priority Support</li>
                <li><span class="check">✓</span> API Access</li>
            </ul>
        </div>
        <div class="price-card">
            <div class="price-name">Enterprise</div>
            <div class="price-amount">Custom</div>
            <p class="price-desc">For large organizations</p>
            <button class="price-btn price-btn-outline">Contact Sales</button>
            <ul class="price-list">
                <li><span class="check">✓</span> Everything in Pro</li>
                <li><span class="check">✓</span> Custom Integrations</li>
                <li><span class="check">✓</span> Dedicated Support</li>
                <li><span class="check">✓</span> SLA Guarantee</li>
            </ul>
        </div>
    </div>
</section>

<section class="section">
    <div class="cta-box">
        <h2>Ready to Get Started?</h2>
        <p>Join thousands building the future. Start your free trial today, no credit card required.</p>
        <button class="btn-primary">Start Building Now →</button>
    </div>
</section>

<footer>
    <div class="footer-inner">
        <div class="footer-grid">
            <div>
                <a href="#" class="nav-brand">
                    <div class="nav-logo" style="width:32px;height:32px;font-size:14px;border-radius:8px;">⚡</div>
                    <span style="font-weight:700;">{safe_name}</span>
                </a>
                <p class="footer-brand-desc">Empowering teams to build and ship faster than ever.</p>
            </div>
            <div class="footer-col">
                <h4>Product</h4>
                <ul><li>Features</li><li>Pricing</li><li>API Docs</li></ul>
            </div>
            <div class="footer-col">
                <h4>Company</h4>
                <ul><li>About</li><li>Blog</li><li>Careers</li></ul>
            </div>
            <div class="footer-col">
                <h4>Legal</h4>
                <ul><li>Privacy</li><li>Terms</li><li>Security</li></ul>
            </div>
        </div>
        <div class="footer-bottom">
            Designed with AutoSDLC — AI-Powered Software Engineering Platform
        </div>
    </div>
</footer>

</body>
</html>'''
