import streamlit as st
from openai import OpenAI

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)
import pandas as pd
from reportlab.pdfgen import canvas
import urllib.parse
from openai import OpenAI

# ================================
# API CLIENT (OpenRouter)
# ================================

client = OpenAI(
    api_key="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",
    base_url="https://openrouter.ai/api/v1"
)

# ================================
# PAGE SETTINGS
# ================================

st.set_page_config(page_title="AffiNexa Travel AI Demo", layout="wide")

# ================================
# LOGIN SYSTEM
# ================================

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if username != "demo" or password != "affinexa":
    st.title("AffiNexa Travel AI Demo")
    st.info("Enter demo credentials in sidebar to access.")
    st.stop()

# ================================
# HEADER
# ================================

st.title("✈️ AI Travel Assistant")
st.write(
    "Paste a travel inquiry and generate itinerary, hotels, flights, and WhatsApp reply."
)

# ================================
# DESTINATION IMAGE
# ================================

def destination_image(text):

    text = text.lower()

    if "goa" in text:
        return "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"

    if "corbett" in text:
        return "https://images.unsplash.com/photo-1546182990-dffeafbe841d"

    if "manali" in text:
        return "https://images.unsplash.com/photo-1609947017136-9daf32a5eb16"

    if "dubai" in text:
        return "https://images.unsplash.com/photo-1512453979798-5ea266f8880c"

    return "https://images.unsplash.com/photo-1488646953014-85cb44e25828"

# ================================
# AI ITINERARY
# ================================

def generate_itinerary(text):

    prompt = f"""
You are a travel planning expert.

Customer inquiry:
{text}

Generate:

Destination
Trip duration
Day-by-day itinerary
Estimated trip budget
Recommended activities
"""

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# ================================
# WHATSAPP REPLY
# ================================

def whatsapp_reply(text):

    prompt = f"""
Write a short friendly WhatsApp reply to this travel inquiry:

{text}

Offer itinerary and hotel suggestions.
"""

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# ================================
# HOTEL DATA
# ================================

def get_hotels():

    hotels = [
        {
            "name": "Luxury Resort",
            "price": "₹7500",
            "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945"
        },
        {
            "name": "Ocean View Hotel",
            "price": "₹6200",
            "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa"
        },
        {
            "name": "Boutique Stay",
            "price": "₹5400",
            "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4"
        }
    ]

    return hotels

# ================================
# FLIGHT ESTIMATE
# ================================

def flight_prices():

    flights = {
        "Delhi → Goa": "₹6500",
        "Mumbai → Goa": "₹4500",
        "Bangalore → Goa": "₹5200",
        "Delhi → Dubai": "₹22000"
    }

    return flights

# ================================
# PDF CREATOR
# ================================

def create_pdf(text):

    file = "itinerary.pdf"

    c = canvas.Canvas(file)

    y = 750

    for line in text.split("\n"):
        c.drawString(50, y, line)
        y -= 20

    c.save()

    return file

# ================================
# CRM SAVE
# ================================

def save_to_crm(inquiry):

    df = pd.DataFrame({"Inquiry":[inquiry]})

    try:
        old = pd.read_csv("crm.csv")
        df = pd.concat([old, df])
    except:
        pass

    df.to_csv("crm.csv", index=False)

# ================================
# MAIN INPUT
# ================================

inquiry = st.text_area("Customer Inquiry")

if inquiry:
    st.image(destination_image(inquiry))

# ================================
# GENERATE BUTTON
# ================================

if st.button("Generate Travel Plan"):

    itinerary = generate_itinerary(inquiry)

    st.subheader("📅 AI Itinerary")

    st.markdown(
    f"""
    <div style="background:#f4f6ff;padding:25px;border-radius:10px">
    {itinerary}
    </div>
    """,
    unsafe_allow_html=True
    )

    # HOTELS

    st.subheader("🏨 Suggested Hotels")

    hotels = get_hotels()

    cols = st.columns(3)

    for i, hotel in enumerate(hotels):

        with cols[i]:

            st.image(hotel["image"])
            st.markdown(f"### {hotel['name']}")
            st.markdown(f"💰 {hotel['price']}")
            st.markdown("⭐ ⭐ ⭐ ⭐")

    # FLIGHTS

    st.subheader("✈️ Estimated Flights")

    st.write(flight_prices())

    # WHATSAPP MESSAGE

    st.subheader("💬 WhatsApp Reply")

    reply = whatsapp_reply(inquiry)

    st.markdown(
    f"""
    <div style="background:#e9fff1;padding:20px;border-radius:10px">
    {reply}
    </div>
    """,
    unsafe_allow_html=True
    )

    encoded = urllib.parse.quote(reply)

    link = f"https://wa.me/?text={encoded}"

    st.link_button("Send via WhatsApp", link)

    # PDF DOWNLOAD

    pdf = create_pdf(itinerary)

    st.download_button(
        "Download Itinerary PDF",
        open(pdf, "rb"),
        file_name="itinerary.pdf"
    )

    # CRM

    save_to_crm(inquiry)

    st.success("Customer inquiry saved to CRM.")

# ================================
# COST CHART
# ================================

budget = pd.DataFrame({
    "Category":["Flights","Hotels","Activities","Food"],
    "Cost":[15000,22000,8000,6000]
})

st.subheader("💸 Trip Cost Breakdown")

st.bar_chart(budget.set_index("Category"))