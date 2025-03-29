// src/App.jsx
// Version: Redesigned Welcome Screen, Connects final button to backend, Staggering

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
// Import SECTIONS array and ensure surveyData path is correct
import { surveySteps, getProgressSteps, SECTIONS, PROVIT_GRADIENT_GREEN, PROVIT_GRADIENT_BLUE } from './data/surveyData';
import ProgressBar from './components/ProgressBar';
import './styles/App.css';

// Calculate progress steps outside component
const actualProgressSteps = getProgressSteps(surveySteps);
const totalProgressSteps = actualProgressSteps.length;

// --- Framer Motion Variants ---
const stepVariants = {
  enter: (direction) => ({ y: direction > 0 ? 30 : -30, opacity: 0 }),
  center: { zIndex: 1, y: 0, opacity: 1 },
  exit: (direction) => ({ zIndex: 0, y: direction < 0 ? 30 : -30, opacity: 0 }),
};
const stepContentVariants = {
  hidden: { opacity: 0, y: 15 },
  visible: (i = 1) => ({ opacity: 1, y: 0, transition: { delay: i * 0.1, duration: 0.4, ease: "easeOut" }, }),
  exit: { opacity: 0, y: -10, transition: {duration: 0.2} }
};

function App() {
  // ============================================
  // ===== 1. STATE HOOKS ==========
  // ============================================
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [direction, setDirection] = useState(1);
  const [showProgress, setShowProgress] = useState(true); // Changed default? Check useEffect logic
  const [validationError, setValidationError] = useState('');
  const [viewedSectionHeaders, setViewedSectionHeaders] = useState({});
  const [isLoadingResults, setIsLoadingResults] = useState(false);

  // ==========================================================
  // ===== 2. CORE MEMOS & CALLBACKS ========
  // ==========================================================
  const currentStepData = useMemo(() => surveySteps[currentStepIndex], [currentStepIndex]);
  const currentSectionId = useMemo(() => { if (!currentStepData || ['welcome','loading','results'].includes(currentStepData.type)) return null; let activeSection = null; for(let i = currentStepIndex; i >= 0; i--) { if(surveySteps[i].type === 'section-marker' || surveySteps[i].sectionId) { activeSection = surveySteps[i].sectionId; break; }} return activeSection; }, [currentStepData, currentStepIndex]);
  const findValidStepIndex = useCallback((startIndex, moveDirection) => { let nextIndex = startIndex + moveDirection; while (nextIndex >= 0 && nextIndex < surveySteps.length) { const step = surveySteps[nextIndex]; if (step.type === 'section-marker') { nextIndex += moveDirection; continue; } if (!step.condition || step.condition(answers)) { return nextIndex; } nextIndex += moveDirection; } return -1; }, [answers]);
  const updateMultiSelectState = useCallback((key, optionId, isExclusive) => { if (!key) return; setAnswers(prev => { const currentArray = Array.isArray(prev[key]) ? [...prev[key]] : []; let newSelection; if (isExclusive) { newSelection = currentArray.includes(optionId) ? [] : [optionId]; } else { const exclusiveOptionId = currentStepData?.options?.find(opt => opt.exclusive)?.id; newSelection = currentArray.filter(id => id !== exclusiveOptionId); const index = newSelection.indexOf(optionId); if (index > -1) newSelection.splice(index, 1); else newSelection.push(optionId); } return { ...prev, [key]: newSelection }; }); setValidationError(''); }, [currentStepData, setAnswers, setValidationError]);

  // NEXT Button Handler
  const handleNext = useCallback(() => {
    setValidationError(''); if (currentStepData?.validation && currentStepData.type !== 'email') { /* Validate non-email steps */ const answer = answers[currentStepData.inputKey]; if (!currentStepData.validation(answer)) { setValidationError(currentStepData.validationMessage || 'Invalid...'); return; }} setDirection(1); const nextIdx = findValidStepIndex(currentStepIndex, 1); if (nextIdx !== -1) { setCurrentStepIndex(nextIdx); }
    // Submission is handled separately
  }, [currentStepData, answers, currentStepIndex, findValidStepIndex, setValidationError]);

  // SUBMIT Results Handler
   const handleSubmitResults = useCallback(async () => {
       console.log("Submitting results..."); setValidationError('');
       if (currentStepData?.type === 'email' && currentStepData?.validation) { /* Final email validation */ const answer = answers[currentStepData.inputKey]; const consent = currentStepData.consentInputKey ? !!answers[currentStepData.consentInputKey] : true; if (!consent) { setValidationError('Please agree...'); return; } if (!currentStepData.validation(answer)) { setValidationError(currentStepData.validationMessage || 'Provide valid email.'); return; } }
       setIsLoadingResults(true);
       try { /* Fetch logic as before... */ const response = await fetch('http://localhost:5001/generate-results', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(answers) }); setIsLoadingResults(false); if (!response.ok) { let errorMsg = `Server error: ${response.status}`; try { const errData = await response.json(); errorMsg = errData.error || errorMsg; } catch(e){} console.error("Backend Error:", errorMsg); setValidationError(errorMsg); return; } const htmlResults = await response.text(); const newWindow = window.open("", "_blank"); if (newWindow) { newWindow.document.open(); newWindow.document.write(htmlResults); newWindow.document.close(); } else { setValidationError("Check pop-up blocker."); } } catch (error) { setIsLoadingResults(false); console.error("Network/Fetch Error:", error); setValidationError(`Connection error. (${error.message})`); }
   }, [answers, currentStepData, setIsLoadingResults, setValidationError]); // Removed findValidStepIndex


   // ======================================================
   // ===== 3. OTHER MEMOS, CALLBACKS & EFFECTS ==========
   // ======================================================
   const currentProgressPosition = useMemo(() => { if (!currentStepData || !currentStepData.sectionId || ['welcome','loading','results','section-marker'].includes(currentStepData.type)) return 0; const indexInProg = actualProgressSteps.findIndex(step => step.id === currentStepData.id); return indexInProg >= 0 ? indexInProg + 1 : 0; }, [currentStepData, actualProgressSteps]);
   const showBackButton = useMemo(() => { if (currentStepIndex === 0) return false; const prevIndex = findValidStepIndex(currentStepIndex, -1); return prevIndex >= 0 && surveySteps[prevIndex]?.type !== 'welcome'; }, [currentStepIndex, findValidStepIndex]);
   const isNextDisabled = useMemo(() => { if (validationError) return true; if (isLoadingResults) return true; /* <<< Also disable when loading >>> */ if (!currentStepData?.validation) return false; const answer = answers[currentStepData.inputKey]; if (currentStepData.type === 'email' && currentStepData.consentInputKey && !answers[currentStepData.consentInputKey]) return true; return !currentStepData.validation(answer); }, [currentStepData, answers, validationError, isLoadingResults]); // <<< Added isLoadingResults
   const handlePrev = useCallback(() => { if (currentStepIndex === 0) return; setValidationError(''); setDirection(-1); const prevIdx = findValidStepIndex(currentStepIndex, -1); if (prevIdx !== -1) setCurrentStepIndex(prevIdx); }, [currentStepIndex, findValidStepIndex, setValidationError]);
   const handleInputChange = useCallback((e) => { const { name, value, type, checked } = e.target; const key = name || currentStepData?.inputKey; if (!key) return; setAnswers(prev => ({ ...prev, [key]: type === 'checkbox' ? checked : value })); if (validationError) setValidationError(''); }, [currentStepData, setAnswers, validationError, setValidationError]);
   const handleMultiSelectClick = useCallback((optionId) => { const key = currentStepData?.inputKey; const isExclusive = currentStepData?.options?.find(opt => opt.id === optionId)?.exclusive || false; updateMultiSelectState(key, optionId, isExclusive); }, [currentStepData, updateMultiSelectState]);
   const handleSingleSelect = useCallback((optionId) => { const key = currentStepData?.inputKey; if (!key) return; setAnswers(prev => ({ ...prev, [key]: optionId })); setValidationError(''); if (currentStepData.autoAdvance) { setTimeout(handleNext, 250); } }, [currentStepData, setAnswers, setValidationError, handleNext]);

  // Effects
  useEffect(() => { /* Section marker effect */ if (currentStepData?.type === 'section-marker') { const sectionId = currentStepData.sectionId; const alreadyViewed = viewedSectionHeaders[sectionId]; if (!alreadyViewed) { setViewedSectionHeaders(prev => ({ ...prev, [sectionId]: true })); } const shouldDelay = !alreadyViewed && direction === 1; const nextAction = () => { const nextRealStepIndex = findValidStepIndex(currentStepIndex, direction); if (nextRealStepIndex !== -1 && nextRealStepIndex !== currentStepIndex) { setCurrentStepIndex(nextRealStepIndex); } else if (direction === -1) { const prevRealIndex = findValidStepIndex(currentStepIndex - 1, -1); if (prevRealIndex !== -1) setCurrentStepIndex(prevRealIndex); }}; if (shouldDelay) { const timer = setTimeout(nextAction, 1800); return () => clearTimeout(timer); } else { nextAction(); }}}, [currentStepIndex, currentStepData, findValidStepIndex, direction, viewedSectionHeaders, setViewedSectionHeaders]);
  useEffect(() => { /* Other effects */ let timerId = null; const advanceDelay = currentStepData?.autoAdvanceDelay; if (advanceDelay && currentStepData.type === 'info') timerId = setTimeout(handleNext, advanceDelay); if (currentStepData?.type === 'loading' && !isLoadingResults) timerId = setTimeout(() => { const rIdx = surveySteps.findIndex(s => s.type === 'results'); if (rIdx > -1) setCurrentStepIndex(rIdx); else console.error("No results!"); }, 2000); const isProgressRelevant = currentStepIndex > 0 && !['welcome','loading','results','section-marker'].includes(currentStepData?.type); setShowProgress(isProgressRelevant); window.scrollTo({ top: 0, behavior: 'smooth' }); return () => { if (timerId) clearTimeout(timerId); }; }, [currentStepIndex, currentStepData, handleNext, isLoadingResults]);

  // Animation Variants
  const variants = { enter: (d) => ({ y: d > 0 ? 20 : -20, opacity: 0 }), center: { zIndex: 1, y: 0, opacity: 1 }, exit: (d) => ({ zIndex: 0, y: d < 0 ? 20 : -20, opacity: 0 }), };


  // =========================================
  // ===== 4. RENDER STEP CONTENT FUNCTION ====
  // =========================================
  const renderStepContent = () => {
    // Handle loading state first
      if (isLoadingResults) {
          return (
              <div className="question-step loader" aria-live="assertive">
                  <img src="/provit-icon.png" alt="" /> {/* Ensure icon is in public */}
                  <p>Generating your personalized results...</p>
              </div>
           );
      }

    // Handle section marker display
    if (currentStepData?.type === 'section-marker') { if (viewedSectionHeaders[currentStepData.sectionId]) { const section = SECTIONS.find(s => s.id === currentStepData.sectionId); const sectionIndex = SECTIONS.findIndex(s => s.id === currentStepData.sectionId); return ( <motion.div key={currentStepData.id} initial={{opacity: 0}} animate={{opacity: 1}} exit={{opacity: 0}} transition={{duration: 0.3}} className="question-step section-header-display">{sectionIndex !== -1 && <span className="step-indicator">Step {sectionIndex + 1}</span>}<h2>{section?.title || 'Section'}</h2></motion.div> ); } else { return <div className="question-step" style={{minHeight: '350px'}} aria-hidden="true"> </div>; } }

    // Standard step display
    if (!currentStepData) return <div className="question-step">Loading...</div>;
    const { type, id, question, subText, inputKey } = currentStepData;
    const hasActiveError = !!validationError;
    const currentAnswer = answers[inputKey]; // Needed for shouldShowError maybe
    const shouldShowError = (fieldKey) => { if (!hasActiveError) return false; const isConsentError = fieldKey === currentStepData?.consentInputKey && !answers[currentStepData?.consentInputKey]; const isMainInputError = fieldKey === inputKey && currentStepData?.validation && !currentStepData.validation(currentAnswer); return isConsentError || isMainInputError;};

     // Render main content structure with stagger
     return (
      <motion.div>
        {/* Welcome screen handles its own animation */}
        {type !== 'welcome' && question && ( <motion.h2 key={`${id}-question`} custom={1} variants={stepContentVariants} initial="hidden" animate="visible" exit="exit">{question}</motion.h2> )}
        {type !== 'welcome' && subText && ( <motion.p key={`${id}-subtext`} className="sub-text" custom={1.5} variants={stepContentVariants} initial="hidden" animate="visible" exit="exit">{subText}</motion.p> )}
        <motion.div key={`${id}-options`} custom={2} variants={stepContentVariants} initial="hidden" animate="visible" exit="exit">
          {renderOptions()}
        </motion.div>
        {shouldShowError(inputKey || currentStepData?.consentInputKey) && (<motion.p key={`${id}-error`} id={shouldShowError(inputKey)? `${inputKey}-error` : `${currentStepData.consentInputKey}-error`} className="validation-error-msg" role="alert" custom={2.5} variants={stepContentVariants} initial="hidden" animate="visible" exit="exit">{validationError}</motion.p> )}
       </motion.div>
     );
  };


  // Helper function to render just the options/input part of a step
  const renderOptions = () => {
    if (!currentStepData || isLoadingResults) return null;
    const { type, id, options = [], inputKey, gridColumns, placeholder, inputType='text', consentText, consentInputKey, title, text, buttonText } = currentStepData; // Get all props
    const currentAnswer = answers[inputKey];
    const hasActiveError = !!validationError; // Get error state
    const shouldShowError = (fieldKey) => { /* simplified for context */ };

    switch (type) {
        case 'welcome': // <<< UPDATED: Render Welcome content via this helper >>>
             return (
                  <div className="welcome-screen"> {/* Outer container */}
                      <div className="welcome-content">
                           <div className="welcome-text">
                               <img src="/provit-logo-white.png" alt="PROVIT Logo" className="welcome-logo" />
                               <h1 className="welcome-title">{title || 'Nutrition tailored...'}</h1>
                               <p className="welcome-tagline">{text || "Let's find..."}</p>
                               <p className="welcome-description">Answer a few short questions about your goals, diet, and lifestyle, and get a personalised recommendation in minutes. Start your journey to better health today!</p>
                                <button className="welcome-button" onClick={handleNext}>{buttonText || "Let's Get Started"}</button>
                           </div>
                           <div className="welcome-image-container">
                               <img src="/provit-hero-image.png" alt="Personalized vitamins" className="welcome-hero-image" /> {/* Make sure image exists */}
                           </div>
                      </div>
                 </div>
             );

         case 'text': case 'email': return ( <div className="text-input-container"><input id={inputKey || id} type={inputType} name={inputKey} placeholder={placeholder} value={currentAnswer || ''} onChange={handleInputChange} className={`text-input ${!!validationError && (!currentStepData.validation || !currentStepData.validation(currentAnswer)) ? 'error' : ''}`} aria-invalid={!!validationError && (!currentStepData.validation || !currentStepData.validation(currentAnswer))} aria-describedby={!!validationError ? `${inputKey}-error` : undefined} autoFocus={id !== 'email'} key={id} />{type === 'email' && consentInputKey && (<><label className="consent-label"><input type="checkbox" name={consentInputKey} checked={!!answers[consentInputKey]} onChange={handleInputChange} aria-describedby={!!validationError && !answers[consentInputKey] ? `${consentInputKey}-error` : undefined}/> <span dangerouslySetInnerHTML={{ __html: consentText?.replace('Privacy Policy', '<a href="/privacy-policy" target="_blank" rel="noopener noreferrer">Privacy Policy</a>') || "I agree."}}></span></label></>)}</div> );
         case 'icon-select': case 'yes-no-circle': case 'single-button': case 'multi-grid': case 'checkbox': { const isYesNo = type === 'yes-no-circle'; const isMulti = type === 'multi-grid' || type === 'checkbox'; const isButtonLike = !isYesNo; const El = isButtonLike ? 'button' : 'span'; const isGrid = type === 'multi-grid' || (type === 'checkbox' && !!gridColumns); const containerClass = isGrid ? 'options-grid-container' : (['icon-select', 'yes-no-circle'].includes(type) ? 'options-icon-container' : 'options-container'); const gridStyle = isGrid ? { gridTemplateColumns: `repeat(${gridColumns || 3}, 1fr)` } : {}; const C = 'div'; return (<C className={containerClass} style={gridStyle} role={isYesNo ? 'radiogroup': (isMulti ? 'group' : undefined)} aria-labelledby={currentStepData?.question ? `${id}-q`:undefined}>{options.map((opt, idx) => { const isSel = isMulti ? (Array.isArray(currentAnswer) && currentAnswer.includes(opt.id)) : (currentAnswer === opt.id); const clickH = isMulti ? ()=>handleMultiSelectClick(opt.id) : ()=>handleSingleSelect(opt.id); const className = `${isButtonLike?'option-button':'yes-no-option'} ${isGrid?'grid-item':''} ${type==='icon-select'?'icon-select-option':''} ${type==='checkbox'?'checkbox-option-simplified':''} ${isSel ? 'selected' : ''}`; return (<El key={opt.id} className={className} onClick={clickH} type={El==='button'?'button':undefined} role={isYesNo?'radio':(isMulti?'checkbox':undefined)} aria-checked={isYesNo || isMulti?isSel:undefined} tabIndex={isYesNo?((currentAnswer==null&&idx===0)||isSel?0:-1):0} onKeyDown={e=>{if(e.key===' '||e.key==='Enter'){e.preventDefault();clickH();}}} data-id={isYesNo?opt.id:undefined}>{opt.icon&&<span className={`icon ${type==='icon-select' ? 'large-icon' : ''}`} aria-hidden="true">{opt.icon}</span>}<span>{opt.text}</span></El>);})}</C>); }
         // Info, Loading, Results don't have standard options
         case 'info': case 'loading': case 'results': return null;
        default: return null;
    }
  }; // End renderOptions

  // ======================================
  // ===== 5. MAIN JSX RETURN STATEMENT ====
  // ======================================
  return (
    <>
      <div className="background-elements" aria-hidden="true">{[1,2,3,4,5,6,7,8].map(i=><div key={i} className={`bg-element el-${i}`}></div>)}</div>
      <div className="survey-container">
          <header className="survey-header"><img src="/provit-logo-white.png" alt="PROVIT Logo" /></header>
          <div className="section-nav-container" aria-label="Survey Sections">{SECTIONS.map((sec) => (<div key={sec.id} className={`section-nav-item ${currentSectionId === sec.id ? 'active' : ''} ${viewedSectionHeaders[sec.id] ? 'viewed' : ''}`}>{sec.title}</div>))}</div>
          <div className='survey-header-spacer'></div>
          <AnimatePresence>{showProgress && <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.3 }} style={{ width: '100%', overflow: 'hidden' }}><ProgressBar current={currentProgressPosition} total={totalProgressSteps} /></motion.div>}</AnimatePresence>

          <div className='step-wrapper'>
              <AnimatePresence initial={false} custom={direction} mode="wait">
                   {/* Key change on currentStepIndex triggers the main slide/fade animation */}
                   <motion.div key={currentStepIndex} custom={direction} variants={stepVariants} initial="enter" animate="center" exit="exit" transition={{ type: "spring", stiffness: 100, damping: 20 }} >
                        {renderStepContent()} {/* Renders inner animated divs for stagger */}
                   </motion.div>
                </AnimatePresence>
          </div>

          <AnimatePresence>
              {currentStepData && !['welcome', 'loading', 'results', 'info', 'section-marker'].includes(currentStepData.type) && !(currentStepData.autoAdvance && !currentStepData.inputKey) && (
               <motion.div className={`navigation-buttons ${!showBackButton ? 'center' : ''}`} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} transition={{ delay: 0.4, duration: 0.4}}>
                    {showBackButton && (<button className="nav-button prev" onClick={handlePrev} type="button">Back</button>)}
                    {!(currentStepData.autoAdvance && ['single-button', 'yes-no-circle','icon-select'].includes(currentStepData.type)) && (
                      <button className={`nav-button next ${currentStepData.type === 'email' ? 'submit' : ''}`}
                           onClick={currentStepData.type === 'email' ? handleSubmitResults : handleNext} // Calls correct handler
                           type="button"
                           disabled={isNextDisabled || isLoadingResults}> {/* Correct disable check */}
                               {isLoadingResults ? 'Generating...' : (currentStepData.buttonText || 'Continue')} {/* Correct text */}
                        </button>
                    )}
               </motion.div>
              )}
          </AnimatePresence>
      </div>
    </>
  );
}

export default App;