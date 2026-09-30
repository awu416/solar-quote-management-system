from io import BytesIO
from pathlib import Path

from flask import current_app
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def format_currency(value):
    return f"${value:,.2f}"


def generate_quote_pdf(quote):
    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=f"Solar Quote #{quote.id}",
        author="Tasmania Reliable Solar",
    )

    styles = getSampleStyleSheet()

    # Brand colours
    navy = colors.HexColor("#001C3B")
    gold = colors.HexColor("#FFB52E")
    light_background = colors.HexColor("#F4F6F8")
    border_colour = colors.HexColor("#D5D9DD")

    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=navy,
        spaceAfter=5,
    )

    quote_title = ParagraphStyle(
        "QuoteTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=23,
        alignment=TA_RIGHT,
        textColor=navy,
        spaceAfter=3,
    )

    quote_meta = ParagraphStyle(
        "QuoteMeta",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#555555"),
    )

    detail_text = ParagraphStyle(
        "DetailText",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#222222"),
    )

    small_text = ParagraphStyle(
        "SmallText",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#666666"),
    )

    total_label_style = ParagraphStyle(
        "TotalLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        alignment=TA_RIGHT,
        textColor=navy,
    )

    total_value_style = ParagraphStyle(
        "TotalValue",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        alignment=TA_RIGHT,
        textColor=navy,
    )

    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#666666"),
    )

    story = []

    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------

    logo_path = Path(current_app.static_folder) / "images" / "trs_logo.png"

    logo = Image(
        str(logo_path),
        width=75 * mm,
        height=26.4 * mm,
    )

    created_date = (
        quote.created_at.strftime("%d %B %Y")
        if quote.created_at
        else "N/A"
    )

    header_right = [
        Paragraph("SOLAR QUOTATION", quote_title),
        Paragraph(
            f"Quote #{quote.id}<br/>"
            f"{created_date}<br/>"
            f"Status: {quote.status.title()}",
            quote_meta,
        ),
    ]

    header_table = Table(
        [
            [
                logo,
                header_right,
            ]
        ],
        colWidths=[95 * mm, 79 * mm],
    )

    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    story.append(header_table)

    story.append(
        Table(
            [[""]],
            colWidths=[174 * mm],
            rowHeights=[1.2 * mm],
            style=TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        gold,
                    ),
                ]
            ),
        )
    )

    story.append(Spacer(1, 8 * mm))

    # ---------------------------------------------------------
    # Customer + System details
    # ---------------------------------------------------------

    customer = quote.customer

    customer_content = [
        Paragraph("CUSTOMER DETAILS", section_heading),
        Paragraph(
            f"<b>{customer.first_name} {customer.last_name}</b><br/>"
            f"{customer.email or 'N/A'}<br/>"
            f"{customer.phone or 'N/A'}",
            detail_text,
        ),
    ]

    battery_display = (
        f"{quote.battery_size:g} kWh"
        if quote.battery_size is not None
        else "None"
    )

    system_content = [
        Paragraph("SYSTEM DETAILS", section_heading),
        Paragraph(
            f"<b>Solar System:</b> {quote.system_size:g} kW<br/>"
            f"<b>Battery:</b> {battery_display}<br/>"
            f"<b>Status:</b> {quote.status.title()}",
            detail_text,
        ),
    ]

    details_table = Table(
        [[customer_content, system_content]],
        colWidths=[87 * mm, 87 * mm],
    )

    details_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    light_background,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    border_colour,
                ),
                (
                    "LINEAFTER",
                    (0, 0),
                    (0, -1),
                    0.5,
                    border_colour,
                ),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(details_table)

    story.append(Spacer(1, 9 * mm))

    # ---------------------------------------------------------
    # Products
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "PRODUCTS",
            section_heading,
        )
    )

    product_data = [
        [
            Paragraph("<b>Product</b>", small_text),
            Paragraph("<b>Category</b>", small_text),
            Paragraph("<b>Qty</b>", small_text),
            Paragraph("<b>Unit Price</b>", small_text),
            Paragraph("<b>Line Total</b>", small_text),
        ]
    ]

    for item in quote.items:
        product = item.product

        product_name = f"{product.brand} {product.model}"

        product_data.append(
            [
                Paragraph(product_name, detail_text),
                Paragraph(product.category.title(), detail_text),
                str(item.quantity),

                # Historical Snapshot Pricing
                format_currency(item.unit_price),

                format_currency(item.line_total),
            ]
        )

    product_table = Table(
        product_data,
        colWidths=[
            64 * mm,
            28 * mm,
            14 * mm,
            31 * mm,
            37 * mm,
        ],
        repeatRows=1,
    )

    product_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    navy,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "ALIGN",
                    (2, 0),
                    (-1, -1),
                    "RIGHT",
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LINEBELOW",
                    (0, 1),
                    (-1, -1),
                    0.5,
                    border_colour,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(product_table)

    story.append(Spacer(1, 6 * mm))

    # ---------------------------------------------------------
    # Total
    # ---------------------------------------------------------

    total_table = Table(
        [
            [
                "",
                Paragraph("QUOTE TOTAL", total_label_style),
                Paragraph(
                    format_currency(quote.total_price),
                    total_value_style,
                ),
            ]
        ],
        colWidths=[92 * mm, 37 * mm, 45 * mm],
    )

    total_table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (1, 0),
                    (-1, 0),
                    light_background,
                ),
                (
                    "LINEABOVE",
                    (1, 0),
                    (-1, 0),
                    1.2,
                    gold,
                ),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (1, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (1, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(total_table)

    story.append(Spacer(1, 15 * mm))

    # ---------------------------------------------------------
    # Footer
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "<b>Tasmania Reliable Solar</b><br/>"
            "Reliable Today, Sustainable Tomorrow.<br/><br/>"
            "Thank you for considering Tasmania Reliable Solar "
            "for your solar solution.",
            footer_style,
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer