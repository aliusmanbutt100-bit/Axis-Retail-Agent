from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from typing import TypedDict, Annotated
from dotenv import load_dotenv
from tools import check_inventory, placeorder
import os
#This is used to remove agent tool calling history
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

def clean_history(messages):
    """Tool-call messages hata deta hai, sirf plain conversation rakhta hai"""
    cleaned = []
    for msg in messages:
        if isinstance(msg, ToolMessage):
            continue   # tool results skip karo
        if isinstance(msg, AIMessage) and msg.tool_calls:
            continue   # tool-call wali AI messages skip karo
        cleaned.append(msg)
    return cleaned

load_dotenv()
#when one limit ends i use another llm

from langchain_groq import ChatGroq

# llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), 
#                 model="openai/gpt-oss-20b")

llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="openrouter/free"
)

# Alag alag LLM instances, har agent ke apne tools ke sath
inventory_llm = llm.bind_tools([check_inventory])
order_llm = llm.bind_tools([placeorder])

# STATE — next_agent field add hui, Supervisor ka decision store karne ke liye
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str


# SUPERVISOR — decide karta hai kis agent ko kaam dena hai
def supervisor_node(state: AgentState) -> dict:
    prompt = f"""Tum ek clothing store jis a name Styluxe Wears hai os ke supervisor ho. Store sirf clothes/shoes sell karta hai.
    
    Customer ka latest message: {state['messages'][-1].content}
    Poora conversation: {state['messages']}
    
    Batao is message ko kis agent ko dena hai:
    - 'inventory': customer SIRF stock, price, size, color, availability POOCH raha hai (order nahi kar raha)
    - 'order': customer order karna chahta hai - "order", "chahiye", "lena hai", "book karo" jaisay words use kare, ya size/color/quantity/naam/phone/address de raha ho order complete karne ke liye
    - 'faq': customer timing, delivery, return policy jaisa general sawal pooche
    - 'done': conversation khatam ho gayi ho
    
    IMPORTANT: Agar customer product LENA chahta hai (na ke sirf information maang raha hai), hamesha 'order' return karo.
    
    Sirf ek word return karo: inventory, order, faq, ya done"""

    decision = llm.invoke(prompt)
    return {"next_agent": decision.content.strip().lower()}


# INVENTORY AGENT — stock/price/size check karta hai
def inventory_node(state: AgentState) -> dict:
    system = SystemMessage(content="""Tum ek clothing store styluxe wears ke inventory assistant ho.

    STRICT RULES:
    1. Kabhi bhi khud se product information mat do - hamesha check_inventory tool call karo, chahe customer kitna bhi generic sawal kare.
    2. Agar customer generic sawal kare ("kya hai store mein"), check_inventory ko empty string se call karo taake saare products aayen.
    3. Sirf wahi products batao jo tool se actual result mein aaye hon.
    4. Price hamesha "Rs" mein likho, kabhi ₹ symbol use mat karo.
    5. Response ek hi single message mein do, plain text mein, koi * ya markdown symbols use mat karo.
    6. Agar customer order karna chahta hai, usay bolo "order agent aapki madad karega" - khud order process mat karo.""")
    clean_messages = clean_history(state["messages"])
    response = inventory_llm.invoke([system] + clean_messages)
    return {"messages": [response]}

# ORDER AGENT — order place karta hai
def order_node(state: AgentState) -> dict:
    system = SystemMessage(content="""Tum ek clothing store styluxe wears ke order-taking assistant ho. Ye hamara APNA store hai - koi external brand ya SKU system nahi hai.

    STRICT RULES:
    1. Customer se KABHI bhi product ID, SKU, ya brand name mat pucho - hamare products ka apna simple naam/category/size/color hota hai (jaise "Men Jeans", "Kurti").
    2. Jab customer product mange (jaise "jeans chahiye"), turant check_inventory tool call karo us keyword se - customer se extra details (fit, wash, rise, brand) mat maango, ye humare paas hote hi nahi.
    3. check_inventory se jo bhi results aayen, unme se customer ko options dikhao (size, color, price ke sath) - customer se poocho konsa chahiye.
    4. product_id sirf tum khud check_inventory ke result se nikaloge - customer se kabhi mat maango.
    5. Order se pehle size, color, quantity, naam, phone, address customer se one by one lo.
    6. Koi detail miss ho to zaroor pucho.
    7. Requested item/option unavailable ho to customer ko available options batao.
    8. Chahe sirf ek hi size/color available ho, phir bhi customer se confirm lo.
    9. placeorder se PEHLE customer ko complete order summary dikhao.
    10. Customer ki FINAL confirmation ke baad hi placeorder tool use karo.
    11. Price hamesha "Rs" mein likho, plain text mein.
    12. Customer jis language mein baat kare, usi mein jawab do(english,urdu) but dont use hindi words.""")
    clean_messages = clean_history(state["messages"])
    response = inventory_llm.invoke([system] + clean_messages)
    return {"messages": [response]}

# FAQ AGENT — koi tool nahi, seedha LLM jawab deta hai
def faq_node(state: AgentState) -> dict:
    system = SystemMessage(content="""Tum ek clothing store ke FAQ assistant ho. Strictly follow:

    1. Store timing: 10 AM - 10 PM.
    2. Delivery: 2-3 din.
    3. Return: 7 din ke andar, tags lage hone chahiye.
    4. Customer jis language mein baat kare, usi mein jawab do (Urdu/English mix bhi), lekin Hindi words use mat karo and greet them with assalamualaikum.
    5. Har fabric premium aur har design unique hai.
    6. Har item 100% cotton hai.
    7. Response plain text mein do, koi * ya markdown symbols use mat karo.""")
    response = llm.invoke([system] + state["messages"])
    return {"messages": [response]}


# Tool nodes — inventory aur order agents ke tools alag alag
inventory_tool_node = ToolNode([check_inventory])
order_tool_node = ToolNode([placeorder])


# Inventory agent ke baad: tool chahiye ya supervisor ke pass wapis jao
def route_after_inventory(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "inventory_tools"
    return "end"

# Order agent ke baad: tool chahiye ya supervisor ke pass wapis jao
def route_after_order(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "order_tools"
    return "end"


# Supervisor ke decision ke hisaab se agla agent
def route_supervisor(state: AgentState) -> str:
    return state["next_agent"]


# GRAPH BANANA
graph = StateGraph(AgentState)

graph.add_node("supervisor", supervisor_node)
graph.add_node("inventory", inventory_node)
graph.add_node("order", order_node)
graph.add_node("faq", faq_node)
graph.add_node("inventory_tools", inventory_tool_node)
graph.add_node("order_tools", order_tool_node)

graph.add_edge(START, "supervisor")

graph.add_conditional_edges(
    "supervisor",
    route_supervisor,
    {"inventory": "inventory", "order": "order", "faq": "faq", "done": END}
)

# Inventory agent: tool chahiye to jao, warna khatam
graph.add_conditional_edges("inventory", route_after_inventory, {"inventory_tools": "inventory_tools", "end": END})
graph.add_edge("inventory_tools", "inventory")

# Order agent: tool chahiye to jao, warna khatam
graph.add_conditional_edges("order", route_after_order, {"order_tools": "order_tools", "end": END})
graph.add_edge("order_tools", "order")

# FAQ seedha khatam ho jata hai (tool nahi hai)
graph.add_edge("faq", END)

memory = MemorySaver()
app = graph.compile(checkpointer=memory)


# # for memory
# config = {"configurable": {"thread_id": "customer_1"}}
# #Take user input
# while True:
#     user_msg = input("you: ")
#     if user_msg.lower() == "bye":
#         break

#     result = app.invoke({"messages": [("user", user_msg)]}, config=config)
#     print("Assistant:", result["messages"][-1].content)

# Ye function abh bana diya jisko whatsapp-chatbot import or use kary ha
def get_agent_response(user_message: str, thread_id: str) -> str:
    config = {"configurable": {"thread_id": thread_id}}
    try:
        result = app.invoke({"messages": [("user", user_message)]}, config=config)
        return result["messages"][-1].content
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "rate_limit" in error_str.lower():
            return "Please wait for some seconds and then try again,our system is busy right now."
        print(f"Agent error: {e}")
        return "Sorry,There is a problem so please try again or ask your question in another way."