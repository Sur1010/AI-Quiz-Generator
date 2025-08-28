// DOM Elements
const startQuizBtn = document.getElementById('startQuiz');
const loading = document.getElementById('loading');
const error = document.getElementById('error');

// File upload elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileStatus = document.getElementById('fileStatus');

// Sections
const textInputSection = document.getElementById('textInputSection');
const quizSection = document.getElementById('quizSection');
const resultsSection = document.getElementById('resultsSection');

// Quiz elements
const questionCounter = document.getElementById('questionCounter');
const progressFill = document.getElementById('progressFill');
const currentQuestion = document.getElementById('currentQuestion');
const submitAnswerBtn = document.getElementById('submitAnswer');
const nextQuestionBtn = document.getElementById('nextQuestion');
const finishQuizBtn = document.getElementById('finishQuiz');
const answerFeedback = document.getElementById('answerFeedback');

// Results elements
const scoreDisplay = document.getElementById('scoreDisplay');
const restartQuizBtn = document.getElementById('restartQuiz');
const newQuizBtn = document.getElementById('newQuiz');

// Quiz state
let currentQuizSession = null;
let currentQuestionIndex = 0;
let allQuestions = [];
let selectedAnswer = null;


// Event Listeners

// File upload event listeners
uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', handleDragOver);
uploadArea.addEventListener('dragleave', handleDragLeave);
uploadArea.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);

startQuizBtn.addEventListener('click', startInteractiveQuiz);
submitAnswerBtn.addEventListener('click', submitCurrentAnswer);
nextQuestionBtn.addEventListener('click', showNextQuestion);
finishQuizBtn.addEventListener('click', showResults);
restartQuizBtn.addEventListener('click', restartQuiz);
newQuizBtn.addEventListener('click', showTextInput);

async function startInteractiveQuiz() {
    alert('Please upload a file to generate a quiz.');
    return;
}

function initializeQuiz(quizData) {
    currentQuizSession = quizData.session_id;
    currentQuestionIndex = 0;
    
    // Combine all questions
    allQuestions = [
        ...quizData.mcq_questions,
        ...quizData.tf_questions
    ];

    // Show quiz section
    textInputSection.style.display = 'none';
    quizSection.style.display = 'block';
    resultsSection.style.display = 'none';

    showCurrentQuestion();
}

function showCurrentQuestion() {
    if (currentQuestionIndex >= allQuestions.length) {
        showResults();
        return;
    }

    const question = allQuestions[currentQuestionIndex];
    selectedAnswer = null;

    // Update progress
    questionCounter.textContent = `Question ${currentQuestionIndex + 1} of ${allQuestions.length}`;
    const progress = ((currentQuestionIndex + 1) / allQuestions.length) * 100;
    progressFill.style.width = `${progress}%`;

    // Clear previous content
    currentQuestion.innerHTML = '';
    answerFeedback.style.display = 'none';
    submitAnswerBtn.disabled = true;
    submitAnswerBtn.style.display = 'inline-block';
    nextQuestionBtn.style.display = 'none';
    finishQuizBtn.style.display = 'none';

    if (question.type === 'mcq') {
        showMCQQuestion(question);
    } else if (question.type === 'true_false') {
        showTrueFalseQuestion(question);
    }
}

function showMCQQuestion(question) {
    const html = `
        <div class="question-text">
            ${question.question}
            <span class="difficulty-badge difficulty-${question.difficulty.toLowerCase()}">${question.difficulty}</span>
        </div>
        <div class="question-options">
            ${question.options.map((option, index) => `
                <button class="option-button" data-index="${index}">
                    ${String.fromCharCode(65 + index)}) ${option}
                </button>
            `).join('')}
        </div>
    `;
    
    currentQuestion.innerHTML = html;

    // Add click handlers
    const optionButtons = currentQuestion.querySelectorAll('.option-button');
    optionButtons.forEach(button => {
        button.addEventListener('click', () => {
            optionButtons.forEach(btn => btn.classList.remove('selected'));
            button.classList.add('selected');
            selectedAnswer = button.dataset.index;
            submitAnswerBtn.disabled = false;
        });
    });
}

function showTrueFalseQuestion(question) {
    const html = `
        <div class="question-text">
            ${question.statement}
            <span class="difficulty-badge difficulty-${question.difficulty.toLowerCase()}">${question.difficulty}</span>
        </div>
        <div class="true-false-options">
            <button class="tf-button" data-answer="true">✓ True</button>
            <button class="tf-button" data-answer="false">✗ False</button>
        </div>
    `;
    
    currentQuestion.innerHTML = html;

    // Add click handlers
    const tfButtons = currentQuestion.querySelectorAll('.tf-button');
    tfButtons.forEach(button => {
        button.addEventListener('click', () => {
            tfButtons.forEach(btn => btn.classList.remove('selected'));
            button.classList.add('selected');
            selectedAnswer = button.dataset.answer;
            submitAnswerBtn.disabled = false;
        });
    });
}

async function submitCurrentAnswer() {
    if (!selectedAnswer) return;

    const question = allQuestions[currentQuestionIndex];

    try {
        const response = await fetch('/submit_answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentQuizSession,
                question_id: question.id,
                answer: selectedAnswer
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Failed to submit answer');
        }

        showAnswerFeedback(result.is_correct, result.correct_answer, question);

    } catch (err) {
        showError(err.message);
    }
}

function showAnswerFeedback(isCorrect, correctAnswer, question) {
    // Update button states
    if (question.type === 'mcq') {
        const optionButtons = currentQuestion.querySelectorAll('.option-button');
        optionButtons.forEach((button, index) => {
            if (index == correctAnswer) {
                button.classList.add('correct');
            } else if (index == selectedAnswer && !isCorrect) {
                button.classList.add('incorrect');
            }
            button.disabled = true;
        });
    } else {
        const tfButtons = currentQuestion.querySelectorAll('.tf-button');
        tfButtons.forEach(button => {
            if ((button.dataset.answer === 'true') === correctAnswer) {
                button.classList.add('correct');
            } else if (button.dataset.answer === selectedAnswer && !isCorrect) {
                button.classList.add('incorrect');
            }
            button.disabled = true;
        });
    }

    // Show feedback
    const feedbackClass = isCorrect ? 'feedback-correct' : 'feedback-incorrect';
    const feedbackIcon = isCorrect ? '✅' : '❌';
    const feedbackText = isCorrect ? 'Correct!' : 'Incorrect!';
    
    let correctAnswerText = '';
    if (!isCorrect) {
        if (question.type === 'mcq') {
            correctAnswerText = `<br><strong>Correct answer:</strong> ${String.fromCharCode(65 + correctAnswer)}) ${question.options[correctAnswer]}`;
        } else {
            correctAnswerText = `<br><strong>Correct answer:</strong> ${correctAnswer ? 'True' : 'False'}`;
        }
    }

    answerFeedback.innerHTML = `
        <div class="${feedbackClass}">
            ${feedbackIcon} <strong>${feedbackText}</strong>
            ${correctAnswerText}
        </div>
    `;
    answerFeedback.style.display = 'block';

    // Show next/finish button
    submitAnswerBtn.style.display = 'none';
    if (currentQuestionIndex < allQuestions.length - 1) {
        nextQuestionBtn.style.display = 'inline-block';
    } else {
        finishQuizBtn.style.display = 'inline-block';
    }
}

function showNextQuestion() {
    currentQuestionIndex++;
    showCurrentQuestion();
}

async function showResults() {
    try {
        const response = await fetch('/get_results', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentQuizSession
            })
        });

        const results = await response.json();

        if (!response.ok) {
            throw new Error(results.error || 'Failed to get results');
        }

        displayResults(results);

    } catch (err) {
        showError(err.message);
    }
}

function displayResults(results) {
    quizSection.style.display = 'none';
    resultsSection.style.display = 'block';

    const percentage = results.score_percentage;
    let scoreClass, scoreText;

    if (percentage >= 90) {
        scoreClass = 'score-excellent';
        scoreText = 'Excellent!';
    } else if (percentage >= 70) {
        scoreClass = 'score-good';
        scoreText = 'Good Job!';
    } else if (percentage >= 50) {
        scoreClass = 'score-fair';
        scoreText = 'Fair';
    } else {
        scoreClass = 'score-poor';
        scoreText = 'Keep Trying!';
    }

    scoreDisplay.innerHTML = `
        <div class="score-circle ${scoreClass}">
            ${percentage}%
        </div>
        <h3>${scoreText}</h3>
        <p>You answered <strong>${results.correct_answers}</strong> out of <strong>${results.total_questions}</strong> questions correctly.</p>
    `;
}

function restartQuiz() {
    currentQuestionIndex = 0;
    selectedAnswer = null;
    resultsSection.style.display = 'none';
    quizSection.style.display = 'block';
    showCurrentQuestion();
}

function showTextInput() {
    resultsSection.style.display = 'none';
    quizSection.style.display = 'none';
    textInputSection.style.display = 'block';
    fileStatus.style.display = 'none';
    uploadButton.addEventListener('click', function() {
        fileInput.click();
    });

    fileInput.addEventListener('change', function(e) {
        handleFileUploadAndQuizGeneration(e.target.files[0]);
    });

    // Handle drag and drop
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileUploadAndQuizGeneration(files[0]);
        }
    });
}

function startQuizFromData(quizData) {
    // Set up quiz with pre-generated data
    window.currentSessionId = quizData.session_id;
    window.mcqQuestions = quizData.mcq_questions;
    window.tfQuestions = quizData.tf_questions;
    window.totalQuestions = quizData.total_questions;
    window.currentQuestionIndex = 0;
    window.userAnswers = {};
    
    // Hide upload section and show quiz
    textInputSection.style.display = 'none';
    quizSection.style.display = 'block';
    
    showCurrentQuestion();
}

async function handleFileUploadAndQuizGeneration(file) {
    // Validate file type
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!allowedTypes.includes(file.type)) {
        showFileStatus('error', 'Please select a PDF, DOCX, or TXT file.');
        return;
    }

    // Validate file size (50MB)
    if (file.size > 50 * 1024 * 1024) {
        showFileStatus('error', 'File size must be less than 50MB.');
        return;
    }

    showFileStatus('processing', `Processing ${file.name}...`);

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/upload_file', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to process file');
        }

        // Success - quiz is already generated by the server
        showFileStatus('success', `✅ Quiz generated from ${data.filename} using ${data.analysis_method} analysis!`);
        
        // Store quiz data and start quiz immediately
        window.currentQuizData = data;
        setTimeout(() => {
            startQuizFromData(data);
        }, 1000);

    } catch (err) {
        showFileStatus('error', `❌ Error: ${err.message}`);
    }
}

function showFileStatus(type, message) {
    fileStatus.className = `file-status ${type}`;
    fileStatus.textContent = message;
    fileStatus.style.display = 'block';
    
    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            fileStatus.style.display = 'none';
        }, 5000);
    }
}




function createQuestionElement(questionText, difficulty, options = null, answer = null) {
    const div = document.createElement('div');
    div.className = `question-item ${difficulty.toLowerCase()}`;
    
    let html = `
        <div class="question-text">
            ${questionText}
            <span class="difficulty-badge difficulty-${difficulty.toLowerCase()}">${difficulty}</span>
        </div>
    `;
    
    if (options) {
        html += `<div class="question-options">${options.split('\n').map(opt => `<div>${opt}</div>`).join('')}</div>`;
    }
    
    if (answer) {
        html += `<div class="correct-answer">${answer}</div>`;
    }
    
    div.innerHTML = html;
    return div;
}

function showLoading() {
    loading.style.display = 'block';
    startQuizBtn.disabled = true;
}

function hideLoading() {
    loading.style.display = 'none';
    startQuizBtn.disabled = false;
}

function showError(message) {
    error.textContent = message;
    error.style.display = 'block';
}

function hideError() {
    error.style.display = 'none';
}
