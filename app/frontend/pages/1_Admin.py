import os

import requests
import streamlit as st


st.set_page_config(
    page_title="IPO Intelligence Admin",
    page_icon="⚙️",
    layout="centered",
)


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = os.getenv(
    "API_URL",
    "http://localhost:8080",
)


# ============================================================
# PAGE HEADER
# ============================================================

st.title("IPO Intelligence Admin")

st.caption(
    "Add and index an IPO in the research system."
)


# ============================================================
# ADMIN AUTHENTICATION
# ============================================================

st.markdown("### Admin Authentication")

admin_key = st.text_input(
    "Admin API Key",
    type="password",
    help="The API key configured on the backend.",
)


st.divider()


# ============================================================
# IPO FORM
# ============================================================

st.markdown("### Add IPO")

with st.form("add_ipo_form"):

    ipo_id = st.text_input(
        "IPO ID",
        placeholder="example-ipo-2026",
    )

    company_name = st.text_input(
        "Company Name",
        placeholder="Example Limited",
    )

    document_id = st.text_input(
        "Document ID",
        placeholder="example-drhp-2026",
    )

    document_type = st.selectbox(
        "Document Type",
        [
            "DRHP",
            "RHP",
        ],
    )

    submitted = st.form_submit_button(
        "Add & Index IPO",
        use_container_width=True,
    )


# ============================================================
# SUBMIT
# ============================================================

if submitted:

    if not admin_key:
        st.error(
            "Enter the admin API key."
        )

    elif not ipo_id.strip():
        st.error(
            "IPO ID is required."
        )

    elif not company_name.strip():
        st.error(
            "Company name is required."
        )

    elif not document_id.strip():
        st.error(
            "Document ID is required."
        )

    else:

        payload = {
            "ipo_id": ipo_id.strip(),
            "company_name": company_name.strip(),
            "document_id": document_id.strip(),
            "document_type": document_type,
        }

        headers = {
            "X-Admin-Key": admin_key,
        }

        try:

            with st.spinner(
                "Discovering, downloading and indexing..."
            ):

                response = requests.post(
                    f"{API_URL}/admin/ipos",
                    json=payload,
                    headers=headers,
                    timeout=300,
                )

            if response.status_code == 200:

                result = response.json()

                st.success(
                    "IPO added successfully."
                )

                st.json(result)

            elif response.status_code == 401:

                st.error(
                    "Invalid admin API key."
                )

            elif response.status_code == 404:

                detail = (
                    response.json()
                    .get(
                        "detail",
                        "IPO document could not be found.",
                    )
                )

                st.error(detail)

            elif response.status_code == 400:

                detail = (
                    response.json()
                    .get(
                        "detail",
                        "Invalid request.",
                    )
                )

                st.error(detail)

            else:

                st.error(
                    f"Admin API returned "
                    f"HTTP {response.status_code}."
                )

                st.code(
                    response.text
                )

        except requests.RequestException as exc:

            st.error(
                "Could not connect to the backend."
            )

            st.code(str(exc))