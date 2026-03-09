import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from openai import OpenAI
import urllib.parse
import io

# ===============================
# PAGE CONFIG
# ===============================

st.set_page_config(
    page_title="Travel AI Demo",
    page_icon="✈️",
    layout="wide"
)

st.title("✈️ AI Travel Planner")
st.caption("Instant itineraries, hotel suggestions, flight ideas, and proposal generation.")

# ===============================
# OPENROUTER CLIENT
# ===============================

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# ===============================
# DESTINATION DETECTION
# ===============================

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


# ===============================
# DESTINATION PHOTO GALLERY
# ===============================

def get_destination_photos(destination):

    photos = {
        "Goa":[
            "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2",
            "https://images.unsplash.com/photo-1582972236019-ea8a97ef5d8c",
            "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6"
        ],
        "Dubai":[
            "https://images.unsplash.com/photo-1512453979798-5ea266f8880c",
            "https://images.unsplash.com/photo-1526495124232-a04e1849168c",
            "https://images.unsplash.com/photo-1504274066651-8d31a536b11a"
        ],
        "Manali":[
            "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23",
            "https://images.unsplash.com/photo-1613649532404-3c3b5f1f8f54",
            "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23"
        ]
    }

    return photos.get(destination, photos["Goa"])


# ===============================
# FLIGHTS
# ===============================

def get_flights(destination):

    if destination == "Goa":
        return [
            {"route":"Delhi → Goa","airline":"IndiGo","price":6200},
            {"route":"Mumbai → Goa","airline":"Air India","price":4500},
            {"route":"Bangalore → Goa","airline":"SpiceJet","price":5200}
        ]

    elif destination == "Dubai":
        return [
            {"route":"Delhi → Dubai","airline":"Emirates","price":22000},
            {"route":"Mumbai → Dubai","airline":"FlyDubai","price":21000},
            {"route":"Bangalore → Dubai","airline":"Air India","price":24000}
        ]

    else:
        return [
            {"route":"Delhi → Destination","airline":"IndiGo","price":7000},
            {"route":"Mumbai → Destination","airline":"Air India","price":6500},
            {"route":"Bangalore → Destination","airline":"SpiceJet","price":7500}
        ]


# ===============================
# HOTELS
# ===============================

def get_hotels(destination):

    if destination == "Goa":

        return [
            {"name":"Taj Holiday Village","price":8500,
            "image":"https://images.unsplash.com/photo-1582719508461-905c673771fd"},
            {"name":"W Goa","price":12000,
            "image":"https://images.unsplash.com/photo-1566073771259-6a8506099945"},
            {"name":"La Calypso Beach Resort","price":6500,
            "image":"https://images.unsplash.com/photo-1551882547-ff40c63fe5fa"}
        ]

    elif destination == "Dubai":

        return [
            {"name":"Atlantis The Palm","price":22000,
            "image":"https://images.unsplash.com/photo-1576675784201-0e142b423952"},
            {"name":"Burj Al Arab","price":45000,
            "image":"https://images.unsplash.com/photo-1542314831-068cd1dbfeeb"},
            {"name":"Jumeirah Beach Hotel","price":18000,
            "image":"https://images.unsplash.com/photo-1520250497591-112f2f40a3f4"}
        ]

    else:

        return [
            {"name":"Luxury Resort","price":7500,
            "image":"https://images.unsplash.com/photo-1566073771259-6a8506099945"},
            {"name":"Ocean View Hotel","price":6200,
            "image":"https://images.unsplash.com/photo-1551882547-ff40c63fe5fa"},
            {"name":"Boutique Stay","price":5400,
            "image":"https://images.unsplash.com/photo-1520250497591-112f2f40a3f4"}
        ]


# ===============================
# AI ITINERARY
# ===============================

def generate_itinerary(inquiry):

    prompt = f"""
Create a DAY-WISE travel itinerary.

Customer inquiry:
{inquiry}

Format clearly:

Day 1:
Day 2:
Day 3:

Include activities and places.
"""

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role":"user","content":prompt}]
    )

    return response.choices[0].message.content


# ===============================
# AI ATTRACTIONS
# ===============================

def get_attractions(destination):

    prompt = f"""
List top 5 tourist attractions in {destination}.
Return as bullet points.
"""

    response = client.chat.completions.create(
        model="openrouter/auto",
        messages=[{"role":"user","content":prompt}]
    )

    return response.choices[0].message.content


# ===============================
# PDF GENERATOR
# ===============================

def create_pdf(text):

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)

    y = 800

    for line in text.split("\n"):
        pdf.drawString(40,y,line)
        y -= 20

    pdf.save()
    buffer.seek(0)

    return buffer


# ===============================
# CRM LOGGING
# ===============================

def log_lead(name,inquiry):

    data = pd.DataFrame([[name,inquiry]],columns=["Name","Inquiry"])

    try:
        old = pd.read_csv("crm.csv")
        data = pd.concat([old,data])
    except:
        pass

    data.to_csv("crm.csv",index=False)


# ===============================
# TRIP BUILDER UI (small upgrade)
# ===============================

col1,col2,col3 = st.columns(3)

name = col1.text_input("Customer Name")
destination_input = col2.text_input("Destination")
days = col3.selectbox("Trip Duration",["3 Days","4 Days","5 Days","7 Days"])

budget = st.selectbox("Budget Range",["₹20k-₹40k","₹40k-₹80k","₹80k+"])


# Convert UI to inquiry text

inquiry = f"{days} trip to {destination_input} with budget {budget}"


# ===============================
# GENERATE PLAN
# ===============================

if st.button("Generate Travel Plan"):

    destination = detect_destination(inquiry)

    st.success(f"Destination detected: {destination}")

    # PHOTO GALLERY

    st.subheader("📸 Destination Preview")

    photos = get_destination_photos(destination)

    cols = st.columns(3)

    for i,p in enumerate(photos):
        cols[i].image(p,use_container_width=True)

    # ITINERARY

    itinerary = generate_itinerary(inquiry)

    st.subheader("📅 Itinerary")

    days_list = itinerary.split("Day")

    for d in days_list:
        if d.strip() != "":
            st.markdown(f"""
            ### Day {d}
            """)

    st.write(itinerary)

    # ATTRACTIONS

    st.subheader("📍 Top Attractions")

    attractions = get_attractions(destination)

    st.write(attractions)

    # FLIGHTS

    st.subheader("✈️ Flight Options")

    flights = get_flights(destination)

    for f in flights:
        st.write(f"**{f['route']}** — {f['airline']} — ₹{f['price']}")

    # HOTELS

    st.subheader("🏨 Hotel Suggestions")

    hotels = get_hotels(destination)

    cols = st.columns(3)

    for i,h in enumerate(hotels):

        with cols[i]:

            st.image(h["image"])
            st.write(f"**{h['name']}**")
            st.write(f"₹{h['price']} / night")

    # BUDGET CHART

    st.subheader("💰 Trip Budget Estimate")

    avg_flight = sum([f["price"] for f in flights]) / len(flights)
    avg_hotel = sum([h["price"] for h in hotels]) / len(hotels)

    chart = pd.DataFrame({
        "Category":["Flights","Hotels","Activities"],
        "Cost":[avg_flight,avg_hotel*3,5000]
    })

    st.bar_chart(chart.set_index("Category"))

    # WHATSAPP

    msg = f"""
Hello {name},

Here is your {destination} travel proposal.

Flights starting from ₹{int(avg_flight)}
Hotels from ₹{int(avg_hotel)}

Let us know if you want us to confirm bookings.
"""

    whatsapp = "https://wa.me/?text=" + urllib.parse.quote(msg)

    st.link_button("Send Proposal via WhatsApp",whatsapp)

    # PDF

    pdf = create_pdf(itinerary)

    st.download_button(
        "Download Itinerary PDF",
        pdf,
        file_name="travel_itinerary.pdf"
    )

    log_lead(name,inquiry)