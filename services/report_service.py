"""Exportação do prontuário em PDF."""

from fpdf import FPDF

from utils.formatting import age, fmt_date, fmt_datetime, format_cpf, now_local


_TYPOGRAPHY = str.maketrans({"—": "-", "–": "-", "“": '"', "”": '"', "‘": "'", "’": "'", "…": "...", "•": "·"})


def _latin1(text):
    # As fontes padrão do PDF cobrem português (latin-1); emojis e outros
    # símbolos fora dessa faixa são trocados por "?" em vez de quebrar.
    text = (text or "").translate(_TYPOGRAPHY)
    return text.encode("latin-1", "replace").decode("latin-1")


class _RecordPDF(FPDF):

    def __init__(self, professional, patient_name):
        super().__init__(format="A4")
        self.professional = professional
        self.patient_name = patient_name
        self.set_margins(20, 18, 20)
        self.set_auto_page_break(True, margin=20)

    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(151, 86, 112)
        self.cell(0, 5, _latin1("PRONTUÁRIO PSICOLÓGICO — DOCUMENTO SIGILOSO"), new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(110, 110, 110)
        self.cell(0, 5, _latin1(f"{self.patient_name}  ·  {self.professional}"), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(220, 210, 215)
        self.line(20, self.get_y() + 1, 190, self.get_y() + 1)
        self.ln(5)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(140, 140, 140)
        self.cell(
            0, 5,
            _latin1(f"Gerado em {now_local():%d/%m/%Y %H:%M}  ·  página {self.page_no()}/{{nb}}"),
            align="C",
        )


def prontuario_pdf(user, patient, records):
    professional = user.get("name") or "Profissional"

    if user.get("professional_register"):
        professional += f" — CRP {user['professional_register']}"

    pdf = _RecordPDF(professional, patient.full_name)
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("Times", "B", 18)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, _latin1(patient.full_name), new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)

    details = []

    if patient.birth_date:
        details.append(f"Nascimento: {fmt_date(patient.birth_date)} ({age(patient.birth_date)} anos)")

    if patient.cpf:
        details.append(f"CPF: {format_cpf(patient.cpf)}")

    if patient.phone:
        details.append(f"Telefone: {patient.phone}")

    if details:
        pdf.multi_cell(0, 6, _latin1("   ·   ".join(details)), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(4)

    if not records:
        pdf.set_font("Helvetica", "I", 11)
        pdf.cell(0, 8, _latin1("Nenhum registro no prontuário."))

    for record in sorted(records, key=lambda r: (r.session_date, r.created_at)):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(151, 86, 112)
        pdf.cell(0, 7, _latin1(f"Sessão de {fmt_date(record.session_date, with_weekday=True)}"), new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Times", "", 11.5)
        pdf.set_text_color(35, 35, 35)
        pdf.multi_cell(0, 6, _latin1(record.content), new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(150, 150, 150)
        stamp = f"Registrado em {fmt_datetime(record.created_at)}"

        if record.updated_at and record.created_at and (record.updated_at - record.created_at).total_seconds() > 60:
            stamp += f" · editado em {fmt_datetime(record.updated_at)}"

        pdf.cell(0, 5, _latin1(stamp), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    return bytes(pdf.output())
