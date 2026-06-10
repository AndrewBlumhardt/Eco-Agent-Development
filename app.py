# app.py
import streamlit as st
from dotenv import load_dotenv
from src.agent import EcoTravelAgent
from src.models import UserPreferences

load_dotenv()

st.set_page_config(page_title="EcoTravel Agent", layout="wide")
st.title("EcoTravel Agent — Find Low-Crowd Destinations")

if "agent" not in st.session_state:
    st.session_state.agent = EcoTravelAgent()
if "preferences_set" not in st.session_state:
    st.session_state.preferences_set = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "response_feedback" not in st.session_state:
    st.session_state.response_feedback = {}

# ── Step 1: Preference Shelter ─────────────────────────────────────────────
if not st.session_state.preferences_set:
    st.subheader("Step 1: Your Travel Preferences")
    st.caption(
        "These preferences are remembered throughout your session and used to filter all results."
    )
    with st.form("preferences_form"):
        budget = st.number_input(
            "Max budget per night (USD)", min_value=50, max_value=2000, value=200, step=25
        )
        weather = st.selectbox("Preferred weather", ["warm", "cool", "mild", "any"])
        drive_range = st.selectbox(
            "Max drive from destination center",
            [15, 25, 50, 100],
            index=1,
            format_func=lambda x: f"{x} miles",
        )
        crowd_tolerance = st.selectbox(
            "Crowd tolerance",
            ["low", "medium", "high"],
            help="Low = strongly prefer quiet areas; High = crowds are acceptable",
        )
        submitted = st.form_submit_button("Save Preferences and Continue →")

    if submitted:
        prefs = UserPreferences(
            budget_per_night=float(budget),
            weather_preference=weather,
            max_drive_miles=drive_range,
            crowd_tolerance=crowd_tolerance,
        )
        st.session_state.agent.memory.set_preferences(prefs)
        st.session_state.preferences_set = True
        st.rerun()

# ── Step 2: Search + Chat ──────────────────────────────────────────────────
else:
    col_search, col_prefs = st.columns([2, 1])

    with col_search:
        st.subheader("Step 2: Search for Hotels")
        with st.form("search_form"):
            location = st.text_input("Destination", placeholder="e.g. Asheville, NC")
            c1, c2 = st.columns(2)
            with c1:
                checkin = st.date_input("Check-in")
            with c2:
                checkout = st.date_input("Check-out")
            radius = st.selectbox(
                "Search radius",
                [15, 25, 50, 100],
                index=1,
                format_func=lambda x: f"{x} miles",
            )
            search_btn = st.form_submit_button("Search Hotels")

        if search_btn and location:
            query = (
                f"Find hotels in {location} from {checkin} to {checkout} "
                f"within {radius} miles. Show results as a table sorted by crowd score."
            )
            with st.spinner("Searching..."):
                reply = st.session_state.agent.chat(query)
            st.session_state.chat_history.append(("user", query))
            st.session_state.chat_history.append(("assistant", reply))
            st.rerun()

    with col_prefs:
        prefs = st.session_state.agent.memory.get_preferences()
        if prefs:
            st.subheader("Your Preferences")
            st.write(f"**Budget:** ${prefs.budget_per_night:.0f}/night")
            st.write(f"**Weather:** {prefs.weather_preference}")
            st.write(f"**Max drive:** {prefs.max_drive_miles} miles")
            st.write(f"**Crowd tolerance:** {prefs.crowd_tolerance}")
            if st.button("Change Preferences"):
                st.session_state.preferences_set = False
                st.rerun()

    # ── Chat History ────────────────────────────────────────────────────────
    st.divider()
    start_idx = max(len(st.session_state.chat_history) - 8, 0)
    visible_messages = st.session_state.chat_history[start_idx:]

    for idx, (role, message) in enumerate(visible_messages, start=start_idx):
        with st.chat_message(role):
            st.markdown(message)

            if role == "assistant":
                existing_feedback = st.session_state.response_feedback.get(idx, {})
                with st.expander("Feedback on this response", expanded=False):
                    sentiment = st.radio(
                        "Was this response helpful?",
                        ["Helpful", "Not helpful"],
                        index=0 if existing_feedback.get("sentiment", "Helpful") == "Helpful" else 1,
                        horizontal=True,
                        key=f"feedback_sentiment_{idx}",
                    )
                    comment = st.text_area(
                        "Optional comment",
                        value=existing_feedback.get("comment", ""),
                        placeholder="Tell us what was useful or what should improve.",
                        key=f"feedback_comment_{idx}",
                    )
                    if st.button("Save feedback", key=f"save_feedback_{idx}"):
                        st.session_state.response_feedback[idx] = {
                            "sentiment": sentiment,
                            "comment": comment.strip(),
                        }
                        st.success("Feedback saved")

    # ── Action Buttons ──────────────────────────────────────────────────────
    if st.session_state.chat_history:
        st.divider()
        st.caption("Quick Actions")
        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("Tell me more about this hotel"):
                with st.spinner("Fetching details..."):
                    reply = st.session_state.agent.chat(
                        "Tell me more about the top hotel result, including a review summary and rating breakdown."
                    )
                st.session_state.chat_history.append(("assistant", reply))
                st.rerun()
        with b2:
            if st.button("Nearby Destinations"):
                with st.spinner("Finding nearby areas..."):
                    reply = st.session_state.agent.chat(
                        "What are low-crowd towns or destinations nearby? Use geolocation to find options."
                    )
                st.session_state.chat_history.append(("assistant", reply))
                st.rerun()
        with b3:
            if st.button("Build Low-Crowd Itinerary"):
                with st.spinner("Building itinerary..."):
                    reply = st.session_state.agent.chat(
                        "Build a detailed low-crowd itinerary for the recommended destination, including quieter attractions, dining, and timing tips."
                    )
                st.session_state.chat_history.append(("assistant", reply))
                st.rerun()

    # ── Follow-up Chat Input ────────────────────────────────────────────────
    user_input = st.chat_input("Ask about crowd causes, specific hotels, or alternative destinations...")
    if user_input:
        with st.spinner("Thinking..."):
            reply = st.session_state.agent.chat(user_input)
        st.session_state.chat_history.append(("user", user_input))
        st.session_state.chat_history.append(("assistant", reply))
        st.rerun()
