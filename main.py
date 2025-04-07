from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
import json
import requests
from flask_cors import CORS


load_dotenv()


app = Flask(__name__)
CORS(app)


class BaseAgent:
    def __init__(self, name, description):
        self.name = name
        self.description = description

        self.api_key = os.getenv("GROQ_API_KEY")

    def get_response(self, prompt):

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "llama3-8b-8192",
                "messages": [
                    {"role": "system", "content": f"You are {self.name}, {self.description}. Respond in a helpful, concise, and professional manner."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }

            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"Error: {response.status_code} - {response.text}"
        except Exception as e:
            return f"An error occurred: {str(e)}"


class WelcomeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "WelcomeAgent",
            "a welcome specialist who greets visitors and helps them navigate the portfolio website"
        )

    def greet(self, visitor_type=None):
        if visitor_type == "employer":
            return self.get_response("Generate a warm welcome message for an employer visiting a programmer's portfolio website. Suggest they check out the Projects and Career sections.")
        elif visitor_type == "client":
            return self.get_response("Generate a warm welcome message for a potential client visiting a programmer's portfolio website. Suggest they check out the Services section.")
        elif visitor_type == "fellow_programmer":
            return self.get_response("Generate a warm welcome message for a fellow programmer visiting a programmer's portfolio website. Suggest they check out the Projects and Research sections.")
        else:
            return self.get_response("Generate a general welcome message for a visitor to a programmer's portfolio website. Ask if they are an employer, client, or fellow programmer.")

    def suggest_section(self, interest):
        return self.get_response(f"A visitor to my portfolio website has expressed interest in {interest}. Suggest which section(s) of the website they should visit based on this interest.")


class ProjectAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "ProjectAgent",
            "a project specialist who provides detailed information about the programmer's projects"
        )

    def get_project_list(self):
        return self.get_response("Generate a list of 3-5 impressive software development projects that could be in a programmer's portfolio. Include a brief description for each.")

    def get_project_details(self, project_id):
        project_prompts = {
            "project1": "Describe in detail an e-commerce platform project for a programmer's portfolio. Include technologies used, challenges overcome, and key features.",
            "project2": "Describe in detail a task management application project for a programmer's portfolio. Include technologies used, challenges overcome, and key features.",
            "project3": "Describe in detail a data visualization dashboard project for a programmer's portfolio. Include technologies used, challenges overcome, and key features."
        }

        prompt = project_prompts.get(
            project_id, f"Describe a project called {project_id} in detail.")
        return self.get_response(prompt)

    def answer_technical_question(self, project_id, question):
        return self.get_response(f"Answer this technical question about a project: '{question}'. The project is {project_id}.")

class CareerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "CareerAgent",
            "a career specialist who provides information about the programmer's skills and experience"
        )

    def get_skills_summary(self):
        return self.get_response("Generate a comprehensive summary of technical and professional skills for a full-stack developer's portfolio.")

    def get_experience_summary(self):
        return self.get_response("Generate a summary of work experience for a full-stack developer with 5+ years of experience.")

    def assess_job_fit(self, job_description):
        return self.get_response(f"Assess how well a full-stack developer with 5+ years of experience would fit this job description: '{job_description}'. Highlight matching skills and experience.")


class ClientAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "ClientAgent",
            "a client specialist who provides information about services, pricing, and the client engagement process"
        )

    def get_services_overview(self):
        return self.get_response("Generate an overview of services that a freelance full-stack developer might offer to clients.")

    def get_service_details(self, service_type):
        service_prompts = {
            "web_development": "Describe web development services offered by a freelance full-stack developer, including technologies, pricing range, and typical timeline.",
            "mobile_development": "Describe mobile app development services offered by a freelance full-stack developer, including technologies, pricing range, and typical timeline.",
            "consulting": "Describe technical consulting services offered by a freelance full-stack developer, including areas of expertise, hourly rate range, and engagement model."
        }

        prompt = service_prompts.get(
            service_type, f"Describe {service_type} services in detail.")
        return self.get_response(prompt)

    def explain_process(self):
        return self.get_response("Explain the client engagement process for a freelance full-stack developer, from initial consultation to project delivery.")

    def generate_proposal(self, project_description):
        return self.get_response(f"Generate a project proposal for this client request: '{project_description}'. Include estimated timeline, cost range, and approach.")


class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            "ResearchAgent",
            "a research specialist who provides information about technologies, trends, and industry news"
        )

    def search_web(self, query):
        return self.get_response(f"Provide information about '{query}' as if you've just searched the web for the latest information. Include key points and insights.")

    def compare_technologies(self, tech1, tech2):
        return self.get_response(f"Compare {tech1} vs {tech2} in terms of features, performance, use cases, community support, and future prospects.")

    def get_industry_trends(self):
        return self.get_response("Describe current trends in software development and technology that are important for developers to be aware of.")


welcome_agent = WelcomeAgent()
project_agent = ProjectAgent()
career_agent = CareerAgent()
client_agent = ClientAgent()
research_agent = ResearchAgent()


@app.route('/static/images/default_avatar.png')
@app.route('/static/images/default_project.jpg')
def block_default_images():

    response = app.make_response(
        b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;')
    response.headers['Content-Type'] = 'image/gif'

    response.headers['Cache-Control'] = 'public, max-age=31536000'
    response.headers['Expires'] = 'Thu, 31 Dec 2037 23:59:59 GMT'
    return response


@app.route('/api/welcome', methods=['POST'])
def welcome_agent_endpoint():
    data = request.json
    message = data.get('message', '')

    visitor_type = None
    if 'employer' in message.lower():
        visitor_type = 'employer'
    elif 'client' in message.lower():
        visitor_type = 'client'
    elif 'programmer' in message.lower() or 'developer' in message.lower():
        visitor_type = 'fellow_programmer'

    if 'interest' in message.lower() or 'looking for' in message.lower():

        interest = message.replace('interest', '').replace(
            'looking for', '').strip()
        response = welcome_agent.suggest_section(interest)
    else:
        response = welcome_agent.greet(visitor_type)

    return jsonify({'response': response})

@app.route('/api/project', methods=['POST'])
def project_agent_endpoint():
    data = request.json
    message = data.get('message', '')

    project_id = None
    if 'e-commerce' in message.lower() or 'ecommerce' in message.lower():
        project_id = 'project1'
    elif 'task' in message.lower() or 'management' in message.lower():
        project_id = 'project2'
    elif 'data' in message.lower() or 'visualization' in message.lower() or 'dashboard' in message.lower():
        project_id = 'project3'

    if project_id and ('tell me more' in message.lower() or 'details' in message.lower()):
        response = project_agent.get_project_details(project_id)
    elif 'list' in message.lower() or 'all projects' in message.lower():
        response = project_agent.get_project_list()
    elif project_id:

        response = project_agent.answer_technical_question(project_id, message)
    else:

        response = project_agent.get_response(
            f"The user asked: '{message}'. Respond as if you are a project specialist for a portfolio website. "
            "If they're asking about a specific project, suggest they mention one of the projects: "
            "E-commerce Platform, Task Management App, or Data Visualization Dashboard."
        )

    return jsonify({'response': response})


@app.route('/api/career', methods=['POST'])
def career_agent_endpoint():
    data = request.json
    message = data.get('message', '')

    if 'skills' in message.lower():
        response = career_agent.get_skills_summary()
    elif 'experience' in message.lower() or 'work history' in message.lower():
        response = career_agent.get_experience_summary()
    elif 'job' in message.lower() or 'position' in message.lower() or 'role' in message.lower():

        response = career_agent.assess_job_fit(message)
    else:

        response = career_agent.get_response(
            f"The user asked: '{message}'. Respond as if you are a career specialist for a portfolio website. "
            "Suggest they ask about skills, experience, or job fit assessment."
        )

    return jsonify({'response': response})


@app.route('/api/client', methods=['POST'])
def client_agent_endpoint():
    data = request.json
    message = data.get('message', '')

    if 'services' in message.lower() or 'offerings' in message.lower():
        response = client_agent.get_services_overview()
    elif 'web' in message.lower() and 'development' in message.lower():
        response = client_agent.get_service_details('web_development')
    elif 'mobile' in message.lower() and 'development' in message.lower():
        response = client_agent.get_service_details('mobile_development')
    elif 'consulting' in message.lower() or 'technical consulting' in message.lower():
        response = client_agent.get_service_details('consulting')
    elif 'process' in message.lower() or 'how does it work' in message.lower():
        response = client_agent.explain_process()
    elif 'proposal' in message.lower() or 'quote' in message.lower() or 'estimate' in message.lower():

        response = client_agent.generate_proposal(message)
    else:

        response = client_agent.get_response(
            f"The user asked: '{message}'. Respond as if you are a client specialist for a portfolio website. "
            "Suggest they ask about services, the client engagement process, or request a proposal."
        )

    return jsonify({'response': response})


@app.route('/api/research', methods=['POST'])
def research_agent_endpoint():
    data = request.json
    message = data.get('message', '')

    if 'compare' in message.lower() and ('vs' in message.lower() or 'versus' in message.lower()):

        tech_parts = message.lower().replace('compare', '').replace(
            'vs', ' ').replace('versus', ' ').split()
        tech1 = tech_parts[0] if len(tech_parts) > 0 else ''
        tech2 = tech_parts[-1] if len(tech_parts) > 1 else ''
        response = research_agent.compare_technologies(tech1, tech2)
    elif 'trends' in message.lower() or 'industry' in message.lower():
        response = research_agent.get_industry_trends()
    else:
        response = research_agent.search_web(message)

    return jsonify({'response': response})


if __name__ == '__main__':

    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['TEMPLATES_AUTO_RELOAD'] = True   # Ensure templates reload

    @app.after_request
    def add_header(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    app.run(host='0.0.0.0', port=5001, debug=True,
            use_reloader=False, threaded=True)