import json
from typing import List, Dict, Any
from dataclasses import dataclass
from enum import Enum
import os

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from docx import Document
except ImportError:
    Document = None

import openai

class Difficulty(Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

@dataclass
class MCQQuestion:
    question: str
    options: List[str]
    correct_answer: str
    difficulty: Difficulty

@dataclass
class TrueFalseQuestion:
    statement: str
    correct_answer: bool
    difficulty: Difficulty

@dataclass
class OpenEndedQuestion:
    question: str
    difficulty: Difficulty

class QuizGenerator:
    def __init__(self, api_key: str = None):
        """Initialize the QuizGenerator with GPT analysis only."""
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        try:
            self.client = openai.OpenAI(api_key=api_key)
        except Exception as e:
            raise Exception(f"Error initializing OpenAI client: {e}")

    def read_pdf_file(self, file_path: str) -> str:
        """Extract text from PDF file."""
        if not PyPDF2:
            raise Exception("PyPDF2 library not installed")
        
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF file: {str(e)}")
    
    def read_docx_file(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        if not Document:
            raise Exception("python-docx library not installed")
        
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading DOCX file: {str(e)}")
    
    def read_file(self, file_path: str) -> str:
        """Read and extract text from various file formats."""
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            return self.read_pdf_file(file_path)
        elif file_extension == '.docx':
            return self.read_docx_file(file_path)
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        else:
            raise Exception(f"Unsupported file format: {file_extension}")

    def generate_complete_quiz_with_gpt(self, text: str) -> Dict[str, Any]:
        """Generate a complete quiz using GPT analysis."""
        try:
            prompt = f"""
            You are an expert educational assessment designer. Analyze the following text and create a comprehensive, high-quality quiz that tests deep understanding of the content.

            TEXT TO ANALYZE:
            {text[:4000]}

            INSTRUCTIONS:
            Create a quiz that demonstrates mastery of the material through varied question types and cognitive levels.

            MULTIPLE CHOICE QUESTIONS (5-8 questions):
            - Focus on key facts, concepts, relationships, and applications
            - Create plausible distractors that test common misconceptions
            - Use clear, unambiguous language
            - Avoid "all of the above" or "none of the above" options
            - Test different cognitive levels: recall, comprehension, application, analysis

            TRUE/FALSE QUESTIONS (3-5 questions):
            - Focus on specific factual claims from the text
            - Avoid absolute terms unless they appear in the source
            - Test important details and relationships
            - Make false statements plausible but clearly incorrect

            OPEN-ENDED QUESTIONS (2-3 questions):
            - Require synthesis, analysis, or evaluation
            - Ask for explanations, comparisons, or applications
            - Encourage critical thinking about the content
            - Should not have simple yes/no answers

            DIFFICULTY LEVELS:
            - Easy: Direct recall of explicitly stated information
            - Medium: Understanding relationships and making connections
            - Hard: Analysis, synthesis, or application of concepts

            QUALITY STANDARDS:
            - Questions must be answerable from the provided text
            - Avoid trivial details unless they're central to understanding
            - Ensure cultural neutrality and accessibility
            - Use precise, professional language
            - Test the most educationally significant content

            Respond ONLY with valid JSON in this exact format:
            {{
                "mcq_questions": [
                    {{
                        "question": "Clear, specific question text?",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": "A) Option A",
                        "difficulty": "Easy"
                    }}
                ],
                "true_false_questions": [
                    {{
                        "statement": "Specific, testable statement",
                        "correct_answer": true,
                        "difficulty": "Medium"
                    }}
                ],
                "open_ended_questions": [
                    {{
                        "question": "Thought-provoking analytical question?",
                        "difficulty": "Hard"
                    }}
                ],
                "key_concepts": ["concept1", "concept2", "concept3", "concept4", "concept5"]
            }}
            """
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educational assessment designer with 20+ years of experience creating high-quality, pedagogically sound quizzes. You excel at identifying the most important learning objectives and creating questions that accurately assess student understanding at multiple cognitive levels."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=3000,
                temperature=0.3
            )
            
            # Parse the JSON response with error handling
            response_content = response.choices[0].message.content.strip()
            
            # Clean up response if it contains markdown code blocks
            if response_content.startswith('```json'):
                response_content = response_content[7:]
            if response_content.endswith('```'):
                response_content = response_content[:-3]
            
            quiz_data = json.loads(response_content)
            
            # Convert to our dataclass format
            mcq_questions = []
            for mcq in quiz_data.get('mcq_questions', []):
                difficulty = Difficulty(mcq.get('difficulty', 'Medium'))
                mcq_questions.append(MCQQuestion(
                    question=mcq['question'],
                    options=mcq['options'],
                    correct_answer=mcq['correct_answer'],
                    difficulty=difficulty
                ))
            
            tf_questions = []
            for tf in quiz_data.get('true_false_questions', []):
                difficulty = Difficulty(tf.get('difficulty', 'Medium'))
                tf_questions.append(TrueFalseQuestion(
                    statement=tf['statement'],
                    correct_answer=tf['correct_answer'],
                    difficulty=difficulty
                ))
            
            open_questions = []
            for oq in quiz_data.get('open_ended_questions', []):
                difficulty = Difficulty(oq.get('difficulty', 'Hard'))
                open_questions.append(OpenEndedQuestion(
                    question=oq['question'],
                    difficulty=difficulty
                ))
            
            return {
                'mcq_questions': mcq_questions,
                'true_false_questions': tf_questions,
                'open_ended_questions': open_questions,
                'key_concepts': quiz_data.get('key_concepts', [])
            }
            
        except Exception as e:
            raise Exception(f"GPT quiz generation failed: {e}")

    def format_quiz_output(self, quiz_data: Dict) -> str:
        """Format the quiz in a readable format."""
        output = []
        output.append("=" * 60)
        output.append("AI-GENERATED QUIZ")
        output.append("=" * 60)
        output.append(f"\nKey Concepts: {', '.join(quiz_data['key_concepts'][:5])}")
        
        # MCQ Questions
        output.append("\n" + "=" * 40)
        output.append("MULTIPLE CHOICE QUESTIONS")
        output.append("=" * 40)
        
        for i, mcq in enumerate(quiz_data['mcq_questions'], 1):
            output.append(f"\n{i}. {mcq.question} ({mcq.difficulty.value})")
            for j, option in enumerate(mcq.options):
                output.append(f"   {chr(65 + j)}) {option}")
            output.append(f"   Correct Answer: {mcq.correct_answer}")
        
        # True/False Questions
        output.append("\n\n" + "=" * 40)
        output.append("TRUE/FALSE QUESTIONS")
        output.append("=" * 40)
        
        for i, tf in enumerate(quiz_data['true_false_questions'], 1):
            output.append(f"\n{i}. {tf.statement} ({tf.difficulty.value})")
            output.append(f"   Correct Answer: {tf.correct_answer}")
        
        # Open-ended Questions
        output.append("\n\n" + "=" * 40)
        output.append("OPEN-ENDED QUESTIONS")
        output.append("=" * 40)
        
        for i, open_q in enumerate(quiz_data['open_ended_questions'], 1):
            output.append(f"\n{i}. {open_q.question} ({open_q.difficulty.value})")
        
        return "\n".join(output)

# Module loaded successfully
if __name__ == "__main__":
    print("GPT-only QuizGenerator module loaded successfully.")
    print("Requires OpenAI API key to function.")
