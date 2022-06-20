# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request, current_app
from flask_login import login_required
from jinja2 import TemplateNotFound


@blueprint.route('/index')
@login_required
def index():

    return render_template('home/index.html', segment='index')


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


@blueprint.route('/iauto_dashboard', defaults={'vehicle_id': ''})
@blueprint.route('/iauto_dashboard/<vehicle_id>')
@login_required
def dashboard_routing(vehicle_id):

    if vehicle_id.endswith('.html'):
        vehicle_id = vehicle_id[:vehicle_id.rfind('.')]

    # Vehicle ID exists and not resolved
    if vehicle_id and not current_app.vehicle.get(vehicle_id, None):
        current_app.logger.error(f'{vehicle_id} not available')
        return render_template('home/page-404.html'), 404

    else:

        return render_template('home/iauto_dashboard.html', vehicle_id = vehicle_id)

# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
