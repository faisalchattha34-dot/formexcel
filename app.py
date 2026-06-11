import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from database import *

init_db()

st.set_page_config(page_title="InformAI Forms", layout="wide")

st.title("📄 Excel → Form Builder")

# Form Name
form_name = st.text_input("Form Name")

# Excel Upload
excel_file = st.file_uploader(
    "Upload Excel File",
    type=["xlsx"]
)

if excel_file:

    df = pd.read_excel(excel_file, engine="openpyxl")

    st.subheader("Detected Columns")

    if "columns_list" not in st.session_state:
        st.session_state.columns_list = df.columns.tolist()

    updated_columns = []

    for i, col in enumerate(st.session_state.columns_list):

        c1, c2 = st.columns([4,1])

        with c1:
            new_name = st.text_input(
                f"Column {i+1}",
                value=col,
                key=f"col_{i}"
            )

        with c2:
            delete = st.checkbox(
                "Delete",
                key=f"del_{i}"
            )

        if not delete:
            updated_columns.append(new_name)

    st.session_state.columns_list = updated_columns

    st.subheader("Form Preview")

    preview_data = {}

    for field in updated_columns:
        preview_data[field] = st.text_input(
            field,
            key=f"preview_{field}"
        )

    if st.button("Create Form"):

        form_id = str(uuid.uuid4())

        create_form(
            form_id=form_id,
            form_name=form_name,
            columns=updated_columns,
            created_at=str(datetime.now())
        )

        st.success("Form Created Successfully")

        st.code(
            f"?form_id={form_id}",
            language="text"
        )
        st.markdown("---")

st.header("📊 Forms Dashboard")

forms = get_forms()

if forms:

    form_names = {
        row["form_name"]: row["form_id"]
        for row in forms
    }

    selected = st.selectbox(
        "Select Form",
        list(form_names.keys())
    )

    selected_form_id = form_names[selected]

    stats = get_stats(selected_form_id)

    c1, c2, c3 = st.columns(3)

    c1.metric("Total Emails", stats["total"])
    c2.metric("Submitted", stats["submitted"])
    c3.metric("Pending", stats["pending"])

    responses = get_form_responses(
        selected_form_id
    )

    if responses:

        rows = []

        import json

        for r in responses:

            row = json.loads(
                r["response_data"]
            )

            row["response_id"] = r["response_id"]

            rows.append(row)

        response_df = pd.DataFrame(rows)

        st.dataframe(
            response_df,
            use_container_width=True
        )

        excel = response_df.to_excel

        output = pd.ExcelWriter(
            "temp.xlsx",
            engine="xlsxwriter"
        )

        response_df.to_excel(
            output,
            index=False
        )

        output.close()

        with open("temp.xlsx", "rb") as f:

            st.download_button(
                "⬇ Download Responses",
                f,
                file_name="responses.xlsx"
            )
        st.subheader("📧 Recipient Emails")

email_file = st.file_uploader(
    "Upload Email Excel",
    type=["xlsx"],
    key="email_upload"
)

manual_emails = st.text_area(
    "Or Enter Emails Manually",
    placeholder="abc@gmail.com, xyz@gmail.com"
)

emails = []

if email_file:
    email_df = pd.read_excel(email_file)

    if "Email" in email_df.columns:
        emails.extend(
            email_df["Email"]
            .dropna()
            .astype(str)
            .tolist()
        )

if manual_emails:
    emails.extend([
        x.strip()
        for x in manual_emails.split(",")
        if x.strip()
    ])

emails = list(set(emails))

if emails:
    st.success(
        f"{len(emails)} emails loaded"
    )

    st.dataframe(
        pd.DataFrame({"Email": emails}),
        use_container_width=True
    )
