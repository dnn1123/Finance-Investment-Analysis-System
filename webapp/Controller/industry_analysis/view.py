from flask import Blueprint, redirect, render_template, url_for, request
import os
from flask_login import login_required, current_user

industry_analysis_view = Blueprint(
    'industry_analysis',
    __name__,
    template_folder=os.path.abspath(os.path.join(os.getcwd(),'webapp', 'Template', 'industry_analysis')),
    url_prefix="/industry_analysis"
)

@industry_analysis_view.route('/mymark', methods=('GET', 'POST'))
@login_required
def mymark():
    return render_template('mymark.html')

