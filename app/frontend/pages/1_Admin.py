import os
import time
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
            response = requests.post(
                f"{API_URL}/admin/ipos",
                json=payload,
                headers=headers,
                timeout=30,
            )

            if response.status_code not in (200, 202):
                try:
                    detail = response.json().get(
                        "detail",
                        response.text,
                    )
                except ValueError:
                    detail = response.text

                if response.status_code == 401:
                    st.error("Invalid admin API key.")
                else:
                    st.error(
                        f"Admin API returned HTTP "
                        f"{response.status_code}: {detail}"
                    )

            else:
                job = response.json()
                job_id = job.get("job_id")

                if not job_id:
                    st.error(
                        "The backend did not return an ingestion "
                        "job ID. Restart the backend with the "
                        "updated API code and try again."
                    )
                    st.json(job)

                else:
                    with st.status(
                        "IPO ingestion queued...",
                        expanded=True,
                    ) as progress:

                        for _ in range(1200):
                            time.sleep(3)

                            status_response = requests.get(
                                f"{API_URL}/admin/ipos/jobs/{job_id}",
                                headers=headers,
                                timeout=30,
                            )

                            if status_response.status_code != 200:
                                progress.update(
                                    label="Could not retrieve job status.",
                                    state="error",
                                )
                                st.error(
                                    f"Status API returned HTTP "
                                    f"{status_response.status_code}."
                                )
                                st.code(status_response.text)
                                break

                            result = status_response.json()
                            job_status = result.get("status")

                            if job_status == "completed":
                                progress.update(
                                    label="IPO added and indexed successfully.",
                                    state="complete",
                                )
                                st.success(
                                    "IPO ingestion completed successfully."
                                )
                                st.json(result)
                                break

                            if job_status == "failed":
                                progress.update(
                                    label="IPO ingestion failed.",
                                    state="error",
                                )
                                st.error(
                                    result.get(
                                        "message",
                                        "IPO ingestion failed.",
                                    )
                                )
                                st.json(result)
                                break

                            progress.update(
                                label=result.get(
                                    "message",
                                    f"Ingestion status: {job_status}",
                                ),
                                state="running",
                            )

                        else:
                            progress.update(
                                label="Still processing; stopped waiting for status.",
                                state="running",
                            )
                            st.warning(
                                "The page stopped polling after 60 minutes. "
                                "The backend job may still be running. "
                                "Do not submit the same IPO again."
                            )
                            st.code(f"Job ID: {job_id}")

        except requests.RequestException as exc:
            st.error("Could not communicate with the backend.")
            st.code(str(exc))
