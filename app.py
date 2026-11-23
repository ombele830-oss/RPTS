"""
RPTS - Research Project Tracking System
Streamlit demonstration interface.

Run:
    pip install streamlit pandas
    streamlit run app.py

This is a standalone demonstration UI using Streamlit session state and sample data.
It does not connect to the original React/Express/SQLite application.
"""

from datetime import date, datetime
from io import BytesIO
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="RPTS | Research Project Tracking System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Demo configuration -----------------------------

DEMO_PASSWORD = "Demo@1234"
USERS = {
    "pi@rpts.edu": ("Faculty PI", "Dr. A. Sharma"),
    "pi2@rpts.edu": ("Faculty PI", "Dr. R. Patil"),
    "hod@rpts.edu": ("Head of Department", "Department HOD"),
    "scholar@rpts.edu": ("Research Scholar", "Research Scholar"),
    "scholar2@rpts.edu": ("Research Scholar", "Research Scholar 2"),
    "admin@rpts.edu": ("Research Office", "Research Office Admin"),
}

def initialize_state():
    defaults = {
        "authenticated": False,
        "email": "",
        "role": "",
        "display_name": "",
        "proposals": [
            {
                "id": "RPTS-001",
                "title": "AI-Based Crop Disease Detection",
                "agency": "DST",
                "budget": 450000,
                "pi": "Dr. A. Sharma",
                "status": "Submitted",
                "submitted": str(date.today()),
                "comment": "",
                "document": "sample_proposal.pdf",
            },
            {
                "id": "RPTS-002",
                "title": "Smart Energy Monitoring System",
                "agency": "AICTE",
                "budget": 320000,
                "pi": "Dr. R. Patil",
                "status": "Approved",
                "submitted": str(date.today()),
                "comment": "Approved for project initiation.",
                "document": "energy_proposal.pdf",
            },
        ],
        "milestones": [
            {"project": "AI-Based Crop Disease Detection", "name": "Dataset collection", "assignee": "Research Scholar", "due": str(date.today()), "status": "In Progress"},
            {"project": "Smart Energy Monitoring System", "name": "Prototype development", "assignee": "Research Scholar 2", "due": str(date.today()), "status": "Completed"},
        ],
        "tranches": [
            {"project": "Smart Energy Monitoring System", "milestone": "Prototype development", "amount": 100000, "status": "Eligible"},
            {"project": "Smart Energy Monitoring System", "milestone": "Final evaluation", "amount": 80000, "status": "Pending"},
        ],
        "progress_reports": [],
        "publications": [],
        "audit": [],
        "next_proposal": 3,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_state()

def log_action(action: str):
    st.session_state.audit.insert(0, {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": st.session_state.get("email", "system"),
        "action": action,
    })

def money(value):
    return f"₹{int(value):,}"

def login():
    st.title("📚 Research Project Tracking System")
    st.caption("A centralized platform for academic research project administration.")
    left, right = st.columns([1.15, 1])
    with left:
        st.markdown("### Manage the complete research lifecycle")
        st.markdown(
            "Proposal submission → HOD approval → milestone-linked funding → "
            "progress reports → publications → agency reporting"
        )
        st.info(
            "**User roles**\n\n"
            "- Faculty Principal Investigator (PI)\n"
            "- Head of Department (HOD)\n"
            "- Research Scholar\n"
            "- Research Office"
        )
    with right:
        st.markdown("### Sign in")
        email = st.text_input("Email address", placeholder="pi@rpts.edu")
        password = st.text_input("Password", type="password")
        if st.button("Login", type="primary", use_container_width=True):
            if email.strip().lower() in USERS and password == DEMO_PASSWORD:
                role, name = USERS[email.strip().lower()]
                st.session_state.authenticated = True
                st.session_state.email = email.strip().lower()
                st.session_state.role = role
                st.session_state.display_name = name
                st.rerun()
            else:
                st.error("Invalid demo email or password.")
        with st.expander("Demo accounts"):
            st.write("Password for all accounts:", f"`{DEMO_PASSWORD}`")
            for demo_email, (demo_role, _) in USERS.items():
                st.write(f"- `{demo_email}` — {demo_role}")

def sidebar():
    with st.sidebar:
        st.title("📚 RPTS")
        st.caption("Research Project Tracking System")
        st.divider()
        st.write(f"**{st.session_state.display_name}**")
        st.caption(st.session_state.role)
        st.write(st.session_state.email)
        if st.button("Log out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.email = ""
            st.session_state.role = ""
            st.session_state.display_name = ""
            st.rerun()
        st.divider()
        st.caption("Demo application · Sample data")

def dashboard():
    st.title("Dashboard")
    st.caption(f"Welcome, {st.session_state.display_name}.")
    proposals = st.session_state.proposals
    total = len(proposals)
    submitted = sum(p["status"] == "Submitted" for p in proposals)
    approved = sum(p["status"] == "Approved" for p in proposals)
    reports = len(st.session_state.progress_reports)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total proposals", total)
    c2.metric("Awaiting review", submitted)
    c3.metric("Approved", approved)
    c4.metric("Progress reports", reports)
    st.subheader("Recent proposals")
    if proposals:
        st.dataframe(pd.DataFrame(proposals)[["id", "title", "agency", "budget", "pi", "status", "submitted"]], use_container_width=True, hide_index=True)
    else:
        st.info("No proposals have been submitted yet.")

def proposal_submission():
    st.title("Submit Research Proposal")
    st.caption("Submit a project proposal and attach its PDF document.")
    with st.form("proposal_form", clear_on_submit=True):
        title = st.text_input("Proposal title")
        agency = st.selectbox("Funding agency", ["DST", "AICTE", "SERB", "UGC", "Other"])
        budget = st.number_input("Proposed budget (₹)", min_value=1, step=1000, value=100000)
        description = st.text_area("Project summary")
        pdf = st.file_uploader("Proposal document (PDF, maximum 10 MB)", type=["pdf"])
        submitted = st.form_submit_button("Submit proposal", type="primary")
    if submitted:
        errors = []
        if not title.strip():
            errors.append("Proposal title is required.")
        if not description.strip():
            errors.append("Project summary is required.")
        if pdf is None:
            errors.append("Please attach a PDF document.")
        elif pdf.size > 10 * 1024 * 1024:
            errors.append("PDF must not exceed 10 MB.")
        if errors:
            for error in errors:
                st.error(error)
        else:
            new_id = f"RPTS-{st.session_state.next_proposal:03d}"
            st.session_state.next_proposal += 1
            st.session_state.proposals.insert(0, {
                "id": new_id,
                "title": title.strip(),
                "agency": agency,
                "budget": int(budget),
                "pi": st.session_state.display_name,
                "status": "Submitted",
                "submitted": str(date.today()),
                "comment": "",
                "document": pdf.name,
            })
            log_action(f"Submitted proposal {new_id}: {title.strip()}")
            st.success(f"Proposal {new_id} submitted successfully.")
            st.caption("In this demo, the uploaded PDF is validated but is not saved to a permanent server.")

def proposal_review():
    st.title("Proposal Review")
    st.caption("HOD can approve, reject, or return submitted proposals with comments.")
    pending = [p for p in st.session_state.proposals if p["status"] == "Submitted"]
    if not pending:
        st.success("There are no proposals awaiting review.")
        return
    for proposal in pending:
        with st.expander(f"{proposal['id']} · {proposal['title']} · {money(proposal['budget'])}", expanded=True):
            st.write(f"**PI:** {proposal['pi']}  |  **Agency:** {proposal['agency']}")
            st.write(f"**Submitted:** {proposal['submitted']}  |  **Document:** {proposal['document']}")
            comment = st.text_area("Review comment", key=f"comment_{proposal['id']}")
            action = st.radio("Decision", ["Approve", "Reject", "Return for changes"], horizontal=True, key=f"decision_{proposal['id']}")
            if st.button("Save decision", key=f"save_{proposal['id']}", type="primary"):
                if action in ("Reject", "Return for changes") and not comment.strip():
                    st.error("A comment is required when rejecting or returning a proposal.")
                else:
                    proposal["status"] = {"Approve": "Approved", "Reject": "Rejected", "Return for changes": "Returned"}[action]
                    proposal["comment"] = comment.strip()
                    log_action(f"{action} decision for proposal {proposal['id']}")
                    st.success(f"{proposal['id']} marked as {proposal['status']}.")
                    st.rerun()

def milestone_and_funding():
    st.title("Milestones & Funding")
    role = st.session_state.role
    if role in ("Faculty PI", "Research Office"):
        with st.expander("Add a project milestone"):
            project_options = [p["title"] for p in st.session_state.proposals if p["status"] == "Approved"]
            if project_options:
                with st.form("milestone_form"):
                    project = st.selectbox("Approved project", project_options)
                    name = st.text_input("Milestone name")
                    assignee = st.text_input("Assigned scholar", value="Research Scholar")
                    due = st.date_input("Due date", value=date.today())
                    save = st.form_submit_button("Add milestone")
                if save:
                    if name.strip():
                        st.session_state.milestones.append({"project": project, "name": name.strip(), "assignee": assignee, "due": str(due), "status": "In Progress"})
                        log_action(f"Added milestone {name.strip()} to {project}")
                        st.success("Milestone added.")
                        st.rerun()
                    else:
                        st.error("Milestone name is required.")
            else:
                st.info("Approve a proposal before creating project milestones.")

    st.subheader("Project milestones")
    if st.session_state.milestones:
        for i, milestone in enumerate(st.session_state.milestones):
            cols = st.columns([2.2, 1.3, 1.2, 1.2])
            cols[0].write(f"**{milestone['name']}**\n\n{milestone['project']}")
            cols[1].write(milestone["assignee"])
            cols[2].write(milestone["due"])
            if role == "Research Scholar" and milestone["status"] != "Completed":
                if cols[3].button("Mark done", key=f"done_{i}"):
                    milestone["status"] = "Completed"
                    for tranche in st.session_state.tranches:
                        if tranche["project"] == milestone["project"] and tranche["milestone"] == milestone["name"]:
                            tranche["status"] = "Eligible"
                    log_action(f"Completed milestone {milestone['name']}")
                    st.success("Milestone completed. Linked funding tranches are now eligible, if configured.")
                    st.rerun()
            else:
                cols[3].write(milestone["status"])
    else:
        st.info("No milestones available.")

    st.subheader("Funding tranches")
    if role in ("Research Office", "Head of Department"):
        for i, tranche in enumerate(st.session_state.tranches):
            cols = st.columns([2, 1.2, 1, 1.2])
            cols[0].write(f"**{tranche['project']}**\n\n{tranche['milestone']}")
            cols[1].write(money(tranche["amount"]))
            cols[2].write(tranche["status"])
            if role == "Research Office" and tranche["status"] == "Eligible":
                if cols[3].button("Release funds", key=f"release_{i}"):
                    tranche["status"] = "Released"
                    log_action(f"Released {money(tranche['amount'])} for {tranche['project']}")
                    st.success("Funds released.")
                    st.rerun()
            else:
                cols[3].write("—")
    else:
        st.info("Funding tranche details are managed by the Research Office.")

def progress_reports():
    st.title("Monthly Progress Reports")
    if st.session_state.role == "Research Scholar":
        approved_projects = [p["title"] for p in st.session_state.proposals if p["status"] == "Approved"]
        with st.form("progress_form", clear_on_submit=True):
            project = st.selectbox("Project", approved_projects or ["No approved projects"])
            report_month = st.date_input("Report month", value=date.today().replace(day=1))
            summary = st.text_area("Progress summary")
            attachment = st.file_uploader("Report attachment (optional)", type=["pdf", "doc", "docx"])
            submit = st.form_submit_button("Upload progress report", type="primary")
        if submit:
            if not approved_projects:
                st.error("There are no approved projects available.")
            elif not summary.strip():
                st.error("Please enter a progress summary.")
            else:
                st.session_state.progress_reports.insert(0, {
                    "project": project,
                    "scholar": st.session_state.display_name,
                    "month": report_month.strftime("%B %Y"),
                    "summary": summary.strip(),
                    "file": attachment.name if attachment else "No attachment",
                    "date": str(date.today()),
                })
                log_action(f"Uploaded progress report for {project} ({report_month:%B %Y})")
                st.success("Progress report uploaded.")
                st.rerun()
    st.subheader("Submitted reports")
    if st.session_state.progress_reports:
        st.dataframe(pd.DataFrame(st.session_state.progress_reports), use_container_width=True, hide_index=True)
    else:
        st.info("No progress reports have been submitted in this session.")

def publications():
    st.title("Research Publications")
    with st.form("publication_form", clear_on_submit=True):
        project_options = [p["title"] for p in st.session_state.proposals if p["status"] == "Approved"]
        project = st.selectbox("Project", project_options or ["No approved projects"])
        title = st.text_input("Publication title")
        journal = st.text_input("Journal / conference")
        doi = st.text_input("DOI (optional)", placeholder="10.xxxx/example")
        save = st.form_submit_button("Add publication", type="primary")
    if save:
        if not project_options:
            st.error("An approved project is required.")
        elif not title.strip() or not journal.strip():
            st.error("Publication title and journal/conference are required.")
        else:
            st.session_state.publications.insert(0, {"project": project, "title": title.strip(), "journal": journal.strip(), "doi": doi.strip(), "added": str(date.today())})
            log_action(f"Added publication: {title.strip()}")
            st.success("Publication record added.")
            st.rerun()
    st.subheader("Publication records")
    if st.session_state.publications:
        st.dataframe(pd.DataFrame(st.session_state.publications), use_container_width=True, hide_index=True)
    else:
        st.info("No publications recorded yet.")

def agency_report():
    st.title("Quarterly Agency Report")
    proposals = st.session_state.proposals
    rows = []
    for p in proposals:
        rows.append({
            "Proposal ID": p["id"],
            "Project": p["title"],
            "Principal Investigator": p["pi"],
            "Agency": p["agency"],
            "Budget (INR)": p["budget"],
            "Status": p["status"],
            "Submission Date": p["submitted"],
        })
    report_df = pd.DataFrame(rows)
    st.caption("Summary generated from the current demonstration data.")
    if report_df.empty:
        st.info("No project data available.")
    else:
        st.dataframe(report_df, use_container_width=True, hide_index=True)
        csv_data = report_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download agency report (CSV)", csv_data, "rpts_agency_report.csv", "text/csv", type="primary")
        st.download_button("Download report data (JSON)", report_df.to_json(orient="records", indent=2).encode("utf-8"), "rpts_agency_report.json", "application/json")

def audit_trail():
    st.title("Fund Audit Trail")
    st.caption("A demonstration log of actions performed in the current session.")
    if st.session_state.audit:
        st.dataframe(pd.DataFrame(st.session_state.audit), use_container_width=True, hide_index=True)
    else:
        st.info("No actions recorded yet.")

def main():
    if not st.session_state.authenticated:
        login()
        return

    sidebar()
    role = st.session_state.role
    pages = ["Dashboard"]

    if role == "Faculty PI":
        pages += ["Submit Proposal", "Milestones & Funding", "Progress Reports", "Publications", "Agency Report"]
    elif role == "Head of Department":
        pages += ["Proposal Review", "Milestones & Funding", "Agency Report", "Audit Trail"]
    elif role == "Research Scholar":
        pages += ["Milestones & Funding", "Progress Reports", "Publications"]
    elif role == "Research Office":
        pages += ["Proposal Submission", "Milestones & Funding", "Agency Report", "Audit Trail"]

    selected = st.sidebar.radio("Navigation", pages)
    st.sidebar.divider()
    st.sidebar.caption("RPTS · Academic Research Administration")

    if selected == "Dashboard":
        dashboard()
    elif selected in ("Submit Proposal", "Proposal Submission"):
        proposal_submission()
    elif selected == "Proposal Review":
        proposal_review()
    elif selected == "Milestones & Funding":
        milestone_and_funding()
    elif selected == "Progress Reports":
        progress_reports()
    elif selected == "Publications":
        publications()
    elif selected == "Agency Report":
        agency_report()
    elif selected == "Audit Trail":
        audit_trail()

    st.divider()
    st.caption(
        "Prototype notice: this Streamlit version uses temporary session data. "
        "Email notifications and external agency submission are not connected. "
        "The original RPTS project uses React, Express and SQLite."
    )

if __name__ == "__main__":
    main()
