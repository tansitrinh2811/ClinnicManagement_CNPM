import re

from fpdf import FPDF

from server_app import app, db
from server_app.models import *
from sqlalchemy.orm.exc import NoResultFound
import hashlib
from sqlalchemy import extract, func, not_
from io import BytesIO
from reportlab.pdfgen import canvas


def add_user(name, username, password):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = NguoiDung(hoTen=name.strip(),
                     username=username.strip(),
                     password=password,
                     loaiNguoiDung=Role.Patient)
    db.session.add(user)
    db.session.commit()


def check_login(username, password, userRole):
    if username and password and userRole:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
        # Tìm kiếm người dùng dựa trên tên đăng nhập va vai tro
        try:
            user = NguoiDung.query.filter_by(username=username.strip(), loaiNguoiDung=userRole).one()
        except NoResultFound:
            return None  # Trả về None nếu không tìm thấy người dùng

        # Kiểm tra mật khẩu
        if user.password == password:
            return user  # Trả về đối tượng người dùng nếu thông tin đăng nhập hợp lệ
        return None  # Trả về None nếu mật khẩu không khớp


def get_user_by_id(user_id):
    return NguoiDung.query.get(user_id)


def update_patient(user_id, **kwargs):
    user = NguoiDung.query.filter_by(id=user_id).first()

    if user:
        user.hoTen = kwargs.get('name')
        user.gioiTinh = kwargs.get('sex')
        user.namSinh = kwargs.get('birth')
        user.email = kwargs.get('email')
        user.avatar = kwargs.get('avatar')

    patient = BenhNhan(nguoiDung=user,
                       diaChi=kwargs.get('address'),
                       soDienThoai=kwargs.get('phone'))
    db.session.add(patient)
    db.session.commit()


def register_medical(**kwargs):
    patient_id = kwargs.get('patient_id')
    phone = kwargs.get('phone')
    nurse_id = kwargs.get('nurse_id')

    if patient_id:
        phieuDK = PhieuDangKy(benhNhan_id=patient_id,
                              yTa_id=nurse_id,
                              ngayKham=kwargs.get('date_time'))
    elif phone:
        benhNhan = BenhNhan.query.filter_by(soDienThoai=phone).first()
        phieuDK = PhieuDangKy(benhNhan_id=benhNhan.id,
                              yTa_id=nurse_id,
                              ngayKham=kwargs.get('date_time'))
    db.session.add(phieuDK)
    db.session.commit()


def count_register_medical(date):
    return PhieuDangKy.query.filter(func.date(PhieuDangKy.ngayKham).__eq__(date)).count()


def get_register_medical_by_date(**kwargs):
    query = db.session.query(
        NguoiDung.hoTen,
        BenhNhan.soDienThoai,
        PhieuDangKy.ngayKham,
        BenhNhan.id
    ).join(BenhNhan, PhieuDangKy.benhNhan_id.__eq__(BenhNhan.id)) \
        .join(NguoiDung, BenhNhan.id.__eq__(NguoiDung.id))

    date = kwargs.get('date')
    print(f"date ne: {date}")
    if date:
        query = query.filter(func.date(PhieuDangKy.ngayKham).__eq__(date))

    return query.all()


def check_medicine_exists(medicine_name):
    try:
        # Kiểm tra tên thuốc trong cơ sở dữ liệu
        result = Thuoc.query.filter(Thuoc.tenThuoc == medicine_name).first()

        if result is None:
            print(f"Không tìm thấy thuốc với tên: {medicine_name}")
        else:
            print(f"Thuốc tìm thấy: {result.tenThuoc}")  # Giả sử `tenThuoc` là trường tên thuốc

        return result is not None  # Trả về True nếu thuốc tồn tại, False nếu không

    except Exception as e:
        print(f"Đã xảy ra lỗi khi kiểm tra tên thuốc: {str(e)}")
        raise e  # Ném lỗi nếu có sự cố


def create_medical_list_pdf(data):
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer)

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 800, "Danh sách khám bệnh")
    y_coordinate = 750

    for record in data:
        pdf.drawString(100, y_coordinate,
                       f"Họ tên: {record[0]}, Ngày giờ khám: {record[2]}, Số điện thoại: {record[1]}")
        y_coordinate -= 20  # Giả sử mỗi dòng là 20 điểm

    pdf.save()
    pdf_buffer.seek(0)
    return pdf_buffer

