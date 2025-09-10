from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from quiz_generator import QuizGenerator
import json
import uuid
import os

app = Flask(__name__)
app.secret_key = 'quiz_generator_secret_key_2024'

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Store quiz sessions in memory (in production, use a database)
quiz_sessions = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Get API key from environment variable
            api_key = os.getenv('OPENAI_API_KEY')
            
            if not api_key:
                # Fallback mode for testing without API key
                # Clean up uploaded file
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                # Create a simple demo quiz for testing
                session_id = str(uuid.uuid4())
                demo_mcq = [{
                    'id': 'demo_mcq_1',
                    'question': 'What is the main topic of this document?',
                    'options': ['Topic A', 'Topic B', 'Topic C', 'Topic D'],
                    'correct_answer': 0,
                    'difficulty': 'Easy',
                    'type': 'mcq'
                }]
                
                demo_tf = [{
                    'id': 'demo_tf_1',
                    'statement': 'This is a test document for demonstration purposes.',
                    'correct_answer': True,
                    'difficulty': 'Easy',
                    'type': 'true_false'
                }]
                
                quiz_sessions[session_id] = {
                    'text': 'Demo text for testing purposes',
                    'mcq_questions': demo_mcq,
                    'tf_questions': demo_tf,
                    'user_answers': {},
                    'score': 0,
                    'completed': False
                }
                
                return jsonify({
                    'session_id': session_id,
                    'mcq_questions': demo_mcq,
                    'tf_questions': demo_tf,
                    'total_questions': len(demo_mcq) + len(demo_tf),
                    'filename': filename,
                    'analysis_method': 'Demo Mode (No API Key)',
                    'warning': 'Running in demo mode. Set OPENAI_API_KEY for full functionality.'
                })
            
            # Initialize quiz generator with GPT only
            try:
                generator = QuizGenerator(api_key=api_key)
            except Exception as e:
                # Clean up uploaded file
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'error': f'Error initializing OpenAI client: {str(e)}'}), 400
            
            try:
                # Extract text from file
                text = generator.read_file(filepath)
                
                # Generate quiz using GPT analysis
                quiz_data = generator.generate_complete_quiz_with_gpt(text)
                
                # Create a unique session ID for the quiz
                session_id = str(uuid.uuid4())
                
                # Prepare quiz questions for interactive session
                mcq_questions = []
                for i, mcq in enumerate(quiz_data['mcq_questions']):
                    correct_option_text = mcq.correct_answer.split(') ', 1)[1]
                    correct_index = mcq.options.index(correct_option_text)
                    mcq_questions.append({
                        'id': f'mcq_{i}',
                        'question': mcq.question,
                        'options': mcq.options,
                        'correct_answer': correct_index,
                        'difficulty': mcq.difficulty.value,
                        'type': 'mcq'
                    })
                
                tf_questions = []
                for i, tf in enumerate(quiz_data['true_false_questions']):
                    tf_questions.append({
                        'id': f'tf_{i}',
                        'statement': tf.statement,
                        'correct_answer': tf.correct_answer,
                        'difficulty': tf.difficulty.value,
                        'type': 'true_false'
                    })
                
                # Store quiz session
                quiz_sessions[session_id] = {
                    'text': text,
                    'mcq_questions': mcq_questions,
                    'tf_questions': tf_questions,
                    'user_answers': {},
                    'score': 0,
                    'completed': False
                }
                
                # Clean up uploaded file
                os.remove(filepath)
                
                return jsonify({
                    'session_id': session_id,
                    'mcq_questions': mcq_questions,
                    'tf_questions': tf_questions,
                    'total_questions': len(mcq_questions) + len(tf_questions),
                    'filename': filename,
                    'analysis_method': 'GPT'
                })
                
            except Exception as e:
                # Clean up uploaded file on error
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'error': f'Error processing file: {str(e)}'}), 400
        else:
            return jsonify({'error': 'File type not supported. Please upload PDF, DOCX, or TXT files.'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/start_quiz', methods=['POST'])
def start_quiz():
    return jsonify({'error': 'Quiz generation is now handled during file upload. Please upload a file to generate a quiz.'}), 400

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        question_id = data.get('question_id')
        user_answer = data.get('answer')
        
        if session_id not in quiz_sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        session_data = quiz_sessions[session_id]
        
        # Find the question and check answer
        is_correct = False
        correct_answer = None
        
        # Check MCQ questions
        for mcq in session_data['mcq_questions']:
            if mcq['id'] == question_id:
                correct_answer = mcq['correct_answer']
                is_correct = int(user_answer) == correct_answer
                break
        
        # Check True/False questions
        for tf in session_data['tf_questions']:
            if tf['id'] == question_id:
                correct_answer = tf['correct_answer']
                is_correct = (user_answer.lower() == 'true') == correct_answer
                break
        
        # Store user answer
        session_data['user_answers'][question_id] = {
            'answer': user_answer,
            'is_correct': is_correct
        }
        
        return jsonify({
            'is_correct': is_correct,
            'correct_answer': correct_answer
        })
        
    except Exception as e:
        return jsonify({'error': f'Error submitting answer: {str(e)}'}), 500

@app.route('/get_results', methods=['POST'])
def get_results():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if session_id not in quiz_sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        session_data = quiz_sessions[session_id]
        
        # Calculate score
        total_questions = len(session_data['mcq_questions']) + len(session_data['tf_questions'])
        correct_answers = sum(1 for answer in session_data['user_answers'].values() if answer['is_correct'])
        score_percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        session_data['score'] = score_percentage
        session_data['completed'] = True
        
        return jsonify({
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'score_percentage': round(score_percentage, 1),
            'user_answers': session_data['user_answers']
        })
        
    except Exception as e:
        return jsonify({'error': f'Error getting results: {str(e)}'}), 500

@app.route('/generate_quiz', methods=['POST'])
def generate_quiz():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({'error': 'Please provide text to analyze'}), 400
        
        generator = QuizGenerator()
        quiz_data = generator.generate_complete_quiz(text)
        
        # Convert dataclass objects to dictionaries for JSON serialization
        serialized_quiz = {
            'key_concepts': quiz_data['key_concepts'],
            'mcq_questions': [
                {
                    'question': mcq.question,
                    'options': mcq.options,
                    'correct_answer': mcq.correct_answer,
                    'difficulty': mcq.difficulty.value
                } for mcq in quiz_data['mcq_questions']
            ],
            'true_false_questions': [
                {
                    'statement': tf.statement,
                    'correct_answer': tf.correct_answer,
                    'difficulty': tf.difficulty.value
                } for tf in quiz_data['true_false_questions']
            ],
            'open_ended_questions': [
                {
                    'question': oe.question,
                    'difficulty': oe.difficulty.value
                } for oe in quiz_data['open_ended_questions']
            ],
            'total_questions': quiz_data['total_questions']
        }
        
        return jsonify(serialized_quiz)
        
    except Exception as e:
        return jsonify({'error': f'Error generating quiz: {str(e)}'}), 500

@app.route('/format_quiz', methods=['POST'])
def format_quiz():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text.strip():
            return jsonify({'error': 'Please provide text to analyze'}), 400
        
        generator = QuizGenerator()
        quiz_data = generator.generate_complete_quiz(text)
        formatted_output = generator.format_quiz_output(quiz_data)
        
        return jsonify({'formatted_quiz': formatted_output})
        
    except Exception as e:
        return jsonify({'error': f'Error formatting quiz: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
