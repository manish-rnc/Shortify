import streamlit as st
import requests

# Define the Flask backend API URL
# Update this with your deployed backend URL when in production
BASE_URL = "http://localhost:5000/api"

# Streamlit App Configuration
st.set_page_config(page_title="Shortify", page_icon="🔗", layout="centered")

# Title and Description
st.title("🔗 Shortify - URL Shortener")
st.markdown(
    """
    **Easily shorten your URLs and track their analytics!**  
    Use this app to generate short links and analyze their performance.
    """
)

# Divider for better layout separation
st.divider()

# Section: URL Shortening
st.header("Shorten Your URL")
long_url = st.text_input("Enter the URL to shorten", placeholder="e.g., https://example.com")

# Shorten URL Button
if st.button("Shorten URL", type="primary"):
    if long_url:
        # Send a POST request to the backend
        response = requests.post(f"{BASE_URL}/shorten", json={"long_url": long_url})
        
        if response.status_code == 201:
            # Display the shortened URL
            short_url = response.json().get('short_url')
            st.success("URL successfully shortened!")
            st.write(f"**Shortened URL**: [Click here]({short_url})")
        else:
            # Handle errors from the backend
            st.error("Error: Could not shorten the URL. Please try again.")
    else:
        # Handle empty input
        st.warning("Please enter a valid URL to shorten.")

# Divider for better layout separation
st.divider()

# Section: Analytics for Shortened URLs
st.header("Analytics for Shortened URLs")
short_id = st.text_input("Enter the Short URL ID", placeholder="e.g., abc123")

# Get Analytics Button
if st.button("Get Analytics"):
    if short_id:
        # Send a GET request to the backend for analytics
        response = requests.get(f"{BASE_URL}/analytics/{short_id}")
        
        if response.status_code == 200:
            # Display analytics data
            analytics = response.json()
            st.subheader("Analytics Data:")
            st.write(f"**Short URL**: {analytics['short_id']}")
            st.write(f"**Original URL**: {analytics['long_url']}")
            st.write(f"**Click Count**: {analytics['click_count']}")
            st.write(f"**Created At**: {analytics['created_at']}")
        else:
            # Handle errors from the backend
            st.error("Error: Short URL ID not found.")
    else:
        # Handle empty input
        st.warning("Please enter a valid Short URL ID.")

# Footer Section
st.divider()
st.markdown(
    """
    Developed with using [Streamlit](https://streamlit.io).  
    Backend powered by Flask.  
    """
)
