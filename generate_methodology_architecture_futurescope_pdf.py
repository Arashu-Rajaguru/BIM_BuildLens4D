"""
BuildLens 4D — Technical Whitepaper & Engineering Report Generator
Topic: Methodology, Architecture, and Future Scope
"""

import os
import sys
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_OUTPUT_PATH = r"c:\BuildLens4D\BuildLens4D_Methodology_Architecture_FutureScope_Report.pdf"


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#0284c7"))

        # Running header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 11 * 72 - 36, "BUILDLENS 4D")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(125, 11 * 72 - 36, "— Technical Report: Methodology, Architecture & Future Scope")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 11 * 72 - 40, 8.5 * 72 - 54, 11 * 72 - 40)

        # Running footer
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawRightString(8.5 * 72 - 54, 32, page_str)
        self.drawString(54, 32, "CONFIDENTIAL & PROPRIETARY — Technical Whitepaper & Architectural Specification")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 42, 8.5 * 72 - 54, 42)
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        PDF_OUTPUT_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Color Palette
    c_navy = colors.HexColor("#0f172a")
    c_blue = colors.HexColor("#0284c7")
    c_emerald = colors.HexColor("#059669")
    c_amber = colors.HexColor("#d97706")
    c_dark = colors.HexColor("#1e293b")
    c_slate = colors.HexColor("#475569")
    c_light = colors.HexColor("#f8fafc")
    c_border = colors.HexColor("#e2e8f0")
    c_card_bg = colors.HexColor("#f1f5f9")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=23,
        leading=27,
        textColor=c_navy,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_blue,
        spaceAfter=14
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_slate
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_navy,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_blue,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        textColor=c_dark,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=13,
        textColor=c_dark,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.5,
        leading=12.5,
        textColor=c_dark
    )

    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )

    td_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=10.5,
        textColor=c_dark
    )

    td_bold_style = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=10.5,
        textColor=c_navy
    )

    story = []

    # =========================================================================
    # COVER / HEADER
    # =========================================================================
    story.append(Paragraph("BuildLens 4D — Technical Specification Report", title_style))
    story.append(Paragraph("METHODOLOGY, SYSTEM ARCHITECTURE & FUTURE ROADMAP", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=c_blue, spaceBefore=0, spaceAfter=8))

    meta_table_data = [
        [
            Paragraph("<b>Document Version:</b> 2.4.0 (Production)", meta_style),
            Paragraph("<b>Target Domain:</b> 4D BIM & Physical Verification", meta_style),
            Paragraph(f"<b>Date:</b> {datetime.date.today().strftime('%B %d, %Y')}", meta_style)
        ],
        [
            Paragraph("<b>System Core:</b> FastAPI + React + CV Engine", meta_style),
            Paragraph("<b>Classification:</b> Technical Architecture Dossier", meta_style),
            Paragraph("<b>Status:</b> Verified & Deployed", meta_style)
        ]
    ]
    meta_table = Table(meta_table_data, colWidths=[170, 180, 154])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), c_card_bg),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # Executive Overview Callout
    callout_data = [[
        Paragraph(
            "<b>Executive Summary:</b> BuildLens 4D bridges the high-stakes disconnect between architectural "
            "design plans (2D CAD / 3D BIM) and physical on-site construction reality. By integrating multi-spectral "
            "computer vision, dynamic spatial coordinate alignment, automated schedule simulation, and human-in-the-loop "
            "governance (SRS 8.1/8.3), the platform eliminates manual reporting latency, prevents multi-million dollar "
            "schedule overruns, and enforces an immutable, cryptographic chain of custody for all site evidence.",
            callout_style
        )
    ]]
    callout_table = Table(callout_data, colWidths=[504])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#e0f2fe")),
        ('BOX', (0, 0), (-1, -1), 1, c_blue),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(callout_table)
    story.append(Spacer(1, 12))

    # =========================================================================
    # SECTION 1: METHODOLOGY
    # =========================================================================
    story.append(Paragraph("1. System Methodology & Engineering Mechanics", h1_style))
    story.append(Paragraph(
        "The BuildLens 4D methodology is structured into five interdependent operational phases designed "
        "to ensure mathematical rigor, low false-positive rates, and strict adherence to engineering standards:",
        body_style
    ))

    methodology_steps = [
        ("1.1 4D BIM Baseline Ingestion",
         "The project master schedule (WBS) and structural elements (IFC schema) are parsed into standardized "
         "temporal envelopes. Each element (footing, column, transfer beam, floor slab, curtain wall) receives an immutable "
         "spatial zone, planned start, planned finish, and dependency constraints. The time dimension (4D) turns static BIM "
         "into a continuous calendar-driven state machine."),
        ("1.2 Multi-Spectral Computer Vision Decomposition",
         "When an on-site image is acquired, the BuildingForm AI Model resizes the input to a normalized evaluation "
         "matrix (256x256) and extracts orthogonal spectral features: (a) Earthwork/Soil Pit ratio (brown/amber: R > G > B), "
         "(b) Structural Concrete ratio (|R-G| & |G-B| < 0.08, mid-luminance), (c) Glazing reflection (B > R, luminance > 0.35), "
         "(d) Dark paved asphalt & vehicle parking ratio, (e) Diagonal high-frequency scaffolding entropy, and "
         "(f) Vertical spatial edge gradient slices across structural bays."),
        ("1.3 Dual-Asset Cross-Comparison Protocol",
         "Unlike traditional models that inspect photos in isolation, BuildLens 4D executes a paired cross-comparison. "
         "The 2D CAD architectural blueprint is mapped to coordinate space (Grid 1–6, A–D). The physical site photo is "
         "registered simultaneously. For every planned component, the AI compares the design coordinates on the plan "
         "with the corresponding spatial ray on the physical site photo."),
        ("1.4 Milestone-Calibrated Conformance Scoring",
         "A major breakthrough of BuildLens 4D is its calibrated progress algorithm. Elements are weighted dynamically "
         "by physical state (Verified Complete = 1.0, In-Progress = 0.5, Not Started = 0.0). This prevents premature 80%+ "
         "scores during foundation stages and ensures: (a) Quarter Stage (Foundation Footings & Column Starters) = exactly 25.0%, "
         "(b) Half Stage (Superstructure Concrete Framing & Slabs) = exactly 50.0%, and (c) Full Stage (Enclosed Facade & Paving) = 100.0%."),
        ("1.5 SRS 8.3 Occlusion Management & Human-in-the-Loop",
         "When temporary perimeter staging, safety debris netting, or tower crane counterweights obstruct direct line of sight, "
         "the AI invokes guardrail SRS 8.3. Rather than hallucinating completion, it flags the item as 'needs_manual_review' "
         "(confidence score calibrated < 0.60) and automatically routes it to the Project Manager's Review Queue.")
    ]

    for title, desc in methodology_steps:
        story.append(Paragraph(f"<b>{title}:</b> {desc}", bullet_style))

    story.append(Spacer(1, 8))

    # Methodology Flow Matrix Table
    story.append(Paragraph("<b>Table 1: Operational Methodology Pipeline Matrix</b>", h2_style))
    meth_headers = [
        Paragraph("Phase", th_style),
        Paragraph("Primary Input", th_style),
        Paragraph("Algorithm / Engine", th_style),
        Paragraph("Verification Output", th_style),
        Paragraph("Guardrail / Standard", th_style)
    ]
    meth_rows = [
        [
            Paragraph("Phase 1: Ingest", td_bold_style),
            Paragraph("IFC BIM + Master Schedule", td_style),
            Paragraph("Spatial-Temporal Parser", td_style),
            Paragraph("Structured BIM Elements", td_style),
            Paragraph("ISO 19650 Compliance", td_style)
        ],
        [
            Paragraph("Phase 2: Capture", td_bold_style),
            Paragraph("Mobile AR / Dual Image", td_style),
            Paragraph("SHA-256 Digest Engine", td_style),
            Paragraph("Evidence Record + URL", td_style),
            Paragraph("Cryptographic Proof", td_style)
        ],
        [
            Paragraph("Phase 3: CV Model", td_bold_style),
            Paragraph("Plan + Site Imagery", td_style),
            Paragraph("BuildingFormAI (Spectral)", td_style),
            Paragraph("Stage + Edge Bounding Box", td_style),
            Paragraph("Confidence Calibrator", td_style)
        ],
        [
            Paragraph("Phase 4: Match", td_bold_style),
            Paragraph("Blueprint vs As-Built", td_style),
            Paragraph("Weighted Conformance Alg", td_style),
            Paragraph("25% / 50% / 100% Score", td_style),
            Paragraph("SRS 8.1 Verification", td_style)
        ],
        [
            Paragraph("Phase 5: Audit", td_bold_style),
            Paragraph("Low Conf / Scaffolding", td_style),
            Paragraph("Review Queue Workflow", td_style),
            Paragraph("Manager Sign-Off / Reject", td_style),
            Paragraph("SRS 8.3 Guardrail", td_style)
        ]
    ]

    meth_table = Table([meth_headers] + meth_rows, colWidths=[70, 110, 120, 110, 94])
    meth_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(meth_table)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 2: SYSTEM ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("2. System Architecture & Topology", h1_style))
    story.append(Paragraph(
        "BuildLens 4D employs a cloud-native, decoupled micro-monolith architecture designed for high throughput, "
        "low latency on mobile networks, and enterprise data durability:",
        body_style
    ))

    arch_sections = [
        ("2.1 Presentation Tier (React 18 + Vite PWA & Mobile Client)",
         "Built with React 18, Vite, and HTML5 Web Standards. It operates as an installable Progressive Web App (PWA) "
         "running seamlessly on mobile browsers (Chrome Android, Safari iOS) and desktop workstations. It features an "
         "interactive 4D Schedule Scrubber (forward simulating from Today to Future Completion), responsive side-by-side "
         "dual viewports, live KPI gauges, and an offline-ready service worker caching strategy."),
        ("2.2 API Gateway & Business Logic Tier (FastAPI + Pydantic v2)",
         "Implemented in Python 3.14 using the asynchronous FastAPI framework. Request and response payloads are "
         "strictly validated at the network boundary using Pydantic v2 models. The core services execute: "
         "(a) Computer vision feature extraction, (b) 4D time simulation calculations, (c) Cryptographic SHA-256 asset hashing, "
         "and (d) Audit trail transaction dispatching."),
        ("2.3 Data Storage Tier (SQLAlchemy ORM + PostgreSQL / SQLite)",
         "Structured business data resides in relational tables managed via SQLAlchemy ORM. The schema cleanly separates "
         "design entities (BIM Elements, Construction Schedules) from observational truth (Progress Observations, Evidence "
         "Records, Review Queue, and Audit Logs). In production, connection pooling connects to PostgreSQL."),
        ("2.4 Secure File Storage Tier (SHA-256 Cryptographic Vault)",
         "Uploaded CAD blueprints, drone surveys, and site photographs are securely persisted with tamper-evident filenames "
         "generated from unique UUIDs and SHA-256 cryptographic hashes. File access is mediated through tokenized endpoints, "
         "with transparent abstraction supporting local file vaults in development and AWS S3 in enterprise production."),
        ("2.5 Mobile Network Connectivity Tier (Cloudflare Tunnel & LAN Gateways)",
         "To accommodate variable construction site connectivity, the backend binds to all interfaces (0.0.0.0:8000), "
         "enabling direct zero-latency LAN Wi-Fi communication (http://192.168.x.x) for on-site crew, alongside an encrypted "
         "Cloudflare HTTPS Tunnel (trycloudflare.com) that provides globally routable, SSL-certified access for remote executives.")
    ]

    for title, desc in arch_sections:
        story.append(Paragraph(f"<b>{title}:</b> {desc}", bullet_style))

    story.append(Spacer(1, 8))

    # Architecture Topology Table
    story.append(Paragraph("<b>Table 2: Architectural Component Specification</b>", h2_style))
    arch_headers = [
        Paragraph("Component", th_style),
        Paragraph("Technology Stack", th_style),
        Paragraph("Primary Responsibility", th_style),
        Paragraph("Protocols / Interfaces", th_style)
    ]
    arch_rows = [
        [
            Paragraph("Mobile & Web UI", td_bold_style),
            Paragraph("React 18, Vite, CSS3, PWA", td_style),
            Paragraph("Field capture, 4D scrubber, review desk", td_style),
            Paragraph("HTTPS, Service Worker, W3C Manifest", td_style)
        ],
        [
            Paragraph("REST Gateway", td_bold_style),
            Paragraph("FastAPI, Uvicorn, Python", td_style),
            Paragraph("API routing, schema validation, auth", td_style),
            Paragraph("HTTP/2, JSON, OpenAPI 3.0", td_style)
        ],
        [
            Paragraph("AI CV Engine", td_bold_style),
            Paragraph("BuildingFormAI, Pillow, NumPy", td_style),
            Paragraph("Spectral decomposition, plan alignment", td_style),
            Paragraph("Internal Python In-Memory Pipeline", td_style)
        ],
        [
            Paragraph("Persistence Engine", td_bold_style),
            Paragraph("SQLAlchemy ORM, PostgreSQL", td_style),
            Paragraph("Transactional state, audit logs, queues", td_style),
            Paragraph("SQL / Connection Pool (Port 5432)", td_style)
        ],
        [
            Paragraph("Asset Vault", td_bold_style),
            Paragraph("Local Vault / AWS S3 Blob", td_style),
            Paragraph("Evidence storage, SHA-256 validation", td_style),
            Paragraph("Multipart Form-Data, HTTPS PUT/GET", td_style)
        ],
        [
            Paragraph("Public Tunnel", td_bold_style),
            Paragraph("Cloudflare Edge / QUIC / HTTP3", td_style),
            Paragraph("Remote mobile access, SSL encryption", td_style),
            Paragraph("TLS 1.3, HTTPS (Port 443)", td_style)
        ]
    ]

    arch_table = Table([arch_headers] + arch_rows, colWidths=[90, 115, 175, 124])
    arch_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(arch_table)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 3: FUTURE SCOPE & NEXT-GEN ROADMAP
    # =========================================================================
    story.append(Paragraph("3. Future Scope & Innovation Roadmap", h1_style))
    story.append(Paragraph(
        "BuildLens 4D is engineered with an extensible modular foundation. The future development roadmap "
        "targets four strategic technology frontiers across the next 12 to 36 months:",
        body_style
    ))

    future_sections = [
        ("3.1 3D LiDAR & Drone Photogrammetry Dense Point Cloud Alignment",
         "While current capabilities analyze high-resolution 2D CAD blueprints against orthographic/perspective photography, "
         "Version 3.0 will ingest raw LAS/PLY point clouds from DJI Terra, Skydio drones, and Leica BLK360 terrestrial scanners. "
         "Using Iterative Closest Point (ICP) and octree-based voxel difference models, the system will measure sub-millimeter "
         "deflection in concrete slabs, beam camber, and structural verticality against IFC geometry."),
        ("3.2 On-Device Edge AI Inference (ONNX / WebGPU / TFLite)",
         "To support subterranean projects, remote mines, and transit tunnels where cellular connectivity is entirely absent, "
         "the BuildingForm AI model will be compiled into lightweight quantized ONNX / WebGPU runtimes running directly inside "
         "the mobile browser. The site engineer will capture photos, receive instant offline verification, and synchronize with "
         "the cloud once returning to Wi-Fi."),
        ("3.3 Autonomous Site Robotics & Rover Fleet Dispatch",
         "Integration with autonomous quadruped robots (e.g., Boston Dynamics Spot) and autonomous docking drones. "
         "Robotic units will follow scheduled inspection waypoints every evening after construction crews depart, capturing "
         "360-degree imagery and feeding the BuildLens 4D API overnight. Project managers will arrive each morning to an "
         "automatically updated 4D progress dashboard."),
        ("3.4 Smart Contract Automated Milestone Escrow Disbursements",
         "Connecting the BuildLens 4D verification engine to blockchain smart contracts (Ethereum / Hyperledger Fabric). "
         "When an objective milestone (e.g., 'Level 3 Concrete Pour verified at 100% compliance with engineer sign-off') is "
         "certified, banking escrow funds will be disbursed automatically to subcontractors, eliminating 60-day billing disputes."),
        ("3.5 Multi-Trade MEP (Mechanical, Electrical & Plumbing) Clash Detection",
         "Expanding beyond structural concrete and steel into HVAC ductwork, fire sprinkler piping, cable trays, and plumbing. "
         "Using semantic segmentation deep neural networks (YOLOv11-OBB / Mask R-CNN), the system will verify sleeve openings, "
         "pipe penetrations, and pre-pour rough-ins before concrete is irreversibly poured.")
    ]

    for title, desc in future_sections:
        story.append(Paragraph(f"<b>{title}:</b> {desc}", bullet_style))

    story.append(Spacer(1, 8))

    # Roadmap Table
    story.append(Paragraph("<b>Table 3: Strategic Future Roadmap Milestones (v3.0 – v5.0)</b>", h2_style))
    road_headers = [
        Paragraph("Release", th_style),
        Paragraph("Target Horizon", th_style),
        Paragraph("Core Capabilities", th_style),
        Paragraph("Industry Impact", th_style)
    ]
    road_rows = [
        [
            Paragraph("v3.0 Edge", td_bold_style),
            Paragraph("Q2 2027", td_style),
            Paragraph("WebGPU edge inference, offline caching, 360-degree photo walk-throughs", td_style),
            Paragraph("Subway tunnels, deep basements, zero internet dependency", td_style)
        ],
        [
            Paragraph("v3.5 LiDAR", td_bold_style),
            Paragraph("Q4 2027", td_style),
            Paragraph("Dense 3D point cloud ICP registration, millimeter tolerance heatmaps", td_style),
            Paragraph("Structural QA/QC certification, slab deflection auditing", td_style)
        ],
        [
            Paragraph("v4.0 Robotics", td_bold_style),
            Paragraph("Q2 2028", td_style),
            Paragraph("Autonomous drone & quadruped robot automated nightly inspection rounds", td_style),
            Paragraph("Zero manual labor inspection overhead, 24/7 site auditing", td_style)
        ],
        [
            Paragraph("v4.5 MEP", td_bold_style),
            Paragraph("Q4 2028", td_style),
            Paragraph("HVAC, plumbing, electrical conduit semantic segmentation & clash audit", td_style),
            Paragraph("Elimination of post-pour concrete core drilling rework", td_style)
        ],
        [
            Paragraph("v5.0 FinTech", td_bold_style),
            Paragraph("Q2 2029", td_style),
            Paragraph("Smart contract escrow payouts, AI risk underwriting for lenders", td_style),
            Paragraph("Instant subcontractor cashflow, automated insurance verification", td_style)
        ]
    ]

    road_table = Table([road_headers] + road_rows, colWidths=[65, 80, 205, 154])
    road_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_navy),
        ('BOX', (0, 0), (-1, -1), 0.5, c_border),
        ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, c_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(road_table)
    story.append(Spacer(1, 14))

    # =========================================================================
    # CONCLUSION / SIGN-OFF
    # =========================================================================
    conclusion_data = [[
        Paragraph(
            "<b>Conclusion & Engineering Sign-Off:</b> BuildLens 4D represents a transformative paradigm shift in "
            "construction monitoring. By uniting 4D schedule automation, multi-spectral computer vision, cryptographic "
            "data provenance, and proactive human-in-the-loop review, the platform delivers unprecedented transparency, "
            "auditability, and cost control across modern civil infrastructure projects.",
            callout_style
        )
    ]]
    concl_table = Table(conclusion_data, colWidths=[504])
    concl_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ('BOX', (0, 0), (-1, -1), 1, c_emerald),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(concl_table)

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated Technical PDF Report: {PDF_OUTPUT_PATH}")


if __name__ == "__main__":
    build_pdf()
