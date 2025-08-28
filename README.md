# GPT-Powered AI Quiz Generator

An advanced quiz generation application that uses OpenAI's GPT models to analyze uploaded files and create sophisticated, pedagogically sound quiz questions automatically.

## Features

- **🤖 GPT-Powered Analysis**: Uses OpenAI GPT-3.5-turbo for intelligent content understanding
- **📁 File Upload Support**: PDF, DOCX, and TXT file processing
- **🎯 Multiple Question Types**:
  - Multiple Choice Questions (MCQ) with 4 plausible options
  - True/False questions with strategic distractors
  - Open-ended questions for critical thinking
- **📊 Cognitive Level Assessment**: Easy (recall), Medium (comprehension), Hard (analysis)
- **🌐 Modern Web Interface**: Drag-and-drop file upload with real-time feedback
- **⚡ Instant Quiz Generation**: Automatic quiz creation upon file upload

## Prerequisites

- **OpenAI API Key**: Required for GPT analysis
- **Python 3.8+**: For running the application
- **Modern Web Browser**: For the interface

## Installation

1. **Clone or download** this repository

2. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up OpenAI API Key**:
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your_openai_api_key_here"

# Linux/Mac
export OPENAI_API_KEY="your_openai_api_key_here"
```

4. **Run the application**:
```bash
python app.py
```

5. **Open your browser** and navigate to `http://localhost:5000`

## Usage

### Web Interface
1. **Upload a file**: Drag and drop or click to select PDF, DOCX, or TXT files
2. **Automatic processing**: GPT analyzes content and generates quiz instantly
3. **Take the quiz**: Interactive quiz starts automatically after generation
4. **View results**: Get detailed feedback and scoring

### Command Line
```python
from quiz_generator import QuizGenerator
import os

# Set API key
api_key = os.getenv('OPENAI_API_KEY')

# Initialize generator (requires API key)
generator = QuizGenerator(api_key=api_key)

# Read file content
text = generator.read_file('path/to/your/file.pdf')

# Generate GPT-powered quiz
quiz_data = generator.generate_complete_quiz_with_gpt(text)

# Get formatted output
formatted_quiz = generator.format_quiz_output(quiz_data)
print(formatted_quiz)
```

## Question Types Generated

### Multiple Choice Questions (MCQ)
- 4 options per question (A, B, C, D)
- One correct answer
- Plausible incorrect options
- Based on key facts and concepts

### True/False Questions
- Clear statements derived from the text
- Mix of true and false statements
- Direct factual assertions

### Open-Ended Questions
- Encourage explanation and analysis
- Test deeper understanding
- Promote critical thinking

## Cognitive Assessment Levels

- **Easy**: Direct recall of explicitly stated information
- **Medium**: Understanding relationships and making connections
- **Hard**: Analysis, synthesis, or application of concepts

The GPT model intelligently assigns difficulty based on cognitive complexity rather than just concept frequency.

## Example Output

```
MULTIPLE CHOICE QUESTIONS
1. Who designed the Eiffel Tower? (Easy)
   A) Thomas Edison
   B) Gustave Eiffel
   C) Leonardo da Vinci
   D) Louis Pasteur
   Correct Answer: B) Gustave Eiffel

TRUE/FALSE QUESTIONS
1. The Eiffel Tower was completed in 1889. (Easy)
   Correct Answer: True

OPEN-ENDED QUESTIONS
1. Explain the significance of Gustave Eiffel based on the provided text. (Easy)
```

## Technical Details

### GPT Integration

- **Model**: OpenAI GPT-3.5-turbo
- **Advanced Prompting**: Expert educational assessment designer persona
- **Temperature**: 0.3 for consistent, focused responses
- **Token Limit**: 3000 for comprehensive quiz generation

### Key Components

- **QuizGenerator**: GPT-powered quiz generation with advanced prompt engineering
- **File Processing**: PDF, DOCX, and TXT text extraction
- **Educational Standards**: Pedagogically sound question creation
- **Quality Assurance**: Plausible distractors and misconception testing

### Supported File Types

- **PDF**: Academic papers, textbooks, reports
- **DOCX**: Word documents, essays, articles
- **TXT**: Plain text files, transcripts
- **Content**: Educational materials, research papers, historical documents, any informational content

## Customization

The application can be customized by modifying:

- **GPT Prompts**: Enhance the educational assessment prompts
- **Question Quantities**: Adjust MCQ (5-8), True/False (3-5), Open-ended (2-3)
- **Cognitive Levels**: Modify difficulty assignment criteria
- **File Processing**: Add support for additional file formats

## Requirements

- **Python 3.8+**
- **OpenAI API Key** (required)
- **Dependencies**:
  - Flask 2.3.3
  - openai 1.3.7
  - PyPDF2 3.0.1
  - python-docx 0.8.11
- **Modern web browser**

## File Structure

```
quiz_generator/
├── quiz_generator.py    # GPT-powered quiz generation
├── app.py              # Flask web application
├── templates/
│   └── index.html      # Modern web interface
├── static/
│   ├── css/
│   │   └── style.css   # Styling
│   └── js/
│       └── app.js      # Frontend logic
├── uploads/            # Temporary file storage
├── requirements.txt    # Python dependencies
├── .env.example       # API key configuration template
└── README.md          # This file
```

## API Key Setup

1. **Get OpenAI API Key**: Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Copy `.env.example` to `.env`**:
```bash
cp .env.example .env
```
3. **Add your API key** to `.env`:
```
OPENAI_API_KEY=your_actual_api_key_here
```

## Contributing

Enhance the application by:
- **Improving GPT prompts** for better question quality
- **Adding new file formats** (PPTX, RTF, etc.)
- **Enhancing the web interface** with new features
- **Adding export functionality** (PDF, Word, etc.)
- **Supporting multiple languages** for international use

## License

This project is open source. Feel free to use and modify for educational purposes.

---

**Note**: This application requires an OpenAI API key and will incur API usage costs. Please monitor your OpenAI usage dashboard.
