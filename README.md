# Axis Retail Agent 🛍️

**A multi-agent AI system that runs a clothing store's customer service over WhatsApp — checks inventory, takes orders, and answers FAQs, in whatever language the customer writes in.**

Built with LangGraph, this project routes every customer message through a supervisor agent to one of three specialized agents, each with its own tools and memory, so conversations feel like talking to a real (very patient) store assistant instead of a rigid chatbot.

---

## 🎯 What it does

A customer messages the store's WhatsApp number:

> "kurti available hai kya?"

The agent checks the live database, replies with real stock — no hallucinated products, no guessed prices. If they want to order, a dedicated Order Agent walks them through size, color, quantity, name, phone, and address **one step at a time**, shows a full summary, and only places the order after explicit confirmation. Ask about store timing or delivery, and a third agent handles that — all without the customer ever noticing the handoff.

---

## 🧠 Architecture

```
Customer (WhatsApp)
        │
        ▼
 Selenium WhatsApp Bridge  ──►  Supervisor Agent
                                       │
                    ┌──────────────────┼──────────────────┐
                    ▼                  ▼                  ▼
            Inventory Agent      Order Agent          FAQ Agent
            (check_inventory)    (placeorder)          (no tools)
                    │                  │
                    └────────► SQLite Database ◄────────┘
```

- **Supervisor Agent** — reads intent and routes the conversation to the right specialist
- **Inventory Agent** — answers stock/price/size questions using a live `check_inventory` tool, never invents product info
- **Order Agent** — collects order details step-by-step, confirms with a summary, then places the order
- **FAQ Agent** — handles timing, delivery, and return policy
- **Memory** — each customer's conversation is tracked independently via LangGraph's `MemorySaver`, keyed by their WhatsApp identity
- **WhatsApp Bridge** — a Selenium-driven layer that reads incoming messages from WhatsApp Web and sends agent replies back, with session persistence so it doesn't need a fresh QR scan every run

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph (StateGraph, conditional edges, checkpointed memory) |
| LLM | Groq / OpenRouter (swappable via a single config line) |
| Database | SQLite |
| Messaging interface | Selenium (WhatsApp Web automation) |
| Language | Python |

---

## ✨ Key features

- **Multi-agent routing** — a supervisor delegates to specialized agents instead of one overloaded prompt trying to do everything
- **Grounded responses** — inventory answers always come from a real database query, never from the model's imagination
- **Structured order flow** — no order is placed without size, color, quantity, and contact details confirmed by the customer first
- **Per-customer memory** — conversations persist across messages without mixing up different customers
- **Multilingual by default** — responds in whichever language (English, Urdu, or a mix) the customer uses
- **Resilient messaging layer** — handles WhatsApp Web's shifting DOM, distinguishes incoming vs. outgoing messages, and recovers from duplicate/stale message states

---

## 🚀 Setup

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/axis-retail-agent.git
cd axis-retail-agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your environment variables
# .env
OPENROUTER_API_KEY=your_key
GROQ_API_KEY=your_key
TAVILY_API_KEY=your_key

# 4. Initialize the database
python database.py

# 5. Run the agent (terminal mode)
python main.py

# 6. Or launch the WhatsApp bridge
python whatsapp_bot.py
```

On first run, `whatsapp_bot.py` opens a Chrome window — scan the QR code once, and the session persists for future runs.

---

## 📂 Project structure

```
├── database.py         # SQLite schema (products, orders)
├── tools.py             # check_inventory, placeorder tool definitions
├── main.py               # LangGraph agent graph (Supervisor, Inventory, Order, FAQ)
├── whatsapp_bot.py    # Selenium bridge between WhatsApp Web and the agent
└── store.db               # SQLite database
```

---

## 🔭 Possible next steps

- Move from Selenium to the official WhatsApp Cloud API for production reliability
- Add order-status tracking and cancellation
- Add a lightweight admin dashboard for managing inventory
- Introduce parallel agent execution for faster multi-part queries

---

## 📌 Note

This project was built as a hands-on exploration of multi-agent systems with LangGraph — from designing state and routing logic to wiring a real (if unofficial) messaging channel end-to-end. It's intended as a portfolio/learning piece; production deployment would need the official WhatsApp Business API and a paid LLM tier for reliability at scale.
