"""
import_product_catalogue — loads MECHPRO's real supplier inventory
(LG, Solstar, Hisense, Midea, S&P) from the MECHPRO_PRODUCT_LIST.pdf,
transcribed faithfully into the catalogue.

    python manage.py import_product_catalogue

Idempotent: matched on (brand, model_number). Re-running updates existing
rows rather than duplicating them. Does NOT touch or delete the original
8 placeholder/demo products from seed_initial — run
`deactivate_demo_products` separately if you want those hidden once the
real catalogue is confirmed correct.
"""
from django.core.management.base import BaseCommand

from catalogue.models import Product, ProductBrand, ProductCategory

# Generic "what it suits" line per category — presentation copy only,
# no fabricated technical specs. Edit anytime in the admin.
IDEAL_FOR = {
    "Wall Mounted": "Bedrooms, offices and small retail spaces.",
    "Cassette": "Open-plan interiors needing even, ceiling-level airflow.",
    "Ducted": "Concealed installations where only grilles should be visible.",
    "Floor Standing": "Halls, showrooms and spaces without ceiling access.",
    "Portable": "Temporary cooling or spaces where a fixed unit isn't practical.",
    "Multi Split Systems": "Multiple rooms run off a single outdoor condenser.",
    "Ventilation Fans": "Kitchens, bathrooms, basements and duct-run ventilation.",
}

# Each section shares a brand, category and (usually) refrigerant.
# items: (capacity_label, capacity_btu_digits, model_number, feature_list)
SECTIONS = [
    # ---------------- LG ----------------
    dict(brand="LG", category="Wall Mounted", product="LG DualCool Inverter Wall Mounted",
         refrigerant="R410A", items=[
             ("12,000 BTU (1.0 TR)", "12,000", "S4-Q12JA3QB",
              ["Dual Inverter Compressor", "Cooling Only", "Low Noise Operation", "Energy Efficient", "Auto Restart", "Wall Mounted"]),
             ("18,000 BTU (1.5 TR)", "18,000", "S4-Q18KL3QE",
              ["Dual Inverter Compressor", "Cooling Only", "Energy Efficient", "Low Noise", "Auto Restart", "Wall Mounted"]),
             ("24,000 BTU (2.0 TR)", "24,000", "S4-Q24K23QE",
              ["Dual Inverter Compressor", "Cooling Only", "Energy Efficient", "High Performance Cooling", "Wall Mounted"]),
         ]),
    dict(brand="LG", category="Cassette", product="LG 4-Way Cassette",
         refrigerant="R410A", items=[
             ("18,000 BTU (1.5 TR)", "18,000", "ATNQ22GPLA4",
              ["4-Way Air Distribution", "Cooling Only", "Ceiling Cassette", "Quiet Operation"]),
             ("24,000 BTU (2.0 TR)", "24,000", "ATNQ30GPLA4",
              ["4-Way Air Distribution", "Cooling Only", "Wide Airflow Coverage", "Ceiling Mounted"]),
             ("36,000 BTU (3.0 TR)", "36,000", "ATNQ40GNLA4",
              ["4-Way Air Distribution", "Cooling Only", "Commercial Application", "Ceiling Mounted"]),
         ]),
    dict(brand="LG", category="Ducted", product="LG Ceiling Concealed Duct",
         refrigerant="R410A", items=[
             ("18,000 BTU (1.5 TR)", "18,000", "ABNW18GM1S1",
              ["Inverter", "Heating & Cooling", "Concealed Installation", "High Static Pressure"]),
             ("24,000 BTU (2.0 TR)", "24,000", "ABNW24GM1S1",
              ["Inverter", "Heating & Cooling", "Concealed Installation", "Commercial HVAC"]),
             ("36,000 BTU (3.0 TR)", "36,000", "ABNW36GM2S1",
              ["Inverter", "Heating & Cooling", "High Static Pressure", "Commercial HVAC"]),
             ("48,000 BTU (4.0 TR)", "48,000", "ABNW48LM3S1",
              ["Inverter", "Heating & Cooling", "Concealed Duct", "Energy Efficient"]),
             ("54,000 BTU (4.5 TR)", "54,000", "ABNW54LM3S1",
              ["Inverter", "Heating & Cooling", "High Capacity", "Concealed Installation"]),
         ]),
    dict(brand="LG", category="Floor Standing", product="LG Floor Standing",
         refrigerant="R410A", items=[
             ("48,000 BTU (4.0 TR)", "48,000", "APNQ50GT3E4",
              ["Floor Standing", "Cooling Only", "High Air Throw", "Commercial Application"]),
         ]),
    dict(brand="LG", category="Wall Mounted", product="LG DualCool Inverter (Heating & Cooling)",
         refrigerant="R410A", items=[
             ("12,000 BTU (1.0 TR)", "12,000", "M13AJH",
              ["Dual Inverter Compressor", "Heating & Cooling", "Energy Efficient", "Low Noise", "Wall Mounted"]),
             ("18,000 BTU (1.5 TR)", "18,000", "M19AKH",
              ["Dual Inverter Compressor", "Heating & Cooling", "Fast Cooling & Heating", "Wall Mounted"]),
             ("24,000 BTU (2.0 TR)", "24,000", "M24AKH",
              ["Dual Inverter Compressor", "Heating & Cooling", "Energy Efficient", "Wall Mounted"]),
         ]),
    dict(brand="LG", category="Wall Mounted", product="LG Artcool Mirror",
         refrigerant="R410A", items=[
             ("12,000 BTU (1.0 TR)", "12,000", "S4-Q12IARTB.ACWGEAF",
              ["Dual Inverter", "Mirror Glass Finish", "Cooling Only", "Wi-Fi Ready", "Premium Design"]),
             ("18,000 BTU (1.5 TR)", "18,000", "S4-Q18KLRTE.ACWGEAF",
              ["Dual Inverter", "Mirror Glass Finish", "Cooling Only", "Wi-Fi Ready"]),
             ("24,000 BTU (2.0 TR)", "24,000", "S4-Q24K2RTD.ACWGEAF",
              ["Dual Inverter", "Mirror Glass Finish", "Cooling Only", "Wi-Fi Ready"]),
         ]),

    # ---------------- SOLSTAR ----------------
    dict(brand="Solstar", category="Wall Mounted", product="Solstar Wall Mounted AC",
         refrigerant="R410A", items=[
             ("9,000 BTU (0.75 TR)", "9,000", "ASI/ASU 09TGASS",
              ["Non-Inverter", "Cooling Only", "Wall Mounted", "Energy Efficient"]),
             ("12,000 BTU (1.0 TR)", "12,000", "ASI/ASU 12TGASS",
              ["Non-Inverter", "Cooling Only", "Wall Mounted"]),
             ("18,000 BTU (1.5 TR)", "18,000", "ASI/ASU 18TGASS",
              ["Non-Inverter", "Cooling Only", "High Cooling Performance"]),
             ("24,000 BTU (2.0 TR)", "24,000", "ASI/ASU 24TGASS",
              ["Non-Inverter", "Cooling Only", "Heavy-Duty Performance"]),
         ]),

    # ---------------- HISENSE ----------------
    dict(brand="Hisense", category="Wall Mounted", product="Hisense Split Air Conditioner (Inverter)",
         refrigerant="", items=[
             ("9,000 BTU (0.75 TR)", "9,000", "AS09UW4SGDTU01",
              ["Inverter Technology", "Cooling & Air Conditioning", "Energy Efficient", "Wall Mounted", "Quiet Operation"]),
             ("18,000 BTU (1.5 TR)", "18,000", "AS18UW4SXATU08",
              ["Inverter Technology", "Cooling & Air Conditioning", "Energy Efficient", "Wall Mounted", "Quiet Operation"]),
         ]),
    dict(brand="Hisense", category="Wall Mounted", product="Hisense Split Air Conditioner (Cooling Only)",
         refrigerant="R419A", items=[
             ("12,000 BTU (1.0 TR)", "12,000", "AS12CR4SVETG07ONE",
              ["Cooling Only", "3m Pipe Included", "TG Basic Panel", "Wall Mounted"]),
             ("18,000 BTU (1.5 TR)", "18,000", "AS-18CR4SXATG0",
              ["Cooling Only", "3m Pipe Included", "TG Basic Panel", "Wall Mounted"]),
             ("22,000 BTU", "22,000", "AS-22CR4SBBTG01",
              ["Cooling Only", "3m Pipe Included", "TG Basic Panel", "Wall Mounted"]),
             ("24,000 BTU (2.0 TR)", "24,000", "AS-24UF4SBBTU00A",
              ["Cooling Only", "Wall Mounted", "High Capacity"]),
         ]),
    dict(brand="Hisense", category="Wall Mounted", product="Hisense Split Air Conditioner (Cooling & Heating)",
         refrigerant="R419A", items=[
             ("12,000 BTU (1.0 TR)", "12,000", "12UW4SGETU00",
              ["Cooling & Heating", "Inverter Technology", "3m Pipe Included", "TG Basic Panel", "Wall Mounted"]),
         ]),
    dict(brand="Hisense", category="Portable", product="Hisense Portable Air Conditioner",
         refrigerant="", items=[
             ("9,000 BTU (0.75 TR)", "9,000", "AP09CR4RKVS00",
              ["Portable Design", "Cooling", "Compact Installation", "Flexible Room Application"]),
             ("12,000 BTU (1.0 TR)", "12,000", "AP12CR4RKVS00",
              ["Portable Design", "Cooling", "Higher Cooling Capacity", "Flexible Room Application"]),
         ]),
    dict(brand="Hisense", category="Cassette", product="Hisense Cassette Air Conditioner",
         refrigerant="", items=[
             ("12,000 BTU (1.0 TR)", "12,000", "AUC-12HRSAA1 / AUW-12H4SS",
              ["Ceiling Cassette Type", "Indoor & Outdoor Unit", "4-Way Ceiling Installation"]),
             ("18,000 BTU (1.5 TR)", "18,000", "AUC-18HR4SAA1 / AUW-18H4SS",
              ["Ceiling Cassette Type", "Indoor & Outdoor Unit", "4-Way Ceiling Installation"]),
             ("24,000 BTU (2.0 TR)", "24,000", "AUC-24HR4SJA / AUW-24H4SF",
              ["Ceiling Cassette Type", "Indoor & Outdoor Unit", "4-Way Ceiling Installation"]),
             ("36,000 BTU (3.0 TR)", "36,000", "AUC-36HR4SKA / AUW-36H4SD",
              ["Ceiling Cassette Type", "Indoor & Outdoor Unit", "4-Way Ceiling Installation"]),
         ]),
    dict(brand="Hisense", category="Floor Standing", product="Hisense Floor Standing AC (Cooling Only)",
         refrigerant="", items=[
             ("18,000 BTU (1.5 TR)", "18,000", "AUF-18CR4SCPA3 / AUW-18C4SM3",
              ["Cooling Only", "Floor Standing Design", "Indoor & Outdoor Unit", "High Airflow", "Large Space Cooling"]),
             ("24,000 BTU (2.0 TR)", "24,000", "AUF-24CR4SJCPA3 / AUW-24C4SJ3",
              ["Cooling Only", "Floor Standing Design", "Indoor & Outdoor Unit", "High Airflow", "Large Space Cooling"]),
             ("48,000 BTU (4.0 TR)", "48,000", "AUF-48HR4SMPA / AUW-48HT6SD",
              ["Cooling Only", "Non-Inverter", "Floor Standing Design", "Indoor & Outdoor Unit", "High Capacity", "Large Space Cooling"]),
         ]),
    dict(brand="Hisense", category="Floor Standing", product="Hisense Floor Standing AC (Inverter)",
         refrigerant="", items=[
             ("18,000 BTU (1.5 TR)", "18,000", "AUF18TR4SMCPE",
              ["Inverter Technology", "Floor Standing Design", "Energy Efficient", "Large Space Cooling"]),
             ("24,000 BTU (2.0 TR)", "24,000", "AUF24TR4SJCPE",
              ["Inverter Technology", "Floor Standing Design", "Energy Efficient", "Large Space Cooling"]),
         ]),
    dict(brand="Hisense", category="Floor Standing", product="Hisense Floor Standing AC (Heating & Cooling)",
         refrigerant="", items=[
             ("36,000 BTU (3.0 TR)", "36,000", "AUF-36HR4SCPA / AUW-36HT4SD",
              ["Heating & Cooling", "Floor Standing Design", "Indoor & Outdoor Unit", "High Capacity", "Large Space Application"]),
         ]),
    dict(brand="Hisense", category="Ducted", product="Hisense Ducted AC (Non-Inverter)",
         refrigerant="", items=[
             ("12,000 BTU (1.0 TR)", "12,000", "AUD12HX4SVNL",
              ["Non-Inverter Technology", "Ducted Type", "Concealed Installation", "Centralized Air Distribution"]),
             ("18,000 BTU (1.5 TR)", "18,000", "AUD18HX4SSNL1",
              ["Non-Inverter Technology", "Ducted Type", "Concealed Installation", "Centralized Air Distribution"]),
             ("24,000 BTU (2.0 TR)", "24,000", "AUD24HX4SFLH1",
              ["Non-Inverter Technology", "Ducted Type", "Concealed Installation", "Centralized Air Distribution"]),
         ]),

    # ---------------- MIDEA ----------------
    dict(brand="Midea", category="Wall Mounted", product="Midea Breezeless E Inverter AC",
         refrigerant="R32", items=[
             ("12,000 BTU (1.0 TR)", "12,000", "MSCB1BU12HRFN8-QRD1GW",
              ["Inverter Technology", "Heating & Cooling", "Breezeless E", "Wall Mounted"]),
             ("18,000 BTU (1.5 TR)", "18,000", "MSCB1CU18HRFN8-QRD1GW",
              ["Inverter Technology", "Heating & Cooling", "Breezeless E", "Wall Mounted"]),
             ("24,000 BTU (2.0 TR)", "24,000", "MSCB1DU24HRFN8-QRD1GW",
              ["Inverter Technology", "Heating & Cooling", "Breezeless E", "Wall Mounted"]),
         ]),
    dict(brand="Midea", category="Wall Mounted", product="Midea Unicool Inverter AC",
         refrigerant="R32", items=[
             ("12,000 BTU (1.0 TR)", "12,000", "MSGP11B12CRDN8-QCO",
              ["Inverter Technology", "Heating & Cooling", "Unicool Series", "Wall Mounted"]),
             ("18,000 BTU (1.5 TR)", "18,000", "MSGP11C18CRFN8-QCO",
              ["Inverter Technology", "Heating & Cooling", "Unicool Series", "Wall Mounted"]),
             ("24,000 BTU (2.0 TR)", "24,000", "MSGP11D21CRFN8-QCO",
              ["Inverter Technology", "Heating & Cooling", "Unicool Series", "Wall Mounted"]),
         ]),
    dict(brand="Midea", category="Ducted", product="Midea ERP Ducted Inverter AC",
         refrigerant="R32", items=[
             ("12,000 BTU (1.0 TR)", "12,000", "MTJ-12HWFNXQRD1W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Ducted Type", "Concealed Installation"]),
             ("18,000 BTU (1.5 TR)", "18,000", "MTJ-18HWFNXQRD1W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Ducted Type", "Concealed Installation"]),
             ("24,000 BTU (2.0 TR)", "24,000", "MTJ-24HWFNXQRD1W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Ducted Type", "Concealed Installation"]),
             ("36,000 BTU (3.0 TR)", "36,000", "MTJ-36HWFNXQRD0W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Ducted Type", "Concealed Installation"]),
             ("48,000 BTU (4.0 TR)", "48,000", "MTJ-48HWFNXQRD0W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Ducted Type", "Concealed Installation"]),
             ("55,000 BTU", "55,000", "MTJ-55HWFNXQRD0W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Ducted Type", "Concealed Installation"]),
         ]),
    dict(brand="Midea", category="Cassette", product="Midea ERP Cassette Inverter AC",
         refrigerant="R32", items=[
             ("12,000 BTU (1.0 TR)", "12,000", "MCA4U-12HRFNXQRD1W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Ceiling Cassette Type", "Concealed Ceiling Installation"]),
             ("18,000 BTU (1.5 TR)", "18,000", "MCA4U-18HRFNXQRD1W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Ceiling Cassette Type", "Concealed Ceiling Installation"]),
             ("24,000 BTU (2.0 TR)", "24,000", "MCD1-24HRFNXQRD0W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Ceiling Cassette Type", "Concealed Ceiling Installation"]),
             ("36,000 BTU (3.0 TR)", "36,000", "MCD1-36HRFN8-QRD0W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Ceiling Cassette Type", "Concealed Ceiling Installation"]),
             ("48,000 BTU (4.0 TR)", "48,000", "MCD1-48HRFNXQRD0W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Ceiling Cassette Type", "Concealed Ceiling Installation"]),
             ("55,000 BTU", "55,000", "MCD1-55HRFNXQRD0W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Ceiling Cassette Type", "Concealed Ceiling Installation"]),
         ]),
    dict(brand="Midea", category="Floor Standing", product="Midea Floor Standing Inverter AC",
         refrigerant="R410A", items=[
             ("24,000 BTU (2.0 TR)", "24,000", "MFPA24HRDN1-QC0W",
              ["Inverter Technology", "Heating & Cooling", "Floor Standing Type", "High Capacity"]),
             ("36,000 BTU (3.0 TR)", "36,000", "MFTM36HRDN1-QC2W",
              ["Inverter Technology", "Heating & Cooling", "Floor Standing Type", "High Capacity"]),
             ("48,000 BTU (4.0 TR)", "48,000", "MM-48HDN1-PC0",
              ["Inverter Technology", "Heating & Cooling", "Floor Standing Type", "High Capacity"]),
             ("60,000 BTU (5.0 TR)", "60,000", "MFTGD60HRDN1-RB9",
              ["Inverter Technology", "Heating & Cooling", "Floor Standing Type", "High Capacity"]),
         ]),
    dict(brand="Midea", category="Portable", product="Midea Portable Inverter AC",
         refrigerant="R410A", items=[
             ("12,000 BTU (1.0 TR)", "12,000", "MPPX12CRN7-QB6",
              ["Inverter Technology", "Heating & Cooling", "Portable Design", "Flexible Installation"]),
         ]),
    dict(brand="Midea", category="Multi Split Systems", product="Midea Multi-Split Outdoor Unit",
         refrigerant="R32", items=[
             ("36,000 BTU (3.0 TR)", "36,000", "M4OB36HFN8-Q",
              ["Inverter Technology", "Heating & Cooling", "Multi-Split System", "Outdoor Unit"]),
             ("42,000 BTU (3.5 TR)", "42,000", "M50E42HFN8-Q",
              ["Inverter Technology", "Heating & Cooling", "Multi-Split System", "Outdoor Unit"]),
         ]),
    dict(brand="Midea", category="Wall Mounted", product="Midea Wall Mounted Multi-Split Indoor Unit",
         refrigerant="R32", items=[
             ("9,000 BTU (0.75 TR)", "9,000", "MSAGAU-09HRFNXQRD0GW",
              ["Inverter Technology", "Heating & Cooling", "Multi-Split Compatible", "Wall Mounted"]),
             ("12,000 BTU (1.0 TR)", "12,000", "MSAGBU-12HRFNXQRD0GW",
              ["Inverter Technology", "Heating & Cooling", "Multi-Split Compatible", "Wall Mounted"]),
             ("18,000 BTU (1.5 TR)", "18,000", "MSAGCU-18HRFNXQRD0GW",
              ["Inverter Technology", "Heating & Cooling", "Multi-Split Compatible", "Wall Mounted"]),
             ("24,000 BTU (2.0 TR)", "24,000", "MSAGDU-24HRFNXQRD0GW",
              ["Inverter Technology", "Heating & Cooling", "Multi-Split Compatible", "Wall Mounted"]),
         ]),
    dict(brand="Midea", category="Ducted", product="Midea Ducted Multi-Split Indoor Unit",
         refrigerant="R32", items=[
             ("9,000 BTU (0.75 TR)", "9,000", "MTJ-09HWFNXQRD1W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Multi-Split Compatible", "Ducted Type"]),
             ("12,000 BTU (1.0 TR)", "12,000", "MTJ-12HWFNXQRD1W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Multi-Split Compatible", "Ducted Type"]),
             ("18,000 BTU (1.5 TR)", "18,000", "MTJ-18HWFNXQRD1W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Multi-Split Compatible", "Ducted Type"]),
             ("24,000 BTU (2.0 TR)", "24,000", "MTJ-24HWFNXQRD1W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Multi-Split Compatible", "Ducted Type"]),
         ]),
    dict(brand="Midea", category="Cassette", product="Midea Cassette Multi-Split Indoor Unit",
         refrigerant="R32", items=[
             ("9,000 BTU (0.75 TR)", "9,000", "MCA4U-09HRFNXQRD1W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Multi-Split Compatible", "Ceiling Cassette Type"]),
             ("12,000 BTU (1.0 TR)", "12,000", "MCA4U-12HRFNXQRD1W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Multi-Split Compatible", "Ceiling Cassette Type"]),
             ("18,000 BTU (1.5 TR)", "18,000", "MCA4U-18HRFNXQRD1W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Multi-Split Compatible", "Ceiling Cassette Type"]),
             ("24,000 BTU (2.0 TR)", "24,000", "MCA4U-24HRFNXQRD0W(GA)",
              ["Inverter Technology", "Heating & Cooling", "Multi-Split Compatible", "Ceiling Cassette Type"]),
         ]),
]

# S&P fans: no BTU/refrigerant. size goes in `coverage`, full spec text in
# `features`. (product, category always "Ventilation Fans", brand "S&P")
FAN_SECTIONS = [
    ("S&P Jetline Centrifugal In-Line Fan", [
        ("125 mm", "JETLINE-125", "Centrifugal In-Line Fan, External Use, 220-240V, 50/60Hz, N8"),
        ("150 mm", "JETLINE-150", "Centrifugal In-Line Fan, External Use, 220-240V, 50/60Hz, N8"),
        ("200 mm", "JETLINE-200", "Centrifugal In-Line Fan, External Use, 220-240V, 50/60Hz, N8"),
        ("250 mm", "JETLINE-250", "Centrifugal In-Line Fan, External Use, 220-240V, 50/60Hz, N8"),
        ("315 mm", "JETLINE-315", "Centrifugal In-Line Fan, External Use, 220-240V, 50Hz, N8"),
    ]),
    ("S&P TD In-Line Mixed Flow Duct Fan", [
        ("250/100", "TD-250/100", "Mixed Flow Duct Fan, 220-240V, 50Hz, Single Phase, RE"),
        ("350/125", "TD-350/125", "Mixed Flow Duct Fan, 220-240V, 50Hz, Single Phase, RE"),
        ("500/150", "TD-500/150 3V", "Mixed Flow Duct Fan, 220-240V, 50/60Hz, N8, 3V"),
        ("800/200", "TD-800/200 3V", "Mixed Flow Duct Fan, 220-240V, 50/60Hz, N8, 3V"),
        ("1300/250", "TD-1300/250N 3V", "Mixed Flow Duct Fan, 220-240V, 50/60Hz, N8, 3V"),
        ("2000/315", "TD-2000/315N 3V", "Mixed Flow Duct Fan, 220-240V, 50/60Hz, N8, 3V"),
        ("4000/355", "TD-4000/355", "Mixed Flow Duct Fan, 230V, 50/60Hz, N8"),
        ("4000/355 (Triple Phase)", "TD-4000/355 TRIF", "Mixed Flow Duct Fan, 400/440V, 50/60Hz, N8, Triple Phase"),
        ("6000/400", "TD-6000/400", "Mixed Flow Duct Fan, 230V, 50/60Hz, N8"),
        ("6000/400 (Triple Phase)", "TD-6000/400 TRIF", "Mixed Flow Duct Fan, 400V, 50Hz, N8, Triple Phase"),
    ]),
    ("S&P VENT Centrifugal In-Line Fan", [
        ("100 mm", "VENT-100NK", "Centrifugal In-Line Fan, 220-240V, 50/60Hz, R8, In-Line Duct Installation"),
        ("125 mm", "VENT-125NK", "Centrifugal In-Line Fan, 220-240V, 50/60Hz, R8, In-Line Duct Installation"),
        ("150 mm", "VENT-150NK", "Centrifugal In-Line Fan, 220-240V, 50/60Hz, N8, In-Line Duct Installation"),
        ("200 mm", "VENT-200NK", "Centrifugal In-Line Fan, 220-240V, 50/60Hz, N8, In-Line Duct Installation"),
        ("250 mm", "VENT-250NK", "Centrifugal In-Line Fan, 220-240V, 50/60Hz, N8, In-Line Duct Installation"),
        ("315 mm", "VENT-315NK", "Centrifugal In-Line Fan, 220-240V, 50/60Hz, N8, In-Line Duct Installation"),
        ("355 mm", "VENT-355 L", "Centrifugal In-Line Fan, 230V, 50/60Hz, NX, In-Line Duct Installation"),
        ("400 mm", "VENT-400 L", "Centrifugal In-Line Fan, 230V, 50/60Hz, NX, In-Line Duct Installation"),
    ]),
    ("S&P TD Ultra-Quiet Mixed Flow Duct Fan (Timer)", [
        ("160/100", "TD-160/100 N T SILENT", "Ultra-Quiet Operation, Timer Function, Mixed Flow Duct Fan, 220-240V, 50Hz, RE"),
        ("160/100 (Kit)", "TD-160/100 N 'KIT'", "Ultra-Quiet Operation, Kit Version, Mixed Flow Duct Fan, 220-240V, 50Hz, RE"),
        ("250/100", "TD-250/100 SILENT T", "Ultra-Quiet Operation, Timer Function, Mixed Flow Duct Fan, 230-240V, 50/60Hz, RE"),
        ("350/125", "TD-350/125 SILENT T", "Ultra-Quiet Operation, Timer Function, Mixed Flow Duct Fan, 230-240V, 50/60Hz, RE"),
        ("500/150-160", "TD-500/150-160 SILENT T 3V", "Ultra-Quiet Operation, Timer Function, Mixed Flow Duct Fan, 220-240V, 50/60Hz, N8, 3V"),
        ("800/200", "TD-800/200 SILENT T 3V", "Ultra-Quiet Operation, Timer Function, Mixed Flow Duct Fan, 220-240V, 50/60Hz, N8, 3V"),
        ("1000/200", "TD-1000/200 SILENT T 3V", "Ultra-Quiet Operation, Timer Function, Mixed Flow Duct Fan, 220-240V, 50/60Hz, N8, 3V"),
    ]),
    ("S&P TD Ultra-Quiet Mixed Flow Duct Fan", [
        ("1300/250", "TD-1300/250 SILENT 3V", "Ultra-Quiet Operation, Mixed Flow Duct Fan, 220-240V, 50/60Hz, N8, 3V"),
        ("2000/315", "TD-2000/315 SILENT 3V", "Ultra-Quiet Operation, Mixed Flow Duct Fan, 220-240V, 50/60Hz, N8, 3V"),
    ]),
    ("S&P Wall & Window Extract Fan", [
        ("230", "HV-230 A E", "Wall & Window Extract Fan, 230-240V, 50Hz, RE"),
        ("300", "HV-300 A E", "Wall & Window Extract Fan, 230-240V, 50Hz, VE"),
    ]),
    ("S&P Bathroom Extract Fan", [
        ("100 mm", "DECOR-100 C DESIGN", "Bathroom Extract Fan, 220-240V, 50Hz, RE, Compact Design"),
        ("200 mm", "DECOR-200 C DESIGN", "Bathroom Extract Fan, 220-240V, 50Hz, RE, Compact Design"),
        ("300 mm", "DECOR-300 C DESIGN", "Bathroom Extract Fan, 220-240V, 50Hz, RE, Compact Design"),
    ]),
    ("S&P Silent Bathroom Extract Fan (Timer)", [
        ("100 mm", "SILENT-100 CRZ", "Low-Noise Operation, Timer Function, Bathroom Extract Fan, 220-240V, 50Hz, RE"),
        ("200 mm", "SILENT-200 CRZ", "Low-Noise Operation, Timer Function, Bathroom Extract Fan, 220-240V, 50Hz, RE"),
        ("300 mm", "SILENT-300 CRZ", "Low-Noise Operation, Timer Function, Bathroom Extract Fan, 220-240V, 50Hz, RE"),
    ]),
    ("S&P Silent Dual Bathroom Extract Fan (PIR/Humidity)", [
        ("100 mm", "SILENT DUAL 100", "PIR Sensor, Humidity Control, Timer Function, Bathroom Extract Fan, 220-240V, 50Hz, RE"),
        ("200 mm", "SILENT DUAL 200", "PIR Sensor, Humidity Control, Timer Function, Bathroom Extract Fan, 220-240V, 50Hz, RE"),
        ("300 mm", "SILENT DUAL 300", "PIR Sensor, Humidity Control, Timer Function, Bathroom Extract Fan, 220-240V, 50Hz, RE"),
    ]),
    ("S&P Acoustic Cabinet Fan", [
        ("315 mm", "CAB-315 RE", "Acoustic Cabinet Fan, 230V, 50/60Hz, VE, Sound-Reduced Cabinet Design"),
        ("355 mm", "CAB-355 RE", "Acoustic Cabinet Fan, 230V, 50Hz, N6, Sound-Reduced Cabinet Design"),
        ("400 mm", "CAB-400 RE", "Acoustic Cabinet Fan, 230V, 50Hz, N6, Sound-Reduced Cabinet Design"),
    ]),
    ("S&P Rectangular Duct Fan (Single Phase)", [
        ("270/270N", "CVB-270/270N T", "Rectangular Duct Fan, 245W, 230V, 50Hz, N6, Export Version"),
        ("320/320N", "CVB-320/320N", "Rectangular Duct Fan, 550W, 230V, 50Hz, VE, Export Version"),
        ("320/240N", "CVB-320/240N T", "Rectangular Duct Fan, 736W, 230V, 50Hz, N6, Export Version"),
        ("320/240N (400V)", "CVT-320/240N T", "Rectangular Duct Fan, 1100W, 230/400V, 50Hz, N6, Export Version"),
        ("380/380N", "CVT-380/380N T", "Rectangular Duct Fan, 2200W, 230/400V, 50Hz, NX, Export Version"),
    ]),
    ("S&P Rectangular Duct Fan (Triple Phase)", [
        ("180", "IRB/2-180", "Performance 190/60 m3/h/Pa, 230V, 50/60Hz, N8, Triple Phase"),
        ("200A", "IRB/2-200A", "Performance 225/88 m3/h/Pa, 230V, 50/60Hz, N8, Triple Phase"),
        ("200B", "IRB/2-200B", "Performance 250/84 m3/h/Pa, 230V, 50/60Hz, N8, Triple Phase"),
        ("225", "IRB/4-225", "Performance 315/90 m3/h/Pa, 230V, 50/60Hz, N8, Triple Phase"),
        ("315A", "IRB/4-315A", "Performance 355/100 m3/h/Pa, 230V, 50Hz, N8, Triple Phase"),
        ("315B", "IRB/4-315B", "Performance 400/140 m3/h/Pa, 230V, 50Hz, N8, Triple Phase"),
        ("355 (IRB/4)", "IRB/4-355", "Performance 450/125 m3/h/Pa, 230V, 50Hz, N8, Triple Phase"),
        ("315 (IRB/6)", "IRB/6-315", "Performance 500/140 m3/h/Pa, 230V, 50Hz, N8, Triple Phase"),
        ("355 (IRB/6)", "IRB/6-355", "Performance 560/125 m3/h/Pa, 230V, 50Hz, N8, Triple Phase"),
        ("400 (IRB/6)", "IRB/6-400", "Performance 560/180 m3/h/Pa, 230V, 50Hz, N8, Triple Phase"),
        ("450 (IRB/6)", "IRB/6-450", "Performance 630/200 m3/h/Pa, 230V, 50Hz, N8, Triple Phase"),
        ("315A (IRT/4)", "IRT/4-315A", "Performance 355/100 m3/h/Pa, 230/400V, 50/60Hz, N8, Triple Phase"),
        ("315B (IRT/4)", "IRT/4-315B", "Performance 400/140 m3/h/Pa, 230/400V, 50/60Hz, N8, Triple Phase"),
        ("355 (IRT/4)", "IRT/4-355", "Performance 450/125 m3/h/Pa, 230/400V, 50Hz, N8, Triple Phase"),
        ("400A (IRT/4)", "IRT/4-400A", "Performance 500/140 m3/h/Pa, 230/400V, 50Hz, N8, Triple Phase"),
        ("400B (IRT/4)", "IRT/4-400B", "Performance 560/140 m3/h/Pa, 230/400V, 50Hz, N8, Triple Phase"),
        ("450 (IRT/4)", "IRT/4-450", "Performance 560/160 m3/h/Pa, 230/400V, 50Hz, N8, Triple Phase"),
        ("355 (IRT/6)", "IRT/6-355", "Performance 560/125 m3/h/Pa, 230/400V, 50Hz, N8, Triple Phase"),
        ("400 (IRT/6)", "IRT/6-400", "Performance 560/180 m3/h/Pa, 230/400V, 50Hz, N8, Triple Phase"),
        ("450 (IRT/6)", "IRT/6-450", "Performance 630/200 m3/h/Pa, 230/400V, 50Hz, N8, Triple Phase"),
    ]),
]


class Command(BaseCommand):
    help = "Import the real MECHPRO supplier catalogue (LG, Solstar, Hisense, Midea, S&P)."

    def handle(self, *args, **options):
        created, updated = 0, 0

        def upsert(brand_name, category_name, name, model, capacity_btu,
                   refrigerant, features, coverage=""):
            nonlocal created, updated
            brand, _ = ProductBrand.objects.get_or_create(name=brand_name)
            category, _ = ProductCategory.objects.get_or_create(name=category_name)
            obj, was_created = Product.objects.update_or_create(
                brand=brand, model_number=model,
                defaults=dict(
                    name=name, category=category,
                    capacity_btu=capacity_btu, coverage=coverage,
                    refrigerant=refrigerant, features=features,
                    ideal_for=IDEAL_FOR.get(category_name, ""),
                    is_active=True,
                ),
            )
            if was_created:
                created += 1
            else:
                updated += 1

        # ---- air conditioners ----
        for section in SECTIONS:
            for capacity_label, capacity_btu, model, extra_features in section["items"]:
                name = f'{section["product"]} {capacity_label}'
                features = list(extra_features)
                upsert(section["brand"], section["category"], name, model,
                       capacity_btu, section["refrigerant"], features)

        # ---- S&P fans ----
        for product_name, items in FAN_SECTIONS:
            for size_label, model, spec_text in items:
                name = f"{product_name} {size_label}"
                features = [f.strip() for f in spec_text.split(",") if f.strip()]
                upsert("S&P", "Ventilation Fans", name, model,
                       "", "", features, coverage=size_label)

        self.stdout.write(self.style.SUCCESS(
            f"Catalogue import complete: {created} products created, {updated} updated."))
        self.stdout.write(
            "NOTE: several Hisense entries list refrigerant 'R419A' exactly as "
            "printed in the supplier PDF. That is not a standard refrigerant code "
            "(R410A and R32 are standard) and is very likely a typo in the source "
            "sheet. Verify with Hisense/your supplier before publishing those "
            "products, then correct in the admin if needed.")
        self.stdout.write(
            "NOTE: this import did not touch the original 8 demo products from "
            "seed_initial. Run `python manage.py deactivate_demo_products` if you "
            "want those hidden now that the real catalogue is loaded.")
