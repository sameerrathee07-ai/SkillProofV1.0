import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiFetch } from '../lib/api';
import { ShieldCheck, AlertCircle, ArrowRight, RotateCcw, Sparkles } from 'lucide-react';

const STEP_QUESTIONS = [
  "Step 1 — Solution Approach: In one sentence (≥10 words), how does your technical or operational solution solve this specific problem? (Must include an action verb like automates, reduces, builds, connects).",
  "Step 2 — Target Role & Pain Point: Who inside the organization experiences this daily, and what specific pain or bottleneck do they feel?",
  "Step 3 font — Cost & Value Justification: What does your solution cost (specify currency & frequency), and how does it justify that cost?",
  "Step 4 — Alternative Approaches: What are 2+ alternative solutions or current workarounds, and what makes your approach better?",
  "Step 5 — Solver Background: What relevant experience or past projects do you have, and what is your unfair technical/domain advantage?",
];

export const PitchGatePage: React.FC = () => {
  const { problemId } = useParams<{ problemId: string }>();
  const navigate = useNavigate();

  const [problemTitle, setProblemTitle] = useState('');
  const [category, setCategory] = useState('');
  const [currentStep, setCurrentStep] = useState(1);
  const [responses, setResponses] = useState<{ [key: string]: string }>({
    step1: '',
    step2: '',
    step3: '',
    step4: '',
    step5: '',
  });

  const [currentInput, setCurrentInput] = useState('');
  const [pushbackMsg, setPushbackMsg] = useState('');
  const [loading, setLoading] = useState(true);
  const [validating, setValidating] = useState(false);

  // Completion / Score state
  const [scoredResult, setScoredResult] = useState<any>(null);

  useEffect(() => {
    if (problemId) {
      fetchSession();
    }
  }, [problemId]);

  const fetchSession = async () => {
    try {
      const data = await apiFetch(`/pitch/${problemId}/session`);
      setProblemTitle(data.problem_title);
      setCategory(data.category);
      setCurrentStep(data.current_step || 1);
      if (data.responses) {
        setResponses(data.responses);
        const activeKey = `step${data.current_step}`;
        setCurrentInput(data.responses[activeKey] || '');
      }
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleNextStep = async (e: React.FormEvent) => {
    e.preventDefault();
    setPushbackMsg('');

    if (!currentInput.trim()) {
      setPushbackMsg('Please articulate your response before proceeding.');
      return;
    }

    setValidating(true);

    try {
      const valData = await apiFetch(`/pitch/${problemId}/step/${currentStep}/validate`, {
        method: 'POST',
        body: JSON.stringify({
          step: currentStep,
          response: currentInput,
        }),
      });

      if (!valData.valid) {
        setPushbackMsg(valData.message);
        setValidating(false);
        return;
      }

      // Valid! Update state
      const nextKey = `step${currentStep}`;
      const updatedResponses = { ...responses, [nextKey]: currentInput };
      setResponses(updatedResponses);

      if (currentStep < 5) {
        const nextS = currentStep + 1;
        setCurrentStep(nextS);
        setCurrentInput(updatedResponses[`step${nextS}`] || '');
      } else {
        // Step 5 completed — Submit full pitch
        submitPitch(updatedResponses);
      }
    } catch (err: any) {
      setPushbackMsg(err.message || 'Validation error.');
    } finally {
      setValidating(false);
    }
  };

  const submitPitch = async (allResponses: { [key: string]: string }) => {
    setValidating(true);
    try {
      const submitData = await apiFetch(`/pitch/${problemId}/submit`, {
        method: 'POST',
        body: JSON.stringify({
          problem_id: problemId,
          responses: allResponses,
        }),
      });

      setScoredResult(submitData);
    } catch (err: any) {
      setPushbackMsg(err.message || 'Submission error.');
    } finally {
      setValidating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brass"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      
      {/* Pitch Gate Header */}
      <div className="bg-ink text-ivory p-6 sm:p-8 rounded-2xl border border-brass/30 shadow-lg space-y-3">
        <div className="flex justify-between items-center text-xs">
          <span className="font-bold uppercase tracking-widest text-brass flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4" />
            <span>5-Step Pitch Quality Gate</span>
          </span>
          <span className="px-2.5 py-1 rounded bg-forest/30 text-forest-light border border-forest/40 font-mono">
            Category: {category}
          </span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-serif font-bold text-ivory">{problemTitle}</h1>
        <p className="text-xs text-ivory/70">
          Every pitch is evaluated rule-by-rule across 6 dimensions. Average score must reach ≥ 6.0/10 to be released to the problem poster.
        </p>
      </div>

      {scoredResult ? (
        /* Results Card — Passed vs Needs Work */
        <div className="bg-ivory border border-ink/10 rounded-2xl p-6 sm:p-8 shadow-md space-y-6">
          
          <div className={`p-6 rounded-xl border ${
            scoredResult.status === 'submitted'
              ? 'bg-forest-light border-forest/40 text-forest'
              : 'bg-brick-light border-brick/40 text-brick'
          } space-y-2`}>
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-widest">
                {scoredResult.status === 'submitted' ? 'Quality Gate Passed ✓' : 'Needs Work ⚠'}
              </span>
              <span className="text-2xl font-serif font-extrabold">
                {scoredResult.average_score} / 10 Avg
              </span>
            </div>
            <p className="text-sm font-semibold">
              {scoredResult.status === 'submitted'
                ? 'Congratulations! Your proposal has cleared the bar and is now live in the poster\'s inbox.'
                : scoredResult.feedback}
            </p>
          </div>

          {/* Dimension Scores Bar Breakdown */}
          <div className="space-y-4 pt-2">
            <h3 className="font-serif font-bold text-lg text-ink">6-Dimension Evaluation Breakdown</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {Object.entries(scoredResult.dimension_scores).map(([dim, score]: [string, any]) => (
                <div key={dim} className="bg-ivory border border-ink/10 p-3.5 rounded-lg space-y-1.5">
                  <div className="flex justify-between text-xs font-bold text-ink uppercase tracking-wider">
                    <span>{dim.replace('_', ' ')}</span>
                    <span className="text-brass">{score} / 10</span>
                  </div>
                  <div className="w-full bg-ink/10 h-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all ${
                        score >= 6 ? 'bg-forest' : 'bg-brick'
                      }`}
                      style={{ width: `${(score / 10) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-6 border-t border-ink/10 flex flex-col sm:flex-row justify-between items-center gap-4">
            {scoredResult.status === 'needs_work' ? (
              <button
                onClick={() => setScoredResult(null)}
                className="w-full sm:w-auto px-6 py-3 bg-brass text-ink font-semibold rounded-lg hover:bg-brass-hover transition-colors flex items-center justify-center gap-2"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Revise & Resubmit Pitch</span>
              </button>
            ) : (
              <button
                onClick={() => navigate(`/proposals/${scoredResult.proposal_id}`)}
                className="w-full sm:w-auto px-6 py-3 bg-forest text-ivory font-semibold rounded-lg hover:bg-forest-hover transition-colors flex items-center justify-center gap-2"
              >
                <span>View Full Submitted Proposal</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            )}

            <button
              onClick={() => navigate('/my-proposals')}
              className="px-4 py-2 text-xs font-semibold text-ink-muted hover:text-ink"
            >
              Go to My Proposals Dashboard
            </button>
          </div>

        </div>
      ) : (
        /* Interactive 5-Step Chat Gate */
        <div className="bg-ivory border border-ink/10 rounded-2xl p-6 sm:p-8 shadow-sm space-y-6">
          
          {/* Progress Tracker */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-bold uppercase tracking-wider text-ink-muted">
              <span>Step {currentStep} of 5</span>
              <span className="text-brass">Token Cost: 2 Tokens / Msg</span>
            </div>
            <div className="w-full bg-ink/10 h-2.5 rounded-full overflow-hidden">
              <div
                className="bg-brass h-full transition-all duration-300"
                style={{ width: `${(currentStep / 5) * 100}%` }}
              />
            </div>
          </div>

          {/* Current Question */}
          <div className="p-4 bg-brass/10 border border-brass/30 rounded-xl space-y-2">
            <div className="text-xs font-bold uppercase tracking-widest text-brass flex items-center gap-1.5">
              <Sparkles className="w-4 h-4" />
              <span>Question {currentStep}</span>
            </div>
            <p className="text-sm font-semibold text-ink leading-relaxed">
              {STEP_QUESTIONS[currentStep - 1]}
            </p>
          </div>

          {/* Inline Pushback Error */}
          {pushbackMsg && (
            <div className="p-4 bg-brick-light border border-brick/40 text-brick text-xs font-semibold rounded-xl flex items-start gap-2.5 animate-fadeIn">
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <div className="space-y-1">
                <span className="font-bold block uppercase tracking-wider">Quality Gate Pushback</span>
                <p className="leading-relaxed">{pushbackMsg}</p>
              </div>
            </div>
          )}

          {/* Response Form */}
          <form onSubmit={handleNextStep} className="space-y-4">
            <textarea
              rows={4}
              required
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              placeholder="Type your structured response here..."
              className="w-full p-4 rounded-xl border border-ink/20 bg-ivory text-ink text-sm font-medium focus:outline-none focus:ring-2 focus:ring-brass leading-relaxed"
            />

            <div className="flex justify-between items-center pt-2">
              <button
                type="button"
                disabled={currentStep === 1}
                onClick={() => {
                  if (currentStep > 1) {
                    const prevS = currentStep - 1;
                    setCurrentStep(prevS);
                    setCurrentInput(responses[`step${prevS}`] || '');
                  }
                }}
                className="px-4 py-2 text-xs font-bold text-ink-muted hover:text-ink disabled:opacity-30"
              >
                ← Back
              </button>

              <button
                type="submit"
                disabled={validating}
                className="px-6 py-3 bg-brass text-ink font-semibold rounded-lg hover:bg-brass-hover transition-colors shadow-sm disabled:opacity-50 flex items-center gap-2 text-sm"
              >
                <span>{validating ? 'Evaluating...' : currentStep === 5 ? 'Submit & Run Quality Gate' : 'Next Step →'}</span>
              </button>
            </div>
          </form>

        </div>
      )}

    </div>
  );
};
