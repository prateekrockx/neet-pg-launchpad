"""
NEET PG Friction-Free Launchpad (v3.0 – polished & fixed)
===========================================================
- One-click micro-session (2 min) or choose longer duration
- Auto subject & micro-topic selection
- Visual countdown timer (non‑blocking)
- Body doubling video (working embed)
- Sensory breaks (dark, stim, breath, walk)
- Sticker rewards & session log
- Custom subject/topic management (file‑based persistence)
- "Break it down" to split large topics

HOW TO RUN:
    pip install streamlit
    streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import time
import random
import json
import os
from datetime import datetime

st.set_page_config(page_title="NEET PG Launchpad", page_icon="🚀", layout="centered", initial_sidebar_state="collapsed")

# ----------------------------------------------
# DEFAULT SUBJECTS & MICRO-TOPICS
# ----------------------------------------------
DEFAULT_SUBJECTS = {
    "Anatomy": ["Brachial plexus", "Femoral triangle", "Portal vein system"],
    "Physiology": ["Action potential", "GFR regulation", "Oxygen-hemoglobin curve"],
    "Biochemistry": ["Glycolysis steps", "Krebs cycle", "Fatty acid oxidation"],
    "Pathology": ["Inflammation", "Neoplasia", "Atherosclerosis"],
    "Pharmacology": ["Beta blockers", "NSAIDs", "Antibiotic classes"],
    "Microbiology": ["Gram staining", "Bacterial toxins", "Viral hepatitis"],
    "Forensic Medicine": ["Rigor mortis", "Wound types", "Asphyxia"],
    "PSM": ["Epidemiological triad", "Screening criteria", "Immunization schedule"],
    "Medicine": ["Thyroid disorders", "Diabetes management", "Hypertension"],
    "Surgery": ["Acute abdomen", "Hernia types", "Gallstone disease"],
    "Pediatrics": ["Neonatal reflexes", "Growth charts", "Kawasaki disease"],
    "OBGYN": ["Placenta previa", "Preeclampsia", "Menstrual cycle"],
    "ENT": ["Tonsillitis", "Otitis media", "Hearing tests"],
    "Ophthalmology": ["Cataract", "Glaucoma", "Retinal detachment"],
    "Psychiatry": ["Depression", "Schizophrenia", "Anxiety disorders"],
    "Radiology": ["Chest X-ray basics", "CT head interpretation", "Ultrasound principles"],
    "Dermatology": ["Psoriasis", "Eczema", "Melanoma ABCDE"],
    "Orthopedics": ["Fracture healing", "Colle's fracture", "Osteoarthritis"],
    "Anesthesia": ["General anaesthesia stages", "Local anaesthetics", "Spinal anaesthesia"]
}

MANTRAS = [
    "A messy 15 minutes is a victory.",
    "You don’t need to be perfect to make progress.",
    "Your worth isn’t tied to your study speed.",
    "Imperfect effort is the real win.",
    "Starting is the hardest part — and you’re doing it.",
    "Anything worth doing is worth doing poorly at first.",
    "Your brain works differently, and that’s a strength."
]

STICKER_POOL = ["⭐", "🌟", "🎉", "🦊", "🐢", "🌸", "🍀", "💖", "🪷", "🎈"]
TOPICS_FILE = "user_topics.json"

# ----------------------------------------------
# FILE PERSISTENCE (no crashing JavaScript)
# ----------------------------------------------
def load_subjects():
    if os.path.exists(TOPICS_FILE):
        try:
            with open(TOPICS_FILE, "r") as f:
                data = json.load(f)
            if isinstance(data, dict) and len(data) > 0:
                return data
        except:
            pass
    return DEFAULT_SUBJECTS.copy()

def save_subjects(subjects):
    with open(TOPICS_FILE, "w") as f:
        json.dump(subjects, f, indent=2)

# ----------------------------------------------
# SESSION STATE INIT
# ----------------------------------------------
if "subjects" not in st.session_state:
    st.session_state.subjects = load_subjects()

if "app_phase" not in st.session_state:
    st.session_state.app_phase = "welcome"

if "subject" not in st.session_state:
    st.session_state.subject = None
if "topic" not in st.session_state:
    st.session_state.topic = None

if "timer_duration" not in st.session_state:
    st.session_state.timer_duration = 2 * 60  # default 2 min

if "timer_start_ts" not in st.session_state:
    st.session_state.timer_start_ts = None

if "data" not in st.session_state:
    st.session_state.data = {"stickers": [], "logs": [], "total_focus_minutes": 0}

# ----------------------------------------------
# CLEAN DARK STYLES (no dyslexia toggle)
# ----------------------------------------------
def apply_styles():
    st.markdown("""
    <style>
    .main, .stApp {
        background-color: #121212;
        color: #e0e0e0;
        font-family: system-ui, sans-serif;
    }
    .stButton>button {
        background-color: #333333;
        color: white;
        border-radius: 30px;
        padding: 15px 25px;
        font-size: 1.2rem;
    }
    .mantra {
        font-style: italic;
        color: #81c784;
        text-align: center;
        margin: 20px;
    }
    .sticker-board {
        font-size: 2.5rem;
        text-align: center;
        word-wrap: break-word;
    }
    </style>
    """, unsafe_allow_html=True)

# ----------------------------------------------
# VISUAL TIMER (non‑blocking)
# ----------------------------------------------
def focus_timer_ui():
    dur = st.session_state.timer_duration
    start = st.session_state.timer_start_ts
    if start is None:
        st.error("Timer error — restarting")
        st.session_state.app_phase = "welcome"
        st.rerun()

    # JavaScript countdown (does not block Streamlit)
    components.html(f"""
    <div id="timer" style="font-size:5rem; text-align:center; color:#81c784; font-family:monospace;">--:--</div>
    <script>
    const dur = {dur};
    const start = new Date({start * 1000});
    function tick() {{
        const now = new Date();
        const secLeft = Math.max(0, dur - Math.floor((now - start)/1000));
        const m = Math.floor(secLeft/60), s = secLeft%60;
        document.getElementById('timer').innerText = `${{String(m).padStart(2,'0')}}:${{String(s).padStart(2,'0')}}`;
        if(secLeft > 0) setTimeout(tick, 500);
    }}
    tick();
    </script>
    """, height=150)

    if st.button("✅ Finish session (it’s okay!)", key="finish"):
        st.session_state.app_phase = "session_done"
        st.rerun()

# ----------------------------------------------
# TOPIC MANAGER
# ----------------------------------------------
def manage_topics_ui():
    st.markdown("## ✏️ Customise Your Topics")
    st.caption("Changes are saved automatically on the server.")

    subjects = st.session_state.subjects

    with st.expander("➕ Add a new subject"):
        new_sub = st.text_input("Subject name")
        if st.button("Add subject") and new_sub:
            if new_sub not in subjects:
                subjects[new_sub] = []
                save_subjects(subjects)
                st.success(f"Added “{new_sub}”")
                st.rerun()
            else:
                st.warning("Already exists.")

    subj_list = list(subjects.keys())
    if not subj_list:
        st.warning("No subjects yet — add one above.")
        return

    sel_subj = st.selectbox("Choose a subject to edit", subj_list)

    if sel_subj:
        st.subheader(f"Topics under “{sel_subj}”")
        topics = subjects[sel_subj]

        if topics:
            for i, t in enumerate(topics):
                c1, c2 = st.columns([4,1])
                c1.write(f"• {t}")
                if c2.button("🗑", key=f"del_{sel_subj}_{i}"):
                    topics.pop(i)
                    save_subjects(subjects)
                    st.rerun()
        else:
            st.write("No micro‑topics yet. Add one below.")

        new_topic = st.text_input("Add a micro‑topic", key=f"new_{sel_subj}")
        if st.button("Add micro‑topic", key=f"add_{sel_subj}"):
            if new_topic and new_topic not in topics:
                topics.append(new_topic)
                save_subjects(subjects)
                st.rerun()

        # ---- Break it down ----
        st.markdown("---")
        st.markdown("### ✂️ Break a large topic into smaller pieces")
        to_split = st.selectbox("Choose a topic to split", topics, key=f"split_sel_{sel_subj}")
        if to_split:
            txt = st.text_area("List smaller topics (comma‑separated)", placeholder="ECG basics, Heart sounds, Cardiac cycle")
            if st.button("Split", key=f"split_btn_{sel_subj}"):
                if txt:
                    parts = [p.strip() for p in txt.split(",") if p.strip()]
                    if to_split in topics:
                        topics.remove(to_split)
                    for p in parts:
                        if p not in topics:
                            topics.append(p)
                    save_subjects(subjects)
                    st.success(f"Split into {len(parts)} pieces!")
                    st.rerun()

        if st.button(f"🗑 Delete whole subject “{sel_subj}”", key=f"del_sub_{sel_subj}"):
            del subjects[sel_subj]
            save_subjects(subjects)
            st.rerun()

    if st.button("🔄 Reset all to default NEET PG topics"):
        st.session_state.subjects = DEFAULT_SUBJECTS.copy()
        if os.path.exists(TOPICS_FILE):
            os.remove(TOPICS_FILE)
        st.success("Reset complete!")
        st.rerun()

# ----------------------------------------------
# APP SCREENS
# ----------------------------------------------
def show_welcome():
    st.title("🚀 NEET PG Launchpad")
    st.markdown("### Ready to just exist near your books for a moment?")

    # Quick start (2 min)
    if st.button("⚡ Just 2 minutes?", key="quickstart"):
        subjects = st.session_state.subjects
        st.session_state.subject = random.choice(list(subjects.keys()))
        st.session_state.topic = random.choice(subjects[st.session_state.subject])
        st.session_state.timer_duration = 2 * 60
        st.session_state.timer_start_ts = time.time()
        st.session_state.app_phase = "focus_timer"
        st.rerun()

    # Longer options
    with st.expander("🕒 Or choose your session length & topic"):
        dur_opts = {"2 minutes": 2, "5 minutes": 5, "15 minutes": 15, "25 minutes": 25, "45 minutes": 45}
        chosen_dur = st.radio("How long feels doable?", list(dur_opts.keys()), index=2)  # default 15 min
        st.session_state.timer_duration = dur_opts[chosen_dur] * 60

        subjects = st.session_state.subjects
        subj = st.selectbox("Subject (optional)", list(subjects.keys()), index=None, placeholder="Auto‑picked if left empty")
        if subj:
            st.session_state.subject = subj
            topic = st.selectbox("Micro‑topic", subjects[subj], index=None, placeholder="Tiny chunk")
            if topic:
                st.session_state.topic = topic
        else:
            st.session_state.subject = random.choice(list(subjects.keys()))
            st.session_state.topic = random.choice(subjects[st.session_state.subject])

        if st.button("Start session"):
            st.session_state.timer_start_ts = time.time()
            st.session_state.app_phase = "focus_timer"
            st.rerun()

def show_focus_timer():
    st.markdown(f"<div class='mantra'>{random.choice(MANTRAS)}</div>", unsafe_allow_html=True)
    st.markdown(f"### 📖 {st.session_state.subject} — {st.session_state.topic}")
    focus_timer_ui()
    # Body double (working embed)
    with st.expander("🤝 Need a body double?"):
        st.video("https://www.youtube.com/watch?v=jfKfPfyJRdk")

def show_session_done():
    # Reward
    new_sticker = random.choice(STICKER_POOL)
    st.session_state.data["stickers"].append(new_sticker)
    st.session_state.data["total_focus_minutes"] += st.session_state.timer_duration // 60
    st.balloons()
    st.markdown(f"<div class='sticker-board'>{new_sticker}</div>", unsafe_allow_html=True)
    st.success("You showed up. That’s 100% a win!")

    note = st.text_input("💡 One tiny thing you remember (optional)")
    if st.button("Save note"):
        st.session_state.data["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "subject": st.session_state.subject,
            "topic": st.session_state.topic,
            "note": note or "showed up"
        })
        st.success("Logged!")

    # Break menu (all working)
    st.markdown("---")
    st.markdown("### 🧘 Brain break (if you want)")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("🌑 Quiet dark"):
        st.session_state.app_phase = "break_dark"; st.rerun()
    if c2.button("🌀 Stim break"):
        st.session_state.app_phase = "break_stim"; st.rerun()
    if c3.button("🌬️ Breathe"):
        st.session_state.app_phase = "break_breathe"; st.rerun()
    if c4.button("🚶 Walk & water"):
        st.info("Get up, drink water, look outside. I’ll wait right here.")

    if st.button("🔁 Another session?"):
        st.session_state.app_phase = "welcome"
        st.session_state.subject = None
        st.session_state.topic = None
        st.rerun()

def show_break_dark():
    st.markdown("<div style='background:#000;height:80vh;display:flex;align-items:center;justify-content:center;color:#fff;font-size:2rem;'>Quiet. Dark. Rest.</div>", unsafe_allow_html=True)
    if st.button("Back", key="back_dark"):
        st.session_state.app_phase = "session_done"; st.rerun()

def show_break_stim():
    st.image("https://media.giphy.com/media/3o7aTskHEUdgCQtuU4/giphy.gif", use_column_width=True)
    if st.button("Back", key="back_stim"):
        st.session_state.app_phase = "session_done"; st.rerun()

def show_break_breathe():
    st.markdown("""
    <div style="text-align:center;">
        <div style="width:100px;height:100px;background:#81c784;border-radius:50%;margin:0 auto;animation:breathe 8s infinite;"></div>
        <p>Inhale (4s) … Exhale (4s)</p>
    </div>
    <style>@keyframes breathe{0%,100%{transform:scale(1)}50%{transform:scale(2)}}</style>
    """, unsafe_allow_html=True)
    if st.button("Back", key="back_breathe"):
        st.session_state.app_phase = "session_done"; st.rerun()

def sidebar():
    with st.sidebar:
        st.markdown("## 🏆 Sticker Board")
        stickers = st.session_state.data["stickers"]
        if stickers:
            st.markdown(f"<div class='sticker-board'>{' '.join(stickers)}</div>", unsafe_allow_html=True)
            st.caption(f"Total focus time: {st.session_state.data['total_focus_minutes']} min")
        else:
            st.write("No stickers yet — even 2 minutes gets one!")
        if st.button("🎁 Surprise sticker"):
            st.session_state.data["stickers"].append(random.choice(STICKER_POOL))
            st.rerun()

        st.markdown("---")
        if st.button("⚙️ Manage Topics"):
            st.session_state.app_phase = "manage_topics"
            st.rerun()

# ----------------------------------------------
# ROUTER
# ----------------------------------------------
def main():
    apply_styles()
    sidebar()

    phase = st.session_state.app_phase
    if phase == "welcome":
        show_welcome()
    elif phase == "focus_timer":
        show_focus_timer()
    elif phase == "session_done":
        show_session_done()
    elif phase == "break_dark":
        show_break_dark()
    elif phase == "break_stim":
        show_break_stim()
    elif phase == "break_breathe":
        show_break_breathe()
    elif phase == "manage_topics":
        manage_topics_ui()
        if st.button("← Back to Launchpad"):
            st.session_state.app_phase = "welcome"
            st.rerun()
    else:
        st.session_state.app_phase = "welcome"
        st.rerun()

if __name__ == "__main__":
    main()
