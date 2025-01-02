from flask import render_template, url_for, redirect, request, session, jsonify, send_file, Response, flash
from server_app import app, db, dao, login, utils, admin, client, verify_sid
from flask_login import login_user, logout_user, login_required, current_user
from server_app.models import Role, HoaDon, NguoiDung, PhieuKham
from datetime import datetime
import cloudinary
import cloudinary.uploader
import math

@app.route("/")
def home_page():
    return render_template("home_page.html")

@app.route("/register", methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        try:
            if(password.strip().__eq__(confirm.strip())):
                dao.add_user(name=name,
                             username=username,
                             password=password)
                return redirect(url_for('user_login'))
            else:
                err_msg = 'Mật khẩu không khớp'
        except Exception as ex:
            err_msg = 'Hệ thống đang có lỗi' +str(ex)

    return render_template("register_page.html",
                           err_msg=err_msg)

@app.route("/login", methods=['get', 'post'])
def user_login():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        userRole = request.form.get('userRole')

        user = dao.check_login(username=username,
                               password=password,
                               userRole=userRole)

        if user:
            login_user(user=user) #current_user

            return redirect(url_for('home_page'))
        else:
            err_msg = 'Username hoặc password không chính xác'

    return render_template("login_page.html",
                           err_msg=err_msg)

@app.route('/logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_login'))

@login.user_loader
def user_load(user_id):
    return dao.get_user_by_id(user_id=user_id)

@app.context_processor
def common_responses():
    return {
        'medicine_state': utils.counter_medicine(session.get('medicine')),
        'Role': Role
    }


@app.route("/patient_information")
def patient_information():
    return render_template("patient_infomation_page.html")


@app.route("/patient_information/<int:user_id>", methods=['get', 'post'])
def update_patient_infor(user_id):
    if request.method.__eq__('POST'):
        name = request.form.get('namebn')
        sex = request.form.get('sex')
        birth = request.form.get('birth')
        email = request.form.get('email')
        avatar = request.files.get('avatar')
        avatar_path = None
        if avatar:
            res = cloudinary.uploader.upload(avatar)
            avatar_path = res['secure_url']
        address = request.form.get('address')
        phone = request.form.get('phone')

        dao.update_patient(user_id=user_id,
                           name=name,
                           sex=sex,
                           birth=birth,
                           email=email,
                           avatar=avatar_path,
                           address=address,
                           phone=phone)
        return redirect(url_for('home_page'))


@app.route('/register_medical', methods=['get', 'post'])
def medical_register():
    msg = ''
    if not current_user.is_authenticated:
        return redirect('/login')
    elif current_user.loaiNguoiDung == Role.Patient:
        if request.method.__eq__('POST'):
            date = request.form.get('date')
            time = request.form.get('time')

            date_time = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M')
            count = dao.count_register_medical(date=date)
            quyDinh = dao.lay_so_luong('Mỗi ngày khám tối đa 40 bệnh nhân')

            if count >= 0 and count < quyDinh:
                dao.register_medical(patient_id=current_user.id,
                                     date_time=date_time)
            else:
                msg = 'Đã đủ số lượng đăng ký'

            if not msg:
                return redirect(url_for('home_page'))

    elif current_user.loaiNguoiDung == Role.Nurse:
        if request.method.__eq__('POST'):
            phone = request.form.get('phone')
            date = request.form.get('date')
            time = request.form.get('time')

            date_time = datetime.strptime(f'{date} {time}', '%Y-%m-%d %H:%M')
            count = dao.count_register_medical(date=date)
            quyDinh = dao.lay_so_luong('Mỗi ngày khám tối đa 40 bệnh nhân')
            print("count:" + str(count));
            print("quyDinh:" + str(quyDinh));
            if count >= 0 and count < quyDinh:
                dao.register_medical(phone=phone,
                                     date_time=date_time,
                                     nurse_id=current_user.id)
            else:
                msg = 'Đã đủ số lượng đăng ký'

            if not msg:
                return redirect(url_for('home_page'))
    return render_template('medical_register_page.html',
                           msg=msg)


@app.route("/medical_list", methods=['get'])
def medical_list():
    date = request.args.get('date')
    medical_list = dao.get_register_medical_by_date(date=date)

    return render_template('medical_examination_list_page.html',
                           medical_list=medical_list)


@app.route('/generate_pdf/<date>', methods=['GET'])
def generate_pdf(date):
    # date = request.args.get('date')
    print(f"date ne 123: {date}")

    medical_list = dao.get_register_medical_by_date(date=date)
    pdf = dao.create_medical_list_pdf(medical_list)
    pdf.seek(0)  # Đảm bảo con trỏ ở đầu tệp

    return send_file(
        pdf,
        download_name='medical_list.pdf',  # Sửa 'attachment_filename' thành 'download_name'
        as_attachment=True,
        mimetype='application/pdf'  # Thiết lập mimetype cho header
    )
