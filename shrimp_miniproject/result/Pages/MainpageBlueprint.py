from flask.blueprints import Blueprint
from flask import render_template

class MainpageBlueprint:
    '''

        이 클래스는..
         메인 홈페이지를 단순히 반환하는 라우팅을 생성하는 클래스입니다.

    '''

    '''
        메인 홈페이지의 블루프린트를 초기화하고 메인 라우팅을 등록합니다.
    '''
    def __init__(self):
        self.__bp = Blueprint("mainpage","mainpage",url_prefix="/")
        self.__bp.route("/")(self.route)
        pass


    '''
        이 메서드는
        내부의 라우팅을 정의하는 함수 입니다.
        
        실제 홈페이지가 여기서 반환되며, render_template를 사용하여
        index.html 의 내용을 반환합니다.
    '''
    def route(self) -> str:
        return render_template("index.html")

    '''
        블루프린트 속성을 반환합니다.
        이 속성은 추후 메인에서 연결할 때 사용해야 합니다.
    '''
    def get_blueprint(self):
        return self.__bp
