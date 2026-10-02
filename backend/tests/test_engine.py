import pytest
from app.engine import (
    validate_step, process_answer, score_pitch, gate_decision,
    generate_outline, compute_credibility, _parse_pitch_lines,
    Step, COMPLETE_MESSAGE
)


class TestValidation:
    def test_step1_pass(self):
        answer = "A mobile app that automatically schedules hotel housekeeping shifts and alerts managers when rooms are delayed."
        passed, reply = validate_step(Step.IDEA, answer)
        assert passed is True
        assert "Good" in reply
    
    def test_step1_fail_short(self):
        answer = "A short one."
        passed, reply = validate_step(Step.IDEA, answer)
        assert passed is False
        assert "action verb" in reply
    
    def test_step1_fail_no_verb(self):
        answer = "This is a solution for the problem that helps companies."
        passed, reply = validate_step(Step.IDEA, answer)
        assert passed is False
    
    def test_step2_pass(self):
        answer = "Front-desk managers at mid-size hotels lose hours every day reassigning rooms by hand, which delays check-ins and frustrates guests."
        passed, reply = validate_step(Step.CUSTOMER, answer)
        assert passed is True
    
    def test_step2_fail_no_role(self):
        answer = "It helps the company."
        passed, reply = validate_step(Step.CUSTOMER, answer)
        assert passed is False
    
    def test_step3_pass(self):
        answer = "We charge Rs 4,999 per month per hotel, which pays back in one month because it saves about 40 staff hours compared to manual scheduling."
        passed, reply = validate_step(Step.COST_VALUE, answer)
        assert passed is True
    
    def test_step3_fail_no_price(self):
        answer = "It is a good product."
        passed, reply = validate_step(Step.COST_VALUE, answer)
        assert passed is False
    
    def test_step4_pass(self):
        answer = "Hotels currently use Excel sheets or Opera PMS add-ons, but this is different because it reassigns rooms live from check-out signals."
        passed, reply = validate_step(Step.ALTERNATIVES, answer)
        assert passed is True
    
    def test_step4_fail_few_alternatives(self):
        answer = "Nobody does this."
        passed, reply = validate_step(Step.ALTERNATIVES, answer)
        assert passed is False
    
    def test_step5_pass(self):
        answer = "I have two years of experience building hotel software as an intern and my advantage is a family-run hotel where I can test it daily."
        passed, reply = validate_step(Step.SOLVER, answer)
        assert passed is True
    
    def test_step5_fail_no_experience(self):
        answer = "I am a student."
        passed, reply = validate_step(Step.SOLVER, answer)
        assert passed is False
    
    def test_empty_answer(self):
        for step in Step:
            passed, reply = validate_step(step, "   ")
            assert passed is False
            assert "empty" in reply.lower()
    
    def test_whitespace_only(self):
        passed, reply = validate_step(Step.IDEA, "\n\t  ")
        assert passed is False


class TestProcessAnswer:
    def test_advances_on_pass(self):
        answer = "A mobile app that automatically schedules hotel housekeeping shifts and alerts managers when rooms are delayed."
        result = process_answer(1, answer)
        assert result.passed is True
        assert result.next_step == 2
    
    def test_stays_on_fail(self):
        answer = "A short one."
        result = process_answer(1, answer)
        assert result.passed is False
        assert result.next_step == 1
    
    def test_step5_completes(self):
        answer = "I have two years of experience building hotel software as an intern and my advantage is a family-run hotel where I can test it daily."
        result = process_answer(5, answer)
        assert result.passed is True
        assert result.next_step == 5
        assert COMPLETE_MESSAGE in result.reply


class TestParsePitchLines:
    def test_parses_correctly(self):
        pitch = "[1] First answer\n[2] Second answer\n[3] Third answer"
        result = _parse_pitch_lines(pitch)
        assert result[1] == "First answer"
        assert result[2] == "Second answer"
        assert result[3] == "Third answer"
    
    def test_ignores_invalid_lines(self):
        pitch = "[1] Valid\ninvalid line\n[2] Also valid"
        result = _parse_pitch_lines(pitch)
        assert len(result) == 2


class TestScoring:
    def test_strong_pitch_scores(self):
        pitch = (
            "[1] A mobile app that automatically schedules hotel housekeeping shifts and alerts managers when rooms are delayed.\n"
            "[2] Front-desk managers at mid-size hotels lose hours every day reassigning rooms by hand, which delays check-ins and frustrates guests.\n"
            "[3] We charge Rs 4,999 per month per hotel, which pays back in one month because it saves about 40 staff hours compared to manual scheduling.\n"
            "[4] Hotels currently use Excel sheets or Opera PMS add-ons, but this is different because it reassigns rooms live from check-out signals.\n"
            "[5] I have two years of experience building hotel software as an intern and my advantage is a family-run hotel where I can test it daily."
        )
        scores, feedback = score_pitch(pitch)
        
        assert all(1 <= v <= 10 for v in scores.values())
        assert len(scores) == 6
        assert feedback
        assert isinstance(feedback, str)
    
    def test_scores_in_range(self):
        pitch = "[1] Test solution that automates things.\n[2] Managers have pain with delays.\n[3] Costs Rs 1000 per month saves time.\n[4] Alternative is manual process vs our solution better.\n[5] I built projects and have advantage."
        scores, _ = score_pitch(pitch)
        for score in scores.values():
            assert 1 <= score <= 10
    
    def test_net_boost_cap(self):
        pitch = (
            "[1] " + "automate " * 20 + "\n"
            "[2] manager " * 20 + " pain " * 20 + "\n"
            "[3] Rs 1000 saves " + "saves " * 20 + "\n"
            "[4] Excel vs manual vs our better " + "vs " * 20 + "\n"
            "[5] built " * 20 + " advantage " * 20
        )
        scores, _ = score_pitch(pitch)
        for dim, score in scores.items():
            from app.engine import DIMENSION_CONFIG
            config = DIMENSION_CONFIG[dim]
            assert score <= config["base"] + config["max_boost"]
    
    def test_net_penalty_cap(self):
        pitch = (
            "[1] maybe kind of somehow possibly perhaps\n"
            "[2] everyone global all people\n"
            "[3] free not sure depends\n"
            "[4] no competition nobody does first ever\n"
            "[5] just started no experience never done"
        )
        scores, _ = score_pitch(pitch)
        for dim, score in scores.items():
            from app.engine import DIMENSION_CONFIG
            config = DIMENSION_CONFIG[dim]
            assert score >= config["base"] - config["max_penalty"]


class TestGate:
    def test_gate_pass(self):
        scores = {dim: 7 for dim in [
            "Problem Clarity", "Customer Specificity", "Cost and Value Case",
            "Alternatives Awareness", "Solver Capability", "Delivery Readiness"
        ]}
        passed, avg = gate_decision(scores, 6.0)
        assert passed is True
        assert avg >= 6.0
    
    def test_gate_fail(self):
        scores = {dim: 5 for dim in [
            "Problem Clarity", "Customer Specificity", "Cost and Value Case",
            "Alternatives Awareness", "Solver Capability", "Delivery Readiness"
        ]}
        passed, avg = gate_decision(scores, 6.0)
        assert passed is False
        assert avg < 6.0
    
    def test_gate_threshold_exact(self):
        scores = {dim: 6 for dim in [
            "Problem Clarity", "Customer Specificity", "Cost and Value Case",
            "Alternatives Awareness", "Solver Capability", "Delivery Readiness"
        ]}
        passed, avg = gate_decision(scores, 6.0)
        assert passed is True


class TestOutline:
    def test_generates_outline(self):
        answers = {
            1: "Solution does X.",
            2: "Managers face pain.",
            3: "Costs Rs 1000.",
            4: "Alternative A vs B.",
            5: "I have experience.",
        }
        outline = generate_outline(answers, "Test Solver")
        assert "Problem" in outline
        assert "Solution" in outline
        assert "Affected People" in outline
        assert "Cost and Value" in outline
        assert "Alternatives and Edge" in outline
        assert "Solver and Advantage" in outline
        assert "Proposed Next Step" in outline
    
    def test_uses_defaults_for_missing(self):
        answers = {1: "Only step 1"}
        outline = generate_outline(answers)
        assert outline["Solution"] == "Only step 1"
        assert "not specified" in outline["Affected People"]


class TestCredibility:
    def test_empty_proposals(self):
        cred = compute_credibility([])
        assert cred["avg_gate_score"] == 0.0
        assert cred["total_passes"] == 0
    
    def test_computes_correctly(self):
        proposals = [
            {"status": "submitted", "gate_score": 70, "attempts": 1},
            {"status": "submitted", "gate_score": 80, "attempts": 2},
            {"status": "needs_work", "gate_score": 50, "attempts": 1},
        ]
        cred = compute_credibility(proposals)
        assert cred["avg_gate_score"] == 75.0
        assert cred["first_attempt_passes"] == 1
        assert cred["total_attempts"] == 3
        assert cred["total_passes"] == 2


class TestWordBoundary:
    def test_age_not_in_manage(self):
        from app.engine import _word_boundary_match
        matches = _word_boundary_match("manage the project", {"age"})
        assert "age" not in matches
    
    def test_exact_match(self):
        from app.engine import _word_boundary_match
        matches = _word_boundary_match("age is just a number", {"age"})
        assert "age" in matches