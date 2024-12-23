import re

from fpdf import FPDF

from server_app import app, db
from server_app.models import *
from sqlalchemy.orm.exc import NoResultFound
import hashlib
from sqlalchemy import extract, func, not_
from io import BytesIO
from reportlab.pdfgen import canvas


class Role(UserEnum):
    Admin = 1
    Nurse = 2
    Doctor = 3
    Cashier = 4
    Patient = 5


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class NguoiDung(BaseModel, UserMixin):
    __tablename__ = 'nguoi_dung'
    hoTen = Column(String(50), nullable=False)
    gioiTinh = Column(String(10))
    namSinh = Column(DateTime)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100))
    email = Column(String(50))
    loaiNguoiDung = Column(Enum(Role))

    benhNhan = relationship("BenhNhan", uselist=False, back_populates="nguoiDung")
    yTa = relationship("YTa", uselist=False, back_populates="nguoiDung")
    bacSi = relationship("BacSi", uselist=False, back_populates="nguoiDung")
    thuNgan = relationship("ThuNgan", uselist=False, back_populates="nguoiDung")
    quanTriVien = relationship("QuanTriVien", uselist=False, back_populates="nguoiDung")

    def __str__(self):
        return self.hoTen


class BenhNhan(db.Model):
    __tablename__ = 'benh_nhan'
    id = Column(Integer, ForeignKey("nguoi_dung.id"), primary_key=True)
    diaChi = Column(String(100))
    soDienThoai = Column(String(100), nullable=False)

    phieuDangKy = relationship('PhieuDangKy', backref='benhNhan', lazy=True)
    phieuKham = relationship("PhieuKham", uselist=False, back_populates="benhNhan")
    nguoiDung = relationship("NguoiDung", back_populates="benhNhan")


class YTa(db.Model):
    __tablename__ = 'y_ta'
    id = Column(Integer, ForeignKey("nguoi_dung.id"), primary_key=True)
    phuTrach = Column(String(50))

    phieuDangKy = relationship('PhieuDangKy', backref='yTa', lazy=True)
    nguoiDung = relationship("NguoiDung", back_populates="yTa")


class BacSi(db.Model):
    __tablename__ = 'bac_si'
    id = Column(Integer, ForeignKey("nguoi_dung.id"), primary_key=True)
    chuyenMon = Column(String(100))

    phieuKham = relationship('PhieuKham', backref='bacSi', lazy=True)
    nguoiDung = relationship("NguoiDung", back_populates="bacSi")


class ThuNgan(db.Model):
    __tablename__ = 'thu_ngan'
    id = Column(Integer, ForeignKey("nguoi_dung.id"), primary_key=True)
    trinhDo = Column(String(50))

    hoaDon = relationship('HoaDon', backref='thuNgan', lazy=True)
    nguoiDung = relationship("NguoiDung", back_populates="thuNgan")


class QuanTriVien(db.Model):
    __tablename__ = 'quan_tri_vien'
    id = Column(Integer, ForeignKey("nguoi_dung.id"), primary_key=True)
    ghiChu = Column(String(100))

    nguoiDung = relationship("NguoiDung", back_populates="quanTriVien")
    quyDinh = relationship('QuyDinh', backref='quanTriVien', lazy=True)

    def __str__(self):
        return self.nguoiDung.hoTen