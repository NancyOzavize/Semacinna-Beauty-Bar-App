import streamlit as st
import csv
import re
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


def chat():

    # Create receipt folder if it doesn't exist
    os.makedirs("uploaded_receipts", exist_ok=True)

    # === Email credentials ===
    EMAIL_ADDRESS = "nancytijani1@gmail.com"
    EMAIL_PASSWORD = "juhw yvcr vlbu ihux"

    # === Groq API ===
    GROQ_API_KEY = "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"
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

    BUSINESS_CONTEXT = """
    You are a chatbot for Semacinna Cosmetics. 
    Only answer questions related to cosmetics, skincare, pricing, products, store information, and customer service.
    If a user asks about anything else, say:
    "I'm here to assist only with Semacinna Cosmetics. Please ask me about our products or services."
    """

    # === Session state initialization ===
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'cart' not in st.session_state:
        st.session_state.cart = []

    if "order_confirmed" not in st.session_state:
        st.session_state.order_confirmed = False


    # === Function: Talk to Groq ===
    def chat_with_groq(message):
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": BUSINESS_CONTEXT},
                {"role": "user", "content": message}
            ]
        }
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            return f"Error: {response.status_code} - {response.text}"

    # === Function: Get product details ===
    def get_product_details(user_input):
        try:
            with open("pricelist.csv", mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                user_input_lower = user_input.lower()
                best_match = None
                max_overlap = 0

                for row in reader:
                    product_name = row["Product"].strip().lower()
                    normalized_input = user_input_lower.replace(" ", "")
                    normalized_product = product_name.replace(" ", "")

                    if normalized_input == normalized_product:
                        return {
                            "name": row["Product"],
                            "price": int(row["Price"]),
                            "description": row.get("Description", "").strip(),
                            "shades": row.get("Shades", "").strip()
                        }

                    product_words = set(product_name.split())
                    user_words = set(user_input_lower.split())
                    overlap = len(user_words & product_words)
                    if overlap > max_overlap:
                        best_match = row
                        max_overlap = overlap

                if best_match and max_overlap > 1:
                    return {
                        "name": best_match["Product"],
                        "price": int(best_match["Price"]),
                        "description": best_match.get("Description", "").strip(),
                        "shades": best_match.get("Shades", "").strip()
                    }
                else:
                    return None
        except FileNotFoundError:
            return None

    # === Function: Get all items in a category ===
    def get_category_products(category):
        try:
            with open("pricelist.csv", mode="r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                return [
                    f"{row['Product']} – ₦{row['Price']}"
                    for row in reader if row["Category"].lower() == category.lower()
                ]
        except FileNotFoundError:
            return []

    # === Supported categories ===
    supported_categories = [
        "Powder", "Foundation", "Lipgloss", "Body Lotion", "Concealer",
        "Mascara", "Eyeshadow", "Face Wash", "Face Cream", "Body Wash",
        "Serum", "Brush", "Pencil", "Eyeliner"
    ]


    # === Function: Display chat history ===
    def display_chat():
        for sender, msg in st.session_state.chat_history:
            with st.chat_message(sender):
                st.markdown(msg)

    # === Function: Send order email ===
    def send_order_email(cart, to_email):
        subject = "Semacinna Order – Stock Confirmation Needed"
        body = "Hi,\n\nA customer just placed the following order. Please check if all items are in stock and reply 'yes' or list any unavailable products:\n\n"

        total = 0
        for item in cart:
            line = f" - {item['quantity']} x {item['name']} (Shade: {item['shade']}) – ₦{item['price'] * item['quantity']}\n"
            body += line
            total += item['price'] * item['quantity']

        body += f"\nTotal: ₦{total}\n\nThank you!\nSemacinna Chatbot"
        body = body.replace('\xa0', ' ')

        message = MIMEMultipart()
        message["From"] = EMAIL_ADDRESS
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain", _charset="utf-8"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                server.send_message(message)
            return True
        except Exception:
            return False

    # === Streamlit UI ===
    st.set_page_config(page_title="Semacinna Cosmetics Chatbot", layout="centered")
    st.title("💄 Semacinna Cosmetics Chatbot")

    user_input = st.chat_input("Ask a question or search for a product...")


    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        # 🌍 Handle store location questions
        if any(kw in user_input.lower() for kw in ["where is your store", "location", "store address", "are you in lagos", "are you in abuja"]):
            location_response = "📍 Our physical store is located in **Lagos**, but we are fully operational online in **Abuja** and deliver nationwide."
            st.session_state.chat_history.append(("assistant", location_response))
            display_chat()
            st.stop()
        product = get_product_details(user_input)

        category_response = ""
        category_handled = False
        for category in supported_categories:
            if category.lower() in user_input.lower():
                items = get_category_products(category)
                if "how much" in user_input.lower() or "price" in user_input.lower() or "add" in user_input.lower() or "have" in user_input.lower() or "available" in user_input.lower() :
                    if items:
                        category_response += f"Here are our {category.lower()} options:\n"
                        for i in items:
                            category_response += f" - {i}\n"
                        category_response += "Please tell me which one you're interested in."
                    else:
                        category_response += f"Sorry, we currently have no {category.lower()} listed."
                    category_handled = True
                    break
                elif "i want" in user_input.lower() or "show" in user_input.lower():
                    if items:
                        category_response += f"We have several {category.lower()} products:\n"
                        for i in items:
                            category_response += f" - {i}\n"
                        category_response += "Please tell me which one you'd like to buy."
                    else:
                        category_response += f"Sorry, we currently have no {category.lower()} products."
                    category_handled = True
                    break

        if category_handled:
            st.session_state.chat_history.append(("assistant", category_response))
            display_chat()
            st.stop()

        if product:
            bot_response = f"**{product['name']}** – ₦{product['price']}\n"
            if product['description']:
                bot_response += f"📝 {product['description']}\n"
            if product['shades']:
                bot_response += f"🎨 Available shades: {product['shades']}\n"
                bot_response += "Please enter the quantity and shade name (e.g., '2 Sugar Plum') to add to cart."
            else:
                bot_response += "Would you like to add this to your cart?"
            st.session_state.selected_product = product

        elif hasattr(st.session_state, 'selected_product'):
            selected_product = st.session_state.selected_product
            if selected_product:
                if not selected_product.get('shades'):  # No shades
                    if any(word in user_input.lower() for word in ["yes", "add to cart", "yes please", "okay", "sure"]):
                        st.session_state.cart.append({
                            "name": selected_product["name"],
                            "shade": "N/A",
                            "price": selected_product["price"],
                            "quantity": 1
                        })
                        bot_response = f"✅ 1 x {selected_product['name']} has been added to your cart."
                        del st.session_state.selected_product
                    else:
                        bot_response = f"Would you like to add **{selected_product['name']}** to your cart? Please type 'yes' or 'add to cart' to confirm."
                else:
                    entries = re.split(r',| and ', user_input.lower())
                    added = []
                    for entry in entries:
                        match = re.match(r'(\d+)\s+(.+)', entry.strip())
                        if match:
                            qty = int(match.group(1))
                            shade = match.group(2).strip().title()
                            added.append({
                                "name": selected_product["name"],
                                "shade": shade,
                                "price": selected_product["price"],
                                "quantity": qty
                            })

                    if added:
                        st.session_state.cart.extend(added)
                        bot_response = "Items added to cart:\n" + "\n".join([
                            f" - {item['quantity']} x {item['name']} (Shade: {item['shade']})"
                            for item in added
                        ])
                        del st.session_state.selected_product
                    else:
                        bot_response = "❌ I couldn't understand your input. Please try again like '2 Sugar Plum'."
            else:
                bot_response = chat_with_groq(user_input)
        else:
            bot_response = chat_with_groq(user_input)

        st.session_state.chat_history.append(("assistant", bot_response))

            
        
    # === Display conversation ===
    display_chat()



    # === Cart section ===
    st.sidebar.header("🛒 Shopping Cart")
    if st.session_state.cart:
        total = 0
        for item in st.session_state.cart:
            st.sidebar.write(f"{item['quantity']} x {item['name']} ({item['shade']}) – ₦{item['price'] * item['quantity']}")
            total += item['price'] * item['quantity']
        st.sidebar.write(f"**Total:** ₦{total}")

        # Step 1: Collect customer email input (persistent across reruns)
        customer_email = st.sidebar.text_input("Enter your email to receive order summary")

        # Step 2: Send email when button is clicked and email is filled
        if st.sidebar.button("📨 Confirm Order"):
            if customer_email:
                store_owner_email = "nancytijani1@gmail.com"
                subject = "Semacinna Order – 🛍️ Your Semacinna Cosmetics Order Confirmation"
                body = f"Hi there,\n\nThank you for shopping at Semacinna Beauty Bar!\n\nLove,\nSemacinna Bot"

                for item in st.session_state.cart:
                    line = f" - {item['quantity']} x {item['name']} (Shade: {item['shade']}) – ₦{item['price'] * item['quantity']}\n"
                    body += line
                

                message = MIMEMultipart()
                message["From"] = EMAIL_ADDRESS
                message["To"] =  store_owner_email
                message["Subject"] = subject
                message.attach(MIMEText(body, "plain", _charset="utf-8"))

                try:
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                        server.send_message(message)

                    st.sidebar.success("✅ Final Order Reciept Sent.")
                    st.session_state.order_confirmed = True
                    

                except Exception as e:
                    st.sidebar.error(f"❌ Failed to send email: {e}")

                message = MIMEMultipart()
                message["From"] = EMAIL_ADDRESS
                message["To"] = customer_email
                message["Subject"] = subject
                message.attach(MIMEText(body, "plain", _charset="utf-8"))

                try:
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                        server.send_message(message)

                    st.sidebar.success("✅ Final Order Reciept Sent.")
                    st.session_state.order_confirmed = True
                    

                except Exception as e:
                    st.sidebar.error(f"❌ Failed to send email: {e}")
            else:
                st.sidebar.warning("⚠️ Please enter your email before confirming.")



    if st.session_state.order_confirmed:
        if st.button("💳 Checkout"):
            st.session_state.page = "checkout"

    

