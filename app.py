"""HireScope AI — AI-powered resume screener for HR teams."""
import json
import re

import pdfplumber
import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="HireScope AI — Resume Screener",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- custom css ----------------
st.markdown(
    """
    <style>
    .score-bar { height: 10px; border-radius: 999px; background: #27272a; overflow: hidden; }
    .score-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #f59e0b, #fbbf24); }
    .pill { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12px; margin: 2px 4px 2px 0; font-weight: 600; }
    .pill-ok { background: rgba(34,197,94,.15); color: #4ade80; border: 1px solid rgba(34,197,94,.4); }
    .pill-miss { background: rgba(244,63,94,.12); color: #fb7185; border: 1px solid rgba(244,63,94,.4); }
    .cand-card { border: 1px solid rgba(255,255,255,.08); border-radius: 16px; padding: 18px 20px; margin-bottom: 14px; background: rgba(255,255,255,.02); }
    .top-badge { background: linear-gradient(90deg,#f59e0b,#fbbf24); color: #000; font-weight: 800; font-size: 12px; padding: 3px 12px; border-radius: 999px; }
    </style>
    """,
    unsafe_allow_html=True,
)

MODELS = ["llama-3.1-8b-instant", "openai/gpt-oss-20b"]

# ---------------- sidebar ----------------
with st.sidebar:
    st.header("💼 Job Requirements")
    saved_key = ""
    try:
        saved_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        pass
    if saved_key:
        api_key = saved_key
        st.success("✅ API key loaded")
    else:
        api_key = st.text_input("Groq API Key", type="password")
        st.caption("Free key: console.groq.com")
    job_title = st.text_input("Job Title", placeholder="e.g. Python Developer")
    req_skills = st.text_area(
        "Required Skills (comma separated)",
        placeholder="Python, Django, REST APIs, PostgreSQL",
        height=80,
    )
    min_exp = st.number_input("Min. Experience (years)", min_value=0.0, value=1.0, step=0.5)
    job_desc = st.text_area("Job Description (optional)", height=100)

# ---------------- helpers ----------------
def extract_text(uploaded_file):
    text = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += (page.extract_text() or "") + "\n"
    except Exception:
        return ""
    return text.strip()


def clean_json(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return raw.strip()


def analyze(client, cv_text, job_title, req_skills, min_exp, job_desc):
    prompt = (
        "You are an expert HR recruiter. Score the resume below against the job requirements.\n\n"
        f"JOB TITLE: {job_title}\n"
        f"REQUIRED SKILLS: {req_skills}\n"
        f"MINIMUM EXPERIENCE: {min_exp} years\n"
        f"JOB DESCRIPTION: {job_desc or 'Not provided'}\n\n"
        f"RESUME:\n{cv_text[:8000]}\n\n"
        "Scoring: skill match 50%, relevant experience 30%, education & overall fit 20%.\n"
        "Return ONLY valid JSON with keys: name, email, phone, skills (list), "
        "experience_years (number), education, match_score (0-100 integer), "
        "matched_skills (list), missing_skills (list), strengths (one line), "
        "concern (one line or null)."
    )
    last_err = None
    for model in MODELS:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            return json.loads(clean_json(resp.choices[0].message.content))
        except Exception as e:
            last_err = e
    raise last_err

# ---------------- main ----------------
st.title("📄 HireScope AI")
st.markdown("**AI-powered resume screening** — upload CVs, define the role, get ranked candidates in seconds.")

uploaded = st.file_uploader("Upload CVs (PDF)", type=["pdf"], accept_multiple_files=True)

go = st.button("🔍 Screen Resumes", type="primary")

if go:
    if not api_key:
        st.warning("⚠️ Groq API key dalo (sidebar me).")
    elif not uploaded:
        st.warning("⚠️ Pehle CVs upload karo.")
    elif not job_title or not req_skills:
        st.warning("⚠️ Job title aur required skills likho.")
    else:
        client = Groq(api_key=api_key)
        results = []
        bar = st.progress(0, text="CVs parhi ja rahi hain...")
        for i, f in enumerate(uploaded):
            bar.progress(i / len(uploaded), text=f"Parh raha hun: {f.name}...")
            text = extract_text(f)
            if not text:
                results.append({"file": f.name, "error": "PDF se text nahi nikla (scanned image ho sakti hai)."})
                continue
            try:
                data = analyze(client, text, job_title, req_skills, min_exp, job_desc)
                data["file"] = f.name
                results.append(data)
            except Exception as e:
                results.append({"file": f.name, "error": f"AI analysis fail: {e}"})
        bar.progress(1.0, text="Ho gaya!")
        bar.empty()
        st.session_state["results"] = results

# ---------------- results ----------------
results = st.session_state.get("results", [])
if results:
    ok = [r for r in results if "match_score" in r]
    bad = [r for r in results if "match_score" not in r]
    ok.sort(key=lambda r: r["match_score"], reverse=True)

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("CVs Screened", len(results))
    c2.metric("Strong Matches (70+)", sum(1 for r in ok if r["match_score"] >= 70))
    c3.metric("Top Score", f"{ok[0]['match_score']}/100" if ok else "—")

    for idx, r in enumerate(ok):
        score = r["match_score"]
        pills_ok = "".join(
            f'<span class="pill pill-ok">✓ {s}</span>' for s in r.get("matched_skills", [])
        )
        pills_miss = "".join(
            f'<span class="pill pill-miss">✗ {s}</span>' for s in r.get("missing_skills", [])
        )
        badge = (
            '<span class="top-badge">🏆 TOP MATCH</span>'
            if idx == 0
            else f'<span class="pill">#{idx + 1}</span>'
        )
        st.markdown(
            f"""
            <div class="cand-card">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <h3 style="margin:0;">{r.get("name", "Unknown")}</h3>
                {badge}
              </div>
              <p style="color:#a1a1aa;font-size:13px;margin:4px 0 8px;">📧 {r.get("email") or "—"} &nbsp; 📞 {r.get("phone") or "—"} &nbsp; 🗂️ {r.get("file", "")}</p>
              <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                <div class="score-bar" style="flex:1;"><div class="score-fill" style="width:{score}%;"></div></div>
                <b style="color:#fbbf24;">{score}/100</b>
              </div>
              <p style="font-size:13px;color:#a1a1aa;margin:4px 0;">💼 {r.get("experience_years", "?")} yrs exp &nbsp; • &nbsp; 🎓 {r.get("education", "—")}</p>
              <div style="margin:6px 0;">{pills_ok}{pills_miss}</div>
              <p style="font-size:13px;margin:4px 0;">💪 <b>Strength:</b> {r.get("strengths", "—")}</p>
              <p style="font-size:13px;margin:4px 0;">⚠️ <b>Concern:</b> {r.get("concern") or "—"}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if bad:
        st.subheader("⚠️ Skipped")
        for r in bad:
            st.error(f"{r['file']}: {r['error']}")

# ---------------- footer ----------------
st.divider()
st.markdown(
    "<p style='text-align:center; color:#71717a; font-size:12px; margin-top:8px;'>"
    "Crafted with ❤️ by <b style='color:#fbbf24;'>Engr. Muhammad Shehryar Khan</b></p>",
    unsafe_allow_html=True,
)
