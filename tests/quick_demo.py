#!/usr/bin/env python3
"""
Quick Demo - Client Workflow Demonstration
==========================================

This script demonstrates the complete client workflow WITHOUT requiring
heavy dependencies like easyocr. It shows:
1. How documents are created/received
2. How the system processes them
3. What output clients receive

This is useful for understanding the architecture and flow.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Rich console for beautiful output
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.syntax import Syntax
    from rich import box
    console = Console()
    RICH = True
except ImportError:
    RICH = False


def banner(text, style="bold cyan"):
    if RICH:
        console.print(Panel(f"[{style}]{text}[/{style}]", box=box.DOUBLE))
    else:
        print(f"\n{'='*60}\n  {text}\n{'='*60}")


def step(num, text):
    if RICH:
        console.print(f"\n[bold green]Step {num}:[/bold green] {text}")
    else:
        print(f"\n→ Step {num}: {text}")


def output(title, content):
    if RICH:
        console.print(Panel(content, title=f"[yellow]{title}[/yellow]", border_style="yellow"))
    else:
        print(f"\n--- {title} ---\n{content}\n{'-'*40}")


def create_invoice_image(path: str):
    """Create a sample invoice."""
    img = Image.new('RGB', (800, 600), 'white')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except:
        font = ImageFont.load_default()
        font_big = font

    # Header
    draw.rectangle([(0, 0), (800, 60)], fill='#1a4b8c')
    draw.text((20, 15), "ACME CORPORATION - INVOICE", fill='white', font=font_big)

    # Invoice details
    draw.text((20, 80), "Invoice #: INV-2024-0892", fill='black', font=font)
    draw.text((20, 105), "Date: December 24, 2024", fill='black', font=font)
    draw.text((20, 130), "Due: January 24, 2025", fill='black', font=font)

    draw.text((400, 80), "Bill To:", fill='gray', font=font)
    draw.text((400, 105), "TechStart Solutions Inc.", fill='black', font=font)
    draw.text((400, 130), "456 Innovation Drive, Austin TX", fill='black', font=font)

    # Table header
    draw.rectangle([(20, 180), (780, 210)], fill='lightgray')
    draw.text((30, 185), "Description", fill='black', font=font)
    draw.text((450, 185), "Qty", fill='black', font=font)
    draw.text((550, 185), "Price", fill='black', font=font)
    draw.text((680, 185), "Amount", fill='black', font=font)

    # Items
    items = [
        ("Cloud Infrastructure Setup", "1", "$2,500", "$2,500"),
        ("API Integration Services", "40 hrs", "$150/hr", "$6,000"),
        ("Database Migration", "1", "$3,500", "$3,500"),
        ("Training Sessions", "8 hrs", "$200/hr", "$1,600"),
    ]

    y = 220
    for desc, qty, price, amount in items:
        draw.text((30, y), desc, fill='black', font=font)
        draw.text((450, y), qty, fill='black', font=font)
        draw.text((550, y), price, fill='black', font=font)
        draw.text((680, y), amount, fill='black', font=font)
        y += 30

    # Totals
    y += 20
    draw.line([(450, y), (780, y)], fill='black', width=2)
    draw.text((550, y + 10), "Subtotal:", fill='black', font=font)
    draw.text((680, y + 10), "$13,600.00", fill='black', font=font)
    draw.text((550, y + 35), "Tax (8.25%):", fill='black', font=font)
    draw.text((680, y + 35), "$1,122.00", fill='black', font=font)

    draw.rectangle([(540, y + 60), (780, y + 95)], fill='#1a4b8c')
    draw.text((550, y + 68), "TOTAL DUE:", fill='white', font=font)
    draw.text((680, y + 68), "$14,722.00", fill='white', font=font)

    # Footer
    draw.text((20, 550), "Payment: Wire to Bank of America, Acc# 4521-8876-3321", fill='gray', font=font)

    img.save(path)
    return path


def create_receipt_image(path: str):
    """Create a sample receipt."""
    img = Image.new('RGB', (400, 500), 'white')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 12)
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 14)
    except:
        font = ImageFont.load_default()
        font_bold = font

    y = 15
    draw.text((130, y), "TECHMART", fill='black', font=font_bold); y += 20
    draw.text((100, y), "ELECTRONICS STORE", fill='black', font=font); y += 18
    draw.text((70, y), "1250 Market St, SF CA 94102", fill='black', font=font); y += 18
    draw.text((100, y), "Tel: (415) 555-8899", fill='black', font=font); y += 25

    draw.text((20, y), "=" * 50, fill='black', font=font); y += 18
    draw.text((130, y), "RECEIPT", fill='black', font=font_bold); y += 18
    draw.text((20, y), "=" * 50, fill='black', font=font); y += 20

    draw.text((20, y), "Date: 12/24/2024  Time: 14:32", fill='black', font=font); y += 16
    draw.text((20, y), "Trans#: TM-20241224-0847", fill='black', font=font); y += 20

    draw.text((20, y), "-" * 50, fill='black', font=font); y += 18

    items = [
        ("USB-C Hub 7-Port", "$45.99"),
        ("Wireless Mouse Pro", "$29.99"),
        ("HDMI Cable 6ft", "$12.99"),
        ("Phone Case Premium", "$24.99"),
    ]

    for item, price in items:
        draw.text((20, y), item, fill='black', font=font)
        draw.text((310, y), price, fill='black', font=font)
        y += 18

    y += 5
    draw.text((20, y), "-" * 50, fill='black', font=font); y += 18

    draw.text((20, y), "SUBTOTAL:", fill='black', font=font)
    draw.text((310, y), "$113.96", fill='black', font=font); y += 18
    draw.text((20, y), "TAX (8.625%):", fill='black', font=font)
    draw.text((310, y), "$9.83", fill='black', font=font); y += 18

    draw.text((20, y), "=" * 50, fill='black', font=font); y += 18
    draw.text((20, y), "TOTAL:", fill='black', font=font_bold)
    draw.text((300, y), "$123.79", fill='black', font=font_bold); y += 20
    draw.text((20, y), "=" * 50, fill='black', font=font); y += 20

    draw.text((20, y), "VISA ****4521", fill='black', font=font); y += 16
    draw.text((20, y), "AUTH: 847291", fill='black', font=font); y += 25

    draw.text((80, y), "*** THANK YOU! ***", fill='black', font=font_bold)

    img.save(path)
    return path


def simulate_ocr_extraction(doc_type: str) -> dict:
    """Simulate what the OCR system would extract."""

    if doc_type == "invoice":
        return {
            "document_type": "invoice",
            "extracted_data": {
                "vendor": "ACME CORPORATION",
                "invoice_number": "INV-2024-0892",
                "date": "December 24, 2024",
                "due_date": "January 24, 2025",
                "bill_to": {
                    "company": "TechStart Solutions Inc.",
                    "address": "456 Innovation Drive, Austin TX"
                },
                "line_items": [
                    {"description": "Cloud Infrastructure Setup", "qty": 1, "unit_price": 2500, "amount": 2500},
                    {"description": "API Integration Services", "qty": 40, "unit_price": 150, "amount": 6000},
                    {"description": "Database Migration", "qty": 1, "unit_price": 3500, "amount": 3500},
                    {"description": "Training Sessions", "qty": 8, "unit_price": 200, "amount": 1600}
                ],
                "subtotal": 13600.00,
                "tax_rate": "8.25%",
                "tax_amount": 1122.00,
                "total_due": 14722.00,
                "payment_info": {
                    "bank": "Bank of America",
                    "account": "4521-8876-3321"
                }
            },
            "confidence": 0.94,
            "processing_time_ms": 1250
        }

    elif doc_type == "receipt":
        return {
            "document_type": "receipt",
            "extracted_data": {
                "store_name": "TECHMART ELECTRONICS STORE",
                "store_address": "1250 Market St, SF CA 94102",
                "store_phone": "(415) 555-8899",
                "transaction_id": "TM-20241224-0847",
                "date": "12/24/2024",
                "time": "14:32",
                "items": [
                    {"name": "USB-C Hub 7-Port", "price": 45.99},
                    {"name": "Wireless Mouse Pro", "price": 29.99},
                    {"name": "HDMI Cable 6ft", "price": 12.99},
                    {"name": "Phone Case Premium", "price": 24.99}
                ],
                "subtotal": 113.96,
                "tax_rate": "8.625%",
                "tax_amount": 9.83,
                "total": 123.79,
                "payment_method": "VISA ****4521",
                "auth_code": "847291"
            },
            "confidence": 0.96,
            "processing_time_ms": 890
        }

    return {}


def main():
    """Run the quick demo."""

    banner("🏢 MULTIMODAL VISION AGENTIC SYSTEM")
    banner("Industry Use Case Demonstration", "bold white")

    print("""
┌─────────────────────────────────────────────────────────────────┐
│                    CLIENT WORKFLOW OVERVIEW                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   📄 Document Input    →   🤖 Agent Processing   →   📊 Output │
│                                                                 │
│   • Invoice PDF/Image      • OCR Extraction         • JSON     │
│   • Receipt Photo          • Structure Analysis     • Summary  │
│   • Business Card          • QA Processing          • CRM Data │
│   • Form Scan              • Quality Check          • Report   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
""")

    # Create test directory
    test_dir = PROJECT_ROOT / "test_images"
    test_dir.mkdir(exist_ok=True)

    # =========================================================================
    # USE CASE 1: INVOICE PROCESSING (Accounts Payable)
    # =========================================================================
    banner("USE CASE 1: Invoice Processing", "bold blue")
    print("\n[BUSINESS CONTEXT] Accounts Payable department needs to process")
    print("incoming invoices and extract data for ERP system integration.\n")

    step(1, "Client uploads invoice document")
    invoice_path = create_invoice_image(str(test_dir / "demo_invoice.png"))
    output("Input", f"Document uploaded: {invoice_path}\nFormat: PNG, Size: 800x600px")

    step(2, "System performs OCR and document analysis")
    print("   → Vision Agent: Assessing document quality...")
    print("   → OCR Agent: Extracting text regions...")
    print("   → QA Agent: Structuring financial data...")

    step(3, "Structured output returned to client")
    invoice_result = simulate_ocr_extraction("invoice")

    output("API Response (JSON)", json.dumps(invoice_result, indent=2))

    step(4, "Client receives actionable data")
    data = invoice_result["extracted_data"]
    if RICH:
        table = Table(title="Extracted Invoice Data", box=box.ROUNDED)
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Vendor", data["vendor"])
        table.add_row("Invoice #", data["invoice_number"])
        table.add_row("Due Date", data["due_date"])
        table.add_row("Total Due", f"${data['total_due']:,.2f}")
        table.add_row("Bank Account", data["payment_info"]["account"])
        console.print(table)
    else:
        print(f"\n  Vendor: {data['vendor']}")
        print(f"  Invoice #: {data['invoice_number']}")
        print(f"  Total Due: ${data['total_due']:,.2f}")

    # =========================================================================
    # USE CASE 2: RECEIPT SCANNING (Expense Management)
    # =========================================================================
    banner("USE CASE 2: Receipt Scanning", "bold green")
    print("\n[BUSINESS CONTEXT] Employee submits expense receipt for")
    print("reimbursement via mobile app.\n")

    step(1, "Employee captures receipt photo")
    receipt_path = create_receipt_image(str(test_dir / "demo_receipt.png"))
    output("Input", f"Photo captured: {receipt_path}\nDevice: Mobile Camera")

    step(2, "Real-time processing begins")
    print("   → Quality check: ✓ Image clarity OK")
    print("   → OCR extraction: ✓ 12 text regions detected")
    print("   → Data parsing: ✓ Receipt format recognized")

    step(3, "Structured expense data returned")
    receipt_result = simulate_ocr_extraction("receipt")
    output("Expense Data (JSON)", json.dumps(receipt_result, indent=2))

    step(4, "Auto-populated expense form")
    data = receipt_result["extracted_data"]
    if RICH:
        table = Table(title="Expense Report Entry", box=box.ROUNDED)
        table.add_column("Field", style="cyan")
        table.add_column("Auto-filled Value", style="green")
        table.add_row("Merchant", data["store_name"])
        table.add_row("Date", data["date"])
        table.add_row("Amount", f"${data['total']:.2f}")
        table.add_row("Category", "Electronics")
        table.add_row("Payment", data["payment_method"])
        console.print(table)
    else:
        print(f"\n  Merchant: {data['store_name']}")
        print(f"  Amount: ${data['total']:.2f}")
        print(f"  Date: {data['date']}")

    # =========================================================================
    # USE CASE 3: MULTI-STEP WORKFLOW
    # =========================================================================
    banner("USE CASE 3: Multi-Step Agentic Workflow", "bold magenta")
    print("\n[BUSINESS CONTEXT] Complex query requiring multiple agents")
    print("working together autonomously.\n")

    step(1, "Client sends complex query")
    query = "Analyze the invoice, verify the math is correct, and flag any discrepancies"
    output("Client Query", query)

    step(2, "Supervisor routes to specialists")
    print("""
    ┌─────────────────────────────────────────────────────────────┐
    │                   AGENT ORCHESTRATION                       │
    ├─────────────────────────────────────────────────────────────┤
    │                                                             │
    │   [Supervisor] "Complex query detected, routing..."         │
    │        │                                                    │
    │        ├──→ [Vision Agent] Check document quality           │
    │        │         └── Result: Quality OK ✓                   │
    │        │                                                    │
    │        ├──→ [OCR Agent] Extract all text & numbers          │
    │        │         └── Result: 4 line items, totals found ✓   │
    │        │                                                    │
    │        └──→ [QA Agent] Verify calculations                  │
    │                  └── Result: Math verified ✓                │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
    """)

    step(3, "QA Agent performs verification")
    verification = {
        "line_items_sum": 13600.00,
        "stated_subtotal": 13600.00,
        "subtotal_match": True,
        "calculated_tax": 1122.00,
        "stated_tax": 1122.00,
        "tax_match": True,
        "calculated_total": 14722.00,
        "stated_total": 14722.00,
        "total_match": True,
        "discrepancies": [],
        "status": "VERIFIED - All calculations correct"
    }
    output("Verification Result", json.dumps(verification, indent=2))

    step(4, "Final response synthesized")
    final_response = """
✅ **Invoice Analysis Complete**

**Document Quality:** Good (94% confidence)

**Financial Summary:**
- Invoice #: INV-2024-0892
- Vendor: ACME CORPORATION
- Total Due: $14,722.00
- Due Date: January 24, 2025

**Verification Status:** ✓ PASSED
- Line items sum correctly: $13,600.00
- Tax calculation correct: $1,122.00 (8.25%)
- Total matches: $14,722.00

**Discrepancies Found:** None

**Recommendation:** Approved for payment processing.
"""
    output("Final Agent Response", final_response)

    # =========================================================================
    # SUMMARY
    # =========================================================================
    banner("📊 DEMONSTRATION SUMMARY", "bold yellow")

    if RICH:
        summary = Table(title="Test Results", box=box.DOUBLE)
        summary.add_column("Use Case", style="cyan")
        summary.add_column("Status", style="green")
        summary.add_column("Processing Time")
        summary.add_row("Invoice Processing", "✓ Success", "1.25s")
        summary.add_row("Receipt Scanning", "✓ Success", "0.89s")
        summary.add_row("Multi-Agent Workflow", "✓ Success", "2.14s")
        console.print(summary)
    else:
        print("\nTest Results:")
        print("  ✓ Invoice Processing - Success (1.25s)")
        print("  ✓ Receipt Scanning - Success (0.89s)")
        print("  ✓ Multi-Agent Workflow - Success (2.14s)")

    print("""
┌─────────────────────────────────────────────────────────────────┐
│                     INTEGRATION OPTIONS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔌 REST API         POST /api/v1/process                       │
│  🐍 Python SDK       from vision_agent import process_document  │
│  📦 Batch Mode       process_batch(documents, output_format)    │
│  🔄 Webhooks         Real-time status callbacks                 │
│  📊 Dashboard        Web UI for manual review                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Generated test documents:
  • {test_dir}/demo_invoice.png
  • {test_dir}/demo_receipt.png

To run with full OCR (requires API key):
  python tests/industry_use_case_test.py
""")

    print(f"\n✅ Demo completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


if __name__ == "__main__":
    main()
