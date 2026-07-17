from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from datetime import datetime


# Litir frá Kaupfjelag Nærsveitamanna
KN_APPELSÍNUGULT = colors.HexColor('#D97525')
KN_BLÁ = colors.HexColor('#2E3192')
KN_HVÍTT = colors.HexColor('#FFFFFF')
KN_SVART = colors.HexColor('#000000')


def create_pdf_header(canvas, doc, titill):
    """Búa til haus á PDF skýrslu"""
    canvas.saveState()
    
    # Bakgrunnur
    canvas.setFillColor(KN_BLÁ)
    canvas.rect(0, A4[1] - 3*cm, A4[0], 3*cm, fill=1)
    
    # Titill
    canvas.setFillColor(KN_HVÍTT)
    canvas.setFont('Helvetica-Bold', 18)
    canvas.drawString(2*cm, A4[1] - 2*cm, titill)
    
    # Dagsetning
    canvas.setFont('Helvetica', 10)
    canvas.drawString(2*cm, A4[1] - 2.5*cm, f"Dagsetning: {datetime.now().strftime('%d.%m.%Y')}")
    
    canvas.restoreState()


def generate_pdf(titill, gogn, dalkur_heiti, skra_nafn):
    """Almenn aðferð til að búa til PDF skýrslu"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=KN_BLÁ,
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Titill
    elements.append(Paragraph(titill, title_style))
    elements.append(Spacer(1, 0.5*cm))
    
    # Tafla
    if gogn:
        table_data = [dalkur_heiti]
        table_data.extend(gogn)
        
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            # Haus
            ('BACKGROUND', (0, 0), (-1, 0), KN_APPELSÍNUGULT),
            ('TEXTCOLOR', (0, 0), (-1, 0), KN_SVART),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body
            ('BACKGROUND', (0, 1), (-1, -1), KN_HVÍTT),
            ('TEXTCOLOR', (0, 1), (-1, -1), KN_SVART),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        elements.append(table)
    else:
        elements.append(Paragraph("Engin gögn til að sýna", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    # Sækja PDF
    buffer.seek(0)
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{skra_nafn}"'
    
    return response


def generate_starfsmann_pdf(starfsmenn):
    """PDF skýrsla fyrir starfsmenn"""
    titill = "Starfsmannaskrá"
    dalkur_heiti = ['Starfsmannanúmer', 'Nafn', 'Kennitala', 'Símanúmer', 'Staða']
    
    gogn = []
    for s in starfsmenn:
        gogn.append([
            s.starfsmannanumer,
            s.notandi.fullt_nafn,
            s.kennitala,
            s.simanumer,
            'Virkur' if s.er_virkur else 'Óvirkur'
        ])
    
    return generate_pdf(titill, gogn, dalkur_heiti, 'starfsmannaskra.pdf')


def generate_maeting_pdf(maetingar):
    """PDF skýrsla fyrir mætingar"""
    titill = "Mætingaskrá"
    dalkur_heiti = ['Dagsetning', 'Starfsmaður', 'Mætingartími', 'Brottfarartími', 'Staða']
    
    gogn = []
    for m in maetingar:
        gogn.append([
            str(m.dagsetning),
            m.starfsmadur.notandi.fullt_nafn,
            m.moettartimi.strftime('%H:%M') if m.moettartimi else '-',
            m.brottfararstimi.strftime('%H:%M') if m.brottfararstimi else '-',
            m.get_status_display()
        ])
    
    return generate_pdf(titill, gogn, dalkur_heiti, 'maetingaskra.pdf')


def generate_vidskiptavin_pdf(vidskiptavinir):
    """PDF skýrsla fyrir viðskiptavini"""
    titill = "Viðskiptavinaskrá"
    dalkur_heiti = ['Customer ID', 'Nafn', 'Kennitala', 'Símanúmer', 'Skuldastaða']
    
    gogn = []
    for v in vidskiptavinir:
        gogn.append([
            v.customer_id,
            v.nafn,
            v.kennitala,
            v.simanumer,
            f"{v.skuldastada:,.2f} kr."
        ])
    
    return generate_pdf(titill, gogn, dalkur_heiti, 'vidskiptavinaskra.pdf')


def generate_verkefni_pdf(verkefni_list):
    """PDF skýrsla fyrir verkefni"""
    titill = "Verkefnalisti"
    dalkur_heiti = ['Titill', 'Starfsmaður', 'Staða', 'Deadline', 'Framvinda']
    
    gogn = []
    for v in verkefni_list:
        gogn.append([
            v.titill,
            v.starfsmadur.notandi.fullt_nafn if v.starfsmadur else '-',
            v.get_stada_display(),
            v.deadline.strftime('%d.%m.%Y') if v.deadline else '-',
            f"{v.progress_percent}%"
        ])
    
    return generate_pdf(titill, gogn, dalkur_heiti, 'verkefnalisti.pdf')


def generate_reikningur_pdf(reikningar):
    """PDF skýrsla fyrir reikninga"""
    titill = "Reikningalisti"
    dalkur_heiti = ['Reikningsnr.', 'Viðskiptavinur', 'Dagsetning', 'Gjalddagi', 'Fjárhæð', 'Staða']
    
    gogn = []
    for r in reikningar:
        gogn.append([
            r.reikningsnumer,
            r.vidskiptavinur.nafn,
            r.reikningsdagsetning.strftime('%d.%m.%Y'),
            r.gjalddagi.strftime('%d.%m.%Y'),
            f"{r.heildarfjarhaed:,.2f} kr.",
            r.get_stada_display()
        ])
    
    return generate_pdf(titill, gogn, dalkur_heiti, 'reikningalisti.pdf')


def generate_bokhald_pdf(faerslur):
    """PDF skýrsla fyrir bókhaldsfærslur"""
    titill = "Bókhaldsfærslur"
    dalkur_heiti = ['Færslunr.', 'Dagsetning', 'Lýsing', 'Lykill', 'Debet', 'Kredit']
    
    gogn = []
    heildar_debet = 0
    heildar_kredit = 0
    
    for f in faerslur:
        gogn.append([
            f.faerslunumer,
            f.dagsetning.strftime('%d.%m.%Y'),
            f.lysing,
            f"{f.bokhaldslykill.lykilnumer} - {f.bokhaldslykill.heiti}",
            f"{f.debet_fjarhaed:,.2f}" if f.debet_fjarhaed > 0 else '-',
            f"{f.kredit_fjarhaed:,.2f}" if f.kredit_fjarhaed > 0 else '-'
        ])
        heildar_debet += f.debet_fjarhaed
        heildar_kredit += f.kredit_fjarhaed
    
    # Bæta við samtölu
    gogn.append(['', '', '', 'SAMTALS:', f"{heildar_debet:,.2f} kr.", f"{heildar_kredit:,.2f} kr."])
    
    return generate_pdf(titill, gogn, dalkur_heiti, 'bokhaldsferslur.pdf')


def generate_arsreikningur_pdf(ar, tekjur, gjold, eignir, skuldir):
    """Ársreikningur PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Titill
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=KN_BLÁ,
        alignment=1
    )
    elements.append(Paragraph(f"Ársreikningur {ar}", title_style))
    elements.append(Spacer(1, 1*cm))
    
    # Rekstrarreikningur
    elements.append(Paragraph("Rekstrarreikningur", styles['Heading2']))
    rekstrar_data = [
        ['', 'Fjárhæð'],
        ['Tekjur', f"{tekjur:,.2f} kr."],
        ['Gjöld', f"{gjold:,.2f} kr."],
        ['Hagnaður/(Tap)', f"{(tekjur - gjold):,.2f} kr."]
    ]
    
    rekstrar_table = Table(rekstrar_data)
    rekstrar_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), KN_APPELSÍNUGULT),
        ('TEXTCOLOR', (0, 0), (-1, 0), KN_SVART),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(rekstrar_table)
    elements.append(Spacer(1, 1*cm))
    
    # Efnahagsreikningur
    elements.append(Paragraph("Efnahagsreikningur", styles['Heading2']))
    efnahags_data = [
        ['', 'Fjárhæð'],
        ['Eignir', f"{eignir:,.2f} kr."],
        ['Skuldir', f"{skuldir:,.2f} kr."],
        ['Eigið fé', f"{(eignir - skuldir):,.2f} kr."]
    ]
    
    efnahags_table = Table(efnahags_data)
    efnahags_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), KN_APPELSÍNUGULT),
        ('TEXTCOLOR', (0, 0), (-1, 0), KN_SVART),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightblue),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(efnahags_table)
    
    doc.build(elements)
    buffer.seek(0)
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="arsreikningur_{ar}.pdf"'
    
    return response
