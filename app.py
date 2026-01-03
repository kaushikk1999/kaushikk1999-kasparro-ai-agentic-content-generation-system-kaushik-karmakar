import streamlit as st
import json
import os
import time
import uuid
import subprocess
import sys
from datetime import datetime, timezone
from jsonschema.validators import Draft202012Validator
from jsonschema.exceptions import ValidationError, SchemaError

st.set_page_config(page_title="Kasparro Content Viewer", layout="wide")


st.title("Kasparro AI Content Preview")

# --- Pipeline execution proof state ---
if "pipeline_running" not in st.session_state:
    st.session_state.pipeline_running = False


if "last_run_meta" not in st.session_state:
    st.session_state.last_run_meta = None   # will hold dict like {"run_id":..., "started_at":..., "finished_at":..., "exit_code":...}

RUN_META_PATH = os.path.join("outputs", "ui_run_meta.json")

def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def save_run_meta(meta: dict):
    # Safe best-effort persistence (works in local + most deployments)
    try:
        with open(RUN_META_PATH, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
    except Exception:
        pass

def load_saved_run_meta():
    try:
        if os.path.exists(RUN_META_PATH):
            with open(RUN_META_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        return None
    return None

def run_pipeline_with_proof():
    run_id = str(uuid.uuid4())[:8]
    run_id = str(uuid.uuid4())[:8]
    started_at = now_iso()
    t0 = time.time()
    st.session_state.pipeline_running = True

    meta = {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": None,
        "duration_sec": None,
        "exit_code": None,
        "error": None,
    }
    st.session_state.last_run_meta = meta
    save_run_meta(meta)

    # A visible long-running status container in the UI
    with st.status(f"Running agent pipeline (run {run_id})...", expanded=True, state="running") as status:
        st.write(f"**Started:** {started_at}")
        st.write("Executing: `python main.py`")

        try:
            # Capture output so we can show proof inside the UI
            result = subprocess.run(
                [sys.executable, "main.py"],
                check=False,
                capture_output=True,
                text=True,
            )

            # Show subprocess logs as execution proof
            if result.stdout:
                st.code(result.stdout, language="text")
            if result.stderr:
                st.code(result.stderr, language="text")

            finished_at = now_iso()
            duration = round(time.time() - t0, 2)
            meta["finished_at"] = finished_at
            meta["duration_sec"] = duration
            meta["exit_code"] = result.returncode

            if result.returncode == 0:
                status.update(label=f"Pipeline complete (run {run_id})", state="complete", expanded=False)
                st.toast(f"Pipeline finished ✅ (run {run_id}) in {duration}s")  # optional
            else:
                meta["error"] = f"Pipeline failed with exit code {result.returncode}"
                status.update(label=f"Pipeline failed (run {run_id})", state="error", expanded=True)
                st.toast(f"Pipeline failed ❌ (run {run_id})")  # optional

            st.session_state.last_run_meta = meta
            save_run_meta(meta)

        except Exception as e:
            finished_at = now_iso()
            duration = round(time.time() - t0, 2)
            meta["finished_at"] = finished_at
            meta["duration_sec"] = duration
            meta["exit_code"] = -1
            meta["error"] = str(e)

            st.session_state.last_run_meta = meta
            save_run_meta(meta)

            status.update(label=f"Pipeline exception (run {run_id})", state="error", expanded=True)
            st.exception(e)

        finally:
            st.session_state.pipeline_running = False

    # Force a clean rerun so the app reloads fresh outputs after completion.
    st.rerun()  # reruns immediately; stops further execution in this run


# Helper to load JSON
def load_json(filename):
    path = os.path.join("outputs", filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

def validate_against_schema(data, schema_path: str):
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    Draft202012Validator.check_schema(schema)  # validates the schema itself
    Draft202012Validator(schema).validate(data)  # validates the instance

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Product Page", "FAQ Page", "Comparison Page", "Validation Summary"])

# --- Validation Summary ---
with tab4:
    st.header("Pipeline Validation Summary")

    # Pull last run meta from session_state, fall back to saved file
    meta = st.session_state.last_run_meta or load_saved_run_meta()

    if meta:
        st.subheader("Execution Proof")
        st.write(f"**Last run ID:** {meta.get('run_id')}")
        st.write(f"**Started:** {meta.get('started_at')}")
        st.write(f"**Finished:** {meta.get('finished_at')}")
        st.write(f"**Duration:** {meta.get('duration_sec')}s")
        st.write(f"**Exit code:** {meta.get('exit_code')}")
        if meta.get("error"):
            st.error(meta["error"])
    else:
        st.info("No pipeline run recorded yet. Click 'Regenerate Content'.")

    
    # 1. File Existence
    files = ["product_page.json", "faq.json", "comparison_page.json"]
    missing = [f for f in files if not os.path.exists(os.path.join("outputs", f))]
    
    if missing:
        st.error(f"Missing Files: {missing}")
    else:
        st.success("All required JSON artifacts exist.")
        
        # 2. Content Checks
        faq_data = load_json("faq.json")
        comp_data = load_json("comparison_page.json")
        

        # Counts
        q_bank = faq_data.get("question_bank", [])
        q_count = len(q_bank)
        f_count = len(faq_data.get("faqs", []))
        
        # New checks: Categories & Uniqueness
        cats = {q.get("category") for q in q_bank if q.get("category")}
        questions_text = [q.get("question","").strip() for q in q_bank]
        unique_q_count = len(set([q for q in questions_text if q]))

        # Display Metrics (2 rows or 5 cols)
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Generated Questions", q_count, delta="≥ 15" if q_count >= 15 else "-FAIL")
        c2.metric("FAQ Answers", f_count, delta="≥ 5" if f_count >= 5 else "-FAIL")
        c3.metric("Categories", len(cats), delta="≥ 5" if len(cats) >= 5 else "-FAIL")
        c4.metric("Unique Questions", unique_q_count, delta="Pass" if unique_q_count == q_count else "Duplicate Found")

        

        # Product B Check
        pb = comp_data.get("product_b", {})
        pb_keys = set(pb.keys())
        req_keys = {"name", "key_ingredients", "benefits", "price"}
        missing_pb = req_keys - pb_keys
        
        c5.metric("Product B Structure", "PASS" if not missing_pb else "FAIL")

        if missing_pb:
            st.error(f"Product B missing keys: {missing_pb}")
            
        # 3. Schema Check (Live)
        st.subheader("Schema Compliance (live)")
        schema_map = {
            "faq.json": "src/schemas/faq_schema.json",
            "product_page.json": "src/schemas/product_page_schema.json",
            "comparison_page.json": "src/schemas/comparison_page_schema.json",
        }
        
        for out_file, schema_file in schema_map.items():
            data = load_json(out_file)
            if not data:
                st.error(f"{out_file}: missing")
                continue
            try:
                validate_against_schema(data, schema_file)
                st.success(f"{out_file}: Schema PASS")
            except (ValidationError, SchemaError) as e:
                st.error(f"{out_file}: Schema FAIL")
                st.code(str(e))


# --- Product Page ---
with tab1:
    data = load_json("product_page.json")
    if data:
        st.header(data.get("hero", {}).get("title", "Product Title"))
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Details")
            st.write("**Ingredients:**", ", ".join(data.get("details", {}).get("ingredients", [])))
            st.write("**Benefits:**", ", ".join(data.get("details", {}).get("benefits", [])))
            
        with col2:
            st.subheader("Pricing")
            pricing = data.get("pricing", {})
            st.metric("Price", f"{pricing.get('amount', 0)} {pricing.get('currency', 'USD')}")
            
        st.subheader("Usage")
        st.info(data.get("usage", "N/A"))
        
        st.subheader("Safety")
        st.warning(data.get("safety", "N/A"))
        

        st.json(data)
        st.download_button(
            label="Download Product JSON",
            data=json.dumps(data, indent=2),
            file_name="product_page.json",
            mime="application/json"
        )
    else:
        st.error("outputs/product_page.json not found")

# --- FAQ Page ---
with tab2:
    data = load_json("faq.json")
    if data:
        st.header(f"FAQ: {data.get('title', 'Product')}")
        
        for item in data.get("faqs", []):
            with st.expander(item.get("question", "Q?")):
                st.write(item.get("answer", "A."))
                
        st.divider()
        st.subheader("Raw Data")
        st.json(data)
        st.download_button(
            label="Download FAQ JSON",
            data=json.dumps(data, indent=2),
            file_name="faq.json",
            mime="application/json"
        )
    else:
        st.error("outputs/faq.json not found")


# --- Comparison Page ---
with tab3:
    data = load_json("comparison_page.json")
    if data:
        st.header("Product Comparison")
        st.json(data) # Rendering table from JSON cleanly requires known schema, dumping JSON for now as fallback
        
        st.download_button(
            label="Download Comparison JSON",
            data=json.dumps(data, indent=2),
            file_name="comparison_page.json",
            mime="application/json"
        )
    else:
        st.error("outputs/comparison_page.json not found")

# --- Sidebar: Pipeline Control ---
with st.sidebar:
    st.header("Control Panel")

    # Disable button while pipeline is running to avoid overlapping runs
    if st.button("Regenerate Content", disabled=st.session_state.pipeline_running):
        with st.spinner("Running Agent Pipeline..."):  # spinner is built for this use
            run_pipeline_with_proof()


    st.subheader("Download All")
    # Quick access to download all if they exist
    for f_name in ["product_page.json", "faq.json", "comparison_page.json"]:
        d = load_json(f_name)
        if d:
            st.download_button(
                label=f"Download {f_name}",
                data=json.dumps(d, indent=2),
                file_name=f_name,
                mime="application/json",
                key=f"dl_sidebar_{f_name}"
            )

