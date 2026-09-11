import urllib.request
import json

BASE_URL = "http://127.0.0.1:8000"

def post(url, data, token=None):
    req = urllib.request.Request(
        f"{BASE_URL}{url}",
        data=json.dumps(data).encode('utf-8'),
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {token}"} if token else {})
        }
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

def get(url, token=None):
    req = urllib.request.Request(
        f"{BASE_URL}{url}",
        headers={"Authorization": f"Bearer {token}"} if token else {}
    )
    with urllib.request.urlopen(req) as resp:
        content_type = resp.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return json.loads(resp.read().decode('utf-8'))
        return resp.read()

def run_tests():
    print("=== STARTING SKILLPROOF FULL END-TO-END AUTOMATED VERIFICATION ===")

    # 1. Clear Database
    print("\n1. Clearing database state...")
    req = urllib.request.Request(f"{BASE_URL}/admin/clear", method="DELETE")
    urllib.request.urlopen(req)
    print("[PASS] Database cleared")

    # 2. Poster Signup & Login
    print("\n2. Testing Poster Registration & Authentication...")
    poster_auth = post("/auth/signup", {
        "fullName": "Hotel Operations Manager",
        "organization": "Heritage Palace Hotel",
        "email": "poster_test@heritage.com",
        "password": "password123",
        "role": "poster"
    })
    poster_token = poster_auth["access_token"]
    assert poster_auth["role"] == "poster"
    print(f"[PASS] Poster registered with token. User ID: {poster_auth['user_id']}")

    # 3. Post Problem with Heuristic Validation
    print("\n3. Testing Problem Posting & Server-side Validation...")
    problem = post("/problems", {
        "title": "Automate Guest Check-In & Digital Key Dispatch",
        "description": "Our 100-room heritage hotel checks in 40+ guests daily causing 25-minute lobby bottlenecks. We need an automated web app with QR check-in and digital key dispatch.",
        "category": "Hospitality",
        "budgetRange": "₹30,000 - ₹60,000",
        "timeline": "3 weeks"
    }, token=poster_token)
    problem_id = problem["problem_id"]
    print(f"[PASS] Problem posted successfully. Problem ID: {problem_id}")

    # 4. Solver Signup & Login
    print("\n4. Testing Solver Registration & Authentication...")
    solver_auth = post("/auth/signup", {
        "fullName": "Aarav Gupta",
        "organization": "IIT Delhi",
        "email": "aarav.solver@iitd.ac.in",
        "password": "password123",
        "role": "solver"
    })
    solver_token = solver_auth["access_token"]
    assert solver_auth["role"] == "solver"
    print(f"[PASS] Solver registered. User ID: {solver_auth['user_id']}")

    # 5. Browse Problems
    print("\n5. Testing Browse Problems Endpoint...")
    problems_list = get("/problems?category=Hospitality")
    assert len(problems_list["items"]) >= 1
    print(f"[PASS] Found {len(problems_list['items'])} Hospitality problem(s)")

    # 6. Step-by-Step Pitch Gate Progression
    print("\n6. Testing 5-Step Pitch Gate Validation...")
    
    # Step 1: Pushback on short answer
    step1_fail = post(f"/pitch/{problem_id}/step/1/validate", {
        "step": 1,
        "response": "Short idea."
    }, token=solver_token)
    assert step1_fail["valid"] is False
    print(f"[PASS] Quality gate pushback on Step 1: '{step1_fail['message']}'")

    # Step 1: Pass
    step1_pass = post(f"/pitch/{problem_id}/step/1/validate", {
        "step": 1,
        "response": "We build a progressive web application that automates guest mobile check-in via QR scan and issues secure digital room keys instantly."
    }, token=solver_token)
    assert step1_pass["valid"] is True
    print("[PASS] Step 1 Validated successfully")

    # Step 2: Pass
    step2_pass = post(f"/pitch/{problem_id}/step/2/validate", {
        "step": 2,
        "response": "Front desk managers and 4 staff members who suffer from severe 25-minute lobby check-in bottlenecks and manual paper register fatigue daily."
    }, token=solver_token)
    assert step2_pass["valid"] is True
    print("[PASS] Step 2 Validated successfully")

    # Step 3: Pass
    step3_pass = post(f"/pitch/{problem_id}/step/3/validate", {
        "step": 3,
        "response": "We charge a recurring ₹4,000 monthly software fee, which saves the hotel over ₹20,000 monthly in overtime staffing costs."
    }, token=solver_token)
    assert step3_pass["valid"] is True
    print("[PASS] Step 3 Validated successfully")

    # Step 4: Pass
    step4_pass = post(f"/pitch/{problem_id}/step/4/validate", {
        "step": 4,
        "response": "Compared to physical RFID key encoders and manual paper sheets, our system is faster, requires no hardware app download, and delivers a unique custom guest portal."
    }, token=solver_token)
    assert step4_pass["valid"] is True
    print("[PASS] Step 4 Validated successfully")

    # Step 5: Pass
    step5_pass = post(f"/pitch/{problem_id}/step/5/validate", {
        "step": 5,
        "response": "I have 3 years of web software development experience and built the guest check-in portal for Taj Hotels during my final year engineering project."
    }, token=solver_token)
    assert step5_pass["valid"] is True
    print("[PASS] Step 5 Validated successfully")

    # 7. Submit Pitch & Run Scoring Engine
    print("\n7. Submitting Pitch & Evaluating 6 Quality Dimensions...")
    pitch_submit = post(f"/pitch/{problem_id}/submit", {
        "problem_id": problem_id,
        "responses": {
            "step1": "We build a progressive web application that automates guest mobile check-in via QR scan and issues secure digital room keys instantly.",
            "step2": "Front desk managers and 4 staff members who suffer from severe 25-minute lobby check-in bottlenecks and manual paper register fatigue daily.",
            "step3": "We charge a recurring ₹4,000 monthly software fee, which saves the hotel over ₹20,000 monthly in overtime staffing costs.",
            "step4": "Compared to physical RFID key encoders and manual paper sheets, our system is faster, requires no hardware app download, and delivers a unique custom guest portal.",
            "step5": "I have 3 years of web software development experience and built the guest check-in portal for Taj Hotels during my final year engineering project."
        }
    }, token=solver_token)

    proposal_id = pitch_submit["proposal_id"]
    avg_score = pitch_submit["average_score"]
    status = pitch_submit["status"]
    print(f"[PASS] Pitch Scored! Average Score: {avg_score} / 10 | Status: {status}")
    assert avg_score >= 6.0
    assert status == "submitted"

    # 8. Fetch Proposal Detail
    print("\n8. Testing Proposal Detail Retrieval...")
    prop_detail = get(f"/proposals/{proposal_id}", token=poster_token)
    assert prop_detail["proposal_id"] == proposal_id
    assert prop_detail["solver_name"] == "Aarav Gupta"
    print(f"[PASS] Proposal detail loaded for {prop_detail['solver_name']}. 6 dimensions:")
    for dim, score in prop_detail["dimension_scores"].items():
        print(f"    - {dim}: {score}/10")

    # 9. Test PDF Report Generation
    print("\n9. Testing ReportLab PDF Generation...")
    pdf_bytes = get(f"/proposals/{proposal_id}/pdf", token=poster_token)
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")
    print(f"[PASS] Valid ReportLab PDF generated ({len(pdf_bytes)} bytes)")

    # 10. Solver Profile Credibility Aggregation
    print("\n10. Testing Solver Profile Credibility Aggregator...")
    solver_profile = get(f"/solver/{solver_auth['user_id']}")
    assert solver_profile["total_proposals"] == 1
    assert solver_profile["passed_first_attempt"] == 1
    print(f"[PASS] Solver profile credibility score: {solver_profile['credibility_score']} / 5.0")

    # 11. Poster Dashboard Listings & Metrics
    print("\n11. Testing Poster Dashboard Listings & Metrics...")
    listings = get("/my-listings", token=poster_token)
    assert listings["total"] == 1
    assert listings["metrics"]["total_posted"] == 1
    print(f"[PASS] Poster metrics verified: {listings['metrics']}")

    # 12. Full Demo Loop Admin Seeder
    print("\n12. Testing Admin Seed Full Demo Loop...")
    demo_loop = post("/admin/seed/full-demo-loop", {})
    assert demo_loop["score"] >= 6.0
    print(f"[PASS] Admin demo loop executed successfully! Demo proposal ID: {demo_loop['proposal_id']}")

    print("\n=======================================================")
    print("ALL 12 END-TO-END AUTOMATED TESTS PASSED WITH 100% SUCCESS!")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
