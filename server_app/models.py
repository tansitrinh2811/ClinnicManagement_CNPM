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


class PhieuDangKy(BaseModel):
    __tablename__ = 'phieu_dang_ky'
    ngayKham = Column(DateTime, nullable=False, default=datetime.now)

    benhNhan_id = Column(Integer, ForeignKey('benh_nhan.id'), nullable=False)
    yTa_id = Column(Integer, ForeignKey('y_ta.id'))


class PhieuKham(BaseModel):
    __tablename__ = 'phieu_kham'
    ngayKham = Column(DateTime, nullable=False)
    trieuChung = Column(String(100))
    duDoan = Column(String(100))

    bacSi_id = Column(Integer, ForeignKey('bac_si.id'), nullable=False)
    benhNhan_id = Column(Integer, ForeignKey("benh_nhan.id"))
    benhNhan = relationship("BenhNhan", back_populates="phieuKham")
    hoaDon = relationship("HoaDon", uselist=False, back_populates="phieuKham")
    thuoc = relationship("ToaThuoc", backref="phieuKham")


class HoaDon(BaseModel):
    __tablename__ = 'hoa_don'
    tienKham = Column(Float, default=100000)
    tienThuoc = Column(Float, nullable=False)
    tongTien = Column(Float, nullable=False)
    ngayLap = Column(DateTime, nullable=False)

    thuNgan_id = Column(Integer, ForeignKey('thu_ngan.id'), nullable=False)
    phieuKham_id = Column(Integer, ForeignKey("phieu_kham.id"))
    phieuKham = relationship("PhieuKham", back_populates="hoaDon")


class Thuoc(BaseModel):
    __tablename__ = 'thuoc'
    tenThuoc = Column(String(50), nullable=False)
    ngaySX = Column(DateTime, nullable=False)
    hanSD = Column(DateTime, nullable=False)
    donGia = Column(Float, nullable=False)

    phieuKham = relationship("ToaThuoc", backref="thuoc")
    donViThuoc_id = Column(Integer, ForeignKey('don_vi_thuoc.id'), nullable=True, default=1)

    def __str__(self):
        return self.tenThuoc


class ToaThuoc(db.Model):
    __tablename__ = 'toa_thuoc'
    lieuLuong = Column(String(50), nullable=False)
    soLuong = Column(Integer, nullable=False)
    cachDung = Column(String(50))

    phieuKham_id = Column(ForeignKey('phieu_kham.id'), primary_key=True)
    thuoc_id = Column(ForeignKey('thuoc.id'), primary_key=True)


class DonViThuoc(BaseModel):
    __tablename__ = 'don_vi_thuoc'
    donVi = Column(String(50))

    thuoc = relationship('Thuoc', backref='donViThuoc', lazy=True)

    def __str__(self):
        return self.donVi


# trong models
class QuyDinh(BaseModel):
    __tablename__ = 'quy_dinh'
    tenQuyDinh = Column(String(50), nullable=False)
    moTa = Column(String(100))
    quanTriVien_id = Column(Integer, ForeignKey('quan_tri_vien.id'), nullable=True)