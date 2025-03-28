// src/App.jsx
// Version: Final Button Connects to Backend, Includes Loading State

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
  const [showProgress, setShowProgress] = useState(true);
  const [validationError, setValidationError] = useState('');
  const [viewedSectionHeaders, setViewedSectionHeaders] = useState({});
  const [isLoadingResults, setIsLoadingResults] = useState(false); // <<< ADDED State for loading

  // ==========================================================
  // ===== 2. CORE MEMOS & CALLBACKS ========
  // ==========================================================
  const currentStepData = useMemo(() => surveySteps[currentStepIndex], [currentStepIndex]);
  const currentSectionId = useMemo(() => { if (!currentStepData || ['welcome','loading','results'].includes(currentStepData.type)) return null; let activeSection = null; for(let i = currentStepIndex; i >= 0; i--) { if(surveySteps[i].type === 'section-marker' || surveySteps[i].sectionId) { activeSection = surveySteps[i].sectionId; break; }} return activeSection; }, [currentStepData, currentStepIndex]);
  const findValidStepIndex = useCallback((startIndex, moveDirection) => { let nextIndex = startIndex + moveDirection; while (nextIndex >= 0 && nextIndex < surveySteps.length) { const step = surveySteps[nextIndex]; if (step.type === 'section-marker') { nextIndex += moveDirection; continue; } if (!step.condition || step.condition(answers)) { return nextIndex; } nextIndex += moveDirection; } return -1; }, [answers]);
  const updateMultiSelectState = useCallback((key, optionId, isExclusive) => { if (!key) return; setAnswers(prev => { const currentArray = Array.isArray(prev[key]) ? [...prev[key]] : []; let newSelection; if (isExclusive) { newSelection = currentArray.includes(optionId) ? [] : [optionId]; } else { const exclusiveOptionId = currentStepData?.options?.find(opt => opt.exclusive)?.id; newSelection = currentArray.filter(id => id !== exclusiveOptionId); const index = newSelection.indexOf(optionId); if (index > -1) newSelection.splice(index, 1); else newSelection.push(optionId); } return { ...prev, [key]: newSelection }; }); setValidationError(''); }, [currentStepData, setAnswers, setValidationError]);

  // NEXT Button Handler (Most Steps)
  const handleNext = useCallback(() => {
    setValidationError(''); if (currentStepData?.validation) { const answer = answers[currentStepData.inputKey]; const consent = currentStepData.consentInputKey ? !!answers[currentStepData.consentInputKey] : true; if (currentStepData.type === 'email' && !consent) { setValidationError('Please agree...'); return; } /* Need strict check for email type, regular validation doesn't block submit below*/ if (currentStepData.type !== 'email' && !currentStepData.validation(answer)) { setValidationError(currentStepData.validationMessage || 'Invalid...'); return; }} setDirection(1); const nextIdx = findValidStepIndex(currentStepIndex, 1); if (nextIdx !== -1) { setCurrentStepIndex(nextIdx); }
     // Only proceed to loading from email step via handleSubmitResults
   }, [currentStepData, answers, currentStepIndex, findValidStepIndex, setValidationError]);


   // --- ADDED: SUBMIT Results Handler ---
   const handleSubmitResults = useCallback(async () => {
    console.log("Submitting results...");
    setValidationError(''); // Clear previous errors
    // Final validation checks (only needed if isNextDisabled didn't catch it)
    if (currentStepData?.type === 'email' && currentStepData?.validation) { const answer = answers[currentStepData.inputKey]; const consent = currentStepData.consentInputKey ? !!answers[currentStepData.consentInputKey] : true; if (!consent) { setValidationError('Please agree to the terms...'); return; } if (!currentStepData.validation(answer)) { setValidationError(currentStepData.validationMessage || 'Please provide a valid email.'); return; } }

    setIsLoadingResults(true); // Start loading indicator

    try {
        const response = await fetch('http://localhost:5001/generate-results', { // Target Flask
            method: 'POST', headers: {'Content-Type': 'application/json', }, body: JSON.stringify(answers),
        });
        setIsLoadingResults(false); // Stop loading
        if (!response.ok) { // Handle errors
             let errorMsg = `Server error: ${response.status}`; try { const errData = await response.json(); errorMsg = errData.error || errorMsg; } catch(e){} console.error("Backend Error:", errorMsg); setValidationError(errorMsg); return;
        }
        // SUCCESS: Open results in new tab
        const htmlResults = await response.text();
        const newWindow = window.open("", "_blank");
        if (newWindow) { newWindow.document.open(); newWindow.document.write(htmlResults); newWindow.document.close(); }
        else { setValidationError("Could not open results window. Check pop-up blocker."); }
    } catch (error) { // Handle network errors
         setIsLoadingResults(false); console.error("Network/Fetch Error:", error); setValidationError(`Connection error. (${error.message})`);
     }
   }, [answers, currentStepData, setIsLoadingResults, setValidationError]); // Dependencies


   // ======================================================
   // ===== 3. OTHER MEMOS, CALLBACKS & EFFECTS ==========
   // ======================================================
   const currentProgressPosition = useMemo(() => { if (!currentStepData || !currentStepData.sectionId || ['welcome','loading','results','section-marker'].includes(currentStepData.type)) return 0; const indexInProg = actualProgressSteps.findIndex(step => step.id === currentStepData.id); return indexInProg >= 0 ? indexInProg + 1 : 0; }, [currentStepData, actualProgressSteps]);
   const showBackButton = useMemo(() => { if (currentStepIndex === 0) return false; const prevIndex = findValidStepIndex(currentStepIndex, -1); return prevIndex >= 0 && surveySteps[prevIndex]?.type !== 'welcome'; }, [currentStepIndex, findValidStepIndex]);
   // isNextDisabled handles validation for enable/disable state
   const isNextDisabled = useMemo(() => { if (validationError) return true; if (!currentStepData?.validation) return false; const answer = answers[currentStepData.inputKey]; if (currentStepData.type === 'email' && currentStepData.consentInputKey && !answers[currentStepData.consentInputKey]) return true; return !currentStepData.validation(answer); }, [currentStepData, answers, validationError]);
   const handlePrev = useCallback(() => { if (currentStepIndex === 0) return; setValidationError(''); setDirection(-1); const prevIdx = findValidStepIndex(currentStepIndex, -1); if (prevIdx !== -1) setCurrentStepIndex(prevIdx); }, [currentStepIndex, findValidStepIndex, setValidationError]);
   const handleInputChange = useCallback((e) => { const { name, value, type, checked } = e.target; const key = name || currentStepData?.inputKey; if (!key) return; setAnswers(prev => ({ ...prev, [key]: type === 'checkbox' ? checked : value })); if (validationError) setValidationError(''); }, [currentStepData, setAnswers, validationError, setValidationError]);
   const handleMultiSelectClick = useCallback((optionId) => { const key = currentStepData?.inputKey; const isExclusive = currentStepData?.options?.find(opt => opt.id === optionId)?.exclusive || false; updateMultiSelectState(key, optionId, isExclusive); }, [currentStepData, updateMultiSelectState]);
   const handleSingleSelect = useCallback((optionId) => { const key = currentStepData?.inputKey; if (!key) return; setAnswers(prev => ({ ...prev, [key]: optionId })); setValidationError(''); if (currentStepData.autoAdvance) { setTimeout(handleNext, 250); } }, [currentStepData, setAnswers, setValidationError, handleNext]);

  // Effect for section marker logic
  useEffect(() => { if (currentStepData?.type === 'section-marker') { const sectionId = currentStepData.sectionId; const alreadyViewed = viewedSectionHeaders[sectionId]; if (!alreadyViewed) { setViewedSectionHeaders(prev => ({ ...prev, [sectionId]: true })); } const shouldDelay = !alreadyViewed && direction === 1; const nextAction = () => { const nextRealStepIndex = findValidStepIndex(currentStepIndex, direction); if (nextRealStepIndex !== -1 && nextRealStepIndex !== currentStepIndex) { setCurrentStepIndex(nextRealStepIndex); } else if (direction === -1) { const prevRealIndex = findValidStepIndex(currentStepIndex - 1, -1); if (prevRealIndex !== -1) setCurrentStepIndex(prevRealIndex); }}; if (shouldDelay) { const timer = setTimeout(nextAction, 1800); return () => clearTimeout(timer); } else { nextAction(); }} }, [currentStepIndex, currentStepData, findValidStepIndex, direction, viewedSectionHeaders, setViewedSectionHeaders]);
  // Other effect for info/loading auto-advance, scroll, progress visibility
  useEffect(() => { let timerId = null; const advanceDelay = currentStepData?.autoAdvanceDelay; if (advanceDelay && currentStepData.type === 'info') timerId = setTimeout(handleNext, advanceDelay); if (currentStepData?.type === 'loading' && !isLoadingResults /* Don't interfere with fetch loading */ ) timerId = setTimeout(() => { const rIdx = surveySteps.findIndex(s => s.type === 'results'); if (rIdx > -1) setCurrentStepIndex(rIdx); else console.error("No results!"); }, 2000); const isProgressRelevant = currentStepIndex > 0 && !['welcome','loading','results','section-marker'].includes(currentStepData?.type); setShowProgress(isProgressRelevant); window.scrollTo({ top: 0, behavior: 'smooth' }); return () => { if (timerId) clearTimeout(timerId); }; }, [currentStepIndex, currentStepData, handleNext, isLoadingResults]); // Added isLoadingResults dep

  // --- Animation Variants ---
  const variants = { enter: (d) => ({ y: d > 0 ? 20 : -20, opacity: 0 }), center: { zIndex: 1, y: 0, opacity: 1 }, exit: (d) => ({ zIndex: 0, y: d < 0 ? 20 : -20, opacity: 0 }), };

  // =========================================
  // ===== 4. RENDER STEP CONTENT FUNCTION ====
  // =========================================
  const renderStepContent = () => {
      // <<< ADDED Loading check at the start >>>
      if (isLoadingResults) {
         return (
              <div className="question-step loader" aria-live="assertive">
                 <img src="/provit-icon.png" alt="" />
                 <p>Generating your personalized results...</p>
              </div>
          );
      }

      // Handle section marker rendering
      if (currentStepData?.type === 'section-marker') { if (viewedSectionHeaders[currentStepData.sectionId]) { const section = SECTIONS.find(s => s.id === currentStepData.sectionId); const sectionIndex = SECTIONS.findIndex(s => s.id === currentStepData.sectionId); return ( <motion.div key={currentStepData.id} initial={{opacity: 0}} animate={{opacity: 1}} exit={{opacity: 0}} transition={{duration: 0.3}} className="question-step section-header-display">{sectionIndex !== -1 && <span className="step-indicator">Step {sectionIndex + 1}</span>}<h2>{section?.title || 'Section'}</h2></motion.div> ); } else { return <div className="question-step" style={{minHeight: '350px'}} aria-hidden="true"> </div>; } }

      // Handle normal steps
      if (!currentStepData) return <div className="question-step">Loading...</div>;
      const { type, id, question, subText, /*options, inputKey, etc. extracted in renderOptions */ } = currentStepData; // Extract needed here
      const inputKey = currentStepData.inputKey; // Need inputKey for shouldShowError
      const currentAnswer = answers[inputKey];   // Need currentAnswer for shouldShowError
      const hasActiveError = !!validationError;
      const shouldShowError = (fieldKey) => { if (!hasActiveError) return false; if (fieldKey === currentStepData?.inputKey && (!currentStepData.validation || !currentStepData.validation(currentAnswer))) return true; if (fieldKey === currentStepData?.consentInputKey && currentStepData?.type === 'email' && !answers[consentInputKey]) return true; return false; }; // Need consentInputKey from answers

    return (
      <motion.div> {/* Stagger wrapper */}
          {question && (<motion.h2 key={`${id}-question`} custom={1} variants={stepContentVariants} initial="hidden" animate="visible" exit="exit">{question}</motion.h2>)}
          {subText && (<motion.p key={`${id}-subtext`} className="sub-text" custom={1.5} variants={stepContentVariants} initial="hidden" animate="visible" exit="exit">{subText}</motion.p>)}
          {/* Ensure options/inputs render within their own animated container */}
          <motion.div key={`${id}-options`} custom={2} variants={stepContentVariants} initial="hidden" animate="visible" exit="exit">
               {renderOptions()} {/* Delegate rendering specific inputs/options */}
           </motion.div>
          {/* Error message displays below options */}
          {shouldShowError(inputKey || currentStepData.consentInputKey) && ( // Show if error for main input OR consent
              <motion.p key={`${id}-error`} id={shouldShowError(inputKey)? `${inputKey}-error` : `${currentStepData.consentInputKey}-error`} className="validation-error-msg" role="alert" custom={2.5} variants={stepContentVariants} initial="hidden" animate="visible" exit="exit">
                  {validationError}
              </motion.p>
          )}
       </motion.div>
    );
  };

  // --- Helper to Render Specific Option Types ---
  const renderOptions = () => {
    if (!currentStepData || isLoadingResults) return null; // Don't render options if loading results
    const { type, id, options = [], inputKey, gridColumns, placeholder, inputType='text', consentText, consentInputKey } = currentStepData;
    const currentAnswer = answers[inputKey];

    // Logic for rendering different input/option types remains the same
    // Ensure it uses the correct handlers: handleInputChange, handleSingleSelect, handleMultiSelectClick
    switch (type) {
        case 'text': case 'email': return ( <div className="text-input-container"><input id={inputKey || id} type={inputType} name={inputKey} placeholder={placeholder} value={currentAnswer || ''} onChange={handleInputChange} className={`text-input ${!!validationError && (!currentStepData.validation || !currentStepData.validation(currentAnswer)) ? 'error' : ''}`} aria-invalid={!!validationError && (!currentStepData.validation || !currentStepData.validation(currentAnswer))} aria-describedby={!!validationError ? `${inputKey}-error` : undefined} autoFocus={id !== 'email'} key={id} />{type === 'email' && consentInputKey && (<><label className="consent-label"><input type="checkbox" name={consentInputKey} checked={!!answers[consentInputKey]} onChange={handleInputChange} aria-describedby={!!validationError && !answers[consentInputKey] ? `${consentInputKey}-error` : undefined}/> <span dangerouslySetInnerHTML={{ __html: consentText?.replace('Privacy Policy', '<a href="/privacy-policy" target="_blank" rel="noopener noreferrer">Privacy Policy</a>') || "I agree."}}></span></label></>)}</div> );
        case 'icon-select': case 'yes-no-circle': case 'single-button': case 'multi-grid': case 'checkbox': { const isYesNo = type === 'yes-no-circle'; const isMulti = type === 'multi-grid' || type === 'checkbox'; const isButtonLike = !isYesNo; const El = isButtonLike ? 'button' : 'span'; const isGrid = type === 'multi-grid' || (type === 'checkbox' && !!gridColumns); const containerClass = isGrid ? 'options-grid-container' : (['icon-select', 'yes-no-circle'].includes(type) ? 'options-icon-container' : 'options-container'); const gridStyle = isGrid ? { gridTemplateColumns: `repeat(${gridColumns || 3}, 1fr)` } : {}; const C = 'div'; return (<C className={containerClass} style={gridStyle} role={isYesNo ? 'radiogroup': (isMulti ? 'group' : undefined)} aria-labelledby={currentStepData?.question ? `${id}-q`:undefined}>{options.map((opt, idx) => { const isSel = isMulti ? (Array.isArray(currentAnswer) && currentAnswer.includes(opt.id)) : (currentAnswer === opt.id); const clickH = isMulti ? ()=>handleMultiSelectClick(opt.id) : ()=>handleSingleSelect(opt.id); const className = `${isButtonLike?'option-button':'yes-no-option'} ${isGrid?'grid-item':''} ${type==='icon-select'?'icon-select-option':''} ${type==='checkbox'?'checkbox-option-simplified':''} ${isSel ? 'selected' : ''}`; return (<El key={opt.id} className={className} onClick={clickH} type={El==='button'?'button':undefined} role={isYesNo?'radio':(isMulti?'checkbox':undefined)} aria-checked={isYesNo || isMulti?isSel:undefined} tabIndex={isYesNo?((currentAnswer==null&&idx===0)||isSel?0:-1):0} onKeyDown={e=>{if(e.key===' '||e.key==='Enter'){e.preventDefault();clickH();}}} data-id={isYesNo?opt.id:undefined}>{opt.icon&&<span className={`icon ${type==='icon-select' ? 'large-icon' : ''}`} aria-hidden="true">{opt.icon}</span>}<span>{opt.text}</span></El>);})}</C>); }
        // Only render button for welcome step
        case 'welcome': return <button className="nav-button next submit" onClick={handleNext} style={{ background: PROVIT_GRADIENT_GREEN }}>{currentStepData.buttonText}</button>;
        default: return null; // Handles info, loading, results etc which don't render options here
    }
 };


  // ======================================
  // ===== 5. MAIN JSX RETURN STATEMENT ====
  // ======================================
  return (
     <>
        <div className="background-elements" aria-hidden="true">{[1,2,3,4,5,6,7,8].map(i=><div key={i} className={`bg-element el-${i}`}></div>)}</div>
        <div className="survey-container">
          <header className="survey-header"><img src="/provit-logo-white.png" alt="PROVIT Logo" /></header>
          <div className="section-nav-container">{SECTIONS.map((sec) => (<div key={sec.id} className={`section-nav-item ${currentSectionId === sec.id ? 'active' : ''} ${viewedSectionHeaders[sec.id] ? 'viewed' : ''}`}>{sec.title}</div>))}</div>
          <div className='survey-header-spacer'></div>
          <AnimatePresence>{showProgress && <motion.div /*...*/ style={{ width: '100%', overflow: 'hidden' }}><ProgressBar current={currentProgressPosition} total={totalProgressSteps} /></motion.div>}</AnimatePresence>
          <div className='step-wrapper'><AnimatePresence initial={false} custom={direction} mode="wait"><motion.div key={currentStepIndex} custom={direction} variants={stepVariants} initial="enter" animate="center" exit="exit" transition={{ type: "spring", stiffness: 100, damping: 20 }}> {renderStepContent()} </motion.div></AnimatePresence></div>
          <AnimatePresence>
            {currentStepData && !['welcome', 'loading', 'results', 'info', 'section-marker'].includes(currentStepData.type) && !(currentStepData.autoAdvance && !currentStepData.inputKey) && (
              <motion.div className={`navigation-buttons ${!showBackButton ? 'center' : ''}`} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} transition={{ delay: 0.4, duration: 0.4}}>
                 {showBackButton && (<button className="nav-button prev" onClick={handlePrev} type="button">Back</button>)}
                 {!(currentStepData.autoAdvance && ['single-button', 'yes-no-circle','icon-select'].includes(currentStepData.type)) && (
                  <button className={`nav-button next ${currentStepData.type === 'email' ? 'submit' : ''}`}
                     // *** Attach Correct Handler Based on Step Type ***
                     onClick={currentStepData.type === 'email' ? handleSubmitResults : handleNext}
                     type="button"
                     // *** Disable button if needed or during results loading ***
                     disabled={isNextDisabled || isLoadingResults}>
                       {/* *** Show loading text when submitting *** */}
                       {isLoadingResults ? 'Generating...' : (currentStepData.buttonText || 'Continue')}
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