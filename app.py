from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# In-memory data stores
calendar_events = []
reminders = []
tasks = []

# ---------- Agent framework ----------
class TaskObj:
    def __init__(self, name, context, requirements=None):
        self.name = name
        self.context = context
        self.requirements = requirements or []

class Agent:
    def __init__(self, name):
        self.name = name
    def handle_task(self, task):
        raise NotImplementedError()

class WorkflowAnalysisAgent(Agent):
    def handle_task(self, task):
        suggestion = f"Time-blocking & batching suggested for: {task.context['description']}"
        task.requirements.append(suggestion)
        return suggestion

class MeetingSchedulerAgent(Agent):
    def handle_task(self, task):
        meeting_time = "Thu, 2:00 PM - 2:30 PM"
        return f"Meeting scheduled at {meeting_time} for participants: {', '.join(task.context.get('participants', []))}"

class EmailNotificationAgent(Agent):
    def handle_task(self, task):
        recipients = task.context.get('participants', [])
        meeting_time = "Thu, 2:00 PM"
        return f"Email invites sent to {', '.join(recipients)} for meeting at {meeting_time}"

class KnowledgeResourceAgent(Agent):
    def handle_task(self, task):
        docs = ["Workflow Guide.pdf", "Productivity Tips.docx"]
        return f"Recommended docs: {', '.join(docs)}"

class ProductivityAnalyticsAgent(Agent):
    def handle_task(self, task):
        stats = "Weekly: 5 meetings, 20 tasks, avg. focus 90 mins"
        return stats

class TimeWasterAgent(Agent):
    def handle_task(self, task):
        wasted = "Detected 1.5 hours wasted daily on redundant emails"
        improvement = "Suggest template automation and meeting pruning"
        return wasted + ". " + improvement

class AutomationAgent(Agent):
    def handle_task(self, task):
        auto_tasks = ["Daily status email", "Weekly report upload"]
        return f"Automated: {', '.join(auto_tasks)}"

agent_classes = {
    "WorkflowAnalysisAgent": WorkflowAnalysisAgent,
    "MeetingSchedulerAgent": MeetingSchedulerAgent,
    "EmailNotificationAgent": EmailNotificationAgent,
    "KnowledgeResourceAgent": KnowledgeResourceAgent,
    "ProductivityAnalyticsAgent": ProductivityAnalyticsAgent,
    "TimeWasterAgent": TimeWasterAgent,
    "AutomationAgent": AutomationAgent,
}

# ---------- Helpers ----------
def iso(s):
    return None if s is None else str(s)

def validate_event(payload):
    required = ["title", "start", "end"]
    for k in required:
        if k not in payload or not payload[k]:
            return f"Missing field: {k}"
    return None

# ---------- Pages ----------
@app.route("/")
def index():
    return render_template(
        "index.html",
        calendar_events=calendar_events,
        reminders=reminders,
        tasks=tasks,
        agents=list(agent_classes.keys())
    )

# ---------- Calendar API ----------
@app.route("/api/calendar", methods=["GET", "POST", "PUT", "DELETE"])
def calendar_api():
    if request.method == "GET":
        start_q = request.args.get("start")
        end_q = request.args.get("end")
        if start_q and end_q:
            try:
                filtered = [e for e in calendar_events if e.get("start") <= end_q and e.get("end") >= start_q]
                return jsonify(filtered)
            except Exception:
                return jsonify(calendar_events)
        return jsonify(calendar_events)

    data = request.json or {}

    if request.method == "POST":
        err = validate_event(data)
        if err:
            return jsonify({"error": err}), 400
        event = {
            "id": len(calendar_events) + 1,
            "title": str(data["title"]),
            "start": iso(data["start"]),
            "end": iso(data["end"]),
            "participants": list(data.get("participants", [])),
        }
        calendar_events.append(event)
        return jsonify(event), 201

    if request.method == "PUT":
        if "id" not in data:
            return jsonify({"error": "Missing id"}), 400
        for e in calendar_events:
            if e["id"] == data["id"]:
                for k in ["title", "start", "end", "participants"]:
                    if k in data:
                        e[k] = data[k]
                return jsonify(e)
        return jsonify({"error": "Not found"}), 404

    if request.method == "DELETE":
        event_id = data.get("id")
        if not event_id:
            return jsonify({"error": "Missing id"}), 400
        for e in calendar_events:
            if e["id"] == event_id:
                calendar_events.remove(e)
                return jsonify({"status": "deleted"})
        return jsonify({"error": "Not found"}), 404

# ---------- Reminders API ----------
@app.route("/api/reminders", methods=["GET", "POST", "PUT", "DELETE"])
def reminders_api():
    if request.method == "GET":
        return jsonify(reminders)

    data = request.json or {}

    if request.method == "POST":
        reminder = {
            "id": len(reminders) + 1,
            "event_id": data.get("event_id"),
            "reminder_time": iso(data.get("reminder_time")),
            "message": str(data.get("message", "")),
        }
        reminders.append(reminder)
        return jsonify(reminder), 201

    if request.method == "PUT":
        if "id" not in data:
            return jsonify({"error": "Missing id"}), 400
        for r in reminders:
            if r["id"] == data["id"]:
                for k in ["event_id", "reminder_time", "message"]:
                    if k in data:
                        r[k] = data[k]
                return jsonify(r)
        return jsonify({"error": "Not found"}), 404

    if request.method == "DELETE":
        rid = data.get("id")
        if not rid:
            return jsonify({"error": "Missing id"}), 400
        for r in reminders:
            if r["id"] == rid:
                reminders.remove(r)
                return jsonify({"status": "deleted"})
        return jsonify({"error": "Not found"}), 404

# ---------- Tasks API ----------
@app.route("/api/tasks", methods=["GET", "POST", "PUT", "DELETE"])
def tasks_api():
    if request.method == "GET":
        return jsonify(tasks)

    data = request.json or {}

    if request.method == "POST":
        task = {
            "id": len(tasks) + 1,
            "content": str(data.get("content", "")),
            "time": str(data.get("time", "")),  # minutes as string to match existing structure
            "efficiency": int(data.get("efficiency", 0)),
        }
        tasks.append(task)
        return jsonify(task), 201

    if request.method == "PUT":
        if "id" not in data:
            return jsonify({"error": "Missing id"}), 400
        for t in tasks:
            if t["id"] == data["id"]:
                for k in ["content", "time", "efficiency"]:
                    if k in data:
                        t[k] = data[k]
                return jsonify(t)
        return jsonify({"error": "Not found"}), 404

    if request.method == "DELETE":
        tid = data.get("id")
        if not tid:
            return jsonify({"error": "Missing id"}), 400
        for t in tasks:
            if t["id"] == tid:
                tasks.remove(t)
                return jsonify({"status": "deleted"})
        return jsonify({"error": "Not found"}), 404

# ---------- Agent execution ----------
@app.route("/api/execute_task_filtered", methods=["POST"])
def execute_task_filtered():
    data = request.json or {}
    description = data.get("description", "")
    participants = data.get("participants", [])
    selected_agents = set(data.get("agents", []))

    base_task = TaskObj("WorkflowTask", {"description": description, "participants": participants})
    results = {}
    for agent_key in selected_agents:
        agent_class = agent_classes.get(agent_key)
        if agent_class:
            agent = agent_class(agent_key)
            results[agent_key] = agent.handle_task(base_task)
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)