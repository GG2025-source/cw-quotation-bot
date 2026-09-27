
import pathlib, datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

def generate_quotation(data: dict):
    # 模擬你 templates/quotation_template.html 嘅邏輯
    out_dir = pathlib.Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    q_no = f"QU-{datetime.datetime.now():%Y%m%d%H%M}"
    pdf_path = out_dir / f"{q_no}_{data['client']}.pdf"

    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, 280*mm, "CW ENGINEERING SERVICES LTD.")
    c.setFont("Helvetica", 10)
    c.drawString(20*mm, 270*mm, f"Quotation No.: {q_no}")
    c.drawString(20*mm, 265*mm, f"Date: {datetime.datetime.now():%Y-%m-%d}")
    c.drawString(20*mm, 255*mm, f"To: {data['client']}")
    c.drawString(20*mm, 250*mm, f"Attention: {data['attention']}")
    c.drawString(20*mm, 245*mm, f"Project: {data['project']}")
    c.drawString(20*mm, 235*mm, f"Email: {data['email']}")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(20*mm, 220*mm, f"Proposed Fee: HKD {data['total']:,}")
    c.setFont("Helvetica", 9)
    c.drawString(20*mm, 30*mm, f"Valid 30 days | {q_no}")
    # 印章/簽名位置預留
    c.rect(150*mm, 40*mm, 40*mm, 30*mm) 
    c.drawString(152*mm, 55*mm, "[STAMP]")
    c.showPage()
    c.save()
    return str(pdf_path), q_no
