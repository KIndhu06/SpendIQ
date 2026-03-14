import streamlit as st
import pandas as pd
from utils.db import get_connection
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import inch
from datetime import datetime
import io

st.set_page_config(
    page_title="Download Report",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="collapsedControl"] {display: none;}
    </style>
""", unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.switch_page("pages/login.py")

def get_transactions(family_id):
    conn = get_connection()
    df = pd.read_sql(
        "SELECT date, description, amount, type, category FROM transactions WHERE family_id = %s ORDER BY date DESC",
        conn, params=(family_id,))
    conn.close()
    return df

def get_monthly_summary(family_id):
    conn = get_connection()
    df = pd.read_sql(
        """SELECT DATE_FORMAT(date, '%%Y-%%m') as month, type, SUM(amount) as total
        FROM transactions WHERE family_id = %s
        GROUP BY DATE_FORMAT(date, '%%Y-%%m'), type ORDER BY month ASC""",
        conn, params=(family_id,))
    conn.close()
    return df

def get_category_summary(family_id):
    conn = get_connection()
    df = pd.read_sql(
        """SELECT category, SUM(amount) as total FROM transactions
        WHERE family_id = %s AND type = 'expense'
        GROUP BY category ORDER BY total DESC""",
        conn, params=(family_id,))
    conn.close()
    return df

def generate_pdf(user, df, monthly_df, category_df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    elements = []

    title_style = ParagraphStyle('T', parent=styles['Title'],
        fontSize=24, textColor=colors.HexColor('#2C3E50'),
        spaceAfter=10, alignment=1)
    subtitle_style = ParagraphStyle('S', parent=styles['Normal'],
        fontSize=12, textColor=colors.HexColor('#7F8C8D'),
        spaceAfter=5, alignment=1)
    heading_style = ParagraphStyle('H', parent=styles['Heading2'],
        fontSize=14, textColor=colors.HexColor('#2980B9'),
        spaceAfter=8, spaceBefore=15)

    elements.append(Paragraph("💰 SpendIQ ", title_style))
    elements.append(Paragraph("Your Personal Financial Report", subtitle_style))
    elements.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%d %B %Y %I:%M %p')}",
        subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2,
                               color=colors.HexColor('#2980B9')))
    elements.append(Spacer(1, 0.2*inch))

    elements.append(Paragraph("👤 Your Account Details", heading_style))
    user_data = [
        ["Name", str(user[1])],
        ["Email", str(user[2])],
        ["Family ID", str(user[4])],
        ["Report Date", datetime.now().strftime('%d-%m-%Y')]
    ]
    user_table = Table(user_data, colWidths=[2*inch, 4*inch])
    user_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#EBF5FB')),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#2980B9')),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(user_table)
    elements.append(Spacer(1, 0.2*inch))

    if not df.empty:
        total_income = df[df['type']=='income']['amount'].sum()
        total_expense = df[df['type']=='expense']['amount'].sum()
        total_savings = total_income - total_expense
        savings_rate = (total_savings/total_income*100) if total_income > 0 else 0

        elements.append(Paragraph("📊 Your Financial Summary", heading_style))
        summary_data = [
            ["What", "Amount"],
            ["💰 Total Money Received", f"Rs. {total_income:,.2f}"],
            ["💸 Total Money Spent", f"Rs. {total_expense:,.2f}"],
            ["🏦 Total Money Saved", f"Rs. {total_savings:,.2f}"],
            ["📈 Savings Percentage", f"{savings_rate:.1f}%"],
            ["📝 Total Transactions", str(len(df))]
        ]
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2980B9')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
            ('ROWBACKGROUNDS', (1,0), (-1,-1), [
                colors.HexColor('#FDFEFE'),
                colors.HexColor('#EBF5FB')
            ]),
            ('PADDING', (0,0), (-1,-1), 8),
            ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.2*inch))

    if not category_df.empty:
        elements.append(Paragraph("🛒 Where Did Your Money Go?", heading_style))
        cat_data = [["Category", "Amount Spent (Rs.)", "Percentage"]]
        total_exp = category_df['total'].sum()
        for _, row in category_df.iterrows():
            pct = (row['total']/total_exp*100) if total_exp > 0 else 0
            cat_data.append([
                str(row['category']),
                f"Rs. {row['total']:,.2f}",
                f"{pct:.1f}%"
            ])
        cat_table = Table(cat_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E74C3C')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
            ('ROWBACKGROUNDS', (1,0), (-1,-1), [
                colors.HexColor('#FDFEFE'),
                colors.HexColor('#FDEDEC')
            ]),
            ('PADDING', (0,0), (-1,-1), 8),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ]))
        elements.append(cat_table)
        elements.append(Spacer(1, 0.2*inch))

    if not monthly_df.empty:
        elements.append(Paragraph("📅 Month by Month Summary", heading_style))
        pivot_df = monthly_df.pivot_table(
            index='month', columns='type',
            values='total', aggfunc='sum'
        ).fillna(0).reset_index()
        monthly_data = [["Month", "Money Received (Rs.)",
                         "Money Spent (Rs.)", "Money Saved (Rs.)"]]
        for _, row in pivot_df.iterrows():
            income = row.get('income', 0)
            expense = row.get('expense', 0)
            savings = income - expense
            monthly_data.append([
                str(row['month']),
                f"Rs. {income:,.2f}",
                f"Rs. {expense:,.2f}",
                f"Rs. {savings:,.2f}"
            ])
        monthly_table = Table(monthly_data,
            colWidths=[1.5*inch, 1.8*inch, 1.8*inch, 1.8*inch])
        monthly_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#27AE60')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
            ('ROWBACKGROUNDS', (1,0), (-1,-1), [
                colors.HexColor('#FDFEFE'),
                colors.HexColor('#EAFAF1')
            ]),
            ('PADDING', (0,0), (-1,-1), 8),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
        ]))
        elements.append(monthly_table)
        elements.append(Spacer(1, 0.2*inch))

    if not df.empty:
        elements.append(Paragraph("📋 Your Recent Transactions", heading_style))
        trans_data = [["Date", "Description", "Amount", "Type", "Category"]]
        for _, row in df.head(10).iterrows():
            trans_data.append([
                str(row['date'])[:10],
                str(row['description'])[:30],
                f"Rs. {row['amount']:,.2f}",
                str(row['type']),
                str(row['category'])
            ])
        trans_table = Table(trans_data,
            colWidths=[1.1*inch, 2.2*inch, 1.2*inch, 0.9*inch, 1.1*inch])
        trans_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#8E44AD')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#BDC3C7')),
            ('ROWBACKGROUNDS', (1,0), (-1,-1), [
                colors.HexColor('#FDFEFE'),
                colors.HexColor('#F5EEF8')
            ]),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(trans_table)

    elements.append(Spacer(1, 0.3*inch))
    elements.append(HRFlowable(width="100%", thickness=1,
                               color=colors.HexColor('#BDC3C7')))
    elements.append(Paragraph(
        "Generated by SpendIQ | Your Personal Finance Assistant",
        subtitle_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer

st.title("📄 Download Your Financial Report")
st.write(f"Welcome, **{st.session_state['user'][1]}**!")

st.info("""
📋 **What is in your report:**
- Your account summary
- Total money received and spent
- Where your money went (by category)
- Month by month breakdown
- Your recent transactions
""")

family_id = st.session_state['user'][4]
df = get_transactions(family_id)
monthly_df = get_monthly_summary(family_id)
category_df = get_category_summary(family_id)

if df.empty:
    st.warning("⚠️ No transactions found! Please upload your bank statement first.")
    if st.button("💼 Go to My Finances"):
        st.switch_page("pages/finance.py")
else:
    st.write("---")
    st.subheader("📊 Quick Summary")
    total_income = df[df['type']=='income']['amount'].sum()
    total_expense = df[df['type']=='expense']['amount'].sum()
    total_savings = total_income - total_expense

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Total Received", f"₹{total_income:,.2f}")
    with col2:
        st.metric("💸 Total Spent", f"₹{total_expense:,.2f}")
    with col3:
        st.metric("🏦 Total Saved", f"₹{total_savings:,.2f}")

    st.write("---")
    st.subheader("📥 Generate Your Report")
    st.write("Click below to create and download your complete financial report!")

    if st.button("📄 Create My Report", use_container_width=True):
        with st.spinner("Creating your report... please wait!"):
            pdf_buffer = generate_pdf(
                st.session_state['user'],
                df, monthly_df, category_df
            )
            st.success("✅ Your report is ready!")
            st.download_button(
                label="📥 Download My Report",
                data=pdf_buffer,
                file_name=f"my_finance_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

st.write("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("🏠 Back to Home", use_container_width=True):
        st.switch_page("app.py")
with col2:
    if st.button("💼 My Finances", use_container_width=True):
        st.switch_page("pages/finance.py")