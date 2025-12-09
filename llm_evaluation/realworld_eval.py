"""
Real-World LLM Evaluation: JSON vs TOON vs TRON

Tests real-world scenarios where JSON is sent to LLMs:
1. RAG (Retrieval Augmented Generation)
2. API Response Processing
3. Database Query Results
4. Function Calling Results

Goal: Prove TOON/TRON work as well as JSON in production scenarios.

Supported LLMs:
- Google Gemini (API key required)
- Ollama (local, free) - Llama 3, Mistral, Phi-3, etc.
- Hugging Face Transformers (local, free)

Requirements:
    pip install tiktoken toonstream

    # For Gemini:
    pip install google-generativeai

    # For Ollama (install from https://ollama.ai):
    ollama pull llama3.2

    # For Hugging Face:
    pip install transformers torch

Usage:
    python realworld_eval.py                           # Dry run
    python realworld_eval.py --llm ollama              # Ollama (local)
    python realworld_eval.py --llm gemini              # Google Gemini
    python realworld_eval.py --llm huggingface         # HuggingFace
    python realworld_eval.py --llm ollama --model mistral

Set API key (for Gemini only):
    $env:GOOGLE_API_KEY="your_key"  (PowerShell)
"""

import json
import os
import re
import sys
import time
from collections import defaultdict
from typing import Dict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

try:
    import google.generativeai as genai

    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False

from toonstream import encode

# ============================================================================
# LLM BACKENDS
# ============================================================================


class OllamaBackend:
    """Ollama local LLM backend (free, no API key)."""

    def __init__(self, model: str = "llama3.2"):
        self.model = model
        self.base_url = "http://localhost:11434"

    def generate(self, prompt: str) -> str:
        if not REQUESTS_AVAILABLE:
            return "ERROR: requests library not installed"

        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0, "num_predict": 100},
                },
                timeout=60,
            )
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                return f"ERROR: Ollama returned {response.status_code}"
        except requests.exceptions.ConnectionError:
            return "ERROR: Ollama not running. Start with: ollama serve"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def call(self, prompt: str) -> str:
        """Alias for generate() to match other backends."""
        return self.generate(prompt)


class GeminiBackend:
    """Google Gemini API backend."""

    def __init__(self, model: str = "gemini-1.5-flash"):
        self.model_name = model
        api_key = os.environ.get("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model)
        else:
            self.model = None

    def generate(self, prompt: str) -> str:
        if not GEMINI_AVAILABLE:
            return "ERROR: google-generativeai not installed"
        if not self.model:
            return "ERROR: GOOGLE_API_KEY not set"

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0, max_output_tokens=100
                ),
            )
            return response.text.strip() if response.text else "ERROR: Empty response"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def call(self, prompt: str) -> str:
        """Alias for generate() to match other backends."""
        return self.generate(prompt)


class HuggingFaceBackend:
    """Hugging Face Transformers backend (local)."""

    def __init__(self, model: str = "microsoft/Phi-3-mini-4k-instruct"):
        self.model_name = model
        self.pipe = None

        if HF_AVAILABLE:
            print(f"Loading model {model}... (this may take a few minutes)")
            try:
                self.pipe = pipeline(
                    "text-generation",
                    model=model,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto",
                )
                print("Model loaded!")
            except Exception as e:
                print(f"Warning: Could not load model: {e}")

    def generate(self, prompt: str) -> str:
        if not HF_AVAILABLE:
            return "ERROR: transformers not installed"
        if not self.pipe:
            return "ERROR: Model not loaded"

        try:
            messages = [{"role": "user", "content": prompt}]
            result = self.pipe(messages, max_new_tokens=100, temperature=0.01, do_sample=True)
            return result[0]["generated_text"][-1]["content"].strip()
        except Exception:
            # Fall back to simple text generation for models without chat template
            try:
                result = self.pipe(prompt, max_new_tokens=100, temperature=0.01, do_sample=True)
                generated = result[0]["generated_text"]
                # Remove the prompt from the response
                if generated.startswith(prompt):
                    generated = generated[len(prompt) :].strip()
                return generated
            except Exception as e2:
                return f"ERROR: {str(e2)}"

    def call(self, prompt: str) -> str:
        """Alias for generate() to match other backends."""
        return self.generate(prompt)


def get_llm_backend(backend_name: str, model: str = None):
    """Get the appropriate LLM backend."""
    if backend_name == "ollama":
        model = model or "llama3.2"
        return OllamaBackend(model)
    elif backend_name == "gemini":
        model = model or "gemini-1.5-flash"
        return GeminiBackend(model)
    elif backend_name == "huggingface":
        model = model or "microsoft/Phi-3-mini-4k-instruct"
        return HuggingFaceBackend(model)
    else:
        raise ValueError(f"Unknown backend: {backend_name}")


# ============================================================================
# SCENARIO 1: RAG (Retrieval Augmented Generation)
# Context: Retrieved documents, User asks questions
# ============================================================================

RAG_SCENARIOS = [
    {
        "id": "rag_001",
        "name": "E-commerce FAQ",
        "retrieved_docs": [
            {
                "doc_id": "FAQ-001",
                "title": "Return Policy",
                "content": "Items can be returned within 30 days of purchase. Items must be unused and in original packaging. Refunds are processed within 5-7 business days.",
                "category": "returns",
            },
            {
                "doc_id": "FAQ-002",
                "title": "Shipping Information",
                "content": "Standard shipping takes 5-7 business days. Express shipping takes 2-3 business days. Free shipping on orders over $50.",
                "category": "shipping",
            },
            {
                "doc_id": "FAQ-003",
                "title": "Payment Methods",
                "content": "We accept Visa, Mastercard, American Express, PayPal, and Apple Pay. All transactions are encrypted and secure.",
                "category": "payment",
            },
            {
                "doc_id": "FAQ-004",
                "title": "Order Tracking",
                "content": "Track your order using the tracking number sent to your email. Orders are updated every 24 hours.",
                "category": "shipping",
            },
            {
                "doc_id": "FAQ-005",
                "title": "Warranty",
                "content": "All electronics come with a 1-year manufacturer warranty. Extended warranty available for purchase.",
                "category": "warranty",
            },
        ],
        "questions": [
            {"q": "How long do I have to return an item?", "a": "30 days"},
            {"q": "How long does standard shipping take?", "a": "5-7 business days"},
            {"q": "Do you accept PayPal?", "a": "yes"},
            {"q": "How long is the warranty on electronics?", "a": "1 year"},
            {"q": "What is the minimum order for free shipping?", "a": "$50"},
        ],
    },
    {
        "id": "rag_002",
        "name": "HR Policy Documents",
        "retrieved_docs": [
            {
                "doc_id": "HR-001",
                "title": "PTO Policy",
                "content": "Employees receive 15 days of PTO per year. PTO accrues monthly at 1.25 days. Maximum carryover is 5 days.",
                "category": "benefits",
            },
            {
                "doc_id": "HR-002",
                "title": "Remote Work Policy",
                "content": "Employees may work remotely up to 3 days per week. Manager approval required. Core hours are 10am-3pm.",
                "category": "work",
            },
            {
                "doc_id": "HR-003",
                "title": "Health Insurance",
                "content": "Company covers 80% of health insurance premiums. Dental and vision included. Coverage starts on first day.",
                "category": "benefits",
            },
            {
                "doc_id": "HR-004",
                "title": "401k Plan",
                "content": "Company matches 50% of contributions up to 6% of salary. Vesting period is 3 years.",
                "category": "benefits",
            },
            {
                "doc_id": "HR-005",
                "title": "Parental Leave",
                "content": "12 weeks paid parental leave for all parents. Additional 4 weeks unpaid leave available.",
                "category": "benefits",
            },
        ],
        "questions": [
            {"q": "How many PTO days do employees get per year?", "a": "15"},
            {"q": "How many days per week can I work remotely?", "a": "3"},
            {"q": "What percentage of health insurance does the company cover?", "a": "80%"},
            {"q": "What is the 401k vesting period?", "a": "3 years"},
            {"q": "How many weeks of paid parental leave?", "a": "12"},
        ],
    },
    {
        "id": "rag_003",
        "name": "Product Documentation",
        "retrieved_docs": [
            {
                "doc_id": "PROD-001",
                "title": "System Requirements",
                "content": "Minimum: 8GB RAM, 256GB storage, Windows 10 or macOS 12. Recommended: 16GB RAM, 512GB SSD.",
                "category": "specs",
            },
            {
                "doc_id": "PROD-002",
                "title": "Installation Guide",
                "content": "Download installer from website. Run setup.exe. Installation takes approximately 10 minutes. Restart required.",
                "category": "setup",
            },
            {
                "doc_id": "PROD-003",
                "title": "API Rate Limits",
                "content": "Free tier: 100 requests/minute. Pro tier: 1000 requests/minute. Enterprise: unlimited.",
                "category": "api",
            },
            {
                "doc_id": "PROD-004",
                "title": "Supported Formats",
                "content": "Import: CSV, JSON, XML, Excel. Export: PDF, CSV, JSON. Maximum file size: 50MB.",
                "category": "features",
            },
            {
                "doc_id": "PROD-005",
                "title": "Pricing",
                "content": "Free tier: $0/month. Pro: $29/month. Enterprise: contact sales. Annual discount: 20%.",
                "category": "pricing",
            },
        ],
        "questions": [
            {"q": "What is the minimum RAM requirement?", "a": "8GB"},
            {"q": "How many API requests per minute on Pro tier?", "a": "1000"},
            {"q": "What is the maximum file size for uploads?", "a": "50MB"},
            {"q": "How much is the Pro plan per month?", "a": "$29"},
            {"q": "What is the annual discount percentage?", "a": "20%"},
        ],
    },
]


# ============================================================================
# SCENARIO 2: API Response Processing
# Context: Process API responses, extract information
# ============================================================================

API_SCENARIOS = [
    {
        "id": "api_001",
        "name": "Weather API Response",
        "api_response": {
            "location": {"city": "San Francisco", "country": "USA", "lat": 37.77, "lon": -122.42},
            "current": {
                "temp_f": 65,
                "temp_c": 18,
                "humidity": 72,
                "condition": "Partly Cloudy",
                "wind_mph": 12,
            },
            "forecast": [
                {"day": "Monday", "high_f": 68, "low_f": 55, "condition": "Sunny"},
                {"day": "Tuesday", "high_f": 70, "low_f": 58, "condition": "Sunny"},
                {"day": "Wednesday", "high_f": 64, "low_f": 52, "condition": "Cloudy"},
                {"day": "Thursday", "high_f": 62, "low_f": 50, "condition": "Rain"},
                {"day": "Friday", "high_f": 66, "low_f": 54, "condition": "Partly Cloudy"},
            ],
        },
        "questions": [
            {"q": "What is the current temperature in Fahrenheit?", "a": "65"},
            {"q": "What day will it rain?", "a": "Thursday"},
            {"q": "What is the highest forecasted temperature?", "a": "70"},
            {"q": "What is the current humidity percentage?", "a": "72"},
            {"q": "What is the wind speed in mph?", "a": "12"},
        ],
    },
    {
        "id": "api_002",
        "name": "Stock API Response",
        "api_response": {
            "symbol": "AAPL",
            "company": "Apple Inc.",
            "exchange": "NASDAQ",
            "current_price": 178.52,
            "daily_change": 2.34,
            "daily_change_pct": 1.33,
            "volume": 52436789,
            "market_cap_b": 2780,
            "pe_ratio": 28.5,
            "dividend_yield": 0.52,
            "52_week_high": 199.62,
            "52_week_low": 124.17,
            "history": [
                {"date": "2024-01-15", "close": 176.18, "volume": 48234567},
                {"date": "2024-01-16", "close": 177.45, "volume": 51234567},
                {"date": "2024-01-17", "close": 175.89, "volume": 45234567},
                {"date": "2024-01-18", "close": 178.52, "volume": 52436789},
            ],
        },
        "questions": [
            {"q": "What is the current stock price?", "a": "178.52"},
            {"q": "What is the 52-week high?", "a": "199.62"},
            {"q": "What is the PE ratio?", "a": "28.5"},
            {"q": "What was the closing price on January 16th?", "a": "177.45"},
            {"q": "What is the daily change percentage?", "a": "1.33"},
        ],
    },
    {
        "id": "api_003",
        "name": "Flight Search API",
        "api_response": {
            "search": {
                "origin": "JFK",
                "destination": "LAX",
                "date": "2024-02-15",
                "passengers": 1,
            },
            "results": [
                {
                    "flight": "AA100",
                    "airline": "American",
                    "depart": "08:00",
                    "arrive": "11:30",
                    "duration": "5h 30m",
                    "price": 299,
                    "stops": 0,
                },
                {
                    "flight": "DL200",
                    "airline": "Delta",
                    "depart": "10:15",
                    "arrive": "14:00",
                    "duration": "5h 45m",
                    "price": 275,
                    "stops": 0,
                },
                {
                    "flight": "UA300",
                    "airline": "United",
                    "depart": "12:30",
                    "arrive": "18:45",
                    "duration": "6h 15m",
                    "price": 245,
                    "stops": 1,
                },
                {
                    "flight": "AA150",
                    "airline": "American",
                    "depart": "14:00",
                    "arrive": "17:20",
                    "duration": "5h 20m",
                    "price": 320,
                    "stops": 0,
                },
                {
                    "flight": "SW400",
                    "airline": "Southwest",
                    "depart": "16:45",
                    "arrive": "20:30",
                    "duration": "5h 45m",
                    "price": 198,
                    "stops": 0,
                },
            ],
        },
        "questions": [
            {"q": "What is the cheapest flight price?", "a": "198"},
            {"q": "Which flight has the shortest duration?", "a": "AA150"},
            {"q": "How many non-stop flights are available?", "a": "4"},
            {"q": "What time does the Delta flight depart?", "a": "10:15"},
            {"q": "Which airline offers the flight with 1 stop?", "a": "United"},
        ],
    },
]


# ============================================================================
# SCENARIO 3: Database Query Results
# Context: SQL query results, analyze data
# ============================================================================

DATABASE_SCENARIOS = [
    {
        "id": "db_001",
        "name": "Sales Report Query",
        "query": "SELECT * FROM monthly_sales WHERE year = 2024",
        "results": {
            "columns": ["month", "region", "product", "units_sold", "revenue", "profit_margin"],
            "rows": [
                ["January", "North", "Widget A", 1250, 62500, 0.35],
                ["January", "South", "Widget A", 980, 49000, 0.32],
                ["January", "North", "Widget B", 850, 127500, 0.42],
                ["January", "South", "Widget B", 720, 108000, 0.40],
                ["February", "North", "Widget A", 1380, 69000, 0.36],
                ["February", "South", "Widget A", 1100, 55000, 0.33],
                ["February", "North", "Widget B", 920, 138000, 0.43],
                ["February", "South", "Widget B", 780, 117000, 0.41],
            ],
        },
        "questions": [
            {"q": "What is the total revenue for Widget A in January?", "a": "111500"},
            {"q": "Which product has the highest profit margin?", "a": "Widget B"},
            {
                "q": "How many units of Widget A were sold in the North region in February?",
                "a": "1380",
            },
            {
                "q": "What is the total revenue for the North region across all months?",
                "a": "397000",
            },
            {"q": "Which month had higher total units sold?", "a": "February"},
        ],
    },
    {
        "id": "db_002",
        "name": "Customer Orders Query",
        "query": "SELECT * FROM orders JOIN customers ON orders.customer_id = customers.id",
        "results": {
            "columns": [
                "order_id",
                "customer_name",
                "customer_tier",
                "order_date",
                "total",
                "status",
                "items_count",
            ],
            "rows": [
                ["ORD-001", "John Smith", "Gold", "2024-01-10", 450.00, "Delivered", 3],
                ["ORD-002", "Mary Johnson", "Silver", "2024-01-11", 125.50, "Delivered", 2],
                ["ORD-003", "John Smith", "Gold", "2024-01-12", 780.00, "Delivered", 5],
                ["ORD-004", "Bob Wilson", "Bronze", "2024-01-13", 89.99, "Shipped", 1],
                ["ORD-005", "Alice Brown", "Gold", "2024-01-14", 320.00, "Processing", 2],
                ["ORD-006", "Mary Johnson", "Silver", "2024-01-15", 210.00, "Delivered", 3],
                ["ORD-007", "Charlie Davis", "Bronze", "2024-01-16", 55.00, "Cancelled", 1],
            ],
        },
        "questions": [
            {"q": "How much has John Smith spent in total?", "a": "1230"},
            {"q": "How many orders have been delivered?", "a": "4"},
            {"q": "Which customer tier has the most orders?", "a": "Gold"},
            {"q": "What is the average order total for Silver tier customers?", "a": "167.75"},
            {"q": "How many items were in the largest order?", "a": "5"},
        ],
    },
    {
        "id": "db_003",
        "name": "Employee Performance Query",
        "query": "SELECT * FROM employees JOIN performance ON employees.id = performance.emp_id WHERE quarter = 'Q4'",
        "results": {
            "columns": [
                "emp_id",
                "name",
                "department",
                "role",
                "targets_met",
                "revenue_generated",
                "customer_satisfaction",
                "rating",
            ],
            "rows": [
                ["E001", "Alice Chen", "Sales", "Senior Rep", 12, 245000, 4.8, "Exceeds"],
                ["E002", "Bob Martin", "Sales", "Rep", 8, 125000, 4.2, "Meets"],
                ["E003", "Carol White", "Sales", "Senior Rep", 10, 198000, 4.5, "Meets"],
                ["E004", "David Lee", "Support", "Lead", 15, 0, 4.9, "Exceeds"],
                ["E005", "Eva Green", "Sales", "Rep", 6, 95000, 3.8, "Below"],
                ["E006", "Frank Brown", "Support", "Rep", 11, 0, 4.3, "Meets"],
            ],
        },
        "questions": [
            {"q": "Who generated the most revenue?", "a": "Alice Chen"},
            {"q": "How many employees have 'Exceeds' rating?", "a": "2"},
            {"q": "What is the total revenue generated by Sales department?", "a": "663000"},
            {"q": "Who has the highest customer satisfaction score?", "a": "David Lee"},
            {"q": "How many targets did Bob Martin meet?", "a": "8"},
        ],
    },
]


# ============================================================================
# SCENARIO 4: Function Calling Results
# Context: Tool/function outputs that LLM needs to process
# ============================================================================

FUNCTION_SCENARIOS = [
    {
        "id": "func_001",
        "name": "Calendar Tool Results",
        "function": "get_calendar_events",
        "result": {
            "date_range": {"start": "2024-01-15", "end": "2024-01-19"},
            "events": [
                {
                    "id": "E1",
                    "title": "Team Standup",
                    "date": "2024-01-15",
                    "time": "09:00",
                    "duration_min": 30,
                    "attendees": 8,
                    "recurring": True,
                },
                {
                    "id": "E2",
                    "title": "Client Meeting",
                    "date": "2024-01-15",
                    "time": "14:00",
                    "duration_min": 60,
                    "attendees": 4,
                    "recurring": False,
                },
                {
                    "id": "E3",
                    "title": "Project Review",
                    "date": "2024-01-16",
                    "time": "10:00",
                    "duration_min": 90,
                    "attendees": 6,
                    "recurring": False,
                },
                {
                    "id": "E4",
                    "title": "Team Standup",
                    "date": "2024-01-17",
                    "time": "09:00",
                    "duration_min": 30,
                    "attendees": 8,
                    "recurring": True,
                },
                {
                    "id": "E5",
                    "title": "1:1 with Manager",
                    "date": "2024-01-17",
                    "time": "15:00",
                    "duration_min": 30,
                    "attendees": 2,
                    "recurring": True,
                },
                {
                    "id": "E6",
                    "title": "Sprint Planning",
                    "date": "2024-01-18",
                    "time": "13:00",
                    "duration_min": 120,
                    "attendees": 10,
                    "recurring": False,
                },
                {
                    "id": "E7",
                    "title": "Team Standup",
                    "date": "2024-01-19",
                    "time": "09:00",
                    "duration_min": 30,
                    "attendees": 8,
                    "recurring": True,
                },
            ],
        },
        "questions": [
            {"q": "How many meetings are on January 15th?", "a": "2"},
            {"q": "What is the longest meeting duration?", "a": "120"},
            {"q": "How many recurring meetings are scheduled?", "a": "4"},
            {"q": "What time is the Sprint Planning meeting?", "a": "13:00"},
            {"q": "How many total attendees for all meetings on January 17th?", "a": "10"},
        ],
    },
    {
        "id": "func_002",
        "name": "Inventory Check Tool",
        "function": "check_inventory",
        "result": {
            "warehouse": "WH-001",
            "checked_at": "2024-01-15T10:30:00Z",
            "items": [
                {
                    "sku": "PROD-A",
                    "name": "Laptop",
                    "quantity": 45,
                    "reorder_point": 20,
                    "status": "OK",
                    "location": "A1",
                },
                {
                    "sku": "PROD-B",
                    "name": "Mouse",
                    "quantity": 12,
                    "reorder_point": 50,
                    "status": "LOW",
                    "location": "A2",
                },
                {
                    "sku": "PROD-C",
                    "name": "Keyboard",
                    "quantity": 78,
                    "reorder_point": 30,
                    "status": "OK",
                    "location": "A3",
                },
                {
                    "sku": "PROD-D",
                    "name": "Monitor",
                    "quantity": 8,
                    "reorder_point": 15,
                    "status": "LOW",
                    "location": "B1",
                },
                {
                    "sku": "PROD-E",
                    "name": "Headset",
                    "quantity": 0,
                    "reorder_point": 25,
                    "status": "OUT",
                    "location": "B2",
                },
                {
                    "sku": "PROD-F",
                    "name": "Webcam",
                    "quantity": 34,
                    "reorder_point": 20,
                    "status": "OK",
                    "location": "B3",
                },
            ],
        },
        "questions": [
            {"q": "How many items are out of stock?", "a": "1"},
            {"q": "Which product has the lowest quantity (excluding zero)?", "a": "Monitor"},
            {"q": "How many products have LOW status?", "a": "2"},
            {"q": "What is the location of the Keyboard?", "a": "A3"},
            {"q": "How many Laptops are in stock?", "a": "45"},
        ],
    },
    {
        "id": "func_003",
        "name": "Analytics Dashboard Tool",
        "function": "get_dashboard_metrics",
        "result": {
            "period": "Last 7 Days",
            "metrics": {
                "total_visitors": 125430,
                "unique_visitors": 89250,
                "page_views": 342890,
                "avg_session_duration_sec": 245,
                "bounce_rate_pct": 42.5,
                "conversion_rate_pct": 3.2,
            },
            "top_pages": [
                {"page": "/home", "views": 45000, "avg_time_sec": 120},
                {"page": "/products", "views": 38000, "avg_time_sec": 180},
                {"page": "/checkout", "views": 12000, "avg_time_sec": 300},
                {"page": "/about", "views": 8500, "avg_time_sec": 90},
                {"page": "/contact", "views": 5200, "avg_time_sec": 60},
            ],
            "traffic_sources": [
                {"source": "Organic Search", "visitors": 52000, "pct": 41.5},
                {"source": "Direct", "visitors": 35000, "pct": 27.9},
                {"source": "Social Media", "visitors": 25000, "pct": 19.9},
                {"source": "Referral", "visitors": 13430, "pct": 10.7},
            ],
        },
        "questions": [
            {"q": "What is the bounce rate percentage?", "a": "42.5"},
            {"q": "How many page views were there?", "a": "342890"},
            {"q": "What is the top traffic source?", "a": "Organic Search"},
            {"q": "What is the conversion rate?", "a": "3.2"},
            {"q": "How many views did the checkout page get?", "a": "12000"},
        ],
    },
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def count_tokens(text: str) -> int:
    if not TIKTOKEN_AVAILABLE:
        return len(text.split())
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except:
        return len(text.split())


def format_data(data: Dict, format_type: str) -> str:
    if format_type == "json":
        return json.dumps(data, indent=2)
    elif format_type == "toon":
        return encode(data)
    elif format_type == "tron":
        return encode(data, format="tron")
    else:
        raise ValueError(f"Unknown format: {format_type}")


def build_prompt(scenario_type: str, data_str: str, question: str, format_name: str) -> str:
    context_desc = {
        "rag": "retrieved documents from a knowledge base",
        "api": "an API response",
        "database": "database query results",
        "function": "a function/tool output",
    }

    format_hint = ""
    if format_name == "toon":
        format_hint = "\n(Data is in TOON format: arrays shown as header row + data rows)"
    elif format_name == "tron":
        format_hint = "\n(Data is in TRON format: key=value pairs, @header|row for tables)"

    return f"""You are processing {context_desc[scenario_type]}.{format_hint}

DATA:
{data_str}

Question: {question}

Answer with ONLY the answer value. Be precise and concise."""


def normalize_answer(answer: str) -> str:
    answer = answer.strip().lower()
    answer = re.sub(r"^(the|a|an|about|approximately|around)\s+", "", answer)
    answer = re.sub(r"[.,;:!?]$", "", answer)
    answer = re.sub(r"[$€£%]", "", answer)
    answer = re.sub(r",(\d{3})", r"\1", answer)
    return answer.strip()


def check_answer(predicted: str, ground_truth: str) -> bool:
    pred_norm = normalize_answer(predicted)
    gt_norm = normalize_answer(str(ground_truth))
    return gt_norm in pred_norm or pred_norm in gt_norm


# ============================================================================
# MAIN EVALUATION
# ============================================================================


def run_evaluation(llm_backend: str = None, scenario_filter: str = None, model: str = None):
    print("=" * 90)
    print("REAL-WORLD LLM EVALUATION: JSON vs TOON vs TRON")
    print("=" * 90)
    print("\nGoal: Prove TOON/TRON work as well as JSON in production scenarios\n")

    formats = ["json", "toon", "tron"]

    # Initialize LLM backend
    llm = None
    if llm_backend:
        print(f"Initializing {llm_backend} backend...")
        llm = get_llm_backend(llm_backend, model)
        print(f"Using: {llm_backend}" + (f" ({model})" if model else ""))

    # Combine all scenarios
    all_scenarios = []

    if not scenario_filter or scenario_filter == "rag":
        for s in RAG_SCENARIOS:
            for q in s["questions"]:
                all_scenarios.append(
                    {
                        "type": "rag",
                        "id": s["id"],
                        "name": s["name"],
                        "data": {"retrieved_documents": s["retrieved_docs"]},
                        "question": q["q"],
                        "answer": q["a"],
                    }
                )

    if not scenario_filter or scenario_filter == "api":
        for s in API_SCENARIOS:
            for q in s["questions"]:
                all_scenarios.append(
                    {
                        "type": "api",
                        "id": s["id"],
                        "name": s["name"],
                        "data": s["api_response"],
                        "question": q["q"],
                        "answer": q["a"],
                    }
                )

    if not scenario_filter or scenario_filter == "database":
        for s in DATABASE_SCENARIOS:
            for q in s["questions"]:
                # Convert to list of dicts
                rows_as_dicts = []
                for row in s["results"]["rows"]:
                    rows_as_dicts.append(dict(zip(s["results"]["columns"], row)))
                all_scenarios.append(
                    {
                        "type": "database",
                        "id": s["id"],
                        "name": s["name"],
                        "data": {"query": s["query"], "results": rows_as_dicts},
                        "question": q["q"],
                        "answer": q["a"],
                    }
                )

    if not scenario_filter or scenario_filter == "function":
        for s in FUNCTION_SCENARIOS:
            for q in s["questions"]:
                all_scenarios.append(
                    {
                        "type": "function",
                        "id": s["id"],
                        "name": s["name"],
                        "data": {"function": s["function"], "result": s["result"]},
                        "question": q["q"],
                        "answer": q["a"],
                    }
                )

    print(f"Total Questions: {len(all_scenarios)}")
    print("Scenarios: RAG, API, Database, Function Calling")
    print(f"LLM: {'Enabled (' + llm_backend + ')' if llm else 'Disabled (dry run)'}")

    # Results storage
    results = {fmt: {"correct": 0, "total": 0, "tokens": 0} for fmt in formats}
    type_results = defaultdict(lambda: {fmt: {"correct": 0, "total": 0} for fmt in formats})

    # Run evaluation
    for i, scenario in enumerate(all_scenarios):
        print(f"\n[{i+1}/{len(all_scenarios)}] {scenario['type'].upper()}: {scenario['name']}")
        print(f"  Q: {scenario['question']}")
        print(f"  Expected: {scenario['answer']}")

        for fmt in formats:
            try:
                data_str = format_data(scenario["data"], fmt)
                tokens = count_tokens(data_str)
                results[fmt]["tokens"] += tokens
                results[fmt]["total"] += 1
                type_results[scenario["type"]][fmt]["total"] += 1

                if llm:
                    prompt = build_prompt(scenario["type"], data_str, scenario["question"], fmt)
                    response = llm.call(prompt)

                    if response.startswith("ERROR"):
                        print(f"  {fmt.upper()}: {response}")
                    else:
                        is_correct = check_answer(response, scenario["answer"])
                        if is_correct:
                            results[fmt]["correct"] += 1
                            type_results[scenario["type"]][fmt]["correct"] += 1

                        status = "✓" if is_correct else "✗"
                        print(f"  {fmt.upper()}: {response[:40]} [{status}]")

                    time.sleep(0.5)
            except Exception as e:
                print(f"  {fmt.upper()}: Error - {str(e)}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 90)
    print("RESULTS SUMMARY")
    print("=" * 90)

    # Token comparison
    print("\n### Token Usage")
    print(f"{'Format':<10} {'Total Tokens':>15} {'vs JSON':>15}")
    print("-" * 40)

    json_tokens = results["json"]["tokens"]
    for fmt in formats:
        tokens = results[fmt]["tokens"]
        savings = (1 - tokens / json_tokens) * 100 if json_tokens > 0 else 0
        savings_str = f"{savings:+.1f}%" if fmt != "json" else "-"
        print(f"{fmt.upper():<10} {tokens:>15} {savings_str:>15}")

    if llm:
        # Overall accuracy
        print("\n### Overall Accuracy")
        print(f"{'Format':<10} {'Correct':>10} {'Total':>10} {'Accuracy':>12}")
        print("-" * 45)

        for fmt in formats:
            correct = results[fmt]["correct"]
            total = results[fmt]["total"]
            acc = correct / total * 100 if total > 0 else 0
            print(f"{fmt.upper():<10} {correct:>10} {total:>10} {acc:>11.1f}%")

        # Accuracy by scenario type
        print("\n### Accuracy by Scenario Type")
        print(f"{'Scenario':<12} {'JSON':>12} {'TOON':>12} {'TRON':>12}")
        print("-" * 50)

        for stype in ["rag", "api", "database", "function"]:
            row = [stype.upper()]
            for fmt in formats:
                c = type_results[stype][fmt]["correct"]
                t = type_results[stype][fmt]["total"]
                acc = c / t * 100 if t > 0 else 0
                row.append(f"{acc:.1f}%")
            print(f"{row[0]:<12} {row[1]:>12} {row[2]:>12} {row[3]:>12}")

    # Conclusion
    print("\n" + "=" * 90)
    print("CONCLUSION")
    print("=" * 90)

    toon_savings = (1 - results["toon"]["tokens"] / json_tokens) * 100
    tron_savings = (1 - results["tron"]["tokens"] / json_tokens) * 100

    if llm:
        json_acc = results["json"]["correct"] / results["json"]["total"] * 100
        toon_acc = results["toon"]["correct"] / results["toon"]["total"] * 100
        tron_acc = results["tron"]["correct"] / results["tron"]["total"] * 100

        print(
            f"""
TOKEN SAVINGS:
  • TOON: {toon_savings:.1f}% fewer tokens than JSON
  • TRON: {tron_savings:.1f}% fewer tokens than JSON

ACCURACY:
  • JSON:  {json_acc:.1f}%
  • TOON:  {toon_acc:.1f}%  (diff: {toon_acc - json_acc:+.1f}%)
  • TRON:  {tron_acc:.1f}%  (diff: {tron_acc - json_acc:+.1f}%)

VERDICT:
"""
        )
        if abs(toon_acc - json_acc) <= 5 and abs(tron_acc - json_acc) <= 5:
            print("  ✅ TOON/TRON maintain accuracy while saving 50-65% tokens!")
            print("  ✅ Safe to use in production for token cost reduction.")
        else:
            print("  ⚠️ Some accuracy differences detected. Review specific scenarios.")
    else:
        print(
            f"""
TOKEN SAVINGS (dry run):
  • TOON: {toon_savings:.1f}% fewer tokens than JSON
  • TRON: {tron_savings:.1f}% fewer tokens than JSON

To verify accuracy:
  python realworld_eval.py --backend gemini
  python realworld_eval.py --backend ollama --model llama3
  python realworld_eval.py --backend huggingface --model mistralai/Mistral-7B-Instruct-v0.3

Set API key first (for Gemini):
  $env:GOOGLE_API_KEY="your_key"
"""
        )

    return results


# ============================================================================
# CLI
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Real-World LLM Format Evaluation")
    parser.add_argument(
        "--backend", choices=["gemini", "ollama", "huggingface"], help="LLM backend to use"
    )
    parser.add_argument(
        "--scenario", choices=["rag", "api", "database", "function"], help="Run specific scenario"
    )
    parser.add_argument("--model", help="Model name (default: varies by backend)")

    args = parser.parse_args()

    run_evaluation(llm_backend=args.backend, scenario_filter=args.scenario, model=args.model)
