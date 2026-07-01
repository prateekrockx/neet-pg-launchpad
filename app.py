"""
NEET PG Friction-Free Launchpad (v2.2 - fully fixed localStorage)
=================================================================
- One-click micro-session start
- Auto subject & micro-topic selection
- Visual (non-blocking) countdown timer
- Body doubling, sensory breaks, sticker rewards
- Custom subject/topic management (saved in browser's localStorage)
- "Break it down" feature to split large topics
- Fully free & shareable via Streamlit Community Cloud

HOW TO RUN LOCALLY:
    pip install streamlit
    streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import time
import random
import json
from datetime import datetime

# -------------------------------
# 1. PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="NEET PG Launchpad",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------------------
# 2. DEFAULT SUBJECTS & TOPICS
# -------------------------------
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

# -------------------------------
# 3. LOCALSTORAGE BRIDGE (FIXED)
# -------------------------------
def load_subjects_from_storage():
    """Loads subjects from localStorage (returns default if none)."""
    component_value = components.html("""
        <script src="https://cdn.jsdelivr.net/npm/@streamlit/component-lib@latest/streamlit-component-lib.js"></script>
        <script>
            let raw = localStorage.getItem('neetpg_subjects');
            if (raw) {
                try {
                    let data = JSON.parse(raw);
                    window.Streamlit.setComponentValue(data);
                } catch (e) {
                    window.Streamlit.setComponentValue(null);
                }
            } else {
                window.Streamlit.setComponentValue(null);
            }
        </script>
    """, height=0, key="load_subjects")

    if component_value and isinstance(component_value, dict) and len(component_value) > 0:
        return component_value
    return DEFAULT_SUBJECTS.copy()


def save_subjects_to_storage(subjects):
    """Saves the subjects dict to localStorage as a single JSON string."""
    subjects_json_str = json.dumps(subjects)
    components.html(f"""
        <script src="https://cdn.jsdelivr.net/npm/@streamlit/component-lib@latest/streamlit-component-lib.js"></script>
        <script>
            localStorage.setItem('neetpg_subjects', {json.dumps(subjects_json_str)});
            window.Streamlit.setComponentValue(true);
        </script>
    """, height=0, key="save_subjects")

# -------------------------------
# 4. APP STATE
# -------------------------------
if "subjects" not in st.session_state:
    st.session_state.subjects = load_subjects_from_storage()

if "app_phase" not in st.session_state:
    st.session_state.app_phase = "welcome"

if "subject" not in st.session_state:
    st.session_state.subject = None

if "topic" not in st.session_state:
    st.session_state.topic = None

if "timer_duration" not in st.session_state:
    st.session_state.timer_duration = 2 * 60

if "timer_start_ts" not in st.session_state:
    st.session_state.timer_start_ts = None

if "data" not in st.session_state:
    st.session_state.data = {"stickers": [], "logs": [], "total_focus_minutes": 0}

if "dyslexic_font" not in st.session_state:
    st.session_state.dyslexic_font = False
if "high_contrast" not in st.session_state:
    st.session_state.high_contrast = False

# -------------------------------
# 5. CSS / STYLING
# -------------------------------
def apply_styles():
    base_font = "'OpenDyslexic', sans-serif" if st.session_state.dyslexic_font else "system-ui, sans-serif"
    dark_bg = "#121212" if not st.session_state.high_contrast else "#000000"
    text_color = "#e0e0e0" if not st.session_state.high_contrast else "#ffffff"
    accent = "#81c784" if not st.session_state.high_contrast else "#ffff00"
    btn_bg = "#333333" if not st.session_state.high_contrast else "#ffffff"
    btn_text = "#ffffff" if not st.session_state.high_contrast else "#000000"

    st.markdown(f"""
    <style>
    @import url('https://fonts.cdnfonts.com/css/open-dyslexic');
    .main, .stApp {{
        background-color: {dark_bg};
        color: {text_color};
        font-family: {base_font};
    }}
    .stButton>button {{
        background-color: {btn_bg};
        color: {btn_text};
        border-radius: 30px;
        padding: 15px 25px;
        font-size: 1.2rem;
        font-family: {base_font};
    }}
    .mantra {{
        font-style: italic;
        color: {accent};
        text-align: center;
        margin: 20px;
    }}
    .sticker-board {{
        font-size: 2.5rem;
        text-align: center;
        word-wrap: break-word;
    }}
    .timer-big {{
        font-size: 5rem;
        font-weight: bold;
        text-align: center;
        color: {accent};
    }}
    </style>
    """, unsafe_allow_html=True)

# -------------------------------
# 6. TIMER (visual only)
# -------------------------------
def focus_timer_ui():
    """Shows a visual countdown and a button to finish."""
    duration = st.session_state.timer_duration
    start_ts = st.session_state.timer_start_ts
    if start_ts is None:
        st.error("Timer error, restarting.")
        st.session_state.app_phase = "welcome"
        st.rerun()

    components.html(f"""
    <div id="timer-display" style="font-size:5rem; text-align:center; color:#81c784; font-family: monospace;">--:--</div>
    <script>
        const duration = {duration};
        const startTime = new Date({start_ts * 1000});
        function update() {{
            const now = new Date();
            const elapsed = Math.floor((now - startTime) / 1000);
            const remaining = Math.max(duration - elapsed, 0);
            const mins = Math.floor(remaining / 60);
            const secs = remaining % 60;
            document.getElementById('timer-display').innerText = `${{String(mins).padStart(2,'0')}}:${{String(secs).padStart(2,'0')}}`;
            if (remaining > 0) setTimeout(update, 500);
        }}
        update();
    </script>
    """, height=150)

    # PDA-friendly manual finish button
    if st.button("Finish session (that's okay!)", key="finish_early"):
        st.session_state.app_phase = "session_done"
        st.rerun()

# -------------------------------
# 7. TOPIC MANAGEMENT UI
# -------------------------------
def manage_topics_ui():
    """Allow adding/removing subjects and micro-topics, and splitting topics."""
    st.markdown("## ✏️ Customise Your Topics")
    st.caption("All changes are saved to your browser. Only you see them.")

    subjects = st.session_state.subjects

    # Add a new subject
    with st.expander("➕ Add a new subject"):
        new_sub = st.text_input("Subject name (e.g., Radiology)")
        if st.button("Add subject") and new_sub:
            if new_sub not in subjects:
                subjects[new_sub] = []
                save_subjects_to_storage(subjects)
                st.success(f"Added {new_sub}")
                st.rerun()
            else:
                st.warning("Subject already exists.")

    # Select subject to edit
    subject_list = list(subjects.keys())
    if not subject_list:
        st.warning("No subjects. Add one first!")
        return
    selected_subject = st.selectbox("Choose a subject to edit", subject_list, index=0)

    if selected_subject:
        st.subheader(f"Micro-topics under {selected_subject}")
        topics = subjects[selected_subject]

        # Show existing topics
        if topics:
            for i, t in enumerate(topics):
                col1, col2 = st.columns([4, 1])
                col1.write(f"- {t}")
                if col2.button("🗑️", key=f"del_{selected_subject}_{i}"):
                    topics.pop(i)
                    save_subjects_to_storage(subjects)
                    st.rerun()
        else:
            st.write("No micro-topics yet. Add one below!")

        # Add micro-topic
        new_topic = st.text_input("Add a micro-topic", key=f"new_topic_{selected_subject}")
        if st.button("Add micro-topic", key=f"add_topic_{selected_subject}"):
            if new_topic and new_topic not in topics:
                topics.append(new_topic)
                save_subjects_to_storage(subjects)
                st.rerun()

        # Break it down
        st.markdown("---")
        st.markdown("### ✂️ Break a large topic into smaller pieces")
        st.caption("If a topic feels too big, split it into tiny, approachable chunks.")
        topic_to_split = st.selectbox("Choose a topic to break down", topics, key=f"split_sel_{selected_subject}")
        if topic_to_split:
            st.write(f"**{topic_to_split}**  →  smaller parts:")
            breakdown_input = st.text_area("List the smaller topics, separated by commas", placeholder="ECG basics, Heart sounds, Cardiac cycle review")
            if st.button("Split this topic", key=f"split_btn_{selected_subject}"):
                if breakdown_input:
                    new_parts = [part.strip() for part in breakdown_input.split(",") if part.strip()]
                    if topic_to_split in topics:
                        topics.remove(topic_to_split)
                    for part in new_parts:
                        if part not in topics:
                            topics.append(part)
                    save_subjects_to_storage(subjects)
                    st.success(f"Topic split into {len(new_parts)} smaller pieces!")
                    st.rerun()

        # Delete whole subject
        if st.button(f"🗑️ Delete entire subject: {selected_subject}", key=f"del_subject_{selected_subject}"):
            if selected_subject in subjects:
                del subjects[selected_subject]
                save_subjects_to_storage(subjects)
                st.rerun()

    # Reset to defaults
    if st.button("🔄 Reset all topics to original NEET PG list"):
        st.session_state.subjects = DEFAULT_SUBJECTS.copy()
        save_subjects_to_storage(DEFAULT_SUBJECTS)
        st.success("Reset complete!")
        st.rerun()

# -------------------------------
# 8. MAIN APP PHASES
# -------------------------------
def show_welcome():
    st.title("🚀 NEET PG Launchpad")
    st.markdown("### Ready to just exist near your books for a moment?")
    if st.button("Just 2 minutes?", key="welcome_start"):
        subjects = st.session_state.subjects
        if not subjects:
            st.session_state.subjects = DEFAULT_SUBJECTS.copy()
            subjects = st.session_state.subjects
        subj = random.choice(list(subjects.keys()))
        st.session_state.subject = subj
        st.session_state.topic = random.choice(subjects[subj])
        st.session_state.timer_duration = 2 * 60
        st.session_state.timer_start_ts = time.time()
        st.session_state.app_phase = "focus_timer"
        st.rerun()

    with st.expander("Or pick a subject & topic (optional)"):
        subjects = st.session_state.subjects if st.session_state.subjects else DEFAULT_SUBJECTS
        subject_names = list(subjects.keys())
        chosen_subj = st.selectbox("Subject", subject_names, index=None, placeholder="No pressure")
        if chosen_subj:
            st.session_state.subject = chosen_subj
            topics = subjects[chosen_subj]
            chosen_topic = st.selectbox("Micro-topic", topics, index=None, placeholder="Tiny chunk")
            if chosen_topic:
                st.session_state.topic = chosen_topic

def show_focus_timer():
    st.markdown(f"<div class='mantra'>{random.choice(MANTRAS)}</div>", unsafe_allow_html=True)
    st.markdown(f"### 📖 {st.session_state.subject} — {st.session_state.topic}")
    focus_timer_ui()
    with st.expander("🤝 Need a body double?"):
        st.video("https://www.youtube.com/embed/jfKfPfyJRdk?autoplay=1&mute=1")

def show_session_done():
    new_sticker = random.choice(STICKER_POOL)
    st.session_state.data["stickers"].append(new_sticker)
    st.session_state.data["total_focus_minutes"] += st.session_state.timer_duration // 60
    st.balloons()
    st.markdown(f"<div class='sticker-board'>{new_sticker}</div>", unsafe_allow_html=True)
    st.success("You existed near your books and that 100% counts!")
    note = st.text_input("💡 One tiny thing you remember or did (optional)")
    if st.button("Save this tiny win"):
        st.session_state.data["logs"].append({
            "timestamp": datetime.now().isoformat(),
            "subject": st.session_state.subject,
            "topic": st.session_state.topic,
            "note": note or "showed up"
        })
        st.success("Logged!")
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
        st.info("Stand up, get water, look outside. I'll wait here.")
    if st.button("🔁 Another session?"):
        st.session_state.app_phase = "welcome"
        st.session_state.subject = None
        st.session_state.topic = None
        st.rerun()

def show_break_dark():
    st.markdown("<div style='background:#000; height:80vh; display:flex; align-items:center; justify-content:center; color:#fff; font-size:2rem;'>Quiet. Dark. Rest.</div>", unsafe_allow_html=True)
    if st.button("Back"):
        st.session_state.app_phase = "session_done"; st.rerun()

def show_break_stim():
    st.image("https://media.giphy.com/media/3o7aTskHEUdgCQtuU4/giphy.gif", use_column_width=True)
    if st.button("Back", key="back_stim"):
        st.session_state.app_phase = "session_done"; st.rerun()

def show_break_breathe():
    st.markdown("""
    <div style="text-align:center;">
        <div style="width:100px;height:100px;background:#81c784;border-radius:50%;margin:0 auto;animation:breathe 8s infinite;"></div>
        <p>Inhale (4s) ... Exhale (4s)</p>
    </div>
    <style>@keyframes breathe{0%,100%{transform:scale(1)}50%{transform:scale(2)}}</style>
    """, unsafe_allow_html=True)
    if st.button("Back", key="back_breathe"):
        st.session_state.app_phase = "session_done"; st.rerun()

def sidebar():
    with st.sidebar:
        st.markdown("## 🏆 Sticker Board")
        stickers = st.session_state.data.get("stickers", [])
        if stickers:
            st.markdown(f"<div class='sticker-board'>{' '.join(stickers)}</div>", unsafe_allow_html=True)
            st.caption(f"Total focus: {st.session_state.data.get('total_focus_minutes',0)} min")
        else:
            st.write("No stickers yet.")
        if st.button("🎁 Surprise sticker"):
            extra = random.choice(STICKER_POOL)
            st.session_state.data["stickers"].append(extra)
            st.rerun()
        st.markdown("---")
        st.caption("Accessibility")
        dys = st.checkbox("Dyslexia-friendly font", value=st.session_state.dyslexic_font)
        if dys != st.session_state.dyslexic_font:
            st.session_state.dyslexic_font = dys; st.rerun()
        hc = st.checkbox("High contrast", value=st.session_state.high_contrast)
        if hc != st.session_state.high_contrast:
            st.session_state.high_contrast = hc; st.rerun()

        st.markdown("---")
        if st.button("⚙️ Manage Topics"):
            st.session_state.app_phase = "manage_topics"
            st.rerun()

# -------------------------------
# 9. MAIN APP ROUTER
# -------------------------------
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
