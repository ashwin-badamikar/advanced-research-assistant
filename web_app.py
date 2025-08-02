"""
Conversational Web Interface for Advanced Research Assistant System
"""
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import threading
import json
from datetime import datetime
from workflows.research_workflow import ResearchWorkflow, WorkflowUtils
from openai import OpenAI
from config.settings import settings

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Global instances
workflow = ResearchWorkflow()
current_research = {"status": "idle", "results": None}
conversation_context = {"history": [], "last_research": None}

# Initialize OpenAI client for conversational responses
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@app.route('/')
def index():
    """Main chat interface"""
    return render_template('conversational_chat.html')

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    """Handle conversational chat messages"""
    global conversation_context
    
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'})
        
        # Add user message to context
        conversation_context["history"].append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Determine if this is a research request or conversational message
        if is_research_request(message):
            # Handle as research request
            return start_research_from_chat(message, data)
        else:
            # Handle as conversational message
            return handle_conversational_message(message)
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def is_research_request(message):
    """Determine if message is a research request"""
    research_keywords = [
        'research', 'analyze', 'study', 'investigate', 'explore', 'examine',
        'report on', 'tell me about', 'what are the trends', 'comprehensive analysis',
        'deep dive', 'breakdown', 'overview of', 'insights on'
    ]
    
    message_lower = message.lower()
    
    # Check for explicit research requests
    if any(keyword in message_lower for keyword in research_keywords):
        return True
    
    # Check for question patterns that suggest research
    question_patterns = [
        'what is', 'what are', 'how does', 'how do', 'why is', 'why are',
        'when will', 'where is', 'which are', 'who are'
    ]
    
    if any(pattern in message_lower for pattern in question_patterns) and len(message.split()) > 4:
        return True
    
    return False

def start_research_from_chat(message, data):
    """Start research based on chat message"""
    global current_research
    
    if current_research["status"] == "running":
        return jsonify({
            'success': True, 
            'type': 'message',
            'message': '⏳ I\'m currently working on another research task. Please wait for it to complete, then I\'ll be happy to help with your new request!'
        })
    
    # Extract research parameters or use defaults
    output_format = data.get('format', 'executive_briefing')
    audience = data.get('audience', 'professional')
    depth = data.get('depth', 'detailed')
    
    # Set status to running
    current_research["status"] = "running"
    current_research["results"] = None
    
    # Run research in background thread
    def run_research():
        try:
            results = workflow.execute_research_project(
                research_query=message,
                output_format=output_format,
                target_audience=audience,
                depth_level=depth
            )
            
            current_research["results"] = results
            current_research["status"] = "completed"
            
            # Store research results in conversation context
            conversation_context["last_research"] = {
                "query": message,
                "results": results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            current_research["results"] = {"status": "error", "error": str(e)}
            current_research["status"] = "error"
    
    # Start research in background
    thread = threading.Thread(target=run_research)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'type': 'research_started',
        'message': f'🚀 Starting comprehensive research on: "{message}"',
        'estimated_duration': WorkflowUtils.estimate_duration(depth, output_format)
    })

def handle_conversational_message(message):
    """Handle conversational messages using OpenAI"""
    global conversation_context
    
    try:
        # Build context for the conversation
        system_prompt = """You are an Advanced Research Assistant AI. You have access to recent research results and can engage in intelligent conversations about research topics. 

Key capabilities:
- Answer follow-up questions about research results
- Provide additional insights and explanations  
- Suggest related research areas
- Clarify complex concepts
- Offer strategic recommendations

Be conversational, helpful, and professional. If users ask about specific research results, reference the context provided."""

        # Include recent research context if available
        context_info = ""
        if conversation_context.get("last_research"):
            last_research = conversation_context["last_research"]
            context_info = f"\n\nRecent Research Context:\nQuery: {last_research['query']}\nCompleted: {last_research['timestamp']}"
        
        # Prepare conversation messages for OpenAI
        messages = [
            {"role": "system", "content": system_prompt + context_info}
        ]
        
        # Add recent conversation history (last 6 messages)
        recent_history = conversation_context["history"][-6:]
        for msg in recent_history:
            if msg["role"] in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Get response from OpenAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # Add AI response to context
        conversation_context["history"].append({
            "role": "assistant", 
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        return jsonify({
            'success': True,
            'type': 'message',
            'message': ai_response
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Conversation error: {str(e)}'
        })

@app.route('/api/research', methods=['POST'])
def start_research():
    """Start research via HTTP POST (legacy endpoint)"""
    global current_research
    
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        output_format = data.get('format', 'executive_briefing')
        audience = data.get('audience', 'professional')
        depth = data.get('depth', 'detailed')
        
        if not query:
            return jsonify({'success': False, 'error': 'Query is required'})
        
        if current_research["status"] == "running":
            return jsonify({'success': False, 'error': 'Research already in progress'})
        
        # Validate inputs
        validation = WorkflowUtils.validate_inputs(query, output_format, audience, depth)
        if not validation['valid']:
            return jsonify({'success': False, 'error': ', '.join(validation['errors'])})
        
        return start_research_from_chat(query, data).get_json()
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/status')
def get_research_status():
    """Get current research status"""
    global current_research
    
    response = {
        'status': current_research["status"],
        'system_info': {
            'agents': 3,
            'tools': 6,
            'custom_tools': 2
        }
    }
    
    if current_research["status"] == "completed" and current_research["results"]:
        results = current_research["results"]
        if results.get("status") == "success":
            response['results'] = {
                'project_id': results.get('metadata', {}).get('project_id'),
                'duration': results.get('metadata', {}).get('workflow_duration'),
                'output_preview': results.get('final_output', '')[:1000] + '...',
                'files': get_output_files()
            }
        else:
            response['error'] = results.get('error', 'Unknown error')
    elif current_research["status"] == "error" and current_research["results"]:
        response['error'] = current_research["results"].get('error', 'Unknown error')
    
    return jsonify(response)

@app.route('/api/reset')
def reset_research():
    """Reset research status"""
    global current_research
    current_research = {"status": "idle", "results": None}
    return jsonify({'success': True})

@app.route('/api/conversation/clear')
def clear_conversation():
    """Clear conversation history"""
    global conversation_context
    conversation_context = {"history": [], "last_research": None}
    return jsonify({'success': True})

@app.route('/api/files')
def list_files():
    """List generated files"""
    return jsonify({'files': get_output_files()})

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated files"""
    try:
        return send_from_directory('./outputs', filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

def get_output_files():
    """Get list of output files"""
    try:
        files = []
        if os.path.exists('./outputs'):
            for filename in os.listdir('./outputs'):
                if filename.endswith(('.txt', '.json', '.md')):
                    filepath = os.path.join('./outputs', filename)
                    stat = os.stat(filepath)
                    files.append({
                        'name': filename,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
        return files
    except Exception:
        return []

if __name__ == '__main__':
    # Ensure output directory exists
    os.makedirs('./outputs', exist_ok=True)
    
    print("🚀 Advanced Research Assistant - Conversational Web Interface")
    print("🌐 Starting server at http://localhost:5000")
    print("💬 Features: Conversational chat, research automation, file downloads")
    print("🤖 Capabilities: Follow-up questions, clarifications, additional insights")
    
    app.run(debug=True, host='0.0.0.0', port=5000)