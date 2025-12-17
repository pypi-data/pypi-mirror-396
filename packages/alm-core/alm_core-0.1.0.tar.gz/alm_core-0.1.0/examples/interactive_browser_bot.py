"""
Interactive Browser Chatbot
Run this alongside your browser to chat with ALM about any webpage
"""
import os
import webbrowser
from alm_core import AgentLanguageModel

# Check for API key
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("❌ Error: OPENAI_API_KEY environment variable not set")
    exit(1)

print("=" * 70)
print("🤖 ALM Interactive Browser Assistant")
print("=" * 70)
print()

# User details for form filling
USER_DETAILS = {
    "name": "Jalendar Reddy Maligireddy",
    "email": "jalendarreddy97@gmail.com",
    "phone": "555-123-4567",
    "company": "ALM Research",
    "job_title": "AI Research Engineer"
}

# Initialize agent
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
print(f"✓ User profile loaded: {USER_DETAILS['name']}")
print()

# Sanitize user details once
sanitized_details = {}
for key, value in USER_DETAILS.items():
    sanitized_details[key] = agent.airlock.sanitize(value)

print("=" * 70)
print("Commands:")
print("  'open <url>'     - Open a website (e.g., open google.com)")
print("  'open <search>'  - Search Google (e.g., open search for fiserv)")
print("  'fill form'      - Show how to fill a form with your details")
print("  'my details'     - Show your sanitized user details")
print("  'help'           - Show this help message")
print("  'quit'           - Exit the chatbot")
print()
print("Shortcuts: gmail, github, google, yahoo, youtube, linkedin")
print("=" * 70)
print()

# Conversation history
conversation_history = []
current_page_context = None

while True:
    # Get user input
    user_input = input("👤 You: ").strip()
    
    if not user_input:
        continue
    
    # Handle commands
    if user_input.lower() == 'quit' or user_input.lower() == 'exit':
        print("\n👋 Goodbye! Thanks for using ALM Browser Assistant!")
        break
    
    elif user_input.lower() == 'help':
        print("\n🤖 ALM: Available commands:")
        print("  - 'open <url>' to open a website")
        print("  - 'fill form' to see form filling suggestions")
        print("  - 'my details' to view your profile")
        print("  - Ask me anything about web pages, forms, or actions!\n")
        continue
    
    elif user_input.lower().startswith('open '):
        url = user_input[5:].strip()
        
        # Handle common website shortcuts
        shortcuts = {
            'gmail': 'https://mail.google.com',
            'github': 'https://github.com/Jalendar10',
            'google': 'https://google.com',
            'youtube': 'https://youtube.com',
            'twitter': 'https://twitter.com',
            'linkedin': 'https://linkedin.com',
            'yahoo': 'https://yahoo.com'
        }
        
        # Check if it's a shortcut
        if url.lower() in shortcuts:
            url = shortcuts[url.lower()]
        # Check if it's a search query (contains spaces or "search for")
        elif ' ' in url or 'search' in url.lower():
            # Extract search terms
            search_terms = url.replace('search for', '').replace('search', '').strip()
            # Use Google search
            import urllib.parse
            encoded_query = urllib.parse.quote(search_terms)
            url = f'https://www.google.com/search?q={encoded_query}'
        elif not url.startswith('http'):
            url = 'https://' + url
            
        print(f"\n🤖 ALM: Opening {url} in your browser...")
        webbrowser.open(url)
        current_page_context = f"Currently viewing: {url}"
        print(f"✅ Browser opened! You can now ask me about this page.\n")
        continue
    
    elif user_input.lower() == 'my details':
        print("\n🤖 ALM: Here are your details (with PII protection):")
        for key, value in sanitized_details.items():
            original = USER_DETAILS[key]
            if value != original:
                print(f"  {key}: {original} → {value} (protected)")
            else:
                print(f"  {key}: {value}")
        print()
        continue
    
    elif user_input.lower() == 'fill form':
        print("\n🤖 ALM: Here's how I would fill a typical contact form:")
        print("\n  Field Mappings:")
        print(f"    Name:      {sanitized_details['name']}")
        print(f"    Email:     {sanitized_details['email']} (protected)")
        print(f"    Phone:     {sanitized_details['phone']}")
        print(f"    Company:   {sanitized_details['company']}")
        print(f"    Job Title: {sanitized_details['job_title']}")
        print("\n  Note: Your real email is protected by Data Airlock!\n")
        continue
    
    # Regular chat
    print()
    
    # Build context
    context_parts = []
    if current_page_context:
        context_parts.append(f"Context: {current_page_context}")
    
    # Add user details context (sanitized)
    context_parts.append(f"User profile (for form filling): {sanitized_details}")
    
    # Build the full query
    full_query = "\n".join(context_parts) + f"\n\nUser question: {user_input}"
    
    # Add to conversation history
    conversation_history.append({"role": "user", "content": full_query})
    
    # Keep only last 6 messages (3 exchanges) to avoid token limits
    if len(conversation_history) > 6:
        conversation_history = conversation_history[-6:]
    
    try:
        # Get response from ALM
        response = agent.llm.generate(conversation_history)
        
        # Add response to history
        conversation_history.append({"role": "assistant", "content": response})
        
        print(f"🤖 ALM: {response}")
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}\n")

