import streamlit as st
import pandas as pd
from io import BytesIO
from openpyxl import load_workbook

st.set_page_config(page_title="Excel Smart Form", page_icon="📄", layout="centered")
st.title("📄 Dynamic Excel Form with Auto Dropdown Detection + Session Management")

uploaded = st.file_uploader("📂 Upload Excel File", type=["xlsx"])

if uploaded:
    # Step 1️⃣: Detect header row
    df_raw = pd.read_excel(uploaded, header=None)
    header_row_index = None
    for i in range(len(df_raw)):
        row = df_raw.iloc[i]
        if row.notna().sum() > 2:
            header_row_index = i
            break

    # Step 2️⃣: Read DataFrame
    df = pd.read_excel(uploaded, header=header_row_index)
    df.columns = [str(c).strip().replace("_", " ").title() for c in df.columns if pd.notna(c)]

    st.success("✅ Columns Detected Successfully!")
    st.write("**Detected Columns:**", list(df.columns))

    # Step 3️⃣: Detect dropdowns (data validation)
    uploaded.seek(0)
    wb = load_workbook(uploaded, data_only=True)
    ws = wb.active

    dropdown_dict = {}

    if ws.data_validations is not None:
        for dv in ws.data_validations.dataValidation:
            if dv.type == "list" and dv.formula1:
                formula = dv.formula1.strip('"')
                if "," in formula:
                    values = [v.strip() for v in formula.split(",")]
                    for cell_range in dv.cells:
                        col_letter = ''.join([c for c in str(cell_range) if c.isalpha()])
                        if col_letter:
                            col_index = ord(col_letter.upper()[0]) - 65
                            if col_index < len(df.columns):
                                dropdown_dict[df.columns[col_index]] = values

    # Step 4️⃣: Show dropdown detection results
    if dropdown_dict:
        st.info("🎯 **Detected Dropdown Columns:**")
        st.table(pd.DataFrame([
            {"Column": col, "Dropdown Options": ", ".join(vals)}
            for col, vals in dropdown_dict.items()
        ]))
    else:
        st.warning("⚠️ No dropdown lists detected in this Excel file.")

    # Step 5️⃣: Initialize session storage
    if "session_df" not in st.session_state:
        st.session_state.session_df = df.copy()

    # Step 6️⃣: Dynamic Form
    st.subheader("🧾 Fill the Form Below")
    data = {}
    for col in df.columns:
        if col in dropdown_dict:
            data[col] = st.selectbox(f"{col}", dropdown_dict[col], key=col)
        else:
            data[col] = st.text_input(f"{col}", key=col)

    # Step 7️⃣: Submit + Add Data to Session
    if st.button("✅ Submit"):
        new_row = pd.DataFrame([data])
        st.session_state.session_df = pd.concat([st.session_state.session_df, new_row], ignore_index=True)
        st.success("🎉 Data added successfully!")

    # Step 8️⃣: Show all data added in this session
    st.subheader("📋 Current Session Data (All Entries)")
    st.dataframe(st.session_state.session_df)

    # Step 9️⃣: Download updated file
    output = BytesIO()
    st.session_state.session_df.to_excel(output, index=False)
    output.seek(0)

    st.download_button(
        label="⬇️ Download Updated Excel (All Session Data)",
        data=output,
        file_name="updated_form_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
