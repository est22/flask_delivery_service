from flask import Blueprint, render_template, request, url_for, session, flash
from rabbit_delivery.models import *
from werkzeug.utils import redirect
from bcrypt import hashpw, checkpw, gensalt

'''
view는 우리 눈에 보이는 부분을 관리합니다.

지난 시간에 작업했을 때는 view를 여러 파일로 분리하지 않았는데, 상황에 따라 파일을 분리할 수 있습니다.
그러면 어떻게 관리하냐고요?

어차피 각 파일마다 별도의 Blueprint를 만들테니, __init__.py에서 전부 import 하고
각각 다 register_blueprint를 활용해서 이어줍니다.

추가로, 코드를 보다보면 query를 사용한 것이 많은데, 이를 활용하면 SQL 구문을 직접 사용하지 않고
ORM을 통해 간접적으로 db에 작업 명령을 내릴 수 있습니다.
'''

bp = Blueprint('main', __name__, url_prefix='/')

@bp.route('/')
def home():
    store_list = rabbitStore.query.order_by(rabbitStore.name.asc())
    return render_template('main.html', store_list=store_list)

@bp.route('/store/<int:store_id>/')
def store_detail(store_id):
    store_info = rabbitStore.query.filter_by(id=store_id).first()
    store_menu = rabbitMenu.query.filter_by(store_id=store_id).all()
    return render_template('store_detail.html', store_info=store_info, store_menu=store_menu)

@bp.route('/login', methods=('GET',))
def login_try():
    return render_template('login.html')

'''
주의! 우리는 지난 시간에 회원가입/로그인을 빠르게 다루면서, 비밀번호 암호화에 대해 언급하지 않았습니다.
이 부분에 대해서는 다음 시간에 자세하게 설명하도록 할게요!!
우선, DB에서 데이터를 가져와서 비교하고, 비밀번호가 일치한다면 session 을 활성화 시킨다 정도만 이해하시면 됩니다.
'''

@bp.route('/login', methods=('POST',))
def login():
    id = request.form['user_id']
    password = request.form['password']

    user_data = rabbitUser.query.filter_by(id=id).first()

    if not user_data:
        flash("존재하지 않는 아이디입니다.")
        return redirect(url_for('main.login_try'))
    elif not checkpw(password.encode("utf-8"), user_data.password):
        flash("아이디와 비밀번호가 일치하지 않습니다.")
        return redirect(url_for('main.login_try'))
    else:
        session.clear()
        session['user_id'] = id
        session['nickname'] = user_data.nickname

        flash("안녕하세요, {}님!".format(user_data.nickname))

        return redirect(url_for('main.home'))

@bp.route('/register')
def join():
    return render_template('register.html')

@bp.route('/logout')
def logout():
    session.clear()
    flash("로그아웃 되었습니다.")
    return redirect(url_for('main.home'))

@bp.route('/register', methods=('POST',))
def register():
    if request.method == 'POST':
        user = rabbitUser.query.filter_by(id=request.form['user_id']).first()
        if not user:
            password = hashpw(request.form['password'].encode('utf-8'), gensalt())

            user = rabbitUser(id=request.form['user_id'], password=password,
            nickname=request.form['nickname'], telephone=request.form['telephone'])
            db.session.add(user)
            db.session.commit()
            
        else:
            flash("이미 가입된 아이디입니다.")
            return "이미 가입된 아이디입니다."

        return redirect(url_for('main.home'))