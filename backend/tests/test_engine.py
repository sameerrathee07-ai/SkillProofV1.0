import pytest
from engine.validation import process_answer, StepResult
from engine.scoring import score_pitch, DimensionScore
from engine.gate import gate_decision, GATE_THRESHOLD
from engine.suggestions import generate_suggestions
from engine.outline import generate_outline
from engine.parser import parse_pitch_lines, build_pitch_text

class TestValidation:
    def test_step1_pass(self):
        ans = "A mobile app that automatically schedules hotel housekeeping shifts and alerts managers when rooms are delayed."
        res = process_answer(1, ans)
        assert res.passed is True
        assert res.next_step == 2
    
    def test_step1_fail_short(self):
        ans = "A short one."
        res = process_answer(1, ans)
        assert res.passed is False
        assert res.next_step == 1
        assert "10 words" in res.reply
    
    def test_step1_fail_no_verb(self):
        ans = "This is a solution for the problem that we have here today."
        res = process_answer(1, ans)
        assert res.passed is False
        assert "action verb" in res.reply
    
    def test_step1_empty(self):
        res = process_answer(1, "   ")
        assert res.passed is False
        assert "empty" in res.reply.lower()
    
    def test_step2_pass(self):
        ans = "Front-desk managers at mid-size hotels lose hours every day reassigning rooms by hand, which delays check-ins and frustrates guests."
        res = process_answer(2, ans)
        assert res.passed is True
        assert res.next_step == 3
    
    def test_step2_fail_no_role(self):
        ans = "The company has a problem with delays."
        res = process_answer(2, ans)
        assert res.passed is False
        assert "role" in res.reply.lower()
    
    def test_step2_fail_no_pain(self):
        ans = "Front-desk managers work at the hotel."
        res = process_answer(2, ans)
        assert res.passed is False
        assert "pain" in res.reply.lower()
    
    def test_step3_pass(self):
        ans = "We charge Rs 4,999 per month per hotel, which pays back in one month because it saves about 40 staff hours compared to manual scheduling."
        res = process_answer(3, ans)
        assert res.passed is True
        assert res.next_step == 4
    
    def test_step3_fail_no_price(self):
        ans = "It is a good product that saves time."
        res = process_answer(3, ans)
        assert res.passed is False
        assert "price" in res.reply.lower()
    
    def test_step3_fail_no_justification(self):
        ans = "We charge Rs 5000."
        res = process_answer(3, ans)
        assert res.passed is False
        assert "justify" in res.reply.lower()
    
    def test_step4_pass(self):
        ans = "Hotels currently use Excel sheets or Opera PMS add-ons, but this is different because it reassigns rooms live from check-out signals."
        res = process_answer(4, ans)
        assert res.passed is True
        assert res.next_step == 5
    
    def test_step4_fail_one_alt(self):
        ans = "we use excel."
        res = process_answer(4, ans)
        assert res.passed is False
        assert "2 distinct alternatives" in res.reply
    
    def test_step4_fail_no_diff(self):
        ans = "Hotels use Excel sheets and manual process."
        res = process_answer(4, ans)
        assert res.passed is False
        assert "why yours is better" in res.reply.lower()
    
    def test_step5_pass(self):
        ans = "I have two years of experience building hotel software as an intern and my advantage is a family-run hotel where I can test it daily."
        res = process_answer(5, ans)
        assert res.passed is True
        assert res.next_step == 5
        assert "complete" in res.reply.lower()
    
    def test_step5_fail_no_exp(self):
        ans = "I am new to this."
        res = process_answer(5, ans)
        assert res.passed is False
        assert "experience" in res.reply.lower()
    
    def test_step5_fail_no_advantage(self):
        ans = "I have built many projects."
        res = process_answer(5, ans)
        assert res.passed is False
        assert "advantage" in res.reply.lower()

class TestScoring:
    def test_strong_pitch_scores(self):
        pitch = (
            "[1] A mobile app that automatically schedules hotel housekeeping shifts and alerts managers when rooms are delayed. "
            "[2] Front-desk managers at mid-size hotels lose hours every day reassigning rooms by hand, which delays check-ins and frustrates guests. "
            "[3] We charge Rs 4,999 per month per hotel, which pays back in one month because it saves about 40 staff hours compared to manual scheduling. "
            "[4] Hotels currently use Excel sheets or Opera PMS add-ons, but this is different because it reassigns rooms live from check-out signals. "
            "[5] I have two years of experience building hotel software as an intern and my advantage is a family-run hotel where I can test it daily."
        )
        parsed = parse_pitch_lines(pitch)
        scores, feedback = score_pitch(pitch, parsed)
        
        assert len(scores) == 6
        for s in scores:
            assert isinstance(s, DimensionScore)
            assert 1 <= s.score <= 10
        assert feedback
        assert isinstance(feedback, str)
    
    def test_weak_pitch_scores(self):
        pitch = (
            "[1] A short one. "
            "[2] It helps the company. "
            "[3] It is a good product. "
            "[4] Nobody does this. "
            "[5] I am a student."
        )
        parsed = parse_pitch_lines(pitch)
        scores, feedback = score_pitch(pitch, parsed)
        
        assert len(scores) == 6
        for s in scores:
            assert 1 <= s.score <= 10
        assert feedback
    
    def test_score_bounds(self):
        pitch = "[1] " + "build " * 20 + "[2] manager pain " * 10 + "[3] Rs 1000 saves " * 10 + "[4] Excel manual vs better " * 10 + "[5] built shipped advantage " * 10
        parsed = parse_pitch_lines(pitch)
        scores, _ = score_pitch(pitch, parsed)
        for s in scores:
            assert s.score <= 10
            assert s.score >= 1

class TestGate:
    def test_gate_pass(self):
        scores = [DimensionScore(n, 7, "") for n in ["Problem Clarity", "Customer Specificity", "Cost and Value Case", "Alternatives Awareness", "Solver Capability", "Delivery Readiness"]]
        passed, avg = gate_decision(scores)
        assert passed is True
        assert avg >= GATE_THRESHOLD
    
    def test_gate_fail(self):
        scores = [DimensionScore(n, 5, "") for n in ["Problem Clarity", "Customer Specificity", "Cost and Value Case", "Alternatives Awareness", "Solver Capability", "Delivery Readiness"]]
        passed, avg = gate_decision(scores)
        assert passed is False
        assert avg < GATE_THRESHOLD
    
    def test_gate_threshold_exact(self):
        scores = [DimensionScore(n, 6, "") for n in ["Problem Clarity", "Customer Specificity", "Cost and Value Case", "Alternatives Awareness", "Solver Capability", "Delivery Readiness"]]
        passed, avg = gate_decision(scores)
        assert passed is True
        assert avg == 6.0

class TestSuggestions:
    def test_suggestions_generated(self):
        scores = [DimensionScore("Problem Clarity", 4, ""), DimensionScore("Customer Specificity", 6, "")]
        suggestions = generate_suggestions(scores)
        assert "Problem Clarity" in suggestions
        assert "Customer Specificity" in suggestions
        assert "concrete cost" in suggestions["Problem Clarity"]

class TestOutline:
    def test_outline_generation(self):
        pitch = "[1] Solution does X. [2] Role feels pain. [3] Rs 1000 saves time. [4] Excel manual vs better. [5] Built project advantage."
        outline = generate_outline(pitch, "Test Solver")
        assert outline["solver_name"] == "Test Solver"
        assert "Problem" in outline
        assert "Solution" in outline
        assert "Affected People" in outline
        assert "Cost and Value" in outline
        assert "Alternatives and Edge" in outline
        assert "Solver and Advantage" in outline
        assert "Proposed Next Step" in outline

class TestParser:
    def test_parse_pitch_lines(self):
        pitch = "[1] Answer one. [2] Answer two. [3] Answer three."
        parsed = parse_pitch_lines(pitch)
        assert parsed[1] == "Answer one."
        assert parsed[2] == "Answer two."
        assert parsed[3] == "Answer three."
        assert 4 not in parsed
        assert 5 not in parsed
    
    def test_build_pitch_text(self):
        answers = {1: "One", 2: "Two", 3: "Three"}
        text = build_pitch_text(answers)
        assert "[1] One" in text
        assert "[2] Two" in text
        assert "[3] Three" in text
    
    def test_parse_multiline(self):
        pitch = "[1] First answer\nwith multiple lines. [2] Second answer."
        parsed = parse_pitch_lines(pitch)
        assert "First answer" in parsed[1]
        assert "multiple lines" in parsed[1]
        assert parsed[2] == "Second answer."

class TestCalibration:
    STRONG_PITCHES = [
        "[1] A mobile app that automatically schedules hotel housekeeping shifts and alerts managers when rooms are delayed. [2] Front-desk managers at mid-size hotels lose hours every day reassigning rooms by hand, which delays check-ins and frustrates guests. [3] We charge Rs 4,999 per month per hotel, which pays back in one month because it saves about 40 staff hours compared to manual scheduling. [4] Hotels currently use Excel sheets or Opera PMS add-ons, but this is different because it reassigns rooms live from check-out signals. [5] I have two years of experience building hotel software as an intern and my advantage is a family-run hotel where I can test it daily.",
        "[1] An automated tool that generates financial compliance reports for NBFCs and flags discrepancies in real time. [2] Compliance officers at mid-sized NBFCs spend weeks manually compiling RBI reports, risking penalties for late or erroneous filings. [3] Priced at Rs 15,000 per month per branch, it saves 200 staff hours monthly versus manual compilation, paying back in week one. [4] Current alternatives are manual Excel compilation or legacy core banking modules, but this tool auto-validates against RBI schemas before submission. [5] I have three years as a fintech developer at a payments startup and my edge is direct access to a compliant NBFC for pilot testing.",
        "[1] A scheduling platform that creates conflict-free timetables for university departments and notifies faculty of changes instantly. [2] Department admins at state universities waste days resolving room and faculty conflicts each semester, delaying publication and frustrating students. [3] Rs 25,000 per semester per department, saving 80 admin hours versus manual scheduling, break-even in week two. [4] Alternatives are manual spreadsheet scheduling or generic ERP modules, but this handles faculty preferences and room constraints natively. [5] I built a similar scheduler as a capstone project and my advantage is a professor advisor who chairs the timetable committee.",
        "[1] A chatbot that handles routine guest queries for boutique hotels and escalates complex requests to staff. [2] Front-desk staff at boutique hotels spend 40% of shift time answering repetitive questions, causing check-in queues and guest complaints. [3] Rs 3,000 per month per property, saves 60 staff hours monthly versus manual responses, ROI in week two. [4] Alternatives are hiring more staff or basic IVR systems, but this understands natural language and integrates with PMS. [5] I interned at a hotel tech startup building chat integrations and my edge is a pilot hotel owned by a family friend.",
        "[1] A dashboard that tracks student attendance and alerts counselors when patterns indicate dropout risk. [3] College counselors at community colleges manually review attendance weekly, missing early warnings for at-risk students who silently disengage. [3] Rs 8,000 per month per campus, saves 30 counselor hours monthly versus manual review, pays back in month one. [4] Alternatives are manual spreadsheet tracking or generic SIS alerts, but this uses ML to flag subtle patterns. [5] I built an attendance tracker for a hackathon and my advantage is access to anonymized data from a partner college for validation.",
    ]
    
    WEAK_PITCHES = [
        "[1] A short one. [2] It helps the company. [3] It is a good product. [4] Nobody does this. [5] I am a student.",
        "[1] An app for hotels. [2] Everyone benefits. [3] Free maybe. [4] No competition. [5] Just started learning.",
        "[1] A tool that does things. [2] All people like it. [3] Not sure about cost. [4] First ever solution. [5] No experience yet.",
        "[1] Software for schools. [2] Global problem. [3] Depends on budget. [4] Only one like it. [5] Beginner here.",
        "[1] Platform for everyone. [2] Worldwide issue. [3] Negotiable price. [4] Monopoly market. [5] Never done this before.",
    ]
    
    @pytest.mark.parametrize("pitch", STRONG_PITCHES)
    def test_strong_pitches_pass_gate(self, pitch):
        parsed = parse_pitch_lines(pitch)
        scores, _ = score_pitch(pitch, parsed)
        passed, avg = gate_decision(scores)
        assert passed is True, f"Strong pitch failed gate: avg={avg:.2f}, scores={[s.score for s in scores]}"
    
    @pytest.mark.parametrize("pitch", WEAK_PITCHES)
    def test_weak_pitches_fail_gate(self, pitch):
        parsed = parse_pitch_lines(pitch)
        scores, _ = score_pitch(pitch, parsed)
        passed, avg = gate_decision(scores)
        assert passed is False, f"Weak pitch passed gate: avg={avg:.2f}, scores={[s.score for s in scores]}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])