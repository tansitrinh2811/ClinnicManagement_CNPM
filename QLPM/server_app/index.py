from flask import render_template, url_for, redirect, request, session, jsonify, send_file, Response, flash
from server_app import app, db, dao, login, utils, admin, client, verify_sid
from flask_login import login_user, logout_user, login_required, current_user
from server_app.models import Role, HoaDon, NguoiDung, PhieuKham
from datetime import datetime
import cloudinary
import cloudinary.uploader
import math
