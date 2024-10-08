import socket
import streamlit as st
import requests
from ping3 import ping

# Helper function to get public IP address and location
def get_public_ip_info():
    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        public_ip = data.get("ip", "N/A")
        city = data.get("city", "N/A")
        country = data.get("country", "N/A")
        return public_ip, city, country
    except Exception as e:
        return "Error retrieving public IP", str(e), "N/A"

# Helper function to resolve domain to IP and get its geolocation info
def get_domain_info(domain):
    try:
        # Step 1: Resolve domain to IP
        resolved_ip = socket.gethostbyname(domain)
        # Step 2: Fetch information using resolved IP
        response = requests.get(f"https://ipinfo.io/{resolved_ip}/json", timeout=10)
        data = response.json()
        ip = data.get("ip", "N/A")
        city = data.get("city", "N/A")
        country = data.get("country", "N/A")
        return ip, city, country
    except socket.gaierror:
        return None, None, None  # Domain couldn't be resolved
    except requests.exceptions.Timeout:
        return "Timeout", None, None  # Request timed out
    except Exception as e:
        return "Error retrieving domain info", str(e), "N/A"

# Helper function to ping a domain
def ping_domain(domain):
    try:
        ping_result = ping(domain, timeout=10)
        if ping_result is None:
            return "Ping failed or host unreachable"
        return f"{round(ping_result * 1000, 2)} ms"
    except Exception:
        return "Ping failed or host unreachable"

# Helper function to get IP address information (company, location)
def get_ip_info(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        data = response.json()
        city = data.get("city", "N/A")
        country = data.get("country", "N/A")
        org = data.get("org", "N/A")  # Company or organization info
        return city, country, org
    except Exception as e:
        return "Error", str(e), "N/A"

# Streamlit app
st.set_page_config(page_title="IP insight", page_icon="/projects/icon.webp")
st.title("IP and Domain Information Tool")

st.sidebar.markdown("""
## IP Insight

**IP Insight** is a simple tool that allows you to gather information about your public IP, domain names, and specific IP addresses. 

### Key Features:
- **What's My IP:** Find your public IP and its associated location (city and country).
- **Domain Lookup:** Enter a domain, resolve its IP, check its geolocation, and perform a ping test.
- **IP Lookup:** Fetch geolocation and company/organization details about an IP address.

### Technologies Used:
- **Streamlit:** Provides the user interface for this web-based application.
- **Requests:** Handles HTTP requests to obtain geolocation information from external APIs.
- **ping3:** Used to measure the response time when pinging a domain.
- **ipinfo.io API:** Retrieves IP address geolocation data, such as city, country, and organization.

Streamline your IP and domain resolution tasks with **IP Insight**!
""")


# Section 1: What's my IP?
if st.button("What's my IP?"):
    public_ip, city, country = get_public_ip_info()
    st.write(f"**Your Public IP:** {public_ip}")
    st.write(f"**City:** {city}")
    st.write(f"**Country:** {country}")

# Section 2: Domain info
st.subheader("Domain Lookup")
domain_input = st.text_input("Enter a domain (e.g., google.com):")
if st.button("Run Domain Lookup"):
    if domain_input:
        ip, city, country = get_domain_info(domain_input)
        if ip is None:
            st.write(f"The domain '{domain_input}' can't be resolved or reached.")
        else:
            st.write(f"**Domain IP:** {ip}")
            st.write(f"**City:** {city}")
            st.write(f"**Country:** {country}")
            
            ping_result = ping_domain(domain_input)
            st.write(f"**Ping result:** {ping_result}")
    else:
        st.write("Please enter a domain.")

# Section 3: IP Address info
st.subheader("IP Address Lookup")
ip_input = st.text_input("Enter an IP address:")
if st.button("Run IP Lookup"):
    if ip_input:
        city, country, org = get_ip_info(ip_input)
        st.write(f"**City:** {city}")
        st.write(f"**Country:** {country}")
        st.write(f"**Organization/Company:** {org}")
    else:
        st.write("Please enter an IP address.")