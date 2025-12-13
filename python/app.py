# Explanation: Main Flask application with routes and features.
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from config import Config
from python.models import db, User, CommunityReport, Resource, EmergencyPlan, SafetyCheck, Article
from python.forms import RegisterForm, LoginForm, ReportForm, ResourceForm, PlanForm, SafetyForm
from python.utils import login_required, admin_required

app = Flask(__name__)
app.config.from_object(Config)

# Explanation: Initialize extensions.
db.init_app(app)
migrate = Migrate(app, db)  # optional migration support
csrf = CSRFProtect(app)

# --------------------------------
# Index & Home
# --------------------------------
@app.route("/")
def index():
    # Explanation: Landing page showing highlights and public resources/articles.
    latest_articles = Article.query.order_by(Article.published_at.desc()).limit(3).all()
    latest_resources = Resource.query.order_by(Resource.updated_at.desc()).limit(5).all()
    return render_template("index.html", articles=latest_articles, resources=latest_resources)

@app.route("/home")
@login_required
def home():
    # Explanation: User dashboard showing recent reports, safety status, and plan snippet.
    user = User.query.get(session["user_id"])
    reports = CommunityReport.query.filter_by(user_id=user.id).order_by(CommunityReport.created_at.desc()).limit(5).all()
    safety = SafetyCheck.query.filter_by(user_id=user.id).order_by(SafetyCheck.created_at.desc()).first()
    plan = EmergencyPlan.query.filter_by(user_id=user.id).order_by(EmergencyPlan.created_at.desc()).first()
    return render_template("home.html", user=user, reports=reports, safety=safety, plan=plan)

# --------------------------------
# Authentication
# --------------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    # Explanation: Authenticate user and set session.
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and user.check_password(form.password.data):
            session["user_id"] = user.id
            session["role"] = user.role
            flash("Logged in successfully.")
            return redirect(url_for("home"))
        flash("Invalid credentials.")
    return render_template("login.html", form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    # Explanation: Create a new user securely.
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower().strip()).first():
            flash("Email already registered.")
            return redirect(url_for("register"))
        user = User(
            email=form.email.data.lower().strip(),
            full_name=form.full_name.data.strip(),
            phone=form.phone.data.strip() if form.phone.data else None,
            address=form.address.data.strip() if form.address.data else None,
            role="user",
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    # Explanation: Placeholder for password reset (email token flow recommended in prod).
    if request.method == "POST":
        flash("If this email exists, a reset link will be sent.")
        return redirect(url_for("login"))
    return render_template("forgot_password.html")

@app.route("/logout")
def logout():
    # Explanation: Clear user session.
    session.clear()
    flash("Logged out.")
    return redirect(url_for("index"))

# --------------------------------
# Admin authentication & dashboard
# --------------------------------
@app.route("/adminlogin", methods=["GET", "POST"])
def adminlogin():
    form = LoginForm()
    # Explanation: Admin login using existing User accounts with 'admin' role.
    if form.validate_on_submit():
        admin = User.query.filter_by(email=form.email.data.lower().strip(), role="admin").first()
        if admin and admin.check_password(form.password.data):
            session["user_id"] = admin.id
            session["role"] = "admin"
            flash("Admin login successful.")
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin credentials.")
    return render_template("adminlogin.html", form=form)

@app.route("/admin_dashboard")
@admin_required
def admin_dashboard():
    recent_reports = CommunityReport.query.order_by(CommunityReport.created_at.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_safety = SafetyCheck.query.order_by(SafetyCheck.created_at.desc()).limit(10).all()
    resources = Resource.query.order_by(Resource.updated_at.desc()).limit(10).all()
    form = ResourceForm()   # <-- add this
    return render_template("admin_dashboard.html",
                           recent_reports=recent_reports,
                           recent_users=recent_users,
                           recent_safety=recent_safety,
                           resources=resources,
                           form=form)   # <-- pass it

# --------------------------------
# Educational Hub
# --------------------------------
@app.route("/educationalhub")
def educationalhub():
    # Explanation: List of educational articles, guides, and contingency plans.
    articles = Article.query.order_by(Article.published_at.desc()).all()
    return render_template("educationalhub.html", articles=articles)

# --------------------------------
# Community Reporting
# --------------------------------
@app.route("/communityreport", methods=["GET", "POST"])
@login_required
def communityreport():
    form = ReportForm()
    # Explanation: Allow users to submit disaster reports; admin can verify later.
    if form.validate_on_submit():
        report = CommunityReport(
            user_id=session["user_id"],
            disaster_type=form.disaster_type.data,
            location=form.location.data.strip(),
            description=form.description.data.strip(),
            status="pending"
        )
        db.session.add(report)
        db.session.commit()
        flash("Report submitted.")
        return redirect(url_for("communityreport"))
    # Explanation: Show user's reports.
    my_reports = CommunityReport.query.filter_by(user_id=session["user_id"]).order_by(CommunityReport.created_at.desc()).all()
    return render_template("communityreport.html", form=form, my_reports=my_reports)

# Explanation: Admin actions on reports (verify/resolve).
@app.route("/admin/reports/<int:report_id>/verify", methods=["POST"])
@admin_required
def verify_report(report_id):
    report = CommunityReport.query.get_or_404(report_id)
    report.status = "verified"
    report.verified_by_admin_id = session["user_id"]
    db.session.commit()
    flash("Report verified.")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/reports/<int:report_id>/resolve", methods=["POST"])
@admin_required
def resolve_report(report_id):
    report = CommunityReport.query.get_or_404(report_id)
    report.status = "resolved"
    db.session.commit()
    flash("Report marked as resolved.")
    return redirect(url_for("admin_dashboard"))

# --------------------------------
# Resource Directory
# --------------------------------
@app.route("/resourcedirectory", methods=["GET"])
def resourcedirectory():
    # Explanation: Public view of resources.
    resources = Resource.query.order_by(Resource.category.asc()).all()
    return render_template("resourcedirectory.html", resources=resources)

@app.route("/admin/resources", methods=["GET", "POST"])
@admin_required
def admin_resources():
    form = ResourceForm()
    # Explanation: Admin can add/update resource entries.
    if form.validate_on_submit():
        resource = Resource(
            name=form.name.data.strip(),
            category=form.category.data,
            address=form.address.data.strip() if form.address.data else None,
            contact=form.contact.data.strip() if form.contact.data else None,
            latitude=form.latitude.data,
            longitude=form.longitude.data
        )
        db.session.add(resource)
        db.session.commit()
        flash("Resource added.")
        return redirect(url_for("admin_resources"))
    resources = Resource.query.order_by(Resource.updated_at.desc()).all()
    return render_template("resourcedirectory.html", resources=resources, form=form, admin=True)

# --------------------------------
# Emergency Plan Generator
# --------------------------------
@app.route("/emergencyplangenerator", methods=["GET", "POST"])
@login_required
def emergencyplangenerator():
    form = PlanForm()
    # Explanation: Capture user plan inputs and persist.
    if form.validate_on_submit():
        plan = EmergencyPlan(
            user_id=session["user_id"],
            household_members=form.household_members.data or 1,
            meeting_point=form.meeting_point.data.strip() if form.meeting_point.data else None,
            evacuation_routes=form.evacuation_routes.data.strip() if form.evacuation_routes.data else None,
            supply_checklist=form.supply_checklist.data.strip() if form.supply_checklist.data else None,
            notes=form.notes.data.strip() if form.notes.data else None
        )
        db.session.add(plan)
        db.session.commit()
        flash("Emergency plan saved.")
        return redirect(url_for("emergencyplangenerator"))
    plans = EmergencyPlan.query.filter_by(user_id=session["user_id"]).order_by(EmergencyPlan.created_at.desc()).all()
    return render_template("emergencyplangenerator.html", form=form, plans=plans)

# --------------------------------
# Personal information
# --------------------------------
@app.route("/personalinformation", methods=["GET", "POST"])
@login_required
def personalinformation():
    # Explanation: Simple profile view/update for user details.
    user = User.query.get_or_404(session["user_id"])
    if request.method == "POST":
        user.full_name = request.form.get("full_name") or user.full_name
        user.phone = request.form.get("phone") or user.phone
        user.address = request.form.get("address") or user.address
        db.session.commit()
        flash("Profile updated.")
        return redirect(url_for("personalinformation"))
    return render_template("personalinformation.html", user=user)

# --------------------------------
# Safety Check-in
# --------------------------------
@app.route("/safetycheck", methods=["GET", "POST"])
@login_required
def safetycheck():
    form = SafetyForm()
    # Explanation: Log safety status entry for the current user.
    if form.validate_on_submit():
        entry = SafetyCheck(user_id=session["user_id"], status=form.status.data, note=form.note.data)
        db.session.add(entry)
        db.session.commit()
        flash("Safety status updated.")
        return redirect(url_for("safetycheck"))
    history = SafetyCheck.query.filter_by(user_id=session["user_id"]).order_by(SafetyCheck.created_at.desc()).all()
    return render_template("safetycheck.html", form=form, history=history)

# --------------------------------
# App bootstrap
# --------------------------------
@app.cli.command("init-db")
def init_db():
    # Explanation: CLI helper to create tables and seed minimal data.
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email="jiananghelito29@gmail.com").first():
            admin = User(email="jiananghelito29@gmail.com", full_name="Jian Angelo Cutie", role="admin")
            admin.set_password("Admin@123")
            db.session.add(admin)
        if not Article.query.first():
            a1 = Article(title="Emergency Kit Guide", category="Emergency Kit Guide", content="Pack water, food, first aid, flashlight, radio.")
            a2 = Article(title="Contingency Plan Basics", category="Contingency Plan", content="Define roles, routes, contacts, and drills.")
            a3 = Article(title="Typhoon Safety Tips", category="Article", content="Secure windows, monitor advisories, prepare evacuation.")
            db.session.add_all([a1, a2, a3])
        db.session.commit()
        print("Database initialized with admin and sample articles.")

if __name__ == "__main__":
    # Explanation: Run development server.
    app.run(debug=True)
