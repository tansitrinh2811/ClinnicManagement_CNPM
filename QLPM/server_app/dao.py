import re

from fpdf import FPDF

from server_app import app, db
from server_app.models import *
from sqlalchemy.orm.exc import NoResultFound
import hashlib
from sqlalchemy import extract, func, not_
from io import BytesIO
from reportlab.pdfgen import canvas