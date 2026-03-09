import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from openai import OpenAI
import urllib.parse
import io

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# ================================
# PAGE CONFIG
# ================================

st.set_page_config(
    page_title="Travel AI Agent Demo",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ Travel Agency AI Demo")
st.write("AI assistant that creates itineraries, suggests flights & hotels, and prepares proposals instantly.")

# ================================
# OPENROUTER CLIENT
# ================================

client = OpenAI(
    api_key="YOUR_OPENROUTER_KEY",
    base_url="https://openrouter.ai/api/v1"
)

# ================================
# DESTINATION DETECTION
# ================================

def detect_destination(text):

    text = text.lower()

    if "goa" in text:
        return "Goa"

    elif "dubai" in text:
        return "Dubai"

    elif "manali" in text:
        return "Manali"

    elif "corbett" in text:
        return "Jim Corbett"

    else:
        return "Popular Destination"


# ================================
# AI ITINERARY
# ================================

def generate_itinerary(inquiry):

    prompt = f"""
Create a travel itinerary.

Customer inquiry:
{inquiry}

Include:
Day-wise itinerary
Hotel suggestions
Travel tips
Budget estimate

Keep it clear and structured.
"""

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# ================================
# FLIGHT OPTIONS
# ================================

def get_flights(destination):

    if destination == "Goa":

        flights = [
            {"route": "Delhi → Goa", "airline": "IndiGo", "price": 6200},
            {"route": "Mumbai → Goa", "airline": "Air India", "price": 4500},
            {"route": "Bangalore → Goa", "airline": "SpiceJet", "price": 5200}
        ]

    elif destination == "Dubai":

        flights = [
            {"route": "Delhi → Dubai", "airline": "Emirates", "price": 22000},
            {"route": "Mumbai → Dubai", "airline": "FlyDubai", "price": 21000},
            {"route": "Bangalore → Dubai", "airline": "Air India", "price": 24000}
        ]

    elif destination == "Manali":

        flights = [
            {"route": "Delhi → Kullu", "airline": "Alliance Air", "price": 6500},
            {"route": "Mumbai → Kullu", "airline": "IndiGo", "price": 12000},
            {"route": "Bangalore → Kullu", "airline": "Air India", "price": 15000}
        ]

    else:

        flights = [
            {"route": "Delhi → Destination", "airline": "IndiGo", "price": 7000},
            {"route": "Mumbai → Destination", "airline": "Air India", "price": 6500},
            {"route": "Bangalore → Destination", "airline": "SpiceJet", "price": 7500}
        ]

    return flights


# ================================
# HOTEL SUGGESTIONS
# ================================

def get_hotels(destination):

    if destination == "Goa":

        hotels = [
            {"name": "Taj Holiday Village", "price": 8500, "image": "https://images.unsplash.com/photo-1582719508461-905c673771fd"},
            {"name": "W Goa", "price": 12000, "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945"},
            {"name": "La Calypso Beach Resort", "price": 6500, "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa"}
        ]

    elif destination == "Dubai":

        hotels = [
            {"name": "Atlantis The Palm", "price": 22000, "image": "https://images.unsplash.com/photo-1576675784201-0e142b423952"},
            {"name": "Burj Al Arab", "price": 45000, "image": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb"},
            {"name": "Jumeirah Beach Hotel", "price": 18000, "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4"}
        ]

    else:

        hotels = [
            {"name": "Luxury Resort", "price": 7500, "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945"},
            {"name": "Ocean View Hotel", "price": 6200, "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa"},
            {"name": "Boutique Stay", "price": 5400, "image": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4"}
        ]

    return hotels


# ================================
# PDF GENERATOR
# ================================

def create_pdf(text):

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)

    y = 800
    for line in text.split("\n"):
        pdf.drawString(50, y, line)
        y -= 20

    pdf.save()

    buffer.seek(0)
    return buffer


# ================================
# CRM LOGGING
# ================================

def log_lead(name, inquiry):

    data = pd.DataFrame([[name, inquiry]], columns=["Name", "Inquiry"])

    try:
        old = pd.read_csv("crm.csv")
        data = pd.concat([old, data])
    except:
        pass

    data.to_csv("crm.csv", index=False)


# ================================
# USER INPUT
# ================================

name = st.text_input("Customer Name")

inquiry = st.text_area("Customer Travel Inquiry")

if st.button("Generate Travel Plan"):

    destination = detect_destination(inquiry)

    st.success(f"Detected destination: **{destination}**")

    itinerary = generate_itinerary(inquiry)

    log_lead(name, inquiry)

    st.subheader("🧭 AI Itinerary")

    st.write(itinerary)

    # ========================
    # FLIGHTS
    # ========================

    st.subheader("✈️ Flight Options")

    flights = get_flights(destination)

    for flight in flights:

        st.write(f"**{flight['route']}** — {flight['airline']} — ₹{flight['price']}")

    # ========================
    # HOTELS
    # ========================

    st.subheader("🏨 Hotel Suggestions")

    hotels = get_hotels(destination)

    cols = st.columns(3)

    for i, hotel in enumerate(hotels):

        with cols[i]:
            st.image(hotel["image"])
            st.write(f"**{hotel['name']}**")
            st.write(f"₹{hotel['price']} / night")

    # ========================
    # BUDGET CHART
    # ========================

    st.subheader("💰 Estimated Trip Budget")

    avg_flight = sum([f["price"] for f in flights]) / len(flights)
    avg_hotel = sum([h["price"] for h in hotels]) / len(hotels)

    budget = pd.DataFrame({
        "Category": ["Flights", "Hotels", "Activities"],
        "Cost": [avg_flight, avg_hotel*3, 5000]
    })

    st.bar_chart(budget.set_index("Category"))

    # ========================
    # WHATSAPP MESSAGE
    # ========================

    st.subheader("📱 WhatsApp Reply")

    msg = f"""
Hello {name},

Here is your travel proposal for {destination}.

Flights starting from ₹{int(avg_flight)}
Hotels starting from ₹{int(avg_hotel)}

Let us know if you'd like us to confirm bookings.

Best regards
Travel Team
"""

    whatsapp = "https://wa.me/?text=" + urllib.parse.quote(msg)

    st.link_button("Send via WhatsApp", whatsapp)

    # ========================
    # PDF DOWNLOAD
    # ========================

    pdf = create_pdf(itinerary)

    st.download_button(
        "Download Itinerary PDF",
        pdf,
        file_name="travel_plan.pdf"
    )