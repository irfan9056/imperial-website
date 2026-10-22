"""Generates docs/Imperial-Field-Services-Contractor-Agreement.pdf.

Fill in the COMPANY block below, then run:  python3 docs/build_agreement.py
(needs the `reportlab` package: python3 -m pip install reportlab)
"""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

HERE = Path(__file__).resolve().parent
OUT = HERE / "Imperial-Field-Services-Contractor-Agreement.pdf"
LOGO = HERE.parent / "images" / "logo.png"

# ---- Fill these in before sending the packet out ----------------------------
COMPANY = {
    "name": "Imperial Field Services LLC",
    "short": "Imperial Field Services",
    "address": "______________________________",   # street, city, state ZIP
    "phone": "______________",
    "email": "______________________________",
    "website": "",
    "org_state": "______________",                 # state the LLC is organized in
    "law_state": "______________",                 # governing law / arbitration state
    "venue": "the county and state in which Imperial Field Services LLC maintains its principal office",
    "portal": "Vendor Portal",                     # name of the work-order system vendors log into
}
# ------------------------------------------------------------------------------

NAVY = colors.HexColor("#052E56")
GOLD = colors.HexColor("#BE8F27")
INK = colors.HexColor("#222222")
MUTED = colors.HexColor("#666666")

base = ParagraphStyle("base", fontName="Helvetica", fontSize=10.5, leading=15, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=8)
body = base
head = ParagraphStyle("head", parent=base, fontName="Helvetica-Bold", fontSize=12, leading=16, textColor=NAVY, alignment=TA_CENTER, spaceBefore=10, spaceAfter=10)
sec = ParagraphStyle("sec", parent=base, fontName="Helvetica-Bold", fontSize=10.5, textColor=NAVY, spaceBefore=10, spaceAfter=5, alignment=0, leftIndent=18)
lbl = ParagraphStyle("lbl", parent=base, fontName="Helvetica-Bold", textColor=NAVY, alignment=0, spaceBefore=6)
plain = ParagraphStyle("plain", parent=base, alignment=0)
small = ParagraphStyle("small", parent=base, fontSize=9, leading=12, textColor=MUTED, alignment=0)
hdr_b = ParagraphStyle("hdr_b", parent=base, fontName="Helvetica-Bold", fontSize=11, textColor=NAVY, alignment=0, spaceAfter=1)
hdr = ParagraphStyle("hdr", parent=base, fontSize=10, leading=13, alignment=0, spaceAfter=0)
bullet = ParagraphStyle("bullet", parent=base, alignment=0, leftIndent=36, bulletIndent=18, spaceAfter=4)
sub = ParagraphStyle("sub", parent=base, leftIndent=36, spaceAfter=6)

CO = COMPANY["name"]
SH = COMPANY["short"]
PORTAL = COMPANY["portal"]
L = "_" * 34


def sig_line(label, width=3.2 * inch, lw=1.1 * inch):
    return Table([[Paragraph(label, lbl), ""]], colWidths=[lw, width],
                 style=TableStyle([("LINEBELOW", (1, 0), (1, 0), 0.8, INK), ("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]), hAlign="LEFT")


def sig_date_row():
    t = Table([[Paragraph("Signature:", lbl), "", Paragraph("Date:", lbl), ""]],
              colWidths=[0.9 * inch, 2.6 * inch, 0.6 * inch, 1.8 * inch],
              style=TableStyle([("LINEBELOW", (1, 0), (1, 0), 0.8, INK), ("LINEBELOW", (3, 0), (3, 0), 0.8, INK),
                                ("VALIGN", (0, 0), (-1, -1), "BOTTOM"), ("TOPPADDING", (0, 0), (-1, -1), 16)]), hAlign="LEFT")
    return t


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(GOLD); canvas.setLineWidth(0.6)
    canvas.rect(0.45 * inch, 0.45 * inch, letter[0] - 0.9 * inch, letter[1] - 0.9 * inch)
    canvas.setFont("Helvetica", 8); canvas.setFillColor(MUTED)
    canvas.drawString(0.75 * inch, 0.55 * inch, f"{CO} · Subcontractor Packet")
    canvas.drawRightString(letter[0] - 0.75 * inch, 0.55 * inch, f"Page {doc.page}")
    canvas.restoreState()


story = []

# ---------------- Page 1: header, payment terms, ACH ----------------
contact = [Paragraph(CO.upper(), hdr_b), Paragraph(COMPANY["address"], hdr), Paragraph(COMPANY["phone"], hdr),
           Paragraph(COMPANY["email"], hdr)]
if COMPANY["website"]:
    contact.append(Paragraph(COMPANY["website"], hdr))
logo = Image(str(LOGO), width=1.7 * inch, height=1.7 * inch * 752 / 1148) if LOGO.exists() else ""
story.append(Table([[contact, logo]], colWidths=[4.6 * inch, 2.1 * inch],
                   style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (1, 0), (1, 0), "RIGHT")])))
story.append(Spacer(1, 14))
story.append(Paragraph("PAYMENT TERMS", head))
story.append(Paragraph(
    f"Vendors are paid bi-weekly, within 12 to 14 days after completion and approval of the work order, and payments "
    f"are released every week. After a work order is submitted, processing typically requires 24 to 48 hours. Work orders "
    f"that are submitted but not successfully processed may result in a delay in pay. No invoice is needed; payment details "
    f"can be reviewed in the {PORTAL} under the Reports tab.", body))
story.append(Spacer(1, 6))
story.append(sig_line("Name &amp; Title:", 4.6 * inch))
story.append(sig_date_row())
story.append(Spacer(1, 18))
story.append(Paragraph("AUTHORIZATION AGREEMENT FOR DIRECT DEPOSITS (ACH CREDITS)", head))
story.append(sig_line("Bank Account Name:", 4.2 * inch, 1.7 * inch))
story.append(Spacer(1, 8))
story.append(Paragraph(f"I/We hereby authorize {CO} to initiate credit to my (our): (select one)", plain))
for opt in ["Personal Checking Account", "Personal Savings Account", "Business Checking Account", "Business Savings Account"]:
    story.append(Paragraph(f"<font name='ZapfDingbats'>q</font>&nbsp;&nbsp;{opt}", sub))
story.append(Paragraph(f"<font name='ZapfDingbats'>q</font>&nbsp;&nbsp;Any other: {L}; indicated below, at the depository Financial Institution named below, and to "
                       f"credit or debit the same from such account. I/We acknowledge that the authority will remain in effect until I "
                       f"have (or either of us has) cancelled it in writing and that the origination of ACH transactions to my (our) "
                       f"account must comply with the provisions of U.S. law.", sub))
story.append(Spacer(1, 6))
for line in [f"Financial Institution: {'_' * 44};", f"Address on your bank account: {'_' * 38};",
             f"City: {'_' * 18}; State: {'_' * 14}; Zip: {'_' * 14};", f"Routing Number: {'_' * 16}; Account Number: {'_' * 16};"]:
    story.append(Paragraph(line, plain))
story.append(Spacer(1, 6))
story.append(Paragraph(
    f"This authorization is to remain in full force and effect until {SH} has received written notification from me "
    f"(or either of us) of its termination in such time, and in such manner, as to afford {SH} and the Financial "
    f"Institution a reasonable opportunity to act on it.", body))
story.append(sig_line("Name:", 4.6 * inch))
story.append(sig_date_row())
story.append(Spacer(1, 14))
story.append(Paragraph(
    "Be sure to include a voided (cancelled) check from your checking account and/or a statement of account for your "
    "savings account, whichever is applicable. The details from the check will be used to verify the account details. The "
    "information provided on the voided check or statement must match the written information above.", body))
story.append(PageBreak())

# ---------------- Page: required documents + subcontractor info ----------------
story.append(Paragraph("Please attach the following documents with the email when returning your papers in this packet:", lbl))
docs = ["Scanned copy of your driver's license",
        "W-9 form filled out and signed with a valid SSN or EIN",
        "Aspen Grove background check number",
        "Aspen Grove profile screenshot showing your full name, ABC number, status and expiration date",
        f"Certificate of Insurance (general liability, errors and omissions, and workers' compensation if you have "
        f"employees) with {CO} named as a certificate holder",
        "Copy of your Social Security card or EIN paperwork",
        "Any other special license that you hold, e.g. roofing, plumbing, HVAC, general contractor, etc."]
for i, d in enumerate(docs):
    story.append(Paragraph(d, bullet, bulletText=["i.", "ii.", "iii.", "iv.", "v.", "vi.", "vii."][i]))
story.append(Spacer(1, 16))
story.append(Paragraph(f"{CO.upper()} SUBCONTRACTOR INFORMATION", head))
info = [f"Name: {'_' * 30}; Email: {'_' * 28};", f"Company Name: {'_' * 56};",
        f"Driver's License Number: {'_' * 16}; Driver's License Expiration Date: {'_' * 14};",
        f"Primary Phone: {'_' * 24}; Work Phone: {'_' * 20};",
        f"Mailing Address: {'_' * 36}; City: {'_' * 18};", f"State: {'_' * 6}; ZIP: {'_' * 10};",
        f"Shipping Address: {'_' * 36}; City: {'_' * 18};", f"State: {'_' * 6}; ZIP: {'_' * 10};"]
for line in info:
    story.append(Paragraph(line, plain)); story.append(Spacer(1, 8))
story.append(PageBreak())

# ---------------- Page: service area + services ----------------
story.append(Paragraph("SUBCONTRACTOR SERVICE AREA", lbl))
story.append(Paragraph("Please list the names of counties, zip codes or radius you will service (separated by commas):", plain))
story.append(Spacer(1, 22)); story.append(Paragraph("_" * 78, plain)); story.append(Spacer(1, 16))
story.append(Paragraph("SERVICES PERFORMED", lbl))
services = ["Grass cut / Shrubs / Tree Trimming", "Snow Removal", "Winterization / De-winterization", "Lock Change",
            "Maid Service", "Trash Out", "Sales Clean", "Mold Treatment", "Flooring / Carpet Replacement", "Electric Repair",
            "Plumbing Repair", "Roofing Repair", "HVAC Repair", "Occupancy Inspection"]
tbl = Table([[s, "Y", "N"] for s in services], colWidths=[3.6 * inch, 0.5 * inch, 0.5 * inch], rowHeights=0.32 * inch,
            style=TableStyle([("GRID", (0, 0), (-1, -1), 0.6, INK), ("FONT", (0, 0), (-1, -1), "Helvetica", 10),
                              ("FONT", (1, 0), (-1, -1), "Helvetica-Bold", 10), ("ALIGN", (1, 0), (-1, -1), "CENTER"),
                              ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (0, -1), 8)]))
story.append(tbl)
story.append(Spacer(1, 16))
story.append(Paragraph("Have you performed work for a Property Preservation company before:&nbsp;&nbsp;<b>Y / N</b>", plain))
story.append(PageBreak())

# ---------------- Subcontract agreement ----------------
story.append(Paragraph("SUBCONTRACT AGREEMENT", head))
story.append(Paragraph(f"<b>BETWEEN:</b> <b>{CO}</b>, a {COMPANY['org_state']} limited liability company, hereinafter referred to as "
                       f"<b>“{SH}”</b>, with its principal office located at: {COMPANY['address']}", plain))
story.append(Spacer(1, 6))
story.append(Paragraph(f"<b>AND:</b> {L} (the “Subcontractor”), a company organized and existing under the laws of the "
                       f"State of {'_' * 16}, with its head office located at:", plain))
story.append(Spacer(1, 14)); story.append(Paragraph("_" * 78, plain)); story.append(Spacer(1, 10))
story.append(Paragraph(
    f"For the purpose of this document, {CO}'s work order management system is referred to as the “{PORTAL}”. This "
    f"agreement shall be construed as if prepared with equal input by both parties and shall not be construed more strongly "
    f"against either party regardless of who is more responsible for its preparation. If there is a conflict between this "
    f"agreement and any present or future law, this agreement shall be curtailed only to the extent necessary to bring it "
    f"within the requirements of the law.", body))
story.append(Paragraph(
    f"WHEREAS {SH} desires to retain Subcontractor to perform certain contract work in accordance with various contract "
    f"documents and specifications and this Agreement; WHEREAS Subcontractor desires to be retained for such services "
    f"(“Services”) under the terms and conditions herein; NOW THEREFORE, {CO} and Subcontractor agree as follows:", body))

sections = [
    ("1. SERVICES", [
        f"Subcontractor agrees to perform services relating to property maintenance, lawn care, property preservation and "
        f"property improvements/repairs as set forth on work orders {SH} submits to Subcontractor. Subcontractor shall "
        f"determine the method, details and means of performing the services. {SH} may specify only the results desired in "
        f"regard to the specified services."]),
    ("2. RELATIONSHIP", [
        f"Subcontractor is a self-employed, independent contractor of {SH} for all purposes. As such, Subcontractor is solely "
        f"responsible for paying Subcontractor's own taxes. {SH} will submit a Form 1099 to the IRS reporting how much "
        f"Subcontractor earned in a given year; however, {SH} will not withhold or deduct any taxes from payments made to "
        f"Subcontractor. Any persons Subcontractor employs in connection with the performance of its services will be "
        f"Subcontractor's employees, and Subcontractor will be fully responsible for them. Subcontractor will be responsible "
        f"for all acts of its employees and contractors. Subcontractor will not be eligible to participate in any vacation, "
        f"group medical or life insurance, disability, profit sharing or retirement benefits, or any other fringe benefits or "
        f"benefit plans offered by {SH}. Subcontractor has no authority (and shall not hold itself out as having authority) "
        f"to bind {SH}, and Subcontractor shall not make any agreements or representations on {SH}'s behalf without "
        f"{SH}'s prior written consent."]),
    ("3. WORK ORDERS", [
        f"Subcontractor will be given a Work Order for each project, which will set forth the deadline for each project. "
        f"Project-specific requests and instructions may be included in the project Work Order. Failure to follow or perform "
        f"all project-specific requests and instructions included in each Work Order shall be considered a major infraction. "
        f"It is the responsibility of the Subcontractor to know all specifications to which {SH} expects each work order to "
        f"be completed, even if they are not listed on the work order itself. Any Subcontractor-suggested amendments to any "
        f"work order must be approved in writing by {SH} before Subcontractor is authorized to perform any additional work."]),
    ("4. QUALITY CONTROL", [
        f"Upon completion of a work order, a representative of {SH} may conduct an in-office (via photos) and/or on-site "
        f"quality control inspection of the work completed, noting all infractions or deficiencies. In the event of any "
        f"deficiencies or infractions, upon {SH}'s request Subcontractor will revisit the property and correct the "
        f"infractions and deficiencies within 24 hours of {CO}'s request.",
        f"For each such revisit, {SH} may charge Subcontractor a $50.00 penalty, which may be deducted from amounts owed to "
        f"Subcontractor. Regardless of whether {SH} requests a revisit, {SH} may deduct such amounts as it reasonably "
        f"determines are appropriate to compensate {SH} for any deficiencies or infractions in the work performed, and may "
        f"charge {SH}'s expenses incurred as a result of any deficiencies or infractions, including costs {SH} incurs to "
        f"correct the infractions and/or deficiencies. In the event of inconsistencies between this Agreement and the Work "
        f"Order, the provisions of the Work Order shall prevail."]),
    ("5. LABOR SUPERVISION & MANAGEMENT", [
        f"Subcontractor will supply all labor, tools and equipment required to perform the services under this Agreement. "
        f"Subcontractor has the sole obligation and responsibility to supervise, manage, direct and perform the projects "
        f"specified in the Work Orders. {SH} is committed to complying with the Immigration Reform and Control Act. "
        f"Subcontractor and all members of Subcontractor's crew must be lawfully permitted to work in the United States. "
        f"Subcontractor shall indemnify, defend and hold {SH} harmless for any violations relating to immigration and work "
        f"residency violations."]),
    ("6. CONDUCT & SAFETY", [
        f"The Subcontractor and all crew members shall wear appropriate, non-offensive clothing while performing all work and "
        f"services. No member of the crew is permitted to be shirtless at any time. All members of the Subcontractor crew "
        f"shall act professionally and courteously at all times, especially when interacting with a property owner or client "
        f"of {SH}. The members of the Subcontractor crew shall refrain from any profanity while on the job site. The members "
        f"of the Subcontractor crew shall not enter, or request permission to enter, a client residence unless there is prior "
        f"written approval from {SH}. Subcontractor shall not solicit any additional work of any kind or any additional "
        f"payment for work performed from any {CO} client. Smoking of any kind, alcohol consumption and/or the use of any "
        f"illegal or controlled substance is strictly prohibited while members of the Subcontractor crew are on the job site. "
        f"Subcontractor shall adhere to the latest Occupational Safety &amp; Health Administration guidelines, including, but "
        f"not limited to, the use of any required safety gear, e.g. helmets, goggles, harnesses, etc. Subcontractor shall be "
        f"responsible for payment of any fines or penalties relating to worksite safety. All crew members must be at least "
        f"16 years of age. Children are not allowed to be on site even if a parent is present."]),
    ("7. COMPLETION, PHOTOS & PAYMENT", [
        f"A Work Order is not considered complete until all specified work is completed, all tools belonging to the "
        f"Subcontractor are removed, and the job site is cleared of all work-related waste and trash. Subcontractor is not "
        f"entitled to any payment unless the Work Order is viewed as fully complete by {SH} and its clients. Subcontractor is "
        f"not entitled to partial payment if work was partially complete.",
        f"Subcontractor shall prepare and send to {SH} a detailed digital photo catalogue of each completed Work Order. Each "
        f"photo should clearly show that it was taken at the property specified in the Work Order by, at minimum, "
        f"photographing the street sign, house number and front of the home.",
        f"Although most Work Orders have specifically required photos, Subcontractor should at minimum take before, during "
        f"and after photos of each task completed, and the aforementioned photos if applicable. Photos shall be sent by "
        f"Subcontractor to {SH} via the {PORTAL}. The Subcontractor shall have no right to payment unless adequate photos have "
        f"been received by {SH} via the {PORTAL} and approved by {SH} and its clients. It is the Subcontractor's "
        f"responsibility to house all data, including for any lost data submitted by Subcontractor, and Subcontractor may be "
        f"required to resubmit invoices at no additional cost to {SH}."]),
    ("8. PAYMENT DISPUTES & REMEDIES", [
        f"If Subcontractor has not received payment on an order or was “short paid” (paid less than the total believed "
        f"due), Subcontractor shall create a dispute in the {PORTAL} under the “Forms &amp; Docs” tab by completing the Pay "
        f"Dispute Form (if the {PORTAL} was the issuing system). If Subcontractor no longer has access to the {PORTAL}, due to "
        f"termination of the business relationship or otherwise, Subcontractor must send an email to its account manager "
        f"stating the Work Order numbers and street addresses for each individual order that was short paid or not paid.",
        f"Subcontractor has 15 days from the original payment date to dispute short payments, or 15 days after the expected "
        f"payment date (30 total days) to dispute any payment. After these time periods, the order payments are closed and no "
        f"further payments will be issued. Subcontractor waives and releases all claims for payments from {SH} which are not "
        f"disputed by Subcontractor within the time frames set forth above, including but not limited to all work/services "
        f"performed by Subcontractor which pre-date this Agreement.",
        f"It is the Subcontractor's responsibility to keep track of the Work Order numbers for each Work Order completed. Any "
        f"type of payment dispute is evaluated on an individual Work Order basis. Example: if Subcontractor believes it "
        f"completed 50 Work Orders in a given week but only received payment for 40 Work Orders, it is the Subcontractor's "
        f"responsibility to let {SH} know the Work Order numbers for each order it believes it was not paid for. In the event "
        f"of a dispute as to payment or completion of a Work Order, the Subcontractor agrees as follows: 1) Subcontractor "
        f"shall not contact the property owner or client of {SH}; 2) Subcontractor shall not file any liens against the "
        f"property, and although Subcontractor may have rights under state law to execute and file liens for non-payment of "
        f"invoices, the undersigned Subcontractor does hereby waive and release any and all lien rights in connection with "
        f"any work performed or claimed to have been performed on behalf of {SH}, and Subcontractor agrees to indemnify {SH} "
        f"from any lower-tier subcontractors' liens for non-payment of invoices, and Subcontractor agrees that any lower-tier "
        f"subcontractors of Subcontractor shall waive and release their lien rights by executing the lien waiver form "
        f"provided by {SH}; 3) Subcontractor agrees that all payment disputes shall be settled directly with {SH} and that "
        f"there shall be no posted complaints by Subcontractor about {SH} on the internet or any other type of message board; "
        f"and 4) Subcontractor agrees that any disputes pertaining to invoices shall first be submitted to mediation before "
        f"Subcontractor initiates any action in a court of law, in which case Subcontractor consents and agrees that any and "
        f"all litigation shall be filed in {COMPANY['venue']}. In the event of any court action, the Subcontractor hereby "
        f"irrevocably waives, to the fullest extent permitted by law, all rights to a jury in any action, proceeding or "
        f"counter-claim, including but not limited to actions founded in contract, statute, tort, negligence or otherwise "
        f"relating to this Agreement."]),
    ("9. PAYMENT TERMS", [
        f"{SH} agrees to pay Subcontractor for services rendered and determined complete within 30 days of submission into "
        f"the {PORTAL}. Subcontractor may be on a pay schedule (weekly, monthly or otherwise) to be paid sooner. {SH} may "
        f"establish a course of dealing with Subcontractor for payment on a weekly basis or otherwise; however, in no event "
        f"shall any course of dealing establish an obligation for {SH} to pay Subcontractor for services rendered and "
        f"determined complete any sooner than within 30 days of submission into the {PORTAL}."]),
    ("10. INSURANCE", [
        f"Subcontractor shall maintain at its own expense during the term of this Agreement such insurance policies covering "
        f"the products and services to be provided as {SH} reasonably requests, but regardless of whether {SH} so requests, "
        f"Subcontractor will maintain the following insurance:",
        "@1. Commercial General Liability Insurance in the amount of $1,000,000 per each occurrence or claim, with Extended "
        "Property Damage Coverage in the amount of $50,000 per each occurrence or claim for personal property in the care, "
        "custody or control of Subcontractor, occurring as a result of Subcontractor's operations. If coverage is provided "
        f"under a claims-made form, any retro date on such coverage shall be no later than the date Subcontractor first "
        f"provides services to {SH}.",
        "@2. If vehicles, automobile liability insurance covering any such owned or non-owned vehicles with limits of at "
        "least $100,000 per person / $300,000 each accident.",
        "<b>Additional Obligations:</b>",
        f"@<b>A.</b> Subcontractor's policies will be primary and non-contributing with respect to any other insurance or "
        f"self-insurance which may be maintained by {SH}.",
        "@<b>B.</b> Subcontractor and its insurance carriers shall waive subrogation with respect to any Workers' "
        "Compensation and Commercial General Liability policies.",
        "@<b>C.</b> Coverage under the Commercial General Liability policy and, if required, any E&amp;O Liability policy, "
        "must remain in force for a minimum of 12 consecutive months after the conclusion of services under this agreement.",
        f"@<b>D.</b> Thirty (30) days' written notice will be given to {SH} prior to cancellation, non-renewal or material "
        f"reduction in limits of any insurance policy.",
        f"@<b>E.</b> Prior to commencing work under this agreement, and within 10 days of each subsequent policy renewal, "
        f"Subcontractor's insurers or their authorized representatives shall provide {SH} with Certificates of Insurance "
        f"evidencing that all coverage and policy endorsements required under this agreement are maintained in force. With "
        f"respect to any E&amp;O coverage, the certificates must indicate that the coverage applies to mortgage field services "
        f"operations and also show any policy retroactive date. {SH} has the right, but not the duty, to receive certified "
        f"copies of any required insurance policy and to verify that the coverage provided meets the standards set forth herein.",
        f"Subcontractor must ensure that all lower-tier subcontractors meet the insurance requirement minimums as specified "
        f"in this Agreement. Nothing in the insurance requirements section will be construed as limiting the Subcontractor's "
        f"(or any lower-tier subcontractor's) liability to {SH} or a third party. Subcontractor agrees to hold {SH} harmless "
        f"and defend and indemnify {SH} for any and all claims arising out of Subcontractor's performance under this Agreement "
        f"or any Work Order, including any claims for injury, disability or death of Subcontractor or Subcontractor's "
        f"employees or lower-tier subcontractors. Subcontractor further agrees to indemnify, defend and hold {SH} harmless "
        f"from any and all claims arising from any negligent act or omission by Subcontractor or Subcontractor's employees or "
        f"lower-tier subcontractors, including claims of third parties."]),
    ("11. INTELLECTUAL PROPERTY", [
        f"{SH} is and shall be the sole and exclusive owner of all right, title and interest throughout the world in and to "
        f"all the results and proceeds of the services performed under this Agreement (collectively, the "
        f"“Deliverables”), including all patents, copyrights, trademarks, trade secrets and other intellectual property "
        f"rights therein. Subcontractor agrees that the Deliverables are hereby deemed a “work made for hire” as defined in "
        f"17 U.S.C. &sect; 101 for {SH}. If, for any reason, any of the Deliverables do not constitute a “work made for "
        f"hire,” Subcontractor hereby irrevocably assigns to {SH}, in each case without additional consideration, all right, "
        f"title and interest throughout the world in and to the Deliverables, including all Intellectual Property Rights "
        f"therein. Upon {SH}'s request, Subcontractor shall promptly take such further actions, including execution and "
        f"delivery of all appropriate instruments of conveyance, as may be necessary to assist {SH} to prosecute, register, "
        f"perfect, record or enforce its rights in any Deliverables. If {SH} is unable, after reasonable effort, to obtain "
        f"Subcontractor's signature on any such documents, Subcontractor hereby irrevocably designates and appoints {SH} as "
        f"Subcontractor's agent and attorney-in-fact, to act for and on Subcontractor's behalf solely to execute and file any "
        f"such application or other document and do all other lawfully permitted acts to further the prosecution and issuance "
        f"of patents, copyrights or other intellectual property protection related to the Deliverables with the same legal "
        f"force and effect as if Subcontractor had executed them. Subcontractor agrees that this power of attorney is coupled "
        f"with an interest."]),
    ("12. CONFIDENTIALITY", [
        f"To the extent that, in connection with this agreement, Subcontractor comes into possession of any proprietary or "
        f"confidential information of {SH} or of {CO}'s clients, or discloses any other proprietary or confidential "
        f"information of a third party to Subcontractor (collectively, the “Confidential Information”), Subcontractor agrees "
        f"to use such Confidential Information solely for the purposes of the applicable Work Order and not to disclose such "
        f"Confidential Information to any third party without the prior written consent of {SH}. The terms of this Agreement, "
        f"the {SH} software system, client information and lists, information about the properties serviced by {SH}, and all "
        f"information pertaining to {CO}'s business operations and strategies, pricing, marketing, finances, sourcing, "
        f"personnel or operations, shall all be considered Confidential Information. Confidential Information does not "
        f"include any information that is or becomes generally available to the public other than through a breach of this "
        f"Agreement."]),
    ("13. PERFORMANCE", [
        f"Neither this Agreement nor any duties or obligations under this Agreement may be assigned by Subcontractor without "
        f"prior written consent of {SH}. {SH} agrees to comply with all reasonable requests of Subcontractor necessary for "
        f"the performance of Subcontractor's services to be performed under this Agreement. {SH} agrees to pay Subcontractor "
        f"for services in accordance with the description of services and compensation schedule established by the parties "
        f"and incorporated herein by reference (the “Pricing Schedule”)."]),
    ("14. BACKGROUND CHECKS", [
        f"Subcontractor will be required to have an annual background screening by Aspen Grove Background Check (ABC), an "
        f"independent third-party agency specializing in both social and criminal reporting. Failure to submit the background "
        f"screen will result in immediate termination of the subcontract agreement. Further, Subcontractor is responsible for "
        f"obtaining background checks on all of its employees and subcontractors and maintaining up-to-date files with this "
        f"information."]),
    ("15. TERMINATION", [
        "Notwithstanding any other provision of this agreement, either party may terminate this agreement at any time by "
        "giving written notice to the other party.",
        "This Agreement shall terminate automatically on the occurrence of any of the following events:",
        "@1. Bankruptcy or insolvency of either party.", "@2. Death or dissolution of either party.",
        f"@3. Assignment of this Agreement by Subcontractor without the consent of {SH}."]),
    ("16. ARBITRATION", [
        f"Any and all disputes or claims between {SH} and the Subcontractor arising out of this Subcontract shall be resolved "
        f"by binding arbitration according to the applicable Rules of Arbitration in the State of {COMPANY['law_state']}. In "
        f"so agreeing, the parties expressly waive their right to a jury trial, if any, on these issues and further agree that "
        f"the award of the arbitrator shall be final and binding upon them as though rendered by a court of law and shall be "
        f"enforceable in any court having jurisdiction over the same."]),
    ("17. SEVERABILITY", [
        f"If any provision of this Agreement is held by a court of competent jurisdiction to be invalid, void or "
        f"unenforceable, the remaining provisions will nonetheless continue in full force without being impaired or "
        f"invalidated in any way. This Agreement shall be governed and construed in accordance with the laws of the State of "
        f"{COMPANY['law_state']}."]),
    ("18. ENTIRE AGREEMENT", [
        f"This Agreement supersedes any and all other agreements, both oral and written, between the parties with respect to "
        f"the rendering of services by Subcontractor for {SH} and, together with the Work Orders and Pricing Schedule, "
        f"contains all of the covenants and agreements between the parties with respect to the rendering of these services in "
        f"any manner whatsoever. Any modification of this Agreement will be effective only if it is in writing and signed by "
        f"both parties."]),
    ("19. GOVERNING LAW AND RULES OF CONSTRUCTION", [
        f"The validity, interpretation and performance of this Subcontract shall be governed by the laws of the jurisdiction "
        f"where the Project is located or the laws of the State of {COMPANY['law_state']}, as chosen by the parties. Titles, "
        f"captions or headings to any provision, article, etc. shall not limit the full contents of the same. These articles "
        f"have the full force and effect as if no titles existed.",
        "This contract shall be binding upon and inure to the benefit of the respective successors, assigns, representatives "
        "and heirs of the parties herein.",
        "IN WITNESS WHEREOF, the parties hereto have executed this Agreement as of the day and year first above written."]),
]

for title, paras in sections:
    block = [Paragraph(title, sec)]
    for p in paras:
        if p.startswith("@"):
            block.append(Paragraph(p[1:], sub))
        else:
            block.append(Paragraph(p, body))
    story.append(KeepTogether(block[:2]))
    story.extend(block[2:])

story.append(Spacer(1, 30))
sig = Table([[Paragraph("SUBCONTRACTOR", lbl), "", Paragraph(CO.upper(), lbl)],
             ["", "", ""],
             [Paragraph("Signature:", plain), "", Paragraph("Signature:", plain)],
             ["", "", ""],
             [Paragraph("Date:", plain), "", Paragraph("Date:", plain)]],
            colWidths=[3 * inch, 0.6 * inch, 3 * inch], rowHeights=[22, 40, 34, 10, 30],
            style=TableStyle([("LINEBELOW", (0, 1), (0, 1), 1.2, INK), ("LINEBELOW", (2, 1), (2, 1), 1.2, INK),
                              ("VALIGN", (0, 0), (-1, -1), "BOTTOM")]), hAlign="LEFT")
story.append(KeepTogether([sig]))

doc = SimpleDocTemplate(str(OUT), pagesize=letter, leftMargin=0.85 * inch, rightMargin=0.85 * inch, topMargin=0.8 * inch,
                        bottomMargin=0.85 * inch, title=f"{CO} Subcontractor Agreement", author=CO)
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print("wrote", OUT)
