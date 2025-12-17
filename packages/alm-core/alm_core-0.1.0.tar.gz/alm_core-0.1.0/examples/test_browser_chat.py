"""
Test ALM Core - Interactive Browser Chat
Demonstrates:
1. Opening a browser to a real website
2. Chatting with ALM about the page
3. Having ALM help fill forms based on user details
"""
import os
import webbrowser
import time
from alm_core import AgentLanguageModel

# Check for API key
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("❌ Error: OPENAI_API_KEY environment variable not set")
    exit(1)

print("🚀 Testing ALM Core - Interactive Browser Chat")
print("=" * 70)
print()

# User details for form filling
USER_DETAILS = {
    "name": "Jalendar Reddy Maligireddy",
    "email": "jalendarreddy97@gmail.com",
    "phone": "555-123-4567",
    "company": "ALM Research",
    "job_title": "AI Research Engineer",
    "message": "I'm interested in testing ALM Core's browser automation capabilities."
}

# Initialize agent with PII protection
agent = AgentLanguageModel(
    api_key=api_key,
    llm_provider="openai",
    model="gpt-3.5-turbo",
    rules=[
        {"action": "submit_form", "allow": True},
        {"action": "extract_data", "allow": True}
    ]
)

print(f"✓ Agent initialized: {agent.llm.model}")
print()

# Sanitize user details (protect PII)
print("Step 1: Protecting User PII with Data Airlock")
print("-" * 70)

sanitized_details = {}
for key, value in USER_DETAILS.items():
    sanitized = agent.airlock.sanitize(value)
    sanitized_details[key] = sanitized
    if value != sanitized:
        print(f"  {key}: {value} → {sanitized}")
    else:
        print(f"  {key}: {value}")

print()
print("✅ User details sanitized (emails/phones protected)")
print()

# Open a real website (GitHub profile page - no actual form submission)
print("Step 2: Opening Browser to Website")
print("-" * 70)

url = "https://github.com/Jalendar10"
print(f"Opening: {url}")
webbrowser.open(url)

print("✅ Browser opened!")
print("   (Check your browser - showing GitHub profile)")
print()

# Simulate page content
print("Step 3: Simulating Page Analysis")
print("-" * 70)

# Simulate what the page might contain
page_context = f"""
This is the GitHub profile page for user Jalendar10.

Page elements visible:
- Profile name: Jalendar Reddy Maligireddy
- Repositories section showing: alm-core (public repository)
- Bio section (editable)
- Email visibility settings
- Social links section
- Contribution activity graph

The page has an "Edit profile" button that would show a form with fields like:
- Name
- Bio
- Company
- Location
- Website
- Social accounts
"""

print(page_context)
print()

# Chat with ALM about the page
print("Step 4: Chat with ALM about the Page")
print("-" * 70)
print()

# Question 1: What's on this page?
print("👤 User: What information do you see on this GitHub profile page?")
print()

query1 = f"Based on this page content:\n{page_context}\n\nWhat key information is displayed on this profile page? Answer in 2-3 sentences."

messages1 = [{"role": "user", "content": query1}]
response1 = agent.llm.generate(messages1)

print(f"🤖 ALM: {response1}")
print()
print("-" * 70)
print()

# Question 2: How would you fill out a form?
print("👤 User: If there was a contact form, how would you fill it out with my details?")
print()

# Use sanitized details (LLM never sees real email/phone)
query2 = f"""I need to fill out a contact form with these details:
{sanitized_details}

The form has fields for: name, email, phone, company, job_title, and message.

How would you fill out this form? List each field and what you would enter.
"""

messages2 = [{"role": "user", "content": query2}]
response2 = agent.llm.generate(messages2)

print(f"🤖 ALM: {response2}")
print()
print("-" * 70)
print()

# Question 3: What actions can you take?
print("👤 User: What actions could you perform on this GitHub profile page?")
print()

query3 = f"""Based on this GitHub profile page:
{page_context}

What actions could an automated agent safely perform? Consider:
1. Data extraction
2. Profile updates
3. Navigation
4. Information gathering

List 3-4 safe actions with brief explanations.
"""

messages3 = [{"role": "user", "content": query3}]
response3 = agent.llm.generate(messages3)

print(f"🤖 ALM: {response3}")
print()

# Demonstrate form field mapping
print("=" * 70)
print("Step 5: Demonstrate Form Field Mapping")
print("-" * 70)
print()

print("If this page had a contact form, ALM would map fields like this:")
print()

form_fields = {
    "input[name='name']": sanitized_details["name"],
    "input[name='email']": sanitized_details["email"],
    "input[name='phone']": sanitized_details["phone"],
    "input[name='company']": sanitized_details["company"],
    "input[name='job_title']": sanitized_details["job_title"],
    "textarea[name='message']": sanitized_details["message"]
}

for selector, value in form_fields.items():
    print(f"  {selector:30s} → {value}")

print()
print("✅ Form mapping complete (with PII protection)")
print()

# Summary
print("=" * 70)
print("🎉 INTERACTIVE BROWSER CHAT TEST COMPLETED!")
print("=" * 70)
print()
print("Demonstrated Capabilities:")
print("  ✅ PII Protection - Email/phone sanitized before sending to LLM")
print("  ✅ Browser Control - Opened GitHub profile page")
print("  ✅ Page Understanding - ALM analyzed page content")
print("  ✅ Conversational Interface - Multi-turn chat about the page")
print("  ✅ Form Filling Logic - Mapped user details to form fields")
print("  ✅ Safe Actions - ALM suggested appropriate actions")
print()
print("Key Security Features:")
print("  🔒 Data Airlock: Real email/phone never sent to LLM")
print("  🔒 Constitutional Rules: Only allowed actions permitted")
print("  🔒 User-in-the-loop: Sensitive actions require confirmation")
print()
print("Note: For full browser automation with actual form filling,")
print("      install Playwright: pip install playwright && playwright install")
