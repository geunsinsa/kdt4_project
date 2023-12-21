from flask.blueprints import Blueprint
from flask import request
import Pages.modelPredict as predict



class ResponseBlueprint:
    '''

        이 클래스는..
          서버에 어떤 데이터를 요청했을 때 단순히 그 결과만 반환할 수 있도록 합니다.

    '''

    '''
        요청 응답용의 블루프린트를 초기화하고 메인 라우팅을 등록합니다.
    '''
    def __init__(self):
        self.__bp = Blueprint("request","request",url_prefix="/request")
        self.__bp.route("/",methods=["POST"])(self.route_post)
        self.__bp.route("/",methods=["GET"])(self.route_get)
        pass


    '''
        이 메서드는
        내부의 라우팅을 정의하는 함수 입니다.
        
        어떤 요청이 들어온다면 그 요청에 따라 응답할 수 있도록 합니다.
    '''
    def route_post(self) -> str:
        #
        # 서버에 요청을 할 때 POST 내부 바디의 인자로 들어온 message1을 받습니다.
        # 서버에서 보내온 또 다른 데이터가 있는 경우 인자를 추가적으로 늘릴 수 있습니다.
        #
        message1 = str(request.form.get("message1"))
        #
        # 내부 처리 로직
        # 결과로 반환될 응답을 작성합니다.
        #
        #
        result =list(predict.sentence_generation(message1))
        # result2 = list(predict2.model_predict(message1))
        # result.extend(result2)

        result.sort( key=lambda x : x[1])
        result = result[::-1]
           
        ms=[]
        for x in result:
            ps = str(x[0]) +"|" + str(round(x[1]*100,2))
            ms.append(ps)
        ms ="\n".join(ms)
        return ms


    '''
        이 메서드는
        내부의 라우팅을 정의하는 함수 입니다.

         GET 요청에 대해서 응답을 거부합니다.
    '''

    def route_get(self) -> str:
        return "<h1><font color=red>Forbidden!</font> You can not access to /request/ by get_method.</h1>"

    '''
        블루프린트 속성을 반환합니다.
        이 속성은 추후 메인에서 연결할 때 사용해야 합니다.
    '''
    def get_blueprint(self):
        return self.__bp
