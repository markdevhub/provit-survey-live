import os
import subprocess
import sys
from pathlib import Path
from textwrap import dedent

# --- Configuration ---
PROJECT_FOLDER_NAME = "provit-survey" # Expected name, used for confirmation

# --- File Contents (Using textwrap.dedent for clean multi-line strings) ---

INDEX_HTML_CONTENT = dedent("""\
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <!-- UPDATE: Ensure this path is correct relative to index.html (Vite places it in root) -->
        <link rel="icon" type="image/png" href="/provit-icon.png" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>PROVIT Personalised Quiz</title>
      </head>
      <body>
        <div id="root"></div>
        <!-- UPDATE: Ensure this points to your Vite entry point -->
        <script type="module" src="/src/main.jsx"></script>
      </body>
    </html>
""")

SURVEY_DATA_JS_CONTENT = dedent("""\
    // src/data/surveyData.js

    // --- Branding ---
    export const PROVIT_GREEN = '#75C045';
    export const PROVIT_BLUE = '#0BABC3';
    export const PROVIT_LIGHT_GREEN = '#a8d88a'; // Lighter shade for gradient start
    export const PROVIT_LIGHT_BLUE = '#6fc8d7';  // Lighter shade for gradient start
    export const PROVIT_BACKGROUND = '#f8f6f2'; // Off-white background
    export const PROVIT_TEXT_DARK = '#333333';
    export const PROVIT_TEXT_LIGHT = '#555555';
    export const PROVIT_BORDER_COLOR = '#e0e0e0';

    // Gradients (Ensure these match image3.png and image4.png if possible)
    export const PROVIT_GRADIENT_GREEN = `linear-gradient(105deg, ${PROVIT_LIGHT_GREEN} 0%, ${PROVIT_GREEN} 100%)`; // Adjusted angle/stops
    export const PROVIT_GRADIENT_BLUE = `linear-gradient(105deg, ${PROVIT_LIGHT_BLUE} 0%, ${PROVIT_BLUE} 100%)`;  // Adjusted angle/stops


    // --- Survey Structure ---
    export const surveySteps = [
      // STEP 0: Welcome
      {
        id: 'welcome',
        type: 'welcome',
        title: 'Nutrition tailored to you.',
        text: "Let's find the right supplements for your goals, lifestyle, and diet. Get started below!",
        buttonText: "Let's Get Started",
        // No inputKey needed
      },
      // STEP 1: Name
      {
        id: 'name',
        type: 'text',
        question: "What's your first name (or nickname)?",
        placeholder: 'Enter your name', // UPDATE: Match Vitable's cursive placeholder style if possible via CSS font
        inputKey: 'userName',
        nextButtonText: 'Next',
        validation: (value) => !!value && value.trim().length > 0, // Basic non-empty check
        validationMessage: "Please enter your name.",
      },
      // STEP 2: Greeting (Auto-advance)
      {
        id: 'greeting',
        type: 'info',
        // Text generated dynamically in component: `Nice to meet you, ${answers.userName}!`
        autoAdvanceDelay: 1500, // ms
      },
      // --- BASICS Section ---
      // STEP 3: Section Header (Auto-advance)
      {
        id: 'section-basics',
        type: 'section-header',
        title: 'Basics',
        stepNumber: 1,
        autoAdvanceDelay: 1800,
      },
      // STEP 4: Sex (Auto-advance)
      {
        id: 'sex',
        type: 'yes-no-circle',
        question: 'What sex were you assigned at birth?',
        options: [ { id: 'male', text: 'Male' }, { id: 'female', text: 'Female' }],
        inputKey: 'sex',
        autoAdvance: true,
      },
      // STEP 5: Age
      {
        id: 'age',
        type: 'text',
        question: 'How old are you?',
        placeholder: 'Enter your age',
        inputKey: 'age',
        inputType: 'number',
        nextButtonText: 'Next',
        validation: (value) => !!value && parseInt(value, 10) > 10 && parseInt(value, 10) < 120, // Basic age validation (e.g., > 10)
        validationMessage: "Please enter a valid age.",
      },
      // --- GOALS Section ---
      // STEP 6: Section Header (Auto-advance)
       {
        id: 'section-goals',
        type: 'section-header',
        title: 'Goals',
        stepNumber: 2,
        autoAdvanceDelay: 1800,
      },
      // STEP 7: Health Goals (Multi-select grid)
      {
        id: 'goals',
        type: 'multi-grid',
        question: 'Which areas of your health are you looking to improve?',
        subText: "Select the goals you'd like to focus on. We recommend choosing up to 5.", // UPDATE: Vitable prioritizes, simpler select multiple here
        options: [
            // Use relevant icons, emoji placeholders for now
            { id: 'g_sleep', text: 'Sleep', icon: '😴' },
            { id: 'g_bones', text: 'Bones', icon: '🦴' },
            { id: 'g_joints', text: 'Joints', icon: '🤸' },
            { id: 'g_heart', text: 'Heart', icon: '❤️' },
            { id: 'g_hair', text: 'Hair', icon: '💇' },
            { id: 'g_skin', text: 'Skin', icon: '✨' },
            { id: 'g_stress', text: 'Stress', icon: '🤯' },
            { id: 'g_fitness', text: 'Fitness', icon: '💪' },
            { id: 'g_digestion', text: 'Digestion', icon: '🥦' },
            { id: 'g_brain', text: 'Brain', icon: '🧠' },
            { id: 'g_immunity', text: 'Immunity', icon: '🛡️' },
            { id: 'g_energy', text: 'Energy', icon: '⚡️' },
        ],
        inputKey: 'healthGoals',
        nextButtonText: 'Continue',
        validation: (value) => Array.isArray(value) && value.length > 0, // Must select at least one
        validationMessage: "Please select at least one health goal.",
        // REFINEMENT: Add logic for numbered priority badges if needed
      },
       // STEP 8: Conditional Sluggishness (Auto-advance)
       {
        id: 'sluggish',
        type: 'yes-no-circle',
        question: 'Do you often wake up in the morning feeling sluggish?',
        options: [ { id: 'yes', text: 'Yes' }, { id: 'no', text: 'No' }],
        inputKey: 'feelsSluggish',
        autoAdvance: true,
        condition: (answers) =>
            answers.healthGoals?.includes('g_sleep') || answers.healthGoals?.includes('g_energy') ,
      },
       // STEP 9: Conditional Bone History (Auto-advance) - Add more conditionals like this
       {
        id: 'bone_history',
        type: 'yes-no-circle',
        question: 'Do you have a family history of bone issues (such as osteoporosis)?',
        options: [ { id: 'yes', text: 'Yes' }, { id: 'no', text: 'No' }],
        inputKey: 'boneHistory',
        autoAdvance: true,
        condition: (answers) => answers.healthGoals?.includes('g_bones'),
      },
      // --- DIET Section ---
      // STEP 10: Section Header (Auto-advance)
       {
        id: 'section-diet',
        type: 'section-header',
        title: 'Diet',
        stepNumber: 3,
        autoAdvanceDelay: 1800,
       },
      // STEP 11: Describe Diet (Single Button - Auto-advance)
       {
        id: 'diet_describe',
        type: 'single-button',
        question: 'How would you describe your diet?',
        options: [
            { id: 'd_omnivore', text: 'I eat almost everything' },
            { id: 'd_plant_based', text: 'Prefer plant-based foods' },
            { id: 'd_vegetarian', text: 'Vegetarian' },
            { id: 'd_vegan', text: 'Vegan' },
            { id: 'd_other', text: 'Other' },
        ],
        inputKey: 'dietDescription',
        autoAdvance: true,
       },
      // STEP 12: Meat Frequency (Single Button - Auto-advance) - Appears if not vegan/vegetarian?
       {
        id: 'diet_meat',
        type: 'single-button',
        question: 'How often do you eat meat?',
        options: [
            { id: 'meat_never', text: 'Never' },
            { id: 'meat_rarely', text: 'Rarely' },
            { id: 'meat_1_2_week', text: 'Once/twice per week' },
            { id: 'meat_3_plus_week', text: 'Three times per week or more' },
        ],
        inputKey: 'meatFrequency',
        autoAdvance: true,
        condition: (answers) => answers.dietDescription !== 'd_vegan' && answers.dietDescription !== 'd_vegetarian',
       },
       // STEP 13: Fish Frequency (Single Button - Auto-advance)
       {
        id: 'diet_fish',
        type: 'single-button',
        question: 'How often do you eat fish or seafood?',
         options: [
            { id: 'fish_never', text: 'Never' },
            { id: 'fish_rarely', text: 'Rarely' },
            { id: 'fish_1_week', text: 'Once per week' },
            { id: 'fish_2_plus_week', text: 'Twice per week or more' },
        ],
        inputKey: 'fishFrequency',
        autoAdvance: true,
       },
       // STEP 14: Dairy Frequency (Single Button - Auto-advance)
       {
        id: 'diet_dairy',
        type: 'single-button',
        question: 'How often do you eat dairy?',
         options: [
            { id: 'dairy_never', text: 'Never' },
            { id: 'dairy_rarely', text: 'Rarely' },
            { id: 'dairy_1_2_week', text: 'Once/twice per week' },
            { id: 'dairy_3_plus_week', text: 'Three times per week or more' },
        ],
        inputKey: 'dairyFrequency',
        autoAdvance: true,
       },
       // STEP 15: Fruit/Veg Serves (Single Button - Auto-advance)
        {
        id: 'diet_veg',
        type: 'single-button',
        question: 'How many serves of fruit and vegetables do you eat daily?',
         options: [
            { id: 'veg_0', text: 'Almost none' },
            { id: 'veg_1_2', text: '1-2 serves' },
            { id: 'veg_3_plus', text: '3 serves or more' },
        ],
        inputKey: 'vegServings',
        autoAdvance: true,
       },
      // STEP 16: Diet Restrictions (Checkbox)
       {
        id: 'diet_restrictions',
        type: 'checkbox',
        question: 'Do you have any diet restrictions or preferences?',
        options: [
          { id: 'dr_dairy', text: 'Limiting dairy' },
          { id: 'dr_gluten', text: 'Gluten free' },
          { id: 'dr_paleo', text: 'Paleo' },
          { id: 'dr_none', text: 'None', exclusive: true }, // Exclusive option
        ],
        inputKey: 'dietRestrictions',
        nextButtonText: 'Continue',
        validation: (value) => Array.isArray(value), // Needs an array (can be empty if none selected)
       },
       // STEP 17: Allergies (Checkbox)
       {
        id: 'allergies',
        type: 'checkbox', // Similar layout to Vitable's grid might need dedicated component or CSS Grid
        question: 'Are you allergic to any of the following?',
        subText: 'So we can exclude products that contain these allergens, if applicable.',
         options: [
            { id: 'al_none', text: 'None', exclusive: true }, {id: 'al_fish', text: 'Fish'},
            { id: 'al_gluten', text: 'Wheat and/or Gluten' }, {id: 'al_milk', text: 'Milk'},
            { id: 'al_soy', text: 'Soy' }, {id: 'al_sulphites', text: 'Sulphites'},
            { id: 'al_yeast', text: 'Yeast' }, {id: 'al_corn', text: 'Corn/Maize'},
            { id: 'al_treenuts', text: 'Tree nuts' }, {id: 'al_peanuts', text: 'Peanuts'},
            { id: 'al_egg', text: 'Egg' }, {id: 'al_sesame', text: 'Sesame'},
        ],
         inputKey: 'allergies',
         nextButtonText: 'Continue',
        validation: (value) => Array.isArray(value),
        // Layout requires 2 columns - Use CSS Grid
        gridColumns: 2,
       },
      // --- LIFESTYLE Section ---
       // STEP 18: Section Header (Auto-advance)
       {
        id: 'section-lifestyle',
        type: 'section-header',
        title: 'Lifestyle',
        stepNumber: 4,
        autoAdvanceDelay: 1800,
      },
      // STEP 19: Exercise Frequency (Single Button - Auto-advance)
      {
        id: 'exercise',
        type: 'single-button',
        question: 'How many days per week do you exercise on average?',
         options: [
            { id: 'ex_0', text: "I don't exercise" },
            { id: 'ex_1', text: '1' },
            { id: 'ex_2_3', text: '2-3' },
            { id: 'ex_4_plus', text: '4 or more' },
        ],
        inputKey: 'exerciseFrequency',
        autoAdvance: true,
       },
       // STEP 20: Sunshine Exposure (Single Button - Auto-advance)
        {
        id: 'sunshine',
        type: 'single-button',
        question: 'How often do you get 20 min of sunshine (at least on your face and hands, without sunscreen)?',
         options: [
            { id: 'sun_rarely', text: "Rarely, I don't really get in the sun" },
            { id: 'sun_weekends', text: 'On weekends and holidays only' },
            { id: 'sun_daily', text: 'Every day!' },
        ],
        inputKey: 'sunExposure',
        autoAdvance: true,
       },
       // STEP 21: Alcohol Consumption (Yes/No - Auto-advance)
       {
        id: 'alcohol',
        type: 'yes-no-circle',
        question: 'Do you often consume 8 or more alcoholic drinks in a week?',
        options: [ { id: 'yes', text: 'Yes' }, { id: 'no', text: 'No' }],
        inputKey: 'highAlcohol',
        autoAdvance: true,
      },
       // STEP 22: Smoking (Yes/No - Auto-advance)
       {
        id: 'smoking',
        type: 'yes-no-circle',
        question: 'Do you smoke?',
        subText: "Smoking may affect the body's ability to absorb vitamins and minerals.",
        inputKey: 'isSmoker',
        autoAdvance: true,
      },
       // ... Add more lifestyle questions similarly (UT health, sperm health, visual fatigue, iron, traditional med...)

       // STEP X: Email Capture
      {
        id: 'email',
        type: 'email',
        question: 'Which email address should we use?',
        subText: 'So we can save your personalized recommendations.',
        placeholder: 'Enter your email',
        // Use double quotes for the string to easily contain single quotes/apostrophes
        consentText: "By checking this box, you confirm that you have read and agreed to our Privacy Policy. By choosing 'See my results', you also consent to receiving our communications and exclusive offers and can unsubscribe at any time.", // << Added comma
        inputKey: 'email', // Comma OK
        buttonText: 'See My Results', // << Added comma
        validation: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value || ""), // Basic email format check (handle null value) // << Added comma
        validationMessage: "Please enter a valid email address.", // << Added comma
        consentInputKey: 'hasConsented' // Store consent separately // << Last property, no comma
      }, // Comma after closing brace
                                
       // STEP Y: Loading Spinner (Auto-advance simulation)
       {
         id: 'loading',
         type: 'loading',
         // No input key, auto-advances after simulating processing
       },
       // STEP Z: Results Page
       {
        id: 'results',
        type: 'results',
        // No inputKey. Content will be based on final `answers` state.
       }
    ];

    // Helper to get steps relevant for progress bar (exclude welcome, loading, results)
    export const getProgressSteps = (allSteps) => {
        // Count actual question/interaction steps for progress bar
        // Excludes informational, sections, loading, results, welcome
        return allSteps.filter(step =>
            step.id !== 'welcome' &&
            step.type !== 'loading' &&
            step.type !== 'results' &&
            step.type !== 'info' &&
            step.type !== 'section-header'
            // Note: Conditional steps ARE included in the progress count for simplicity,
            // even if they are skipped in navigation.
        );
    }
""")

APP_CSS_CONTENT = dedent("""\
    /* src/styles/App.css */

    /* --- CSS Variables & Basic Reset --- */
    :root {
      --provit-green: #75c045;
      --provit-blue: #0babc3;
      --provit-light-green: #a8d88a;
      --provit-light-blue: #6fc8d7;
      --provit-background: #f8f6f2;
      --provit-text-dark: #333333;
      --provit-text-light: #555555;
      --provit-border-color: #e0e0e0;
      --provit-white: #ffffff;
      --provit-gradient-green: linear-gradient(105deg, var(--provit-light-green) 0%, var(--provit-green) 100%);
      --provit-gradient-blue: linear-gradient(105deg, var(--provit-light-blue) 0%, var(--provit-blue) 100%);
      --provit-error-color: #d9534f;
      /* UPDATE: Define standard font families */
      --font-primary: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
      /* UPDATE: Consider adding a specific 'cursive' font class for inputs if desired */
      /* @import url('...'); /* Import custom fonts here */
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: var(--font-primary);
      background-color: var(--provit-background);
      color: var(--provit-text-dark);
      overflow-x: hidden; /* Prevent horizontal scroll during transitions */
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }

    /* --- Main Container & Header --- */
    .survey-container {
      max-width: 700px; /* Centered content */
      margin: 0 auto;
      padding: 20px 20px 60px 20px; /* Add more bottom padding */
      position: relative;
      min-height: 90vh; /* Ensure vertical space */
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .survey-header {
        width: 100%;
        text-align: center;
        padding: 15px 0;
        margin-bottom: 20px; /* Less margin */
    }

    .survey-header img {
        height: 35px; /* Adjust as needed */
        /* Use the white version as background is light */
    }

    /* --- Progress Bar --- */
    .progress-bar-container {
        width: 80%;
        max-width: 400px;
        margin: 0 auto 40px auto; /* Position and space below */
        height: 8px;
    }

    .progress-bar {
      display: flex;
      height: 100%;
      width: 100%;
      gap: 5px;
    }

    .progress-segment {
      flex: 1;
      height: 100%;
      background-color: var(--provit-border-color); /* Inactive color */
      border-radius: 4px;
      transition: background-color 0.4s ease-out;
    }

    .progress-segment.active {
      background-color: var(--provit-green); /* Active color */
    }

    /* --- Animated Step Wrapper --- */
    .step-wrapper {
        width: 100%;
        position: relative; /* Needed for AnimatePresence mode='wait' */
        min-height: 300px; /* Give wrapper a minimum height to prevent collapse during transition */
    }

    /* --- Question Step General Styling --- */
    .question-step {
      width: 100%;
      text-align: center;
      padding: 10px 0; /* Vertical padding for content */
      /* Framer Motion handles positioning/opacity */
    }

    .question-step h1 { /* For Welcome Screen */
        font-size: 2.2rem;
        font-weight: 600;
        margin-bottom: 15px;
        line-height: 1.3;
    }

    .question-step h2 { /* For Questions */
      font-size: 1.8rem; /* Slightly smaller than Vitable perhaps */
      font-weight: 500;
      margin-bottom: 10px;
      line-height: 1.3;
    }

    .question-step .sub-text {
        font-size: 1rem;
        color: var(--provit-text-light);
        margin-top: 5px; /* Give a little space from h2 */
        margin-bottom: 35px;
        max-width: 550px; /* Limit width */
        margin-left: auto;
        margin-right: auto;
        line-height: 1.5; /* Improve readability */
    }

    /* --- Options Container --- */
    .options-container {
      display: flex;
      flex-direction: column;
      gap: 15px;
      width: 100%;
      max-width: 500px; /* Limit option width */
      margin: 0 auto;
    }

    /* Grid specific layout */
    .options-grid-container {
        display: grid;
        gap: 15px;
        width: 100%;
        max-width: 550px; /* Slightly wider for grid */
        margin: 0 auto;
    }
    /* JS will set grid-template-columns style directly based on gridColumns prop */


    /* --- General Option Button --- */
    .option-button {
      display: flex;
      align-items: center;
      justify-content: center; /* Default center */
      padding: 16px 20px; /* Adjusted padding */
      border: 2px solid var(--provit-border-color);
      border-radius: 12px;
      background-color: var(--provit-white);
      font-size: 1rem;
      text-align: center;
      cursor: pointer;
      transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.15s ease, box-shadow 0.15s ease;
      position: relative;
      min-height: 60px;
      line-height: 1.4; /* Ensure text doesn't get squished */
    }

    .option-button:hover:not(.selected) { /* Don't apply hover transform if already selected */
      border-color: var(--provit-green);
      transform: translateY(-2px);
      box-shadow: 0 3px 8px rgba(0, 0, 0, 0.08);
    }

    .option-button.selected {
      border-color: var(--provit-green);
      background: var(--provit-gradient-green); /* Green Gradient for selected */
      color: var(--provit-white);
      box-shadow: 0 4px 10px rgba(117, 192, 69, 0.3); /* Green shadow */
    }
    /* Fix text color inside selected buttons if needed */
    .option-button.selected span {
        color: var(--provit-white);
    }


    /* Grid item specific styling */
    .option-button.grid-item {
        flex-direction: column;
        gap: 8px;
        font-size: 0.9rem;
        padding: 15px 10px;
    }

    .option-button .icon {
        font-size: 1.6rem; /* Icon size */
        margin-bottom: 4px; /* Space between icon and text */
    }

    /* Checkbox style adjustments */
    .checkbox-option {
        justify-content: flex-start; /* Align left */
        gap: 12px; /* Space between check and text */
        /* Ensure label clicks trigger handler */
        cursor: pointer;
    }

    /* Custom Checkbox Visual */
    .checkbox-option .checkbox-custom {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid var(--provit-border-color);
        border-radius: 4px;
        background-color: var(--provit-white);
        position: relative;
        transition: border-color 0.2s ease, background-color 0.2s ease;
        flex-shrink: 0; /* Prevent shrinking */
    }
    .option-button.checkbox-option.selected .checkbox-custom { /* Style when row is selected */
        border-color: var(--provit-white);
        background-color: var(--provit-white); /* Use white checkmark bg */
    }

    /* Custom checkmark indicator */
    .checkbox-option .checkbox-custom::after {
        content: '';
        position: absolute;
        left: 6px; /* Adjust position */
        top: 2px;  /* Adjust position */
        width: 5px;
        height: 10px;
        border-style: solid;
        border-color: var(--provit-green); /* Green check */
        border-width: 0 3px 3px 0;
        transform: rotate(45deg) scale(0);
        transition: transform 0.15s cubic-bezier(0.18, 0.89, 0.32, 1.28); /* Add bounce */
        transition-delay: 0.05s; /* Slight delay */
    }
    /* Change checkmark color when background changes */
    .option-button.checkbox-option.selected .checkbox-custom::after {
        border-color: var(--provit-green); /* Check remains green on green bg? Maybe white? */
        transform: rotate(45deg) scale(1);
    }


    /* --- Yes/No Circle Style --- */
    .yes-no-container {
        display: flex;
        justify-content: center;
        gap: 40px; /* Space */
        margin-top: 30px;
    }

    .yes-no-option {
        font-size: 1.6rem; /* Larger text */
        font-weight: 500;
        cursor: pointer;
        padding: 8px 15px;
        border-radius: 50%; /* Make it circle-ready */
        position: relative;
        transition: color 0.2s ease;
    }

    .yes-no-option:hover {
        color: var(--provit-green);
    }

    .yes-no-option.selected {
        color: var(--provit-green);
    }

    /* REFINEMENT: Add SVG or pseudo-element for the Vitable hand-drawn circle animation */
    /* Placeholder: simple border animation */
    .yes-no-option::after {
        content: '';
        position: absolute;
        top: -10px; bottom: -10px; left: -15px; right: -15px; /* Expand bounds */
        border: 2.5px solid var(--provit-green);
        border-radius: 50%;
        opacity: 0;
        transform: scale(0.75) rotate(-15deg); /* Start smaller and rotated */
        transition: transform 0.35s cubic-bezier(0.18, 0.89, 0.32, 1.28), opacity 0.3s ease; /* Bounce */
        pointer-events: none;
        transform-origin: center center;
    }
    .yes-no-option.selected::after {
        opacity: 1;
        transform: scale(1) rotate(0deg); /* Grow and un-rotate */
    }


    /* --- Text Input Style --- */
    .text-input-container {
        margin-bottom: 30px;
        width: 100%;
        max-width: 400px;
        margin-left: auto;
        margin-right: auto;
    }
    .text-input {
      width: 100%;
      padding: 10px 5px 8px 5px; /* Adjust padding */
      font-size: 1.8rem; /* Vitable-like large input */
      border: none;
      border-bottom: 2px solid var(--provit-border-color);
      background-color: transparent;
      text-align: center;
      outline: none;
      transition: border-color 0.2s ease;
      color: var(--provit-text-dark);
    }

    /* UPDATE: Style placeholder distinctly (consider a specific font) */
    .text-input::placeholder {
       color: var(--provit-border-color);
       /* Example using a system cursive font */
       font-family: 'Comic Sans MS', 'Brush Script MT', cursive; /* Add fallback */
       font-style: normal; /* Reset italic if needed */
       opacity: 0.9;
    }

    .text-input:focus {
        border-color: var(--provit-green);
    }
    .text-input.error {
        border-color: var(--provit-error-color);
    }
    .validation-error-msg {
        color: var(--provit-error-color);
        font-size: 0.85rem;
        margin-top: 8px;
        text-align: center; /* Center error below input */
    }


    /* --- Navigation Buttons --- */
    .navigation-buttons {
        display: flex;
        /* Dynamically adjusted by JS via inline style or class */
        justify-content: space-between; /* Default: Space out Back and Next */
        gap: 20px;
        margin-top: 40px;
        width: 100%;
        max-width: 550px; /* Align with widest option containers */
        margin-left: auto;
        margin-right: auto;
        padding: 0 10px;
    }
    /* Center nav if only one button (applied via style in component) */
    .navigation-buttons.center {
        justify-content: center;
    }


    .nav-button {
        padding: 14px 45px; /* Slightly larger padding */
        font-size: 1rem;
        font-weight: 600;
        border: none;
        border-radius: 30px; /* More rounded */
        cursor: pointer;
        transition: opacity 0.2s ease, box-shadow 0.2s ease, transform 0.1s ease;
        min-width: 120px; /* Ensure minimum size */
        text-align: center;
    }

    .nav-button.next { /* Also used for Continue */
      color: var(--provit-white);
      background: var(--provit-gradient-blue); /* Default blue gradient */
      box-shadow: 0 4px 10px rgba(11, 171, 195, 0.2);
    }
    /* Specific override for Submit button */
    .nav-button.submit {
         background: var(--provit-gradient-green); /* Green gradient for final submit */
         box-shadow: 0 4px 10px rgba(117, 192, 69, 0.2);
    }

    .nav-button.prev {
      background-color: transparent;
      color: var(--provit-text-light);
      border: 2px solid var(--provit-border-color); /* Add border */
    }

    .nav-button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
       box-shadow: none;
       transform: none;
    }

    .nav-button:not(:disabled):hover {
        opacity: 0.88;
        transform: translateY(-1px);
    }
    .nav-button.next:not(:disabled):hover {
        box-shadow: 0 6px 12px rgba(11, 171, 195, 0.25);
    }
    .nav-button.submit:not(:disabled):hover {
        box-shadow: 0 6px 12px rgba(117, 192, 69, 0.25);
    }
    .nav-button.prev:not(:disabled):hover {
        color: var(--provit-text-dark);
        border-color: var(--provit-text-light);
        box-shadow: none;
    }

    /* --- Section Header Styling --- */
    .section-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 15px; /* Space */
        margin: 30px 0 40px 0; /* Add vertical spacing */
    }
    .section-header .step-indicator {
        font-size: 0.9rem;
        color: var(--provit-text-light);
        position: relative;
        padding: 2px 0;
        /* REFINEMENT: Add SVG circle animation around this text */
    }

    .section-header h2 {
        font-size: 2.2rem;
        font-weight: 500;
        position: relative;
        margin: 0; /* Reset default margins */
        padding: 0 10px 8px 10px; /* Add padding around text */
        /* REFINEMENT: Replace simple border with animated circle effect */
    }
     /* Placeholder simple line for Section Title */
    .section-header h2::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 70px; /* Longer line */
        height: 3px;
        background-color: var(--provit-green);
        border-radius: 2px;
        /* Animate this on appear? */
    }


    /* --- Loader Style --- */
    .loader {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        min-height: 350px; /* Ensure space */
        gap: 25px;
    }
    .loader img {
        height: 70px;
        width: 70px;
        animation: spin 1.5s linear infinite;
        opacity: 0.8;
    }
    .loader p {
        color: var(--provit-text-light);
        font-size: 1rem;
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }


    /* --- Results Page Placeholder --- */
    .results-page {
        width: 100%;
        max-width: 650px; /* Control width */
        margin: 20px auto;
        text-align: left;
    }
    .results-page h2 {
        text-align: center;
        margin-bottom: 30px;
        font-size: 1.8rem;
        font-weight: 600;
    }
    .results-summary {
        background-color: var(--provit-white);
        padding: 25px 30px;
        border-radius: 12px;
        border: 1px solid var(--provit-border-color);
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
    }
    .results-summary p {
        margin-top: 0;
        font-weight: 600;
        color: var(--provit-text-dark);
        margin-bottom: 15px;
    }
    .results-summary pre {
        white-space: pre-wrap;
        word-wrap: break-word;
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 4px;
        border: 1px solid #eee;
        font-size: 0.85rem;
        max-height: 400px;
        overflow-y: auto;
        color: #444;
    }
    .results-summary .results-note {
        margin-top: 25px;
        text-align: center;
        font-style: italic;
        font-size: 0.9rem;
        color: var(--provit-text-light);
    }


    /* --- Email Step Specifics --- */
    .consent-label {
        margin-top: 25px;
        display: flex;
        align-items: flex-start; /* Align checkbox with top of text */
        justify-content: center;
        gap: 10px;
        font-size: 0.8rem; /* Slightly smaller */
        line-height: 1.45;
        color: var(--provit-text-light);
        max-width: 500px;
        margin-left: auto;
        margin-right: auto;
        text-align: left;
    }
    .consent-label input[type="checkbox"] {
         /* Style the checkbox */
         appearance: none; /* Remove default */
         width: 16px;
         height: 16px;
         border: 2px solid var(--provit-border-color);
         border-radius: 3px;
         margin-top: 2px;
         cursor: pointer;
         position: relative;
         flex-shrink: 0;
         transition: background-color 0.2s ease, border-color 0.2s ease;
    }
    .consent-label input[type="checkbox"]:checked {
        background-color: var(--provit-green);
        border-color: var(--provit-green);
    }
    /* Checkmark for custom checkbox */
    .consent-label input[type="checkbox"]:checked::after {
        content: '';
        position: absolute;
        left: 4px; top: 1px;
        width: 4px; height: 8px;
        border: solid var(--provit-white);
        border-width: 0 2px 2px 0;
        transform: rotate(45deg);
    }
    .consent-label a { /* Style links in consent */
        color: var(--provit-blue);
        text-decoration: underline;
    }


    /* --- Basic Responsiveness --- */
    @media (max-width: 600px) {
        .survey-container {
            padding: 15px 15px 40px 15px;
        }
         .question-step h1 { font-size: 1.8rem; }
         .question-step h2 { font-size: 1.5rem; }
         .question-step .sub-text { font-size: 0.9rem; margin-bottom: 25px;}

         .options-container, .options-grid-container {
             max-width: 100%; /* Use full width on small screens */
         }
         .options-grid-container {
             grid-template-columns: repeat(2, 1fr); /* Grid to 2 columns */
          }

         .option-button { padding: 14px 15px; font-size: 0.9rem; }
         .option-button.grid-item { font-size: 0.85rem; }
         .yes-no-option { font-size: 1.3rem; }
         .text-input { font-size: 1.5rem; }
         .text-input::placeholder { font-size: 1.5rem;}

         .navigation-buttons {
             gap: 15px;
             padding: 0 10px;
             max-width: 100%; /* Allow buttons full width */
             /* Buttons might need to stack or become full width */
         }
         .nav-button {
             padding: 12px 25px;
             font-size: 0.95rem;
             min-width: 100px;
         }

          .consent-label {
              font-size: 0.75rem;
          }
           .results-page { max-width: 100%; padding: 0 5px; }
           .results-summary { padding: 20px; }
           .results-summary pre { font-size: 0.75rem; }
    }


    /* --- Accessibility Focus States --- */
    :focus-visible {
      outline: 3px solid var(--provit-blue);
      outline-offset: 2px;
      border-radius: 4px; /* Add radius to outline */
    }
    /* Specific overrides if default isn't good */
    .option-button:focus-visible,
    .nav-button:focus-visible,
    .yes-no-option:focus-visible {
       /* Inherits from general :focus-visible */
    }
    .text-input:focus-visible {
      outline-offset: 0; /* Outline inside for input */
      border-radius: 0;
    }
    .consent-label input[type="checkbox"]:focus-visible {
         outline: 3px solid var(--provit-blue);
         outline-offset: 1px;
    }

""")

PROGRESS_BAR_JSX_CONTENT = dedent("""\
    // src/components/ProgressBar.jsx
    import React from 'react';
    import '../styles/App.css'; // Import shared styles

    const ProgressBar = ({ current, total }) => {
      // current is 1-based index of current step in progress
      // total is the total number of steps in progress
      if (total <= 0 || current <= 0) {
           // Optionally render nothing or an empty container if no progress to show
          // This might happen before the first real question step loads
          return <div className="progress-bar-container" style={{ opacity: 0 }}></div>;
      }

      return (
        // Wrapper controls the centering and max-width
        <div className="progress-bar-container">
            <div className="progress-bar">
            {/* Create segments based on total */}
            {Array.from({ length: total }).map((_, index) => (
                <div
                key={index}
                // Segment is active if its index (0-based) is less than the current step (1-based)
                className={`progress-segment ${index < current ? 'active' : ''}`}
                />
            ))}
            </div>
        </div>
      );
    };

    export default ProgressBar;
""")

APP_JSX_CONTENT = dedent("""\
    // src/App.jsx
    import React, { useState, useEffect, useMemo, useCallback } from 'react';
    import { motion, AnimatePresence } from 'framer-motion';
    import { surveySteps, getProgressSteps, PROVIT_GRADIENT_GREEN, PROVIT_GRADIENT_BLUE } from './data/surveyData';
    import ProgressBar from './components/ProgressBar';
    import './styles/App.css'; // Main styles

    // Calculate steps relevant for progress bar calculation ONCE
    const progressSteps = getProgressSteps(surveySteps);
    const totalProgressSteps = progressSteps.length;

    function App() {
      // --- State ---
      const [currentStepIndex, setCurrentStepIndex] = useState(0);
      const [answers, setAnswers] = useState({});
      // Direction determines animation flow (1 = next, -1 = prev)
      const [direction, setDirection] = useState(1);
      // Control visibility of progress bar
      const [showProgress, setShowProgress] = useState(false);
      // Store validation message for the current step
      const [validationError, setValidationError] = useState('');

      // --- Derived State & Memos ---

      // Get the data object for the current step
      const currentStepData = useMemo(() => surveySteps[currentStepIndex], [currentStepIndex]);

      // Calculate the current position for the ProgressBar (1-based index)
      const currentProgressPosition = useMemo(() => {
        // No progress for welcome, loading, or results steps
        if (!currentStepData || ['welcome', 'loading', 'results'].includes(currentStepData.type)) {
          return 0;
        }
        // Find the index of the current step *within the filtered progressSteps array*
        const indexInProgressBar = progressSteps.findIndex(step => step.id === currentStepData.id);
        // Return 1-based index if found, otherwise 0 (should generally be found)
        return indexInProgressBar >= 0 ? indexInProgressBar + 1 : 0;
      }, [currentStepData]); // Depends only on the current step

      // Check if the 'Back' button should be shown
      const showBackButton = useMemo(() => {
           // Allow back if not on step 0 AND if a valid previous step exists
          if (currentStepIndex === 0) return false;
          const prevIndex = findValidStepIndex(currentStepIndex, -1);
          return prevIndex >= 0;
      }, [currentStepIndex, findValidStepIndex]); // Recalculate if index changes

      // --- Navigation Logic ---

      // Memoized function to find the next/previous valid step index
      const findValidStepIndex = useCallback((startIndex, moveDirection) => {
        let nextIndex = startIndex + moveDirection;
        while (nextIndex >= 0 && nextIndex < surveySteps.length) {
          const step = surveySteps[nextIndex];
          // Check if step has a condition and if that condition is met by current answers
          if (!step.condition || step.condition(answers)) {
            return nextIndex; // Valid step found
          }
          // If condition not met, continue searching in the same direction
          nextIndex += moveDirection;
        }
        return -1; // No valid step found (reached start or end)
      }, [answers]); // Recalculate this function only if answers change

      // --- Event Handlers ---

      // Handles moving to the next step, including validation
      const handleNext = useCallback(() => {
        setValidationError(''); // Clear previous errors

        // --- Validation ---
        if (currentStepData?.validation) {
          const currentAnswer = answers[currentStepData.inputKey];
          const consentAnswer = currentStepData.consentInputKey ? answers[currentStepData.consentInputKey] : true; // Assume true if no consent key

          // Specific check for email consent checkbox
          if (currentStepData.type === 'email' && currentStepData.consentInputKey && !consentAnswer) {
            setValidationError('Please agree to the terms to continue.');
            return; // Stop navigation
          }

          // Run the step's validation function
          if (!currentStepData.validation(currentAnswer)) {
            setValidationError(currentStepData.validationMessage || 'Please provide a valid answer.');
            return; // Stop navigation
          }
        }

        // --- Navigation ---
        setDirection(1); // Set animation direction to forward
        const nextIndex = findValidStepIndex(currentStepIndex, 1);

        if (nextIndex !== -1) {
          setCurrentStepIndex(nextIndex); // Move to the next valid step
        } else {
          // Reached the end of survey logic
          console.log("End of survey path.");
          // If the current step should logically lead to loading (like email step), trigger it
          if (currentStepData?.type === 'email') {
            const loadingIndex = surveySteps.findIndex(s => s.type === 'loading');
            if (loadingIndex > -1) {
              setCurrentStepIndex(loadingIndex);
            } else {
              console.error("Critical: Loading step not found in surveyData.js");
            }
          }
        }
      }, [currentStepIndex, findValidStepIndex, currentStepData, answers]); // Dependencies for useCallback

      // Handles moving to the previous step
      const handlePrev = useCallback(() => {
        if (currentStepIndex === 0) return; // Safety check: Should not be possible if button hidden
        setValidationError(''); // Clear errors when going back
        setDirection(-1); // Set animation direction to backward
        const prevIndex = findValidStepIndex(currentStepIndex, -1);
        if (prevIndex !== -1) {
          setCurrentStepIndex(prevIndex); // Move to previous valid step
        } else {
          console.warn("Could not find a valid previous step (should normally find welcome).");
        }
      }, [currentStepIndex, findValidStepIndex]);

      // Handles text/email/number input changes
      const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        // Use input's 'name' attr or fallback to step's inputKey
        const key = name || currentStepData.inputKey;
        if (!key) return; // No key to store answer against

        setAnswers(prev => ({
          ...prev,
          // Use 'checked' property for checkboxes, 'value' for others
          [key]: type === 'checkbox' ? checked : value
        }));

        // Clear validation error as user types/changes value
        if (validationError) setValidationError('');
      };

      // Handles clicks on button-style options (single & multi-select)
      const handleSelect = (optionId, isMulti = false, isExclusive = false) => {
        const key = currentStepData.inputKey;
        if (!key) return;

        setAnswers(prev => {
          const currentSelection = prev[key];
          let newSelection;

          if (isMulti) {
            // Ensure current value is an array for multi-select
            const currentArray = Array.isArray(currentSelection) ? currentSelection : [];

            if (isExclusive) {
              // Selecting an exclusive option: if it's already selected, deselect all. Otherwise, select only it.
              newSelection = currentArray.includes(optionId) ? [] : [optionId];
            } else {
              // Selecting a non-exclusive option:
              // 1. Filter out any currently selected exclusive option first
              const exclusiveOptionId = currentStepData.options?.find(opt => opt.exclusive)?.id;
              let tempArray = currentArray.filter(id => id !== exclusiveOptionId);

              // 2. Toggle the clicked option ID in the filtered array
              if (tempArray.includes(optionId)) {
                newSelection = tempArray.filter(id => id !== optionId); // Deselect
              } else {
                // Select (Optional: add maxSelection limit check here if needed)
                newSelection = [...tempArray, optionId];
              }
            }
          } else {
            // Single select: just replace the current value with the new optionId
            newSelection = optionId;
          }
          return { ...prev, [key]: newSelection };
        });

        // --- Auto-Advance Logic ---
        // Only auto-advance on single-select button/yes-no types that have the flag
        if (currentStepData.autoAdvance && !isMulti) {
          setTimeout(handleNext, 250); // Delay allows visual feedback of selection
        }

        // Clear validation error upon selection
        if (validationError) setValidationError('');
      };

      // Handles clicks on checkbox options (where the label itself is the button)
      const handleCheckboxGroupClick = (optionId) => {
         // Reuses the multi-select logic from handleSelect
         const isExclusive = currentStepData.options?.find(opt => opt.id === optionId)?.exclusive || false;
         handleSelect(optionId, true, isExclusive); // Always multi-select for checkbox groups
      };


      // --- Effects ---

      // Effect runs when the current step changes
      useEffect(() => {
        let timerId = null;

        // Handle auto-advancing steps (info, section-header)
        const advanceDelay = currentStepData?.autoAdvanceDelay;
        if (advanceDelay && currentStepData.type !== 'loading') {
          timerId = setTimeout(handleNext, advanceDelay);
        }

        // Handle simulated loading time
        if (currentStepData?.type === 'loading') {
          timerId = setTimeout(() => {
            const resultsIndex = surveySteps.findIndex(s => s.type === 'results');
            if (resultsIndex > -1) {
              setCurrentStepIndex(resultsIndex);
            } else {
              console.error("Critical: Results step not found!");
            }
          }, 2000); // Simulate 2 seconds
        }

        // Control visibility of the progress bar
        const isProgressRelevant = currentStepIndex > 0 &&
                                   currentStepData?.type !== 'loading' &&
                                   currentStepData?.type !== 'results';
        setShowProgress(isProgressRelevant);

        // Scroll page to top on step transition for better visibility
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // Cleanup function for the timer
        return () => {
          if (timerId) clearTimeout(timerId);
        };
      }, [currentStepIndex, currentStepData, handleNext]); // Dependencies: run effect when these change

      // --- Framer Motion Animation Variants ---
      const variants = {
        enter: (direction) => ({ // Animate in
          y: direction > 0 ? 20 : -20, // Start slightly offset vertically
          opacity: 0,
        }),
        center: { // State when visible
          zIndex: 1,
          y: 0,
          opacity: 1,
        },
        exit: (direction) => ({ // Animate out
          zIndex: 0,
          y: direction < 0 ? 20 : -20, // Move slightly offset vertically
          opacity: 0,
        }),
      };

      // --- Dynamic Rendering Function for Step Content ---
      const renderStepContent = () => {
        if (!currentStepData) return <div className="question-step">Loading...</div>; // Should not happen normally

        // Destructure step data properties
        const {
          type, id, question, subText, placeholder, options = [], inputKey,
          title, text, buttonText, stepNumber, inputType = 'text',
          consentText, gridColumns, consentInputKey
        } = currentStepData;

        // Get the currently stored answer for this step's key
        const currentAnswer = answers[inputKey];
        // Determine if there's an active validation error for this step
        const hasError = !!validationError; // Simpler: error exists = show (context determined in input/area)


        // Render different components based on step 'type'
        switch (type) {
          case 'welcome':
            return (
              <div className="question-step">
                <h1>{title}</h1>
                <p className="sub-text">{text}</p>
                <button
                  className="nav-button next submit" // Use 'submit' style for green gradient
                  onClick={handleNext}
                  style={{ background: PROVIT_GRADIENT_GREEN }} // Apply green gradient
                >
                  {buttonText}
                </button>
              </div>
            );

          case 'text':
          case 'email':
            return (
              <div className="question-step">
                <h2>{question}</h2>
                {subText && <p className="sub-text">{subText}</p>}
                <div className="text-input-container">
                  <input
                    id={inputKey} // Associate label/error message
                    type={inputType}
                    name={inputKey}
                    placeholder={placeholder}
                    value={currentAnswer || ''}
                    onChange={handleInputChange}
                    className={`text-input ${hasError ? 'error' : ''}`}
                    aria-invalid={hasError}
                    aria-describedby={hasError ? `${inputKey}-error` : undefined}
                    autoFocus={id !== 'email'} // Focus most text inputs on load
                    key={id} // Add key to help React focus correctly
                  />
                  {/* Display validation error message */}
                  {hasError && <p id={`${inputKey}-error`} className="validation-error-msg" role="alert">{validationError}</p>}
                </div>

                {/* Render consent checkbox only for 'email' type */}
                {type === 'email' && consentInputKey && (
                  <label className="consent-label">
                    <input
                      type="checkbox"
                      name={consentInputKey}
                      checked={!!answers[consentInputKey]}
                      onChange={handleInputChange}
                      aria-describedby={hasError && !answers[consentInputKey] ? `${inputKey}-error` : undefined} // Link error to checkbox too if consent failed
                    />
                     {/* UPDATE: Replace <a> with Link component if using React Router */}
                    <span dangerouslySetInnerHTML={{ __html: consentText?.replace('Privacy Policy', '<a href="/privacy" target="_blank" rel="noopener noreferrer">Privacy Policy</a>') || "I agree to the terms." }}>
                       {/* Using dangerouslySetInnerHTML assumes consentText is safe or sanitized */}
                    </span>
                  </label>
                )}
              </div>
            );

           case 'info':
             const infoText = id === 'greeting' && answers.userName
               ? `Nice to meet you, ${answers.userName}!`
               : (text || 'Processing...');
             return <div className="question-step"><h2>{infoText}</h2></div>;

           case 'section-header':
             return (
               <div className="question-step section-header">
                 {/* REFINEMENT: Replace with SVG circle animation */}
                 <span className="step-indicator">Step {stepNumber}</span>
                 <h2>{title}</h2>
               </div>
             );

           case 'single-button':
           case 'multi-grid':
           case 'checkbox':
             // Determine container and styling based on type
             const isGrid = type === 'multi-grid' || !!gridColumns;
             const ContainerComponent = isGrid ? 'div' : 'div'; // Just a div for layout
             const containerClass = isGrid ? 'options-grid-container' : 'options-container';
             const gridStyle = isGrid ? { gridTemplateColumns: `repeat(${gridColumns || (type === 'multi-grid' ? 3 : 1)}, 1fr)` } : {};

             return (
               <div className="question-step">
                 <h2>{question}</h2>
                 {subText && <p className="sub-text">{subText}</p>}
                 <ContainerComponent className={containerClass} style={gridStyle} role={type === 'checkbox' ? 'group' : undefined} aria-labelledby={question ? id + '-q' : undefined}>
                   {/* Assign id to question if needed for aria-labelledby */}
                    {question && <h2 id={id + '-q'} style={{ display: 'none' }}>{question}</h2>}

                   {options.map(opt => {
                     // Determine if the current option is selected
                     const isSelected = type === 'single-button'
                       ? currentAnswer === opt.id
                       : (Array.isArray(currentAnswer) && currentAnswer.includes(opt.id));

                     // Use <label> for checkboxes for better accessibility
                     const ButtonComponent = type === 'checkbox' ? 'label' : 'button';
                     const clickHandler = type === 'checkbox'
                       ? () => handleCheckboxGroupClick(opt.id)
                       : () => handleSelect(opt.id, type === 'multi-grid', opt.exclusive);

                     return (
                       <ButtonComponent
                         key={opt.id}
                         className={`option-button ${type === 'multi-grid' ? 'grid-item' : ''} ${type === 'checkbox' ? 'checkbox-option' : ''} ${isSelected ? 'selected' : ''}`}
                         onClick={clickHandler}
                         // Add type='button' for actual buttons to prevent form submission
                         type={ButtonComponent === 'button' ? 'button' : undefined}
                         // Link label to hidden input for checkboxes
                         htmlFor={type === 'checkbox' ? `${inputKey}-${opt.id}` : undefined}
                         // Add ARIA roles and states
                         role={type !== 'checkbox' ? 'button' : undefined} // Button role if not label
                         aria-pressed={type !== 'checkbox' ? isSelected : undefined} // Indicate toggle state
                         tabIndex={0} // Ensure focusability
                         onKeyDown={(e) => { if(e.key === 'Enter' || e.key === ' ') clickHandler() }} // Keyboard activation
                       >
                         {/* Hidden actual checkbox, state managed visually */}
                         {type === 'checkbox' && (
                           <input
                             id={`${inputKey}-${opt.id}`}
                             type="checkbox"
                             value={opt.id}
                             checked={isSelected || false}
                             onChange={() => {}} // Handler is on the label/button
                             style={{ // Visually hide, but keep accessible
                               position: 'absolute',
                               opacity: 0,
                               width: '1px',
                               height: '1px',
                               overflow: 'hidden'
                              }}
                             tabIndex={-1} // Remove from tab order, label handles focus
                           />
                         )}
                          {/* Custom styled checkbox indicator */}
                         {type === 'checkbox' && (<span className="checkbox-custom" aria-hidden="true"></span>)}
                         {/* Icon for grid items */}
                         {opt.icon && <span className="icon" aria-hidden="true">{opt.icon}</span>}
                         {/* Option Text */}
                         <span>{opt.text}</span>
                          {/* REFINEMENT: Add logic for numbered badges for goal priority */}
                       </ButtonComponent>
                     );
                   })}
                 </ContainerComponent>
                 {/* Display validation errors for multi-select steps if needed */}
                 {hasError && type !== 'single-button' && <p className="validation-error-msg" role="alert" style={{marginTop: '15px'}}>{validationError}</p>}
               </div>
             );

           case 'yes-no-circle':
             return (
               <div className="question-step">
                 <h2>{question}</h2>
                 {subText && <p className="sub-text">{subText}</p>}
                 <div className="yes-no-container" role="radiogroup" aria-labelledby={id + '-q'}>
                     {/* Hidden label */}
                    {question && <h2 id={id + '-q'} style={{ display: 'none' }}>{question}</h2>}
                   {options.map(opt => (
                     <span
                       key={opt.id}
                       className={`yes-no-option ${currentAnswer === opt.id ? 'selected' : ''}`}
                       onClick={() => handleSelect(opt.id, false, false)}
                       role="radio"
                       aria-checked={currentAnswer === opt.id}
                       tabIndex={currentAnswer === opt.id || (currentAnswer == null && opt.id === options[0].id) ? 0 : -1} // Manage focus within group
                       onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') handleSelect(opt.id, false, false)}}
                     >
                       {opt.text}
                     </span>
                   ))}
                 </div>
               </div>
             );

           case 'loading':
             return (
               <div className="question-step loader">
                 <img src="/provit-icon.png" alt="" /> {/* Decorative image */}
                 <p>Personalising your results...</p>
               </div>
             );

           case 'results':
             // UPDATE: Replace with actual results display.
             // Fetch recommendations based on 'answers' state or pass answers to a results component.
             return (
               <div className="question-step results-page">
                 <h2>Your PROVIT Insights</h2>
                 <div className='results-summary'>
                   <p>Survey complete! Here are the answers provided:</p>
                   <pre>{JSON.stringify(answers, null, 2)}</pre>
                   <p className="results-note">
                     (Backend integration needed to show actual product recommendations here)
                   </p>
                 </div>
               </div>
             );

           default:
             console.error(`Unknown step type: ${type}`);
             return <div className="question-step">Error: Step type not configured.</div>;
        }
      };

      // --- Final JSX Output ---
      return (
        <div className="survey-container">
          {/* Logo */}
          <header className="survey-header">
            <img src="/provit-logo-white.png" alt="PROVIT Logo" />
          </header>

          {/* Progress Bar (conditionally rendered) */}
          <AnimatePresence>
            {showProgress && (
              <motion.div
                 initial={{ opacity: 0, height: 0 }}
                 animate={{ opacity: 1, height: 'auto' }}
                 exit={{ opacity: 0, height: 0 }}
                 transition={{ duration: 0.3 }}
                 style={{ width: '100%', overflow: 'hidden' }} // Contain height animation
               >
                  <ProgressBar current={currentProgressPosition} total={totalProgressSteps} />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Step Content Area with Animations */}
          <div className='step-wrapper'>
             <AnimatePresence initial={false} custom={direction} mode="wait">
               <motion.div
                 key={currentStepIndex} // Key change triggers enter/exit animations
                 custom={direction}
                 variants={variants}
                 initial="enter"
                 animate="center"
                 exit="exit"
                 transition={{ // Customize transitions
                   y: { type: "spring", stiffness: 350, damping: 35 },
                   opacity: { duration: 0.25 }
                 }}
               >
                 {renderStepContent()}
               </motion.div>
             </AnimatePresence>
           </div>


          {/* Navigation Buttons Container */}
           <AnimatePresence>
            {currentStepData && // Only show nav container if there's step data
               !['welcome', 'loading', 'results', 'info', 'section-header'].includes(currentStepData.type) && // Exclude certain types
              !(currentStepData.autoAdvance && currentStepData.type !== 'text') // Hide if auto-advancing (unless text?)
             && (
             <motion.div
               className={`navigation-buttons ${!showBackButton ? 'center' : ''}`} // Center if back button is hidden
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                transition={{ delay: 0.1, duration: 0.2}} // Slight delay to appear after content
               >
                 {/* Back Button (conditionally rendered) */}
                 {showBackButton && (
                   <button
                     className="nav-button prev"
                     onClick={handlePrev}
                     type="button"
                   >
                     Back
                   </button>
                 )}
                 {/* Next / Continue / Submit Button */}
                 <button
                   className={`nav-button next ${currentStepData.type === 'email' ? 'submit' : ''}`}
                   onClick={handleNext}
                   type="button"
                   disabled={!!validationError} // Disable if there's a validation error active
                 >
                   {currentStepData.buttonText || 'Continue'}
                 </button>
               </motion.div>
             )}
          </AnimatePresence>

        </div>
      );
    }

    export default App;

""")

MAIN_JSX_CONTENT = dedent("""\
    // src/main.jsx
    import React from 'react';
    import ReactDOM from 'react-dom/client';
    import App from './App.jsx'; // Main survey component
    // Global styles imported within App.jsx now

    ReactDOM.createRoot(document.getElementById('root')).render(
      <React.StrictMode>
        <App />
      </React.StrictMode>,
    )
""")

# Dictionary mapping file paths (relative to project root) to their content
# Uses Path objects for better cross-platform compatibility
FILES_TO_CREATE = {
    Path("index.html"): INDEX_HTML_CONTENT,
    Path("src") / "data" / "surveyData.js": SURVEY_DATA_JS_CONTENT,
    Path("src") / "styles" / "App.css": APP_CSS_CONTENT,
    Path("src") / "components" / "ProgressBar.jsx": PROGRESS_BAR_JSX_CONTENT,
    Path("src") / "App.jsx": APP_JSX_CONTENT,
    Path("src") / "main.jsx": MAIN_JSX_CONTENT,
    # Placeholder files for images (must be replaced manually)
    Path("public") / "provit-logo-white.png": "",
    Path("public") / "provit-icon.png": "",
    # Placeholder for default Vite files (can be deleted by user or script)
    Path("src") / "index.css": "/* Delete this file */",
    Path("src") / "assets" / "react.svg": "/* Delete this folder */"
}

# List of required npm packages beyond the Vite defaults
REQUIRED_NPM_PACKAGES = ['framer-motion']

# --- Helper Functions ---

def create_file_with_content(filepath, content):
    """Creates a file and writes content to it, creating parent dirs if needed."""
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding='utf-8')
        print(f"  Created: {filepath}")
    except OSError as e:
        print(f"  Error creating {filepath}: {e}", file=sys.stderr)
        return False
    return True

def run_npm_install(packages):
    """Runs npm install for the specified packages."""
    command = ['npm', 'install'] + packages
    print(f"\nRunning: {' '.join(command)}")
    try:
        # Use shell=True on Windows if npm is not directly in PATH sometimes needed
        is_windows = sys.platform.startswith('win')
        result = subprocess.run(command, check=True, capture_output=True, text=True, shell=is_windows)
        print("  npm install successful.")
        # print(result.stdout) # Uncomment for detailed npm output
    except subprocess.CalledProcessError as e:
        print(f"  Error running npm install:", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        return False
    except FileNotFoundError:
        print("  Error: 'npm' command not found. Please ensure Node.js and npm are installed and in your PATH.", file=sys.stderr)
        return False
    return True

# --- Main Script Logic ---

def main():
    print("--- PROVIT Survey Project Populator ---")
    print("IMPORTANT: This script should be run *inside* a newly created Vite React project.")

    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")

    # Basic check: does it look like a vite react project?
    if not (Path('vite.config.js').exists() or Path('vite.config.ts').exists()) or not Path('package.json').exists():
         print("\nError: Could not find 'vite.config.js' or 'package.json'.")
         print("Please run this script *inside* the root directory of a project created with:")
         print(f"  npm create vite@latest {PROJECT_FOLDER_NAME} -- --template react")
         print("Then `cd " + PROJECT_FOLDER_NAME + "` and run this script again.")
         sys.exit(1)

    print("\nCreating project structure and files...")
    success_count = 0
    error_count = 0

    for filepath, content in FILES_TO_CREATE.items():
        # For files expected to be overwritten/replaced (like main.jsx, index.html), just create them
        # For optional files/dirs to delete, just create placeholders
        if create_file_with_content(filepath, content):
             success_count += 1
        else:
             error_count += 1

    if error_count > 0:
        print(f"\nWarning: {error_count} error(s) occurred during file creation.")

    print(f"\nCreated {success_count} files/placeholders.")

    # Delete default Vite files if they exist (optional cleanup)
    files_to_delete = [
        Path("src") / "App.css", # Default Vite App.css
        Path("src") / "index.css",
        Path("src") / "assets" / "react.svg"
    ]
    print("\nAttempting to remove default Vite placeholder files...")
    for f_path in files_to_delete:
        try:
            if f_path.is_file():
                f_path.unlink()
                print(f"  Removed: {f_path}")
            elif f_path.is_dir(): # For assets dir
                 if not any(f_path.iterdir()): # Check if empty first
                    f_path.rmdir()
                    print(f"  Removed empty dir: {f_path}")
                 else:
                    print(f"  Skipping non-empty dir: {f_path}")

        except OSError as e:
            print(f"  Could not remove {f_path}: {e}")

     # Check if parent dir 'src/assets' is empty now
    assets_dir = Path("src") / "assets"
    try:
        if assets_dir.is_dir() and not any(assets_dir.iterdir()):
            assets_dir.rmdir()
            print(f"  Removed empty dir: {assets_dir}")
    except OSError as e:
         print(f"  Could not remove {assets_dir}: {e}")


    # Install additional required dependencies
    if REQUIRED_NPM_PACKAGES:
        if not run_npm_install(REQUIRED_NPM_PACKAGES):
            print("\nDependency installation failed. Please run manually:")
            print(f"  npm install {' '.join(REQUIRED_NPM_PACKAGES)}")
        else:
             print(f"\nInstalled required packages: {', '.join(REQUIRED_NPM_PACKAGES)}")

    print("\n--- Setup Complete ---")
    print("\nNext Steps:")
    print("1. IMPORTANT: Replace placeholder image files in `public/` with your actual images:")
    print("   - public/provit-logo-white.png")
    print("   - public/provit-icon.png")
    print("2. Review the generated files, especially `index.html` and paths.")
    print("3. Add any custom fonts to `src/styles/App.css`.")
    print("4. Run the development server: `npm run dev`")
    print("5. Start coding and refining!")

if __name__ == "__main__":
    main()