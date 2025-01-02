import json
import os.path
from server_app import app ,db
from server_app.models  import Thuoc ,Role, NguoiDung, ToaThuoc, PhieuKham,HoaDon
from flask_login import current_user
import hashlib
from sqlalchemy import func