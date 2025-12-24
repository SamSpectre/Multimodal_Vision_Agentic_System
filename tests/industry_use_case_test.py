#!/usr/bin/env python3
"""
Industry Use Case Test - Multimodal Vision Agentic System
==========================================================

This script demonstrates real-world business scenarios showing how clients
interact with the system from input to output.

USE CASES COVERED:
1. Invoice Processing (Accounts Payable)
2. Receipt Scanning (Expense Management)
3. Business Card Processing (CRM Data Entry)
4. Document Quality Assessment (Document Management)
5. Multi-step Workflow (Extract + Analyze + Q&A)

WORKFLOW: User Input → Agent Processing → Structured Output
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
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("[Note: Install 'rich' for better output formatting]")

console = Console() if RICH_AVAILABLE else None


def print_header(title: str):
    """Print a formatted header."""
    if RICH_AVAILABLE:
        console.print(Panel(f"[bold cyan]{title}[/bold cyan]", box=box.DOUBLE))
    else:
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)


def print_step(step: str, description: str):
    """Print a workflow step."""
    if RICH_AVAILABLE:
        console.print(f"[bold green]→ {step}:[/bold green] {description}")
    else:
        print(f"→ {step}: {description}")


def print_result(title: str, content: str):
    """Print a result panel."""
    if RICH_AVAILABLE:
        console.print(Panel(content, title=f"[bold yellow]{title}[/bold yellow]", border_style="yellow"))
    else:
        print(f"\n--- {title} ---")
        print(content)
        print("-" * 40)


def create_sample_invoice(output_path: str) -> str:
    """Create a sample business invoice image for testing."""
    # Create image
    img = Image.new('RGB', (800, 1000), color='white')
    draw = ImageDraw.Draw(img)

    # Try to use a font, fall back to default
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_small = font_large

    # Company Header
    draw.text((50, 30), "ACME CORPORATION", fill='navy', font=font_large)
    draw.text((50, 70), "123 Business Park, Suite 400", fill='gray', font=font_small)
    draw.text((50, 90), "San Francisco, CA 94102", fill='gray', font=font_small)
    draw.text((50, 110), "Tel: (415) 555-0123", fill='gray', font=font_small)

    # Invoice Title
    draw.rectangle([(500, 30), (750, 70)], fill='navy')
    draw.text((550, 40), "INVOICE", fill='white', font=font_large)

    # Invoice Details
    draw.text((500, 90), "Invoice #: INV-2024-0892", fill='black', font=font_small)
    draw.text((500, 110), "Date: December 24, 2024", fill='black', font=font_small)
    draw.text((500, 130), "Due Date: January 24, 2025", fill='black', font=font_small)

    # Bill To
    draw.text((50, 170), "BILL TO:", fill='navy', font=font_medium)
    draw.text((50, 200), "TechStart Solutions Inc.", fill='black', font=font_medium)
    draw.text((50, 225), "456 Innovation Drive", fill='gray', font=font_small)
    draw.text((50, 245), "Austin, TX 78701", fill='gray', font=font_small)
    draw.text((50, 265), "Contact: John Smith", fill='gray', font=font_small)

    # Table Header
    y_start = 320
    draw.rectangle([(50, y_start), (750, y_start + 35)], fill='lightgray')
    draw.text((60, y_start + 8), "Description", fill='black', font=font_medium)
    draw.text((400, y_start + 8), "Qty", fill='black', font=font_medium)
    draw.text((480, y_start + 8), "Unit Price", fill='black', font=font_medium)
    draw.text((620, y_start + 8), "Amount", fill='black', font=font_medium)

    # Line Items
    items = [
        ("Cloud Infrastructure Setup", "1", "$2,500.00", "$2,500.00"),
        ("API Integration Services", "40", "$150.00", "$6,000.00"),
        ("Database Migration", "1", "$3,500.00", "$3,500.00"),
        ("Training & Documentation", "8", "$200.00", "$1,600.00"),
        ("Technical Support (Monthly)", "3", "$500.00", "$1,500.00"),
    ]

    y = y_start + 50
    for desc, qty, unit, amount in items:
        draw.line([(50, y + 30), (750, y + 30)], fill='lightgray')
        draw.text((60, y), desc, fill='black', font=font_small)
        draw.text((410, y), qty, fill='black', font=font_small)
        draw.text((480, y), unit, fill='black', font=font_small)
        draw.text((620, y), amount, fill='black', font=font_small)
        y += 40

    # Totals
    y += 20
    draw.line([(450, y), (750, y)], fill='black', width=2)
    draw.text((480, y + 10), "Subtotal:", fill='black', font=font_medium)
    draw.text((620, y + 10), "$15,100.00", fill='black', font=font_medium)

    draw.text((480, y + 40), "Tax (8.25%):", fill='black', font=font_medium)
    draw.text((620, y + 40), "$1,245.75", fill='black', font=font_medium)

    draw.rectangle([(470, y + 70), (750, y + 110)], fill='navy')
    draw.text((480, y + 80), "TOTAL DUE:", fill='white', font=font_medium)
    draw.text((620, y + 80), "$16,345.75", fill='white', font=font_medium)

    # Payment Terms
    y += 150
    draw.text((50, y), "Payment Terms:", fill='navy', font=font_medium)
    draw.text((50, y + 25), "• Payment due within 30 days", fill='gray', font=font_small)
    draw.text((50, y + 45), "• Wire Transfer: Bank of America, Acc# 4521-8876-3321", fill='gray', font=font_small)
    draw.text((50, y + 65), "• Please include invoice number with payment", fill='gray', font=font_small)

    # Footer
    draw.text((250, 950), "Thank you for your business!", fill='navy', font=font_medium)

    # Save
    img.save(output_path)
    return output_path


def create_sample_receipt(output_path: str) -> str:
    """Create a sample retail receipt image for testing."""
    img = Image.new('RGB', (400, 700), color='white')
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
        font_bold = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 16)
    except:
        font = ImageFont.load_default()
        font_bold = font

    y = 20
    center = 200

    # Store Header
    draw.text((120, y), "TECHMART", fill='black', font=font_bold); y += 25
    draw.text((100, y), "ELECTRONICS", fill='black', font=font_bold); y += 25
    draw.text((70, y), "1250 Market Street", fill='black', font=font); y += 20
    draw.text((60, y), "San Francisco, CA 94102", fill='black', font=font); y += 20
    draw.text((80, y), "Tel: (415) 555-8899", fill='black', font=font); y += 30

    draw.text((20, y), "=" * 45, fill='black', font=font); y += 20
    draw.text((100, y), "SALES RECEIPT", fill='black', font=font_bold); y += 20
    draw.text((20, y), "=" * 45, fill='black', font=font); y += 25

    # Transaction info
    draw.text((20, y), f"Date: 12/24/2024  Time: 14:32", fill='black', font=font); y += 20
    draw.text((20, y), f"Transaction #: TM-20241224-0847", fill='black', font=font); y += 20
    draw.text((20, y), f"Cashier: Emily R.", fill='black', font=font); y += 25

    draw.text((20, y), "-" * 45, fill='black', font=font); y += 20

    # Items
    items = [
        ("USB-C Hub 7-Port", "$45.99"),
        ("Wireless Mouse Pro", "$29.99"),
        ("HDMI Cable 6ft", "$12.99"),
        ("Screen Protector x2", "$19.98"),
        ("Phone Case Premium", "$24.99"),
    ]

    for item, price in items:
        draw.text((20, y), item, fill='black', font=font)
        draw.text((300, y), price, fill='black', font=font)
        y += 22

    y += 10
    draw.text((20, y), "-" * 45, fill='black', font=font); y += 20

    # Totals
    draw.text((20, y), "SUBTOTAL:", fill='black', font=font)
    draw.text((300, y), "$133.94", fill='black', font=font); y += 22

    draw.text((20, y), "TAX (8.625%):", fill='black', font=font)
    draw.text((300, y), "$11.55", fill='black', font=font); y += 22

    draw.text((20, y), "=" * 45, fill='black', font=font); y += 20

    draw.text((20, y), "TOTAL:", fill='black', font=font_bold)
    draw.text((290, y), "$145.49", fill='black', font=font_bold); y += 25

    draw.text((20, y), "=" * 45, fill='black', font=font); y += 25

    # Payment
    draw.text((20, y), "PAYMENT METHOD:", fill='black', font=font); y += 22
    draw.text((20, y), "VISA ************4521", fill='black', font=font); y += 22
    draw.text((20, y), "AUTH CODE: 847291", fill='black', font=font); y += 30

    # Footer
    draw.text((20, y), "-" * 45, fill='black', font=font); y += 20
    draw.text((60, y), "Returns within 30 days", fill='gray', font=font); y += 18
    draw.text((70, y), "with original receipt", fill='gray', font=font); y += 25
    draw.text((50, y), "*** THANK YOU! ***", fill='black', font=font_bold); y += 25
    draw.text((30, y), "Visit us at techmart.com", fill='gray', font=font)

    img.save(output_path)
    return output_path


def create_sample_business_card(output_path: str) -> str:
    """Create a sample business card image for testing."""
    img = Image.new('RGB', (500, 300), color='white')
    draw = ImageDraw.Draw(img)

    # Add gradient-like background element
    draw.rectangle([(0, 0), (8, 300)], fill='#1a4b8c')

    try:
        font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        font_info = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        font_name = ImageFont.load_default()
        font_title = font_name
        font_info = font_name

    # Company logo area
    draw.rectangle([(380, 20), (480, 80)], outline='#1a4b8c', width=2)
    draw.text((395, 35), "NEXUS", fill='#1a4b8c', font=font_title)
    draw.text((395, 52), "TECH", fill='#1a4b8c', font=font_title)

    # Name and Title
    draw.text((30, 40), "Sarah Chen", fill='#1a4b8c', font=font_name)
    draw.text((30, 75), "Senior Product Manager", fill='gray', font=font_title)
    draw.text((30, 95), "Cloud Solutions Division", fill='gray', font=font_info)

    # Contact Info
    y = 150
    draw.text((30, y), "📧  sarah.chen@nexustech.com", fill='black', font=font_info); y += 25
    draw.text((30, y), "📱  +1 (650) 555-0147", fill='black', font=font_info); y += 25
    draw.text((30, y), "🏢  2500 Sand Hill Road, Menlo Park, CA 94025", fill='black', font=font_info); y += 25
    draw.text((30, y), "🌐  www.nexustech.com", fill='black', font=font_info)

    # LinkedIn
    draw.text((30, 270), "in/sarahchen-pm", fill='#0077b5', font=font_info)

    img.save(output_path)
    return output_path


class IndustryUseCaseDemo:
    """Demonstrates industry use cases for the Multimodal Vision Agentic System."""

    def __init__(self):
        self.test_dir = PROJECT_ROOT / "test_images"
        self.test_dir.mkdir(exist_ok=True)
        self.results = {}

    def setup_test_documents(self):
        """Create sample business documents for testing."""
        print_header("📄 Creating Sample Business Documents")

        documents = {}

        print_step("1", "Creating sample invoice...")
        documents['invoice'] = create_sample_invoice(str(self.test_dir / "sample_invoice.png"))

        print_step("2", "Creating sample receipt...")
        documents['receipt'] = create_sample_receipt(str(self.test_dir / "sample_receipt.png"))

        print_step("3", "Creating sample business card...")
        documents['business_card'] = create_sample_business_card(str(self.test_dir / "sample_business_card.png"))

        if RICH_AVAILABLE:
            console.print("\n[green]✓ Sample documents created successfully![/green]")
        else:
            print("\n✓ Sample documents created successfully!")

        return documents

    def test_ocr_tools_directly(self, documents: dict):
        """Test OCR tools directly without LLM (for environments without API keys)."""
        print_header("🔧 Direct OCR Tools Test (No API Required)")

        from src.tools.ocr_tools import (
            extract_text_from_image,
            detect_text_regions,
            analyze_document_structure
        )
        from src.tools.basic_vision_tools import (
            get_image_properties,
            analyze_image_colors,
            detect_image_quality_issues
        )

        results = {}

        # Test 1: Invoice Processing
        print_step("Test 1", "Invoice Processing - Accounts Payable Use Case")
        print("\n[CLIENT INPUT] 'Process this invoice and extract key financial data'\n")

        invoice_path = documents['invoice']

        # Step 1: Quality Check
        quality = detect_image_quality_issues(invoice_path)
        print_result("Step 1: Document Quality Assessment", quality)

        # Step 2: Extract Text
        extracted_text = extract_text_from_image(invoice_path)
        print_result("Step 2: OCR Text Extraction", extracted_text)

        # Step 3: Document Structure
        structure = analyze_document_structure(invoice_path)
        print_result("Step 3: Document Structure Analysis", structure)

        results['invoice'] = {
            'quality': quality,
            'text': extracted_text,
            'structure': json.loads(structure) if not structure.startswith('{') or 'error' not in structure else structure
        }

        # Test 2: Receipt Processing
        print_step("Test 2", "Receipt Processing - Expense Management Use Case")
        print("\n[CLIENT INPUT] 'Scan this receipt for expense reporting'\n")

        receipt_path = documents['receipt']

        # Extract text with regions
        receipt_text = extract_text_from_image(receipt_path)
        print_result("Receipt OCR Output", receipt_text)

        receipt_regions = detect_text_regions(receipt_path)
        print_result("Text Region Detection", receipt_regions[:1000] + "..." if len(receipt_regions) > 1000 else receipt_regions)

        results['receipt'] = {
            'text': receipt_text,
            'regions': json.loads(receipt_regions) if receipt_regions.startswith('{') else receipt_regions
        }

        # Test 3: Business Card Processing
        print_step("Test 3", "Business Card Processing - CRM Data Entry Use Case")
        print("\n[CLIENT INPUT] 'Extract contact information from this business card'\n")

        card_path = documents['business_card']

        # Get properties first
        properties = get_image_properties(card_path)
        print_result("Image Properties", properties)

        # Extract contact info
        card_text = extract_text_from_image(card_path)
        print_result("Contact Information Extracted", card_text)

        results['business_card'] = {
            'properties': properties,
            'text': card_text
        }

        return results

    def test_full_agent_system(self, documents: dict):
        """Test the complete multi-agent system (requires API key)."""
        print_header("🤖 Full Multi-Agent System Test")

        try:
            from graph import build_multiagent_system

            print_step("Init", "Building multi-agent system...")
            agent = build_multiagent_system()

            test_cases = [
                {
                    "name": "Invoice Analysis",
                    "query": f"Analyze the invoice at {documents['invoice']} and tell me: 1) Who is the vendor? 2) What is the total amount due? 3) What is the due date?",
                    "use_case": "Accounts Payable Automation"
                },
                {
                    "name": "Receipt Processing",
                    "query": f"Process the receipt at {documents['receipt']} and extract: store name, total amount, payment method, and list of items purchased.",
                    "use_case": "Expense Management"
                },
                {
                    "name": "Business Card to CRM",
                    "query": f"Extract all contact information from the business card at {documents['business_card']} in a structured format suitable for CRM import.",
                    "use_case": "Contact Data Entry"
                }
            ]

            results = {}
            for test in test_cases:
                print_step(test["name"], f"Use Case: {test['use_case']}")
                print(f"\n[CLIENT QUERY]: {test['query']}\n")

                try:
                    response = agent.invoke({
                        "messages": [{"role": "user", "content": test["query"]}]
                    })

                    output = response['messages'][-1].content
                    print_result(f"Agent Response - {test['name']}", output)
                    results[test["name"]] = {"status": "success", "output": output}

                except Exception as e:
                    print_result(f"Error - {test['name']}", str(e))
                    results[test["name"]] = {"status": "error", "error": str(e)}

            return results

        except Exception as e:
            print(f"\n⚠️  Could not initialize agent system: {e}")
            print("   This usually means API keys are not configured.")
            print("   Running direct tool tests instead...\n")
            return None

    def generate_report(self, results: dict):
        """Generate a summary report of test results."""
        print_header("📊 Test Results Summary")

        if RICH_AVAILABLE:
            table = Table(title="Document Processing Results", box=box.ROUNDED)
            table.add_column("Document Type", style="cyan")
            table.add_column("Text Extracted", style="green")
            table.add_column("Key Data Points", style="yellow")

            for doc_type, data in results.items():
                text_len = len(data.get('text', ''))
                has_text = "✓ Yes" if text_len > 50 else "✗ No/Limited"

                # Count key data points
                if 'regions' in data and isinstance(data['regions'], dict):
                    regions = data['regions'].get('total_regions', 0)
                else:
                    regions = "N/A"

                table.add_row(doc_type.replace('_', ' ').title(), has_text, f"{regions} regions")

            console.print(table)
        else:
            print("\nDocument Processing Results:")
            print("-" * 50)
            for doc_type, data in results.items():
                text_len = len(data.get('text', ''))
                print(f"  {doc_type}: {'✓' if text_len > 50 else '✗'} Text extracted ({text_len} chars)")

        print("\n")


def main():
    """Run the industry use case demonstration."""
    print_header("🏢 INDUSTRY USE CASE DEMONSTRATION")
    print_header("Multimodal Vision & OCR Agentic System")

    print("""
This demonstration shows how enterprise clients interact with the system
for common business document processing tasks.

WORKFLOW OVERVIEW:
┌─────────────────────────────────────────────────────────────────┐
│  USER INPUT          →    AGENT PROCESSING    →    OUTPUT      │
├─────────────────────────────────────────────────────────────────┤
│  "Process invoice"   →    OCR + Analysis      →    Structured  │
│  "Scan receipt"      →    Text Extraction     →    JSON/Text   │
│  "Extract contacts"  →    Multi-step Flow     →    CRM Data    │
└─────────────────────────────────────────────────────────────────┘
""")

    demo = IndustryUseCaseDemo()

    # Step 1: Create test documents
    documents = demo.setup_test_documents()

    # Step 2: Try full agent system first
    agent_results = demo.test_full_agent_system(documents)

    # Step 3: If agent system failed (no API key), run direct tool tests
    if agent_results is None:
        tool_results = demo.test_ocr_tools_directly(documents)
        demo.generate_report(tool_results)
    else:
        demo.generate_report(agent_results)

    # Final summary
    print_header("✅ DEMONSTRATION COMPLETE")
    print("""
KEY TAKEAWAYS FOR CLIENTS:

1. INVOICE PROCESSING (Accounts Payable)
   - Automatic extraction of vendor, amounts, due dates
   - Structured output for ERP integration
   - Quality validation before processing

2. RECEIPT SCANNING (Expense Management)
   - Line item extraction with prices
   - Tax and total calculation verification
   - Payment method identification

3. BUSINESS CARD PROCESSING (CRM)
   - Contact information extraction
   - Structured format for database import
   - Multi-language support

4. DOCUMENT QUALITY ASSESSMENT
   - Automatic quality scoring
   - Recommendations for re-scan if needed
   - Confidence scores for extracted data

INTEGRATION OPTIONS:
- REST API endpoint
- Python SDK
- Batch processing pipeline
- Real-time streaming

For production deployment, contact: support@example.com
""")

    print(f"\nTest documents saved to: {demo.test_dir}")
    print("You can view the generated images to verify quality.\n")


if __name__ == "__main__":
    main()
