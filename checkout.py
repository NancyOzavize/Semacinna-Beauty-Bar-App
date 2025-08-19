import streamlit as st
import csv
import re
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Payment Page
def checkout():

    # Create receipt folder if it doesn't exist
    os.makedirs("uploaded_receipts", exist_ok=True)

    # === Email credentials ===
    EMAIL_ADDRESS = "nancytijani1@gmail.com"
    EMAIL_PASSWORD = "juhw yvcr vlbu ihux"

    # === Groq API ===
    GROQ_API_KEY = "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"
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

    if st.session_state.get("page") == "checkout":
        st.title("💳 Payment & Upload Receipt")

        # === Sidebar Navigation ===
        st.sidebar.header("🔗 Navigation")
        if st.sidebar.button("🏠 Home"):
            st.session_state.page = "home"
        if st.sidebar.button("💬 Chat"):
            st.session_state.page = "chat"
        if st.sidebar.button("🔑 Sign In"):
            st.session_state.page = "signin"
        if st.sidebar.button("📝 Sign Up"):
            st.session_state.page = "signup"

        # === Checkout Content ===
        st.subheader("Bank Account Details")
        st.write("**Bank Name:** Zenith Bank Plc")
        st.write("**Account Name:** Semacinna Nigeria Limited")
        st.write("**Account Number:** 1234567890")
        st.write("**Amount:** ₦{}".format(sum(item['price'] * item['quantity'] for item in st.session_state.cart)))

        st.info("Please make the payment, then upload a clear picture or PDF of your receipt below.")

        receipt = st.file_uploader("📤 Upload your payment receipt", type=["jpg", "jpeg", "png", "pdf"])
        
        # Delivery address
        delivery_address = st.text_area("🏠 Enter your delivery address")

        # Customer email (re-ask here to ensure we have it)
        customer_email = st.text_input("📧 Enter your email for confirmation")

        if st.button("✅ Complete Order"):
            if receipt and delivery_address.strip() and customer_email.strip():
                st.success("Thank you! Your order has been placed successfully. A sales representative will contact you soon.")
                
                # Save uploaded receipt
                save_path = os.path.join("uploaded_receipts", receipt.name)
                with open(save_path, "wb") as f:
                    f.write(receipt.getbuffer())

                # Build email body
                subject = "Semacinna Order – 🛍️ Payment & Delivery Confirmation"
                body = "Hi,\n\nA new order has been placed. Here are the details:\n\n"

                total = 0
                for item in st.session_state.cart:
                    line = f" - {item['quantity']} x {item['name']} (Shade: {item['shade']}) – ₦{item['price'] * item['quantity']}\n"
                    body += line
                    total += item['price'] * item['quantity']

                body += f"\nTotal: ₦{total}\n"
                body += f"\nDelivery Address:\n{delivery_address}\n"
                body += "\nPlease find the attached payment receipt.\n\nThank you,\nSemacinna Bot"

                # Function to send email with attachment
                def send_email_with_attachment(to_email):
                    message = MIMEMultipart()
                    message["From"] = EMAIL_ADDRESS
                    message["To"] = to_email
                    message["Subject"] = subject
                    message.attach(MIMEText(body, "plain", _charset="utf-8"))

                    # Attach receipt
                    with open(save_path, "rb") as f:
                        from email.mime.base import MIMEBase
                        from email import encoders
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename={receipt.name}")
                        message.attach(part)

                    try:
                        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                            server.send_message(message)
                        return True
                    except Exception as e:
                        st.error(f"❌ Failed to send email: {e}")
                        return False

                # Send to store owner
                send_email_with_attachment("nancytijani1@gmail.com")

                # Send confirmation to customer
                send_email_with_attachment(customer_email)

                # Clear cart after sending
                st.session_state.cart = []
                st.session_state.page = "home"

            else:
                st.error("⚠️ Please upload your receipt, enter your delivery address and email.")
