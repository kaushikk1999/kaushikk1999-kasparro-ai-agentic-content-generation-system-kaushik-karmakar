import os
import sys
import json
import subprocess
import glob
from pathlib import Path
import jsonschema

# Check A: Repo naming
def check_repo_naming():
    print("Checking Repo Naming...")
    current_dir = os.path.basename(os.getcwd())
    if not current_dir.startswith("kasparro-ai-agentic-content-generation-system-"):
        print(f"FAIL: Repo name '{current_dir}' does not start with 'kasparro-ai-agentic-content-generation-system-'")
        sys.exit(1)
    print("PASS: Repo naming")

# Check B: Docs check
def check_docs():
    print("Checking Docs...")
    docs_path = Path("docs/projectdocumentation.md")
    if not docs_path.exists():
        print(f"FAIL: {docs_path} does not exist")
        sys.exit(1)
    
    content = docs_path.read_text()
    required = ["Problem Statement", "Solution Overview", "Scopes & Assumptions", "System Design"]
    for req in required:
        if req not in content:
            print(f"FAIL: Docs missing header '{req}'")
            sys.exit(1)
            
    if ("[" in content and "->" in content) or "DAG" in content:
        pass
    else:
        print("FAIL: Docs missing DAG description (did not find DAG keyword or [ -> syntax)")
        sys.exit(1)
    print("PASS: Docs check")

# Check C: Run pipeline
def run_pipeline():
    print("Running Pipeline...")
    # Using strict mode: verify.py runs python main.py
    try:
        subprocess.run([sys.executable, "main.py"], check=True)
    except subprocess.CalledProcessError:
        print("FAIL: Pipeline execution failed")
        sys.exit(1)
    print("PASS: Pipeline run")

# Check D: Output existence + JSON validity
def check_outputs():
    print("Checking Outputs...")
    files = ["outputs/faq.json", "outputs/product_page.json", "outputs/comparison_page.json"]
    for f in files:
        path = Path(f)
        if not path.exists():
            print(f"FAIL: Output {f} missing")
            sys.exit(1)
        try:
            with open(path) as fp:
                json.load(fp)
        except json.JSONDecodeError:
            print(f"FAIL: Output {f} is not valid JSON")
            sys.exit(1)
    print("PASS: Output existence & validity")

# Check E: JSON Schema validation
def check_schemas():
    print("Checking Schemas...")
    schema_map = {
        "outputs/faq.json": "src/schemas/faq_schema.json",
        "outputs/product_page.json": "src/schemas/product_page_schema.json",
        "outputs/comparison_page.json": "src/schemas/comparison_page_schema.json"
    }
    
    for outfile, schemafile in schema_map.items():
        if not os.path.exists(schemafile):
             print(f"FAIL: Schema {schemafile} missing")
             sys.exit(1)
             
        with open(schemafile) as sf:
            schema = json.load(sf)
        with open(outfile) as of:
            instance = json.load(of)
            
        validator = jsonschema.Draft202012Validator(schema)
        try:
            validator.validate(instance)
        except jsonschema.ValidationError as e:
            print(f"FAIL: Schema validation failed for {outfile}: {e.message}")
            sys.exit(1)
    print("PASS: Schema validation")

# Check F: Assignment constraints
def check_constraints():
    print("Checking Constraints...")
    # FAQ
    with open("outputs/faq.json") as f:
        faq = json.load(f)
        # Check if question_bank exists and has length
        qb = faq.get("question_bank", [])
        if len(qb) < 15:
            print(f"FAIL: len(question_bank) < 15 ({len(qb)})")
            sys.exit(1)
        
        categories = {q.get("category") for q in qb if q.get("category")}
        if len(categories) < 5:
            print(f"FAIL: Categories count {len(categories)} < 5")
            sys.exit(1)
            
        # Fact Guard: Usage & Safety
        # Load truth for strict comparison
        with open("data/product_input.json", "r") as f:
            truth = json.load(f)
        
        # Load product_page.json for comparison
        with open("outputs/product_page.json", "r") as f:
            product_page = json.load(f)

        t_usage = truth.get("How to Use", "").strip()
        t_safe = truth.get("Side Effects", "").strip()
        
        p_usage = product_page.get("usage", "").strip()
        p_safe = product_page.get("safety", "")
        
        # Usage must be exact match (or very close if formatting involved, but spec says dataset-only)
        if p_usage != t_usage:
             print(f"FAIL: Product Page usage '{p_usage}' != dataset '{t_usage}'")
             sys.exit(1)

        # Safety: Dataset string must be present (agent adds "Note: " prefix often)
        if t_safe not in p_safe:
             print(f"FAIL: Product Page safety '{p_safe}' does not contain dataset '{t_safe}'")
             sys.exit(1)
            
        if len(faq.get("faqs", [])) < 5:
            print(f"FAIL: len(faqs) < 5 ({len(faq.get('faqs'))})")
            sys.exit(1)

    # Comparison
    with open("outputs/comparison_page.json") as f:
        comp = json.load(f)
        meta = comp.get("meta", {})
        if meta.get("product_b_fictional") is not True:
             print("FAIL: meta.product_b_fictional is not true")
             sys.exit(1)
        
        pb = comp.get("product_b", {})
        required_pb_fields = ["name", "key_ingredients", "benefits", "price"]
        for field in required_pb_fields:
            if field not in pb:
                print(f"FAIL: product_b missing field '{field}'")
                sys.exit(1)

    print("PASS: Constraints")

# Check G: Final 'no new facts' sweep
def check_fact_guard():
    print("Checking Fact Guard...")
    if not os.path.exists("data/product_input.json"):
        print("FAIL: data/product_input.json missing")
        sys.exit(1)
        
    try:
        from src.agents.parse_product import ParseProductAgent
    except ImportError:
        sys.path.append(os.getcwd())
        from src.agents.parse_product import ParseProductAgent

    with open("data/product_input.json") as f:
        raw_input = json.load(f)
    
    agent = ParseProductAgent()
    product_data = agent.run(raw_input)
    
    # Check Product Page
    with open("outputs/product_page.json") as f:
        pp = json.load(f)
        details = pp.get("details", {})
        
        # ingredients
        pp_ing = details.get("ingredients", [])
        if pp_ing != product_data.key_ingredients:
             print(f"FAIL: Product Page ingredients mismatch.\nExpected: {product_data.key_ingredients}\nGot: {pp_ing}")
             sys.exit(1)

        # benefits
        pp_ben = details.get("benefits", [])
        if pp_ben != product_data.benefits:
             print(f"FAIL: Product Page benefits mismatch.\nExpected: {product_data.benefits}\nGot: {pp_ben}")
             sys.exit(1)
             
        # price
        # Pricing might be top level or in details. Checking top level 'pricing' then 'amount'
        if "pricing" in pp:
            pricing = pp["pricing"]
            if "amount" in pricing:
                 if pricing["amount"] != product_data.price_inr:
                     print(f"FAIL: Product Page price mismatch. Expected {product_data.price_inr}, got {pricing['amount']}")
                     sys.exit(1)
        
        # safety (look for side_effects in details as that matches strict property name from parser)
        if "side_effects" in details:
             if details["side_effects"] != product_data.side_effects:
                 print("FAIL: Product Page side_effects mismatch")
                 sys.exit(1)

    # Check Comparison Page (product_a)
    with open("outputs/comparison_page.json") as f:
        cp = json.load(f)
        pa = cp.get("product_a", {})
        
        # If product_a has these fields, they must match
        if "key_ingredients" in pa:
            if pa["key_ingredients"] != product_data.key_ingredients:
                print("FAIL: Comparison Page product_a key_ingredients mismatch")
                sys.exit(1)
        if "benefits" in pa:
            if pa["benefits"] != product_data.benefits:
                print("FAIL: Comparison Page product_a benefits mismatch")
                sys.exit(1)
            
    print("PASS: Fact Guard")

# Check H: Modular + agentic
def check_modularity():
    print("Checking Modularity...")
    agents = glob.glob("src/agents/*.py")
    # exclude __init__
    agents = [a for a in agents if "__init__" not in a]
    if len(agents) < 5:
        print(f"FAIL: Fewer than 5 agent modules found ({len(agents)})")
        sys.exit(1)
        
    templates = ["src/templates/faq_template.py", "src/templates/product_template.py", "src/templates/comparison_template.py"]
    for t in templates:
        if not os.path.exists(t):
            print(f"FAIL: Template {t} missing")
            sys.exit(1)
            
    if not os.path.exists("src/blocks") or not os.path.isdir("src/blocks"):
         print("FAIL: src/blocks missing or not dir")
         sys.exit(1)
         
    blocks = glob.glob("src/blocks/*.py")
    if len(blocks) < 2:
        print("FAIL: src/blocks seems empty or too few blocks")
        sys.exit(1)

    print("PASS: Modularity")

# Check I: Test suite
def check_tests():
    print("Running Tests...")
    try:
        subprocess.run([sys.executable, "-m", "pytest", "-q"], check=True)
    except subprocess.CalledProcessError:
        print("FAIL: Tests failed")
        sys.exit(1)
    print("PASS: Test suite")

if __name__ == "__main__":
    check_repo_naming()
    check_docs()
    run_pipeline()
    check_outputs()
    check_schemas()
    check_constraints()
    check_fact_guard()
    check_modularity()
    check_tests()
    
    print("\n✅ VERIFICATION COMPLETE: ALL CHECKS PASSED")
